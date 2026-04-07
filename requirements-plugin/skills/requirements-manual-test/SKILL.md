---
name: requirements-manual-test
context: fork
description: 要件 YAML から手動テスト観点、手順、期待結果、観測ポイント、証跡収集項目を生成する。手動テストケースを作りたい、受入確認を準備したい、QA チェックリストが欲しい、「manual test を作って」「受入テスト観点を出して」と言われた時に使用する。
---

# Requirements Manual Test

## Overview

要件 YAML をそのまま人手確認に渡せる形へ変換する。
正常系だけではなく、否定例、境界、観測、証跡収集まで含めた手動確認パックを作る。

## Workflow

### Step 1: 要件から観点を抽出する

変換規則は references/manual-test-shaping.md を使う。
特に次の欄を重視する。

- `precondition`
- `guarantee`
- `forbid`
- `timing`
- `observable`
- `positive_examples`
- `negative_examples`

### Step 2: 手動確認ケースへ分解する

最低でも次の種類を作る。

- 正常系
- 否定例
- 境界例
- 観測確認

### Step 3: 証跡の取り方を明示する

画面、戻り値、ログ、イベント、トレースのどれを残すかを各ケースに付ける。
観測不能なケースは完成扱いにしない。

### Step 4: テストケースを整形する

出力は assets/templates/manual-test-case.md を使う。
各ケースに `req_id` を必ず持たせる。

### Step 5: 下流へ渡す

- 自動テスト候補と照らす: `/requirements-traceability`
- 抜け漏れ監査: `/test-design-audit`

## Output Contract

- 手動テストケース一覧
- 要件IDごとの確認観点
- 証跡収集メモ
