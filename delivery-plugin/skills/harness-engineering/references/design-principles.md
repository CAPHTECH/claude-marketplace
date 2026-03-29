# Harness Design Principles

この skill の scaffold は以下の原則を固定する。

## 1. Hermetic

- declared inputs だけで再実行できる
- external dependency は fixture / mock / trace artifact に落とす
- root repo の既存 build chain に依存しない

## 2. Deterministic

- case file は stable `id` を持つ
- report は machine-readable JSON と Markdown summary を両方出す
- run result は `reports/` と `traces/` に残す

## 3. Portable Core

- harness は `harness/` 以下の self-contained workspace とする
- repo root では additive な workflow / devcontainer profile だけ追加する
- target command との接続は environment variable contract に寄せる

## 4. Eval-Ready

- case taxonomy は `smoke`, `regression`, `edge`, `adversarial`
- `agent-eval` case は trace artifact を前提にする
- grader は stdout / exit / trace existence から始める

## 5. CI-Friendly

- GitHub Actions matrix を標準にする
- per-cell artifact upload を前提にする
- `fail-fast` と `max-parallel` を固定し、暴走を防ぐ
