/**
 * validate-report.ts — Validate autopsy report against JSON Schema
 *
 * Usage: node dist/validate-report.mjs <report.json> [--schema <schema.json>]
 */
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

export interface ValidationResult {
  valid: boolean;
  errors: Array<{ path: string; message: string }>;
}

export function validateReport(
  report: unknown,
  schema: Record<string, unknown>,
): ValidationResult {
  const ajv = new Ajv2020({ allErrors: true });
  addFormats(ajv);

  let validate;
  try {
    validate = ajv.compile(schema);
  } catch (e) {
    return {
      valid: false,
      errors: [{ path: "/", message: `Schema compilation failed: ${e instanceof Error ? e.message : e}` }],
    };
  }
  const valid = validate(report) as boolean;

  return {
    valid,
    errors: valid
      ? []
      : (validate.errors ?? []).map((e) => ({
          path: e.instancePath || "/",
          message: e.message ?? "unknown error",
        })),
  };
}

// --- CLI ---

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Usage: validate-report <report.json> [--schema <schema.json>]");
    process.exit(1);
  }

  const reportPath = args[0];
  const schemaIdx = args.indexOf("--schema");
  let schemaPath: string | undefined;
  if (schemaIdx >= 0) {
    const next = args[schemaIdx + 1];
    if (!next || next.startsWith("-")) {
      console.error("Error: --schema requires a path argument");
      process.exit(1);
    }
    schemaPath = next;
  }

  if (!schemaPath) {
    // Default: autopsy-schema.json relative to skill references
    const __dirname = dirname(fileURLToPath(import.meta.url));
    schemaPath = resolve(__dirname, "../../skills/disposable-cycle/references/autopsy-schema.json");
  }

  let report: unknown;
  let schema: Record<string, unknown>;
  try {
    report = JSON.parse(readFileSync(reportPath, "utf-8"));
  } catch (e) {
    console.error(`Error reading report: ${e instanceof Error ? e.message : e}`);
    process.exit(1);
  }
  try {
    schema = JSON.parse(readFileSync(schemaPath, "utf-8"));
  } catch (e) {
    console.error(`Error reading schema: ${e instanceof Error ? e.message : e}`);
    process.exit(1);
  }

  const result = validateReport(report, schema);

  if (result.valid) {
    console.log("Valid autopsy report.");
    process.exit(0);
  } else {
    console.error("Validation errors:");
    for (const err of result.errors) {
      console.error(`  ${err.path}: ${err.message}`);
    }
    process.exit(1);
  }
}

const isMain = process.argv[1]?.endsWith("validate-report.mjs") || process.argv[1]?.endsWith("validate-report.ts");
if (isMain) main();
