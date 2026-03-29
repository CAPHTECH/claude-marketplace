---
name: harness-engineering
description: Harness Engineering environmentを設計・scaffold・validateする。AI/agent eval と integration/regression harness の共通基盤を作り、cases・fixtures・reporting・CI・devcontainer を整える。Use when 「Harness環境を作って」「評価ハーネスを整備して」「回帰検証環境を構築して」 or 「benchmark/eval harness を仕込んで」と言われた時。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[init|validate] [--profile hybrid|agent-eval|software] [--root <path>]"
---

# harness-engineering

Portable Core + TS-first の Harness Engineering 環境を current repo に追加する。

このスキルは以下を扱う:

- `init`: ハーネス環境を scaffold する
- `validate`: scaffold 済み環境の整合性を検証する

v1 は GitHub Actions と additive な devcontainer profile を標準にする。
他の CI や IDE 統合は [extension-patterns.md](references/extension-patterns.md) を参照し、必要な時だけ拡張する。

## Quick Start

### 1. 初回ビルド

スキルディレクトリ内の `scripts/` で一度だけ依存を入れてビルドする。

```bash
cd scripts
npm install
npm run build
```

### 2. Harness を作る

引数なしは `init --profile hybrid --root .` として扱う。

```bash
cd scripts
node dist/init.mjs --root . --profile hybrid
```

### 3. Scaffold を検証する

```bash
cd scripts
node dist/validate.mjs --root .
```

### 4. 生成された Harness を起動する

```bash
npm --prefix harness install
npm --prefix harness run smoke
```

## Modes

### `init`

以下を current repo に追加する。

- `harness/` self-contained workspace
- `.github/workflows/harness.yml`
- `.devcontainer/harness/devcontainer.json`

`init` は既存ファイルを上書きしない。衝突があれば一覧を出して停止する。

### `validate`

以下をチェックする。

- required file の存在
- `harness/harness.config.json` の profile/targets/artifacts
- case JSON の `id` 重複、mode/profile 整合、tag 妥当性
- reports/traces の ignore
- workflow / devcontainer profile の存在

## Inputs

```text
init|validate
  --profile hybrid|agent-eval|software
  --root <path>
```

- `--profile` default: `hybrid`
- `--root` default: `.`

## Workflow

### Step 1: profile を確定する

- `hybrid`: software と agent-eval の両方を残す
- `software`: software target と sample cases だけ残す
- `agent-eval`: trace/grader 向け sample を残す

profile 選定の判断基準は [profiles.md](references/profiles.md) を参照する。

### Step 2: scaffold する

`scripts/dist/init.mjs` は `assets/templates/` を root へ展開し、profile に応じて config と sample cases を絞り込む。

設計原則や layout の意図が必要な時だけ [design-principles.md](references/design-principles.md) を読む。

### Step 3: validate する

`scripts/dist/validate.mjs` で構造と case contract を検証する。

validation が通ったら、生成された `harness/` workspace 側で以下を実行する。

```bash
npm --prefix harness install
npm --prefix harness run build
npm --prefix harness run validate
npm --prefix harness run smoke
```

### Step 4: 必要なら拡張する

外部 API mock、CI matrix 拡張、trace grading 強化は [extension-patterns.md](references/extension-patterns.md) を参照する。

## Guardrails

- repo root の既存 `.devcontainer/devcontainer.json` は触らない
- repo root の既存 `package.json` は触らない
- `harness/` 配下に閉じた workspace として追加する
- traces / reports は artifact として残し、git 管理しない
- profile に不要な sample cases は残さない
