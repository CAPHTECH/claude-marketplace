# Static Analysis Tools

言語別の静的解析ツール検出・実行テーブル。

## 実行順序（言語非依存）

**lint → format-check → type-check → security-scan**

各ステップの失敗は後続ステップの実行を妨げない。全ステップの結果を収集する。

## 言語別ツールテーブル

### JavaScript / TypeScript

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | ESLint | `eslint.config.*` or `.eslintrc*` or `package.json:eslintConfig` | `npx eslint --no-warn-ignored <files>` |
| Lint | Biome | `biome.json` or `biome.jsonc` | `npx biome check <files>` |
| Format | Prettier | `.prettierrc*` or `package.json:prettier` | `npx prettier --check <files>` |
| Type | TypeScript | `tsconfig.json` | `npx tsc --noEmit` |
| Security | npm audit | `package-lock.json` | `npm audit --omit=dev` |
| Security | pnpm audit | `pnpm-lock.yaml` | `pnpm audit --prod` |
| Security | yarn audit | `yarn.lock` | `yarn audit --groups dependencies` |

**検出ヒント:**
- `package.json` の `devDependencies` でツール有無を確認
- ESLint v9+ は flat config (`eslint.config.*`)
- `deno.json` がある場合は `deno lint` / `deno check` を使用

### Python

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | Ruff | `ruff.toml` or `pyproject.toml:[tool.ruff]` | `ruff check <files>` |
| Lint | Flake8 | `.flake8` or `setup.cfg:[flake8]` | `flake8 <files>` |
| Format | Ruff | (Ruff存在時) | `ruff format --check <files>` |
| Format | Black | `pyproject.toml:[tool.black]` | `black --check <files>` |
| Type | mypy | `mypy.ini` or `pyproject.toml:[tool.mypy]` | `mypy <files>` |
| Type | pyright | `pyrightconfig.json` | `pyright <files>` |
| Security | bandit | `pyproject.toml:[tool.bandit]` | `bandit -r <files>` |
| Security | pip-audit | `requirements.txt` | `pip-audit` |

**検出ヒント:**
- `pyproject.toml` の `[tool.*]` セクションでツール設定を確認
- Ruff は Flake8/isort/Black の代替として普及

### Go

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | golangci-lint | `.golangci.yml` or `.golangci.yaml` | `golangci-lint run ./...` |
| Lint | go vet | (Go プロジェクト) | `go vet ./...` |
| Format | gofmt | (Go プロジェクト) | `gofmt -l <files>` |
| Type | go build | `go.mod` | `go build ./...` |
| Security | govulncheck | (Go プロジェクト) | `govulncheck ./...` |

**検出ヒント:**
- `go.mod` があれば Go プロジェクト
- golangci-lint が最も包括的

### Rust

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | Clippy | `Cargo.toml` | `cargo clippy -- -D warnings` |
| Format | rustfmt | `Cargo.toml` | `cargo fmt --check` |
| Type/Build | cargo check | `Cargo.toml` | `cargo check` |
| Security | cargo-audit | `Cargo.lock` | `cargo audit` |

### Ruby

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | RuboCop | `.rubocop.yml` | `rubocop <files>` |
| Type | Sorbet | `sorbet/config` | `srb tc` |
| Security | Brakeman | `Gemfile` (Rails) | `brakeman -q` |
| Security | bundler-audit | `Gemfile.lock` | `bundle audit check` |

### Dart / Flutter

| Category | Tool | 検出条件 | 実行コマンド |
|----------|------|---------|-------------|
| Lint | dart analyze | `analysis_options.yaml` | `dart analyze <files>` |
| Format | dart format | (Dart プロジェクト) | `dart format --set-exit-if-changed <files>` |
| Type | dart analyze | `pubspec.yaml` | (lint と同時実行) |

## ツール不在時の対応

検出されたツールがインストールされていない場合:
1. 結果に `[tool-not-installed: <tool>]` を記録
2. 可能な代替ツールを試行（例: Flake8 不在 → Ruff で代替）
3. ツールなしでも LLM Review (Phase 3) は実行する

## 結果の構造化

```
## Static Analysis Results

### Lint
- Tool: ESLint v9.x
- Status: ⚠ 3 warnings, 0 errors
- Details:
  - src/api.ts:42 — no-unused-vars: 'tempResult' is defined but never used
  - src/api.ts:78 — @typescript-eslint/no-explicit-any: Unexpected any
  - src/utils.ts:15 — prefer-const: 'config' is never reassigned

### Type Check
- Tool: tsc 5.x
- Status: ✅ No errors

### Security
- Tool: npm audit
- Status: ⚠ 1 moderate vulnerability
- Details:
  - lodash < 4.17.21: Prototype Pollution (moderate)
```
