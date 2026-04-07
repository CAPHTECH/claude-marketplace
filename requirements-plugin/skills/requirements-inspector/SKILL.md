---
name: requirements-inspector
context: fork
argument-hint: "lint | diff | full (default: full)"
description: 要件 YAML の必須項目欠落、矛盾、古いリンク、差分との不一致を検査し、反例駆動の下流検査へつなぐ。要件レビュー、変更前ゲート、仕様とコードの乖離確認、「requirements を検査して」「要件 lint して」と言われた時に使用する。
---

# Requirements Inspector

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `lint` | 要件定義の静的検査 | YAML 必須項目、観測可能性、例の有無、基本矛盾を確認する |
| `diff` | 変更差分の検査 | 要件、テスト、コード、Telemetry の差分不整合を確認する |
| `full` | 静的検査 + 差分検査 | 省略時の既定値 |

## Overview

要件 YAML をレビューの感想で終わらせず、欠落、矛盾、古いリンク、差分不整合として検査する。
反例や下流検査に進める前の入口ゲートとして使う。

## Workflow

### Step 1: lint ルールを適用する

検査規則は references/inspection-rules.md を使う。
最低でも次を確認する。

- 必須欄の欠落
- `observable` の空欄
- `negative_examples` の欠落
- 同一 ID の重複
- 露骨な相互矛盾

繰り返し実行する静的検査は scripts/lint_requirements.py を使ってよい。

```bash
python3 requirements-plugin/skills/requirements-inspector/scripts/lint_requirements.py <requirements-dir-or-file>
```

このスクリプトは、要件 YAML の必須欄、空欄、ID 重複、基本矛盾を検査する。
意味的に深い矛盾や実装差分との整合性は、人の判断か下流スキルへ渡す。

### Step 2: 差分ルールを適用する

`$ARGUMENTS` が `diff` か `full` の時は、変更差分とリンク関係を見る。

- コードだけ変わって要件やテストが不変
- 要件だけ変わってテストや観測が不変
- 廃止済み要件に現行コードやテストがぶら下がる
- 要件IDを持たない観測点だけが増える

### Step 3: 深い検査への接続要否を決める

以下に当たる場合は、単純 lint で終わらせない。

- 重要要件に時間制約や状態遷移がある
- 相互矛盾の疑いが強い
- 差分ルールで複数の不整合が出た

その場合は次へ渡す。

- 多層整合性: `/requirements-consistency`
- テスト設計監査: `/test-design-audit`
- 要件リンク補完: `/requirements-traceability`

### Step 4: レポート化する

出力は assets/templates/inspection-report.md を使う。
各指摘に `severity`、`evidence`、`next_action` を付ける。

## Output Contract

- inspection report
- lint error list
- diff inconsistency list
- 下流検査の推奨先

## Stop Conditions

- 要件ファイル自体が読めない
- ID 重複で判定不能
- 主要要件の半数以上で `observable` が空
