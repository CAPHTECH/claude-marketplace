---
name: disposable-spike
context: fork
argument-hint: "<requirements or issue ref>"
description: Generate a disposable prototype (spike) from requirements. Creates isolated branch, generates code, runs lint/test/coverage, and produces unified metrics. Part of H-DGM (Hybrid Disposable Generation Method) cycle. Use when starting a new disposable prototype, rapid exploration, or throwaway implementation.
---

# Disposable Spike — Phase 1: Generate

Generate a disposable prototype from requirements, collect metrics, and prepare for autopsy analysis.

## Prerequisites

- Project has language toolchain installed (see references/tool-profiles.yml in disposable-cycle)
- Git repository with clean working tree
- `.disposable/` directory will be created if absent

## Procedure

### Step 1: Initialize Cycle

1. Determine cycle number:
   - If `.disposable/history.json` exists, read last cycle number and increment
   - Otherwise start at `cycle_1`
2. Create cycle directory: `.disposable/cycles/cycle_{N}/`
3. Check `.disposable/.lock` — if locked and not expired (60min TTL), abort with message
4. Write `.disposable/.lock` with PID, timestamp, TTL

### Step 2: Detect Language & Tool Profile

1. Scan project root for language indicators:
   - `tsconfig.json` / `package.json` → TypeScript
   - `pubspec.yaml` → Dart
   - `Package.swift` / `*.xcodeproj` → Swift
   - `mix.exs` → Elixir
   - `Cargo.toml` → Rust
2. Load matching tool profile from disposable-cycle references/tool-profiles.yml
3. If no match found, ask user to specify language

### Step 3: Create Isolated Branch

```bash
git checkout -b disposable/cycle_{N} HEAD
```

### Step 4: Generate Prototype

1. Read `$ARGUMENTS` as requirements specification
2. Generate implementation code following these constraints:
   - **Speed over perfection** — this code will be thrown away
   - **Cover the interface surface** — focus on API shape and behavior
   - **Include basic tests** — enough for autopsy metrics, not production quality
   - **No external network calls** (per security-policy.md)
3. Commit generated code:
   ```bash
   git add -A && git commit -m "spike(cycle_{N}): disposable prototype"
   ```

### Step 5: Collect Metrics

Run tool profile commands in order:

1. **Lint**: Execute lint command from tool profile, capture output
   - For non-ESLint formats (dart-analyze-json, swiftlint-json, credo-json, cargo-json): convert to ESLint JSON array format `[{ messages: [{ severity: 1|2, ... }] }]` before passing to aggregate
   - Use the tool profile's `severityMap` for mapping
2. **Test**: Execute test command (prefer `junitCommand` if available), capture JUnit XML output
   - For Dart (`dart test --reporter=json`): use `junitCommand` or convert JSON to JUnit XML before passing to aggregate
3. **Coverage**: Execute coverage command, capture LCOV output
   - If tool profile has `tool: null` (e.g., Swift coverage): skip `--coverage` argument in aggregate call

### Step 6: Aggregate Metrics

```bash
node {plugin_root}/scripts/dist/aggregate.mjs \
  --lint {tool_profile.lint.outputPath} \
  --test {tool_profile.test.outputPath} \
  --coverage {tool_profile.coverage.outputPath} \
  --cycle cycle_{N} \
  --lang {detected_language} \
  -o .disposable/cycles/cycle_{N}/spike-complete.json
```

Note: `{tool_profile.*}` paths come from the selected tool profile in references/tool-profiles.yml. Do not hardcode paths — each language has different output paths and formats. Omit `--lint`, `--test`, or `--coverage` arguments when the corresponding tool profile has `tool: null` (e.g., Swift coverage is not yet supported).

### Step 7: Mask & Finalize

1. Run sensitive data masking:
   ```bash
   node {plugin_root}/scripts/dist/mask-sensitive.mjs \
     .disposable/cycles/cycle_{N}/spike-complete.json --in-place
   ```
2. Release lock: remove `.disposable/.lock`
3. Report summary to user:
   - Cycle ID
   - Language detected
   - Lint issues (error/warning/info)
   - Test results (pass/fail/skip)
   - Coverage percentages
   - Data completeness flags

## Output

- `.disposable/cycles/cycle_{N}/spike-complete.json` — unified metrics (metrics-schema.json)
- Generated code on `disposable/cycle_{N}` branch
- Spike is ready for `/disposable-autopsy`

## Error Handling

- If lint/test/coverage tool fails: set `dataCompleteness.{source}=false`, continue with available data
- If git branch creation fails: abort with clean error message
- If lock exists: show lock info (PID, age) and ask user to force-release or wait
