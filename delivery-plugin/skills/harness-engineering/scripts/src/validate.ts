import { readJson } from "./shared.js";
import { access, readdir, readFile } from "node:fs/promises";
import { constants } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { parseCommonArgs } from "./shared.js";

interface HarnessCase {
  id: string;
  mode: "software" | "agent-eval";
  tags: string[];
  expect: {
    exitCode?: number;
    stdoutIncludes?: string[];
    writesTrace?: boolean;
  };
}

interface HarnessConfig {
  profile: "hybrid" | "software" | "agent-eval";
  targets: {
    software?: { command: string };
    agentEval?: { command: string };
  };
  artifacts: {
    reportsDir: string;
    tracesDir: string;
  };
}

const REQUIRED_PATHS = [
  "harness/package.json",
  "harness/tsconfig.json",
  "harness/harness.config.json",
  "harness/src/cli.ts",
  "harness/reports/.gitignore",
  "harness/traces/.gitignore",
  ".github/workflows/harness.yml",
  ".devcontainer/harness/devcontainer.json",
];

async function exists(path: string): Promise<boolean> {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function walkJsonFiles(dir: string): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true });
  const results = await Promise.all(
    entries.map(async (entry) => {
      const entryPath = resolve(dir, entry.name);
      if (entry.isDirectory()) {
        return walkJsonFiles(entryPath);
      }
      return entry.name.endsWith(".json") ? [entryPath] : [];
    }),
  );
  return results.flat();
}

export async function validateScaffold(root: string): Promise<string[]> {
  const errors: string[] = [];

  for (const relativePath of REQUIRED_PATHS) {
    if (!(await exists(resolve(root, relativePath)))) {
      errors.push(`Missing required file: ${relativePath}`);
    }
  }

  if (errors.length > 0) {
    return errors;
  }

  const config = await readJson<HarnessConfig>(resolve(root, "harness", "harness.config.json"));
  if (!["hybrid", "software", "agent-eval"].includes(config.profile)) {
    errors.push(`Unsupported profile: ${config.profile}`);
  }

  if (config.profile !== "agent-eval" && !config.targets.software?.command) {
    errors.push("software target command is required");
  }

  if (config.profile !== "software" && !config.targets.agentEval?.command) {
    errors.push("agentEval target command is required");
  }

  const caseFiles = await walkJsonFiles(resolve(root, "harness", "cases"));
  const ids = new Set<string>();
  for (const file of caseFiles) {
    const caseItem = JSON.parse(await readFile(file, "utf8")) as HarnessCase;
    if (ids.has(caseItem.id)) {
      errors.push(`Duplicate case id: ${caseItem.id}`);
    }
    ids.add(caseItem.id);

    if (config.profile === "software" && caseItem.mode !== "software") {
      errors.push(`software profile contains non-software case: ${caseItem.id}`);
    }
    if (config.profile === "agent-eval" && caseItem.mode !== "agent-eval") {
      errors.push(`agent-eval profile contains non-agent case: ${caseItem.id}`);
    }
  }

  return errors;
}

async function main(): Promise<void> {
  const args = parseCommonArgs(process.argv.slice(2));
  const errors = await validateScaffold(args.root);
  if (errors.length > 0) {
    console.error(errors.map((entry) => `- ${entry}`).join("\n"));
    process.exitCode = 1;
    return;
  }
  console.log(`Harness scaffold is valid: ${args.root}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
