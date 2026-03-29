import { build } from "esbuild";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

await build({
  entryPoints: [
    resolve(__dirname, "src/init.ts"),
    resolve(__dirname, "src/validate.ts"),
  ],
  bundle: true,
  platform: "node",
  target: "node20",
  format: "esm",
  outdir: resolve(__dirname, "dist"),
  outExtension: { ".js": ".mjs" },
  banner: { js: "#!/usr/bin/env node" },
});

console.log("Build complete: dist/*.mjs");
