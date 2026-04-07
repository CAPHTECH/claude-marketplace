---
name: requirements-catalog
context: fork
description: 要件 YAML 群をカタログ化し、状態、優先度、依存、置き換え関係、棚卸し結果を整える。要件一覧を管理したい、変更影響を追いたい、「requirements catalog を更新して」「要件の棚卸しをして」と言われた時に使用する。
---

# Requirements Catalog

## Overview

散らばった要件 YAML を一覧として管理し、どれが現行で、どれが廃止済みで、どれが未接地かを見えるようにする。
単なる一覧表ではなく、差分管理と依存関係の起点を作る。

## Workflow

### Step 1: 要件を棚卸しする

対象の YAML 群を走査し、ID、タイトル、状態、優先度、依存関係を集める。
状態遷移と依存の扱いは references/catalog-lifecycle.md を使う。

### Step 2: カタログへ正規化する

一覧は assets/templates/requirements-catalog.yaml をベースに作る。
最低限、次をそろえる。

- `requirements`
- `status_summary`
- `priority_summary`
- `dependency_edges`
- `supersession_edges`
- `orphan_requirements`

### Step 3: 変更履歴を明示する

新規、更新、廃止、置換を分ける。
`deprecated` と `superseded` を混同しない。

### Step 4: 運用上の穴を出す

次のような要件を別枠で報告する。

- 依存先が不明
- 廃止済みなのに下流リンクが残る
- `draft` のまま長く残る
- `active` なのに `links` が空

### Step 5: 次の作業に渡す

- 実装やテストへ結ぶ: `/requirements-traceability`
- 差分検査する: `/requirements-inspector`
- 手動確認へ流す: `/requirements-manual-test`

## Output Contract

- カタログ YAML または一覧表
- 状態別サマリー
- 優先度別サマリー
- 依存関係と置換関係
- 追跡が必要な要件の一覧
