/**
 * aggregate.ts — SARIF/JUnit/LCOV → metrics.json
 *
 * Usage: node dist/aggregate.mjs --lint <path> --test <path> --coverage <path> --cycle <id> --lang <language> -o <output>
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { XMLParser } from "fast-xml-parser";

function safeInt(value: string | undefined, fallback = 0): number {
  const n = parseInt(value ?? String(fallback), 10);
  return Number.isFinite(n) ? n : fallback;
}

function safeFloat(value: string | undefined, fallback = 0): number {
  const n = parseFloat(value ?? String(fallback));
  return Number.isFinite(n) ? n : fallback;
}

// --- Types ---

interface LintCounts {
  error: number;
  warning: number;
  info: number;
  total: number;
}

interface TestResults {
  passed: number;
  failed: number;
  skipped: number;
  total: number;
  durationMs: number;
}

interface CoverageEntry {
  pct: number;
  covered: number;
  total: number;
}

interface Metrics {
  schemaVersion: "1.0.0";
  cycleId: string;
  parentCycleId?: string;
  language: string;
  timestamp: string;
  toolVersions: Record<string, string>;
  lint: LintCounts;
  tests: TestResults;
  coverage: { line: CoverageEntry; branch: CoverageEntry; function: CoverageEntry };
  dataCompleteness: { lint: boolean; tests: boolean; coverage: boolean };
}

// --- Parsers ---

export function parseSarifLint(content: string): LintCounts {
  const data = JSON.parse(content);
  const counts: LintCounts = { error: 0, warning: 0, info: 0, total: 0 };

  // ESLint JSON format: array of { messages: [{ severity: 1|2 }] }
  if (Array.isArray(data)) {
    // Validate non-empty arrays have ESLint-like structure (objects with messages property)
    if (data.length > 0 && !data.some((entry: unknown) => typeof entry === "object" && entry !== null && "messages" in entry)) {
      throw new Error("Unrecognized lint report format: array entries do not have 'messages' property (expected ESLint JSON)");
    }
    for (const file of data) {
      if (file == null || typeof file !== "object") continue;
      const messages = (file as Record<string, unknown>).messages;
      if (!Array.isArray(messages)) continue;
      for (const msg of messages) {
        if (msg == null || typeof msg !== "object") continue;
        if (msg.severity === 2) counts.error++;
        else if (msg.severity === 1) counts.warning++;
        else if (msg.severity === 0) counts.info++;
        // Skip entries with unrecognized severity (not 0, 1, or 2)
      }
    }
  }
  // SARIF format
  else if (data != null && typeof data === "object" && Array.isArray(data.runs)) {
    for (const run of data.runs) {
      if (run == null || typeof run !== "object") continue;
      for (const result of Array.isArray(run.results) ? run.results : []) {
        if (result == null || typeof result !== "object") continue;
        const level = result.level ?? "warning";
        if (level === "error") counts.error++;
        else if (level === "warning") counts.warning++;
        else counts.info++;
      }
    }
  }
  // Unrecognized format
  else {
    throw new Error("Unrecognized lint report format: expected ESLint JSON array or SARIF object with 'runs'");
  }

  counts.total = counts.error + counts.warning + counts.info;
  return counts;
}

export function parseJUnitTests(content: string): TestResults {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: "@_" });
  const doc = parser.parse(content);

  let passed = 0, failed = 0, skipped = 0, durationMs = 0;

  // Require JUnit root element (testsuites or testsuite)
  if (doc.testsuites === undefined && doc.testsuite === undefined) {
    throw new Error("Unrecognized test report format: expected JUnit XML with <testsuites> or <testsuite> root element");
  }

  const suites = Array.isArray(doc.testsuites?.testsuite)
    ? doc.testsuites.testsuite
    : doc.testsuites?.testsuite
      ? [doc.testsuites.testsuite]
      : doc.testsuite
        ? [doc.testsuite]
        : [];

  // Fallback: if <testsuites> has aggregate attributes but no child <testsuite>, use root attributes
  if (suites.length === 0 && doc.testsuites?.["@_tests"] !== undefined) {
    const tests = Math.max(0, safeInt(doc.testsuites["@_tests"]));
    const failures = Math.max(0, safeInt(doc.testsuites["@_failures"]));
    const errors = Math.max(0, safeInt(doc.testsuites["@_errors"]));
    const skip = Math.max(0, safeInt(doc.testsuites["@_skipped"]));
    const time = safeFloat(doc.testsuites["@_time"]);
    const f = failures + errors;
    const s = skip;
    const p = Math.max(0, tests - f - s);
    return { passed: p, failed: f, skipped: s, total: p + f + s, durationMs: Math.round(time * 1000) };
  }

  for (const suite of suites) {
    const time = safeFloat(suite["@_time"]);
    durationMs += time * 1000;

    // Prefer suite-level attributes, but fall back to counting testcase nodes
    if (suite["@_tests"] !== undefined) {
      const tests = Math.max(0, safeInt(suite["@_tests"]));
      const failures = Math.max(0, safeInt(suite["@_failures"]));
      const errors = Math.max(0, safeInt(suite["@_errors"]));
      const skip = Math.max(0, safeInt(suite["@_skipped"]));
      failed += failures + errors;
      skipped += skip;
      passed += tests - failures - errors - skip;
    } else {
      // Count from testcase child nodes
      const cases = Array.isArray(suite.testcase)
        ? suite.testcase
        : suite.testcase
          ? [suite.testcase]
          : [];
      for (const tc of cases) {
        if (tc.failure !== undefined || tc.error !== undefined) failed++;
        else if (tc.skipped !== undefined) skipped++;
        else passed++;
      }
    }
  }

  const safePassed = Math.max(0, passed);
  return {
    passed: safePassed,
    failed,
    skipped,
    total: safePassed + failed + skipped,
    durationMs: Math.round(durationMs),
  };
}

export function parseLcov(content: string): {
  line: CoverageEntry;
  branch: CoverageEntry;
  function: CoverageEntry;
} {
  let linesHit = 0, linesTotal = 0;
  let branchesHit = 0, branchesTotal = 0;
  let functionsHit = 0, functionsTotal = 0;
  let hasMarkers = false;

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.startsWith("LH:")) { linesHit += safeInt(trimmed.slice(3)); hasMarkers = true; }
    else if (trimmed.startsWith("LF:")) { linesTotal += safeInt(trimmed.slice(3)); hasMarkers = true; }
    else if (trimmed.startsWith("BRH:")) { branchesHit += safeInt(trimmed.slice(4)); hasMarkers = true; }
    else if (trimmed.startsWith("BRF:")) { branchesTotal += safeInt(trimmed.slice(4)); hasMarkers = true; }
    else if (trimmed.startsWith("FNH:")) { functionsHit += safeInt(trimmed.slice(4)); hasMarkers = true; }
    else if (trimmed.startsWith("FNF:")) { functionsTotal += safeInt(trimmed.slice(4)); hasMarkers = true; }
  }

  if (!hasMarkers && content.trim().length > 0) {
    throw new Error("Unrecognized coverage format: no LCOV markers (LF/LH/BRF/BRH/FNF/FNH) found");
  }

  const pct = (hit: number, total: number) =>
    total === 0 ? 0 : Math.round((hit / total) * 10000) / 100;

  // Clamp covered to not exceed total
  const clamp = (hit: number, total: number) => Math.min(Math.max(0, hit), Math.max(0, total));

  return {
    line: { pct: pct(clamp(linesHit, linesTotal), linesTotal), covered: clamp(linesHit, linesTotal), total: Math.max(0, linesTotal) },
    branch: { pct: pct(clamp(branchesHit, branchesTotal), branchesTotal), covered: clamp(branchesHit, branchesTotal), total: Math.max(0, branchesTotal) },
    function: { pct: pct(clamp(functionsHit, functionsTotal), functionsTotal), covered: clamp(functionsHit, functionsTotal), total: Math.max(0, functionsTotal) },
  };
}

// --- CLI ---

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (!next || next.startsWith("-")) {
        console.error(`Error: --${key} requires a value`);
        process.exit(1);
      }
      result[key] = next;
      i++;
    } else if (args[i] === "-o") {
      const next = args[i + 1];
      if (!next || next.startsWith("-")) {
        console.error("Error: -o requires an output path argument");
        process.exit(1);
      }
      result["output"] = next;
      i++;
    }
  }
  return result;
}

const SUPPORTED_LANGUAGES = ["typescript", "dart", "swift", "elixir", "rust"] as const;

function main() {
  const args = parseArgs(process.argv.slice(2));
  const cycleId = args["cycle"] ?? "cycle_1";
  const langArg = args["lang"] ?? "typescript";
  if (!SUPPORTED_LANGUAGES.includes(langArg as typeof SUPPORTED_LANGUAGES[number])) {
    console.error(`Error: unsupported language '${langArg}'. Supported: ${SUPPORTED_LANGUAGES.join(", ")}`);
    process.exit(1);
  }
  const language = langArg;
  const parentCycleId = args["parent"];
  const outputPath = args["output"] ?? ".disposable/metrics.json";

  const dataCompleteness = { lint: false, tests: false, coverage: false };
  let lint: LintCounts = { error: 0, warning: 0, info: 0, total: 0 };
  let tests: TestResults = { passed: 0, failed: 0, skipped: 0, total: 0, durationMs: 0 };
  let coverage = parseLcov("");

  if (args["lint"]) {
    try {
      lint = parseSarifLint(readFileSync(args["lint"], "utf-8"));
      dataCompleteness.lint = true;
    } catch (e) {
      console.warn(`Warning: Could not read lint report: ${e instanceof Error ? e.message : e}`);
    }
  }

  if (args["test"]) {
    try {
      tests = parseJUnitTests(readFileSync(args["test"], "utf-8"));
      dataCompleteness.tests = true;
    } catch (e) {
      console.warn(`Warning: Could not read test report: ${e instanceof Error ? e.message : e}`);
    }
  }

  if (args["coverage"]) {
    try {
      coverage = parseLcov(readFileSync(args["coverage"], "utf-8"));
      dataCompleteness.coverage = true;
    } catch (e) {
      console.warn(`Warning: Could not read coverage report: ${e instanceof Error ? e.message : e}`);
    }
  }

  const metrics: Metrics = {
    schemaVersion: "1.0.0",
    cycleId,
    ...(parentCycleId ? { parentCycleId } : {}),
    language,
    timestamp: new Date().toISOString(),
    toolVersions: {},
    lint,
    tests,
    coverage,
    dataCompleteness,
  };

  // Integrity check: tests.total must equal passed+failed+skipped
  if (metrics.tests.total !== metrics.tests.passed + metrics.tests.failed + metrics.tests.skipped) {
    console.warn(`Warning: tests.total (${metrics.tests.total}) != passed+failed+skipped (${metrics.tests.passed + metrics.tests.failed + metrics.tests.skipped}), correcting`);
    metrics.tests.total = metrics.tests.passed + metrics.tests.failed + metrics.tests.skipped;
  }

  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, JSON.stringify(metrics, null, 2) + "\n");
  console.log(`Metrics written to ${outputPath}`);
}

// Run only when executed directly
const isMain = process.argv[1]?.endsWith("aggregate.mjs") || process.argv[1]?.endsWith("aggregate.ts");
if (isMain) main();
