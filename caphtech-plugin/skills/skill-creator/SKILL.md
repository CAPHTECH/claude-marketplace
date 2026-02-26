---
name: skill-creator
description: Claude Code用のSkillを新規作成・更新するためのガイド。スキルの設計・実装・検証をベストプラクティスに基づいて進める。「スキルを作成して」「新しいスキルを作りたい」「skillを作って」「スキルを更新して」「スキルを改善して」と言われた時に使用する。
---

# Skill Creator

Claude Code用Skillの設計・実装・検証をガイドする。

## Core Principles

### 1. 簡潔さが最優先

コンテキストウィンドウは共有資源。Claudeはすでに賢い — Claudeが知らない情報だけを書く。
各段落に「このトークンコストは正当か？」と問う。冗長な説明より簡潔な例を優先。

### 2. 自由度の設計

タスクの壊れやすさに応じて指示の具体度を変える:

| 自由度 | 使い所 | 例 |
|--------|--------|-----|
| 高（テキスト指示） | 複数アプローチが有効、文脈依存 | コードレビュー観点 |
| 中（擬似コード） | 推奨パターンあり、多少の変動OK | APIコール手順 |
| 低（具体スクリプト） | 壊れやすい、一貫性必須 | PDF変換、デプロイ |

### 3. 段階的開示（Progressive Disclosure）

| レベル | 読み込みタイミング | サイズ目安 |
|--------|-------------------|-----------|
| description | 常時（起動時） | ~100 words |
| SKILL.md本体 | スキル起動時 | <5k words / 500行以下 |
| references/ | 必要時のみ | 無制限 |

500行を超えそうなら references/ に分割する。

## Skill Structure

```
skill-name/
├── SKILL.md           # メイン指示（必須）
├── references/        # 詳細ドキュメント（任意、オンデマンド読込）
├── scripts/           # 実行可能コード（任意、コンテキスト外で実行可能）
└── assets/            # 出力に使うファイル（任意、テンプレート等）
```

### SKILL.md（必須）

- **Frontmatter**（YAML）: `name` + `description` が必須。Claudeはこの情報だけでスキル選択を判断する
- **Body**（Markdown）: スキル起動後に読み込まれる指示

Frontmatter詳細 → [references/frontmatter-fields.md](references/frontmatter-fields.md)

### references/（任意）

Claudeが作業中に参照するドキュメント。SKILL.mdから明示的にリンクし、いつ読むべきか記述する。

- 1階層のみ（ネスト禁止）
- 100行超のファイルにはTOCを含める
- SKILL.mdと情報を重複させない

### scripts/（任意）

繰り返し書き直すコードや決定論的処理に使う。コンテキストに読み込まずに実行可能。

### assets/（任意）

出力に使うファイル（テンプレート、画像、フォント等）。コンテキストに読み込まない。

## Creation Process

### Step 1: ユースケースの理解

スキルの具体的な使い方を明確にする。ユーザーに質問:

- どんな機能をサポートすべきか？
- どんなフレーズでこのスキルが起動されるべきか？
- 具体的な使用例を見せてもらえるか？

一度に多くの質問をしない。最重要な質問から始め、必要に応じてフォローアップ。

### Step 2: リソースの計画

各ユースケースを分析し、再利用可能なリソースを特定:

| パターン | リソース種別 | 例 |
|----------|-------------|-----|
| 毎回同じコードを書く | scripts/ | PDF回転、画像変換 |
| 毎回同じ知識を調べ直す | references/ | DBスキーマ、API仕様 |
| 毎回同じボイラープレート | assets/ | HTMLテンプレート、フォント |

### Step 3: 初期化

新規作成の場合、initスクリプトを実行:

```bash
bash scripts/init_skill.sh <skill-name> <output-directory> [--references] [--scripts] [--assets]
```

既存スキルの更新ならこのステップをスキップ。

### Step 4: 実装

#### 4a. リソースファイルの作成

scripts/、references/、assets/ の中身を先に実装する。
追加したスクリプトは実際に実行してテストすること。

#### 4b. SKILL.md の記述

**Frontmatter**: descriptionが最重要 → [references/description-craft.md](references/description-craft.md)

**Body**: 以下のパターンから選択:

| パターン | 適用場面 | 構造 |
|----------|---------|------|
| ワークフロー型 | 順次処理 | Overview → Step 1 → Step 2 → ... |
| タスク型 | 複数操作 | Quick Start → Task A → Task B → ... |
| リファレンス型 | 規約・仕様 | Guidelines → Specifications → Usage |
| ケイパビリティ型 | 統合機能 | Core Capabilities → Feature 1 → Feature 2 |

コンテンツ構成の詳細 → [references/progressive-disclosure.md](references/progressive-disclosure.md)

#### 記述ルール

- 命令形を使う（「〜すること」ではなく「〜する」）
- references/ のファイルはSKILL.mdから明示的にリンクする
- 不要なドキュメント（README, CHANGELOG等）は作らない

### Step 5: 検証

validateスクリプトで基本チェック:

```bash
python3 scripts/validate_skill.py <path/to/skill-folder>
```

品質チェックリスト → [references/quality-checklist.md](references/quality-checklist.md)

### Step 6: 評価とイテレーション

#### 評価駆動開発

1. スキルなしでタスクを実行 → ギャップを特定
2. 3つ以上のテストシナリオを作成
3. ベースライン計測
4. 最小限の指示を記述
5. テスト → 改善を繰り返す

#### マルチモデルテスト

| モデル | チェック観点 |
|--------|-------------|
| Haiku | ガイダンスは十分か？（最小モデルで動作確認） |
| Sonnet | 明確で効率的か？ |
| Opus | 過剰説明になっていないか？ |

## Reference Timing Table

| フェーズ | 参照すべきファイル |
|----------|-------------------|
| Frontmatter記述時 | [references/frontmatter-fields.md](references/frontmatter-fields.md) |
| description記述時 | [references/description-craft.md](references/description-craft.md) |
| Body構成設計時 | [references/progressive-disclosure.md](references/progressive-disclosure.md) |
| 検証・完成前 | [references/quality-checklist.md](references/quality-checklist.md) |

## Anti-Patterns（速引き）

| NG | 理由 |
|-----|------|
| SKILL.md 500行超 | コンテキスト圧迫 |
| descriptionにYAMLマルチライン(`\|`) | 一部パーサーで問題 |
| Claudeが既知の情報を説明 | トークンの無駄 |
| references/の深いネスト | 追跡困難 |
| SKILL.mdとreferences/で情報重複 | 不整合の温床 |
| README, CHANGELOG等の作成 | AIに不要な文脈 |

詳細 → [references/quality-checklist.md](references/quality-checklist.md)
