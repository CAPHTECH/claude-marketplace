import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { scaffoldHarness } from "../src/init.js";
import { removeIfExists } from "../src/shared.js";
import { validateScaffold } from "../src/validate.js";

const tempDirs: string[] = [];

afterEach(async () => {
  for (const dir of tempDirs.splice(0)) {
    await removeIfExists(dir);
  }
});

describe("validateScaffold", () => {
  it("accepts a fresh scaffold", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "harness-engineering-"));
    tempDirs.push(root);

    await scaffoldHarness(root, "hybrid");
    await expect(validateScaffold(root)).resolves.toEqual([]);
  });

  it("detects duplicate case ids", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "harness-engineering-"));
    tempDirs.push(root);

    await scaffoldHarness(root, "hybrid");
    const duplicateCase = {
      id: "software-smoke",
      mode: "software",
      tags: ["smoke"],
      input: { message: "duplicate" },
      expect: { exitCode: 0, stdoutIncludes: ["duplicate"] },
    };
    await writeFile(
      resolve(root, "harness", "cases", "smoke", "duplicate.json"),
      `${JSON.stringify(duplicateCase, null, 2)}\n`,
    );

    await expect(validateScaffold(root)).resolves.toContain("Duplicate case id: software-smoke");
  });
});
