---
name: requirements-traceability
context: fork
description: 要件 ID を Law、テスト、コード、Telemetry、手動テストへ結び、トレーサビリティ行列と変更影響の起点を作る。要件から実装や検査へ配線したい、リンク漏れを見たい、「traceability を作って」「REQ と test を結んで」と言われた時に使用する。
---

# Requirements Traceability

## Overview

要件を孤立させず、下流アーティファクトへつなぐ。
実装、テスト、観測、手動確認がどの要件を支えているかを見える形にそろえる。

## Workflow

### Step 1: 要件の起点を集める

要件 YAML を読み、`id`、`title`、`guarantee`、`observable`、`links` を抽出する。
行列表現は references/traceability-matrix.md を使う。

### Step 2: 下流アーティファクトを結ぶ

最低でも次の列を埋める。

- Law
- automated tests
- code symbols
- telemetry
- manual checks

証拠が弱いリンクは `assumed` として分け、確定リンクと混ぜない。

### Step 3: 欠落を先に出す

次の欠落を優先して報告する。

- 要件はあるがテストがない
- 要件はあるが観測点がない
- テストはあるが支える要件IDがない
- コード変更点はあるが関連要件が結びついていない

### Step 4: 行列を更新する

出力は assets/templates/traceability-matrix.md の形に合わせる。
必要なら YAML 版でもよいが、レビューしやすい一覧を必ず作る。

### Step 5: 下流へ引き渡す

- 要件の質を検査する: `/requirements-inspector`
- 反例駆動の多層整合性を見る: `/requirements-consistency`
- 手動確認に落とす: `/requirements-manual-test`

## Output Contract

- traceability matrix
- orphan requirements
- orphan tests
- stale links
- 変更影響の候補
