---
name: requirements-author
context: fork
description: 自然言語の要求や議論メモを YAML 要件へ正規化し、REQ ID、観測方法、例、未確定事項までそろえる。要件定義書を作りたい、要件を YAML で管理したい、「要件を構造化して」「requirements yaml を作って」と言われた時に使用する。
---

# Requirements Author

## Overview

自然言語の要件を、そのまま比較しない。
1要件ごとに観測可能で検査可能な YAML に正規化し、後続のカタログ管理、トレーサビリティ、検査、手動テストへ渡せる形にする。

## Workflow

### Step 1: 入力を要件単位に分解する

新機能の説明、会議メモ、Issue、既存仕様の文章を読み、1つの保証ごとに分ける。
1レコードに複数の保証や複数の禁止事項を無理に混ぜない。

### Step 2: YAML へ正規化する

項目定義と必須欄は references/requirements-yaml-schema.md を読む。
出力は assets/templates/requirement.yaml を土台にし、少なくとも次をそろえる。

- `id`
- `title`
- `status`
- `priority`
- `context`
- `trigger`
- `precondition`
- `guarantee`
- `forbid`
- `timing`
- `observable`
- `positive_examples`
- `negative_examples`
- `links`
- `unknowns`

`observable` と `negative_examples` がない要件は未完成として扱う。

### Step 3: 曖昧さを露出する

埋められない欄を推測で埋めない。
代わりに次を明示する。

- `unknowns`: 未決定事項
- `assumptions`: 仮定した内容
- `questions_for_review`: 確認したい点

### Step 4: 要件IDを振る

ID規則は references/requirements-yaml-schema.md を使う。
既存の系列があればそれに合わせ、なければ `REQ-<domain>-<nnn>` を使う。

### Step 5: 次の運用先を示す

作成した YAML を次のスキルへ渡す。

- 要件一覧化: `/requirements-catalog`
- 実装やテストとの接続: `/requirements-traceability`
- 欠落や矛盾の検査: `/requirements-inspector`
- 手動確認手順の生成: `/requirements-manual-test`

## Output Contract

- 要件 YAML 本文
- 要件ごとの `unknowns`
- 要件ごとの `assumptions`
- 追加確認が必要な質問

## Stop Conditions

以下に当たったら完成扱いにしない。

- `observable` が書けない
- `negative_examples` が書けない
- 1つの要件に複数の独立保証が混ざっている
- 実装や運用で観測できる手段がまったくない
