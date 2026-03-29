import { mkdtemp, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { scaffoldHarness } from "../src/init.js";
import { removeIfExists } from "../src/shared.js";

const tempDirs: string[] = [];

afterEach(async () => {
  for (const dir of tempDirs.splice(0)) {
    await removeIfExists(dir);
  }
});

describe("scaffoldHarness", () => {
  it("creates the harness workspace and root integrations", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "harness-engineering-"));
    tempDirs.push(root);

    const created = await scaffoldHarness(root, "hybrid");
    expect(created).toContain("harness/");
    expect(await readFile(resolve(root, "harness", "package.json"), "utf8")).toContain("@generated/harness");
    expect(await readFile(resolve(root, ".github", "workflows", "harness.yml"), "utf8")).toContain("actions/upload-artifact");
  });

  it("filters cases for the software profile", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "harness-engineering-"));
    tempDirs.push(root);

    await scaffoldHarness(root, "software");
    const config = JSON.parse(await readFile(resolve(root, "harness", "harness.config.json"), "utf8"));
    expect(config.profile).toBe("software");
    expect(config.targets.agentEval).toBeUndefined();
  });
});
