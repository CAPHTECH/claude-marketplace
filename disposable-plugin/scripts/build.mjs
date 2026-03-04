import { build } from "esbuild";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

const entryPoints = [
  resolve(__dirname, "src/aggregate.ts"),
  resolve(__dirname, "src/validate-report.ts"),
  resolve(__dirname, "src/mask-sensitive.ts"),
];

await build({
  entryPoints,
  bundle: true,
  platform: "node",
  target: "node18",
  format: "esm",
  outdir: resolve(__dirname, "dist"),
  outExtension: { ".js": ".mjs" },
  banner: { js: "#!/usr/bin/env node" },
});

console.log("Build complete: dist/*.mjs");
