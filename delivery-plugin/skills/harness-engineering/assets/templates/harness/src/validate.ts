import { access } from "node:fs/promises";
import { constants } from "node:fs";
import { HarnessCase, HarnessConfig, discoverCases, loadConfig, resolveHarnessPath } from "./config.js";

const ALLOWED_TAGS = new Set(["smoke", "regression", "edge", "adversarial"]);

async function ensurePath(path: string, label: string, errors: string[]): Promise<void> {
  try {
    await access(path, constants.F_OK);
  } catch {
    errors.push(`Missing ${label}: ${path}`);
  }
}

function validateConfig(config: HarnessConfig, errors: string[]): void {
  if (!["hybrid", "software", "agent-eval"].includes(config.profile)) {
    errors.push(`Unsupported profile: ${config.profile}`);
  }

  if (!config.targets.software && config.profile !== "agent-eval") {
    errors.push("software target is required for hybrid/software profiles");
  }

  if (!config.targets.agentEval && config.profile !== "software") {
    errors.push("agentEval target is required for hybrid/agent-eval profiles");
  }

  if (!config.artifacts.reportsDir || !config.artifacts.tracesDir) {
    errors.push("artifacts.reportsDir and artifacts.tracesDir are required");
  }
}

function validateCase(caseItem: HarnessCase, config: HarnessConfig, seenIds: Set<string>, errors: string[]): void {
  if (!caseItem.id) {
    errors.push(`Case without id: ${caseItem.sourceFile ?? "<unknown>"}`);
    return;
  }

  if (seenIds.has(caseItem.id)) {
    errors.push(`Duplicate case id: ${caseItem.id}`);
  }
  seenIds.add(caseItem.id);

  if (!["software", "agent-eval"].includes(caseItem.mode)) {
    errors.push(`Unsupported mode for ${caseItem.id}: ${caseItem.mode}`);
  }

  if (config.profile === "software" && caseItem.mode !== "software") {
    errors.push(`software profile cannot contain ${caseItem.mode} case: ${caseItem.id}`);
  }

  if (config.profile === "agent-eval" && caseItem.mode !== "agent-eval") {
    errors.push(`agent-eval profile cannot contain ${caseItem.mode} case: ${caseItem.id}`);
  }

  if (!Array.isArray(caseItem.tags) || caseItem.tags.length === 0) {
    errors.push(`Case must have at least one tag: ${caseItem.id}`);
  } else {
    for (const tag of caseItem.tags) {
      if (!ALLOWED_TAGS.has(tag)) {
        errors.push(`Unsupported tag "${tag}" in ${caseItem.id}`);
      }
    }
  }

  if (caseItem.expect.exitCode !== undefined && typeof caseItem.expect.exitCode !== "number") {
    errors.push(`expect.exitCode must be a number in ${caseItem.id}`);
  }
}

export async function validateHarness(rootDir = process.cwd()): Promise<string[]> {
  const errors: string[] = [];
  await ensurePath(resolveHarnessPath(rootDir, "package.json"), "package.json", errors);
  await ensurePath(resolveHarnessPath(rootDir, "tsconfig.json"), "tsconfig.json", errors);
  await ensurePath(resolveHarnessPath(rootDir, "harness.config.json"), "harness.config.json", errors);
  await ensurePath(resolveHarnessPath(rootDir, "cases"), "cases directory", errors);
  await ensurePath(resolveHarnessPath(rootDir, "fixtures"), "fixtures directory", errors);
  await ensurePath(resolveHarnessPath(rootDir, "reports", ".gitignore"), "reports/.gitignore", errors);
  await ensurePath(resolveHarnessPath(rootDir, "traces", ".gitignore"), "traces/.gitignore", errors);

  if (errors.length > 0) {
    return errors;
  }

  const config = await loadConfig(rootDir);
  validateConfig(config, errors);
  const seenIds = new Set<string>();
  const cases = await discoverCases(rootDir);
  for (const caseItem of cases) {
    validateCase(caseItem, config, seenIds, errors);
  }
  return errors;
}
