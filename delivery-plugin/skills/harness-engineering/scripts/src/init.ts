import { cp, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { ParsedArgs, TEMPLATE_ROOT, ensureDir, parseCommonArgs, pathExists, removeIfExists, walkFiles, writeJson } from "./shared.js";

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
  matrix: {
    os: string[];
    node: string[];
  };
}

const SOFTWARE_CASES = [
  resolve("harness", "cases", "smoke", "software-smoke.json"),
  resolve("harness", "cases", "regression", "software-regression.json"),
];

const AGENT_CASES = [
  resolve("harness", "cases", "edge", "agent-eval-edge.json"),
  resolve("harness", "cases", "adversarial", "agent-eval-adversarial.json"),
];

async function renderProfile(root: string, profile: ParsedArgs["profile"]): Promise<void> {
  const configPath = resolve(root, "harness", "harness.config.json");
  const raw = await readFile(configPath, "utf8");
  const config = JSON.parse(raw.replace("__PROFILE__", profile)) as HarnessConfig;
  config.profile = profile;

  if (profile === "software") {
    delete config.targets.agentEval;
    for (const file of AGENT_CASES) {
      await removeIfExists(resolve(root, file));
    }
  }

  if (profile === "agent-eval") {
    delete config.targets.software;
    for (const file of SOFTWARE_CASES) {
      await removeIfExists(resolve(root, file));
    }
  }

  await writeJson(configPath, config);
}

async function collectConflicts(root: string): Promise<string[]> {
  const templateFiles = await walkFiles(TEMPLATE_ROOT);
  const conflicts: string[] = [];

  for (const templateFile of templateFiles) {
    const relativePath = templateFile.slice(TEMPLATE_ROOT.length + 1);
    const targetPath = resolve(root, relativePath);
    if (await pathExists(targetPath)) {
      conflicts.push(relativePath);
    }
  }

  return conflicts.sort();
}

export async function scaffoldHarness(root: string, profile: ParsedArgs["profile"]): Promise<string[]> {
  await ensureDir(root);
  const conflicts = await collectConflicts(root);
  if (conflicts.length > 0) {
    throw new Error(`Refusing to overwrite existing files:\n- ${conflicts.join("\n- ")}`);
  }

  const templateFiles = await walkFiles(TEMPLATE_ROOT);
  for (const templateFile of templateFiles) {
    const relativePath = templateFile.slice(TEMPLATE_ROOT.length + 1);
    const targetPath = resolve(root, relativePath);
    await ensureDir(dirname(targetPath));
    await cp(templateFile, targetPath);
  }

  await renderProfile(root, profile);

  return [
    "harness/",
    ".github/workflows/harness.yml",
    ".devcontainer/harness/devcontainer.json",
  ];
}

async function main(): Promise<void> {
  const args = parseCommonArgs(process.argv.slice(2));
  const created = await scaffoldHarness(args.root, args.profile);
  console.log(`Harness scaffolded at ${args.root}`);
  for (const entry of created) {
    console.log(`- ${entry}`);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
