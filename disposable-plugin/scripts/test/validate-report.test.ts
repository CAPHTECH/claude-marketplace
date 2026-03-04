import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { validateReport } from "../src/validate-report.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const schemaPath = resolve(
  __dirname,
  "../../skills/disposable-cycle/references/autopsy-schema.json",
);
const schema = JSON.parse(readFileSync(schemaPath, "utf-8"));

describe("validateReport", () => {
  it("accepts a valid autopsy report", () => {
    const report = {
      schemaVersion: "1.0.0",
      rubricVersion: "1.0.0",
      cycleId: "cycle_1",
      timestamp: "2026-03-04T00:00:00Z",
      axes: {
        correctness: { status: "scored", score: 4, findings: [] },
        architecture: { status: "scored", score: 3, findings: [] },
        security: { status: "scored", score: 4, findings: [] },
        performance: { status: "scored", score: 3, findings: [] },
        testability: { status: "scored", score: 4, findings: [] },
        readability: { status: "scored", score: 4, findings: [] },
        maintainability: { status: "scored", score: 3, findings: [] },
        "error-handling": { status: "scored", score: 3, findings: [] },
        "dependency-hygiene": { status: "scored", score: 4, findings: [] },
        documentation: { status: "na" },
      },
      summary: {
        verdict: "PASS",
        strengths: ["Clean architecture"],
        criticalIssues: [],
        averageScore: 3.6,
      },
    };

    const result = validateReport(report, schema);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("rejects report missing required fields", () => {
    const result = validateReport({}, schema);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it("rejects invalid score range", () => {
    const report = {
      schemaVersion: "1.0.0",
      rubricVersion: "1.0.0",
      cycleId: "cycle_1",
      timestamp: "2026-03-04T00:00:00Z",
      axes: {
        correctness: { status: "scored", score: 6, findings: [] },
        architecture: { status: "scored", score: 3, findings: [] },
        security: { status: "scored", score: 3, findings: [] },
        performance: { status: "scored", score: 3, findings: [] },
        testability: { status: "scored", score: 3, findings: [] },
        readability: { status: "scored", score: 3, findings: [] },
        maintainability: { status: "scored", score: 3, findings: [] },
        "error-handling": { status: "scored", score: 3, findings: [] },
        "dependency-hygiene": { status: "scored", score: 3, findings: [] },
        documentation: { status: "scored", score: 3, findings: [] },
      },
      summary: {
        verdict: "PASS",
        strengths: [],
        criticalIssues: [],
        averageScore: 3.0,
      },
    };
    const result = validateReport(report, schema);
    expect(result.valid).toBe(false);
  });
});
