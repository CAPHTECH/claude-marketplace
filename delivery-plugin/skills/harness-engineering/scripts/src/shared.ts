import { access, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export type HarnessProfile = "hybrid" | "software" | "agent-eval";

export interface ParsedArgs {
  profile: HarnessProfile;
  root: string;
}

export const SKILL_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
export const TEMPLATE_ROOT = resolve(SKILL_ROOT, "assets", "templates");

export async function pathExists(path: string): Promise<boolean> {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

export async function readJson<T>(path: string): Promise<T> {
  return JSON.parse(await readFile(path, "utf8")) as T;
}

export async function writeJson(path: string, value: unknown): Promise<void> {
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

export async function walkFiles(rootDir: string): Promise<string[]> {
  const entries = await readdir(rootDir, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const entryPath = resolve(rootDir, entry.name);
      if (entry.isDirectory()) {
        return walkFiles(entryPath);
      }
      return [entryPath];
    }),
  );
  return nested.flat();
}

export function relativeTemplatePath(templateFile: string): string {
  return templateFile.slice(TEMPLATE_ROOT.length + 1);
}

export function parseCommonArgs(argv: string[]): ParsedArgs {
  let profile: HarnessProfile = "hybrid";
  let root = ".";

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--profile") {
      profile = argv[index + 1] as HarnessProfile;
      index += 1;
    } else if (arg === "--root") {
      root = argv[index + 1] ?? ".";
      index += 1;
    }
  }

  if (!["hybrid", "software", "agent-eval"].includes(profile)) {
    throw new Error(`Unsupported profile: ${profile}`);
  }

  return {
    profile,
    root: resolve(root),
  };
}

export async function ensureDir(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}

export async function removeIfExists(path: string): Promise<void> {
  if (await pathExists(path)) {
    await rm(path, { recursive: true, force: true });
  }
}
