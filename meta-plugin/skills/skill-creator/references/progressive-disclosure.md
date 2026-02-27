# Progressive Disclosure パターン集

SKILL.mdの肥大化を防ぎ、コンテキスト効率を最大化するための構成パターン。

## 基本原則

- SKILL.md本体は500行以下
- 実行に必須の手順・判断条件・入出力だけをSKILL.mdに書く
- 背景説明・詳細例・仕様はreferences/に分離
- references/からの参照は1階層のみ（ネスト禁止）

## Pattern 1: ハイレベルガイド + リファレンス

コア手順をSKILL.mdに、詳細をreferences/に分離。最も一般的なパターン。

```markdown
# PDF Processing

## Quick Start
pdfplumberでテキスト抽出:
[コード例]

## Advanced Features
- **フォーム入力**: [references/forms.md](references/forms.md)
- **API仕様**: [references/api.md](references/api.md)
- **使用例**: [references/examples.md](references/examples.md)
```

Claudeは必要時にのみ references/ を読む。

## Pattern 2: ドメイン別分離

複数ドメインを扱うスキルで、無関係なコンテキストの読み込みを防ぐ。

```
bigquery-skill/
├── SKILL.md (概要 + ナビゲーション)
└── references/
    ├── finance.md    (売上、請求)
    ├── sales.md      (商談、パイプライン)
    ├── product.md    (API利用、機能)
    └── marketing.md  (キャンペーン)
```

SKILL.mdにはドメイン選択ガイドだけ書く:

```markdown
## Available Datasets

| ドメイン | 内容 | 参照 |
|----------|------|------|
| Finance | 売上、ARR、請求 | [references/finance.md](references/finance.md) |
| Sales | 商談、パイプライン | [references/sales.md](references/sales.md) |
| Product | API利用、機能 | [references/product.md](references/product.md) |
```

ユーザーがセールスについて聞いたら、Claudeは sales.md だけを読む。

## Pattern 3: フレームワーク/バリアント別分離

同じワークフローで技術スタックが異なる場合。

```
cloud-deploy/
├── SKILL.md (共通ワークフロー + プロバイダー選択)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

SKILL.mdにはプロバイダー非依存のワークフローと選択基準を書く。

## Pattern 4: 条件付き詳細

基本機能をSKILL.mdに、高度な機能をreferences/に。

```markdown
# DOCX Processing

## Creating Documents
docx-jsで新規ドキュメントを作成。[references/docx-js.md](references/docx-js.md) 参照。

## Editing Documents
シンプルな編集はXMLを直接操作。

**変更履歴が必要な場合**: [references/tracked-changes.md](references/tracked-changes.md)
**OOXML詳細が必要な場合**: [references/ooxml.md](references/ooxml.md)
```

Claudeは変更履歴やOOXML詳細が必要な時だけ該当ファイルを読む。

## SKILL.md本体の構成テンプレート

### ワークフロー型

```markdown
# [Skill Name]

## Overview
[1-2文の概要]

## Workflow
### Step 1: [アクション]
[手順]
### Step 2: [アクション]
[手順]

## Reference
- 詳細A → [references/a.md](references/a.md)
- 詳細B → [references/b.md](references/b.md)
```

### タスク型

```markdown
# [Skill Name]

## Quick Start
[最も一般的なタスクの最短手順]

## Tasks
### [タスクA]
[手順]
### [タスクB]
[手順]
```

### リファレンス型

```markdown
# [Skill Name]

## Guidelines
[ルール・規約の要約]

## Specifications
[重要な仕様のみ。詳細はreferences/へ]

## Usage
[適用方法]
```

## references/ ファイルのガイドライン

### ファイル名

- 記述的に: `form-validation-rules.md`（`doc2.md` ではなく）
- kebab-case を使用
- 内容が推測できる名前にする

### 構造

- 100行超のファイルにはTOC（目次）を冒頭に含める
- セクションを明確に分割
- コード例は具体的に（実際に動くコードを書く）

### 参照方法

SKILL.mdからの参照は必ず以下を含める:

1. **何が書いてあるか**（1行の説明）
2. **いつ読むべきか**（トリガー条件）
3. **リンク**（相対パス、フォワードスラッシュ）

```markdown
フォーム入力の詳細手順（fillable PDFを扱う場合に参照）→ [references/forms.md](references/forms.md)
```

## 判断フローチャート

```
その情報はスキル実行に必須か？
├── YES → SKILL.md本体に書く
└── NO → 特定の状況でのみ必要か？
    ├── YES → references/ に分離してSKILL.mdからリンク
    └── NO → 書かない（Claudeは既に知っている可能性が高い）
```
