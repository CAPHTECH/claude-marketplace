import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { parseSarifLint, parseJUnitTests, parseLcov } from "../src/aggregate.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixtures = resolve(__dirname, "fixtures");

describe("parseSarifLint", () => {
  it("parses ESLint JSON format", () => {
    const content = readFileSync(resolve(fixtures, "eslint-report.json"), "utf-8");
    const result = parseSarifLint(content);
    expect(result).toEqual({ error: 2, warning: 2, info: 0, total: 4 });
  });

  it("skips null and non-object entries in ESLint messages", () => {
    const data = [{ messages: [null, 42, "x", { severity: 2 }, { severity: 1 }] }];
    const result = parseSarifLint(JSON.stringify(data));
    expect(result).toEqual({ error: 1, warning: 1, info: 0, total: 2 });
  });

  it("handles empty array", () => {
    const result = parseSarifLint("[]");
    expect(result).toEqual({ error: 0, warning: 0, info: 0, total: 0 });
  });

  it("skips null entries in SARIF results", () => {
    const sarif = { runs: [{ results: [null, { level: "error" }] }] };
    const result = parseSarifLint(JSON.stringify(sarif));
    expect(result).toEqual({ error: 1, warning: 0, info: 0, total: 1 });
  });

  it("parses SARIF format", () => {
    const sarif = {
      runs: [{
        results: [
          { level: "error" },
          { level: "warning" },
          { level: "note" },
        ],
      }],
    };
    const result = parseSarifLint(JSON.stringify(sarif));
    expect(result).toEqual({ error: 1, warning: 1, info: 1, total: 3 });
  });
});

describe("parseJUnitTests", () => {
  it("parses JUnit XML", () => {
    const content = readFileSync(resolve(fixtures, "test-report.xml"), "utf-8");
    const result = parseJUnitTests(content);
    expect(result.passed).toBe(3);
    expect(result.failed).toBe(1);
    expect(result.skipped).toBe(1);
    expect(result.total).toBe(5);
    expect(result.durationMs).toBe(342);
  });

  it("uses root testsuites attributes when no child testsuite exists", () => {
    const xml = '<testsuites tests="10" failures="2" errors="1" skipped="0" time="1.5"></testsuites>';
    const result = parseJUnitTests(xml);
    expect(result.passed).toBe(7);
    expect(result.failed).toBe(3);
    expect(result.skipped).toBe(0);
    expect(result.total).toBe(10);
    expect(result.durationMs).toBe(1500);
  });
});

describe("parseLcov", () => {
  it("parses LCOV info", () => {
    const content = readFileSync(resolve(fixtures, "lcov.info"), "utf-8");
    const result = parseLcov(content);

    // Lines: 68/80 = 85%
    expect(result.line.covered).toBe(68);
    expect(result.line.total).toBe(80);
    expect(result.line.pct).toBe(85);

    // Branches: 23/30 = 76.67%
    expect(result.branch.covered).toBe(23);
    expect(result.branch.total).toBe(30);
    expect(result.branch.pct).toBe(76.67);

    // Functions: 13/15 = 86.67%
    expect(result.function.covered).toBe(13);
    expect(result.function.total).toBe(15);
    expect(result.function.pct).toBe(86.67);
  });

  it("handles empty input", () => {
    const result = parseLcov("");
    expect(result.line).toEqual({ pct: 0, covered: 0, total: 0 });
  });

  it("throws on non-LCOV content", () => {
    expect(() => parseLcov("this is not lcov data")).toThrow("Unrecognized coverage format");
  });
});
