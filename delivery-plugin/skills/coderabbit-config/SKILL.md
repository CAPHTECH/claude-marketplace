---
name: coderabbit-config
context: fork
description: Generate or improve .coderabbit.yaml by analyzing project structure, languages, and conventions. Optimizes path_instructions, path_filters, tools, and knowledge_base. Triggers on "CodeRabbitを設定して", ".coderabbit.yamlを作って", "CodeRabbit設定を改善して", "レビュー設定を最適化して", or "/coderabbit-config".
---

# CodeRabbit Config

プロジェクトを分析し、最適な `.coderabbit.yaml` を生成・改善する。

## ワークフロー

```
既存.coderabbit.yamlあり? ──Yes──→ Audit → Propose → Confirm → Update
                          └─No──→ Analyze → Propose → Confirm → Generate
```

## Phase 1: Analyze（プロジェクト分析）

以下を調査し、設定に必要な情報を収集する:

### 1a. プロジェクト構造

- 主要言語・フレームワークの特定（package.json, Cargo.toml, go.mod, pyproject.toml等）
- ディレクトリ構造のパターン（src/, lib/, tests/, docs/ 等）
- ビルド成果物・自動生成ファイルの特定（dist/, .next/, *.min.js等）

### 1b. 既存の規約・ガイドライン

- CLAUDE.md, CONTRIBUTING.md, CODING_GUIDELINES.md の有無
- .cursorrules, .cursor/rules/, copilot-instructions.md の有無
- lint設定（.eslintrc, ruff.toml, .golangci.yml等）

### 1c. 既存設定の監査（既存.coderabbit.yamlがある場合）

- 非推奨オプションの検出
- 設定漏れ・冗長設定の特定
- プロジェクト実態との乖離

## Phase 2: Propose（設定提案）

分析結果に基づき、以下の設定をユーザーに提案する。

### 2a. 基本設定

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "<プロジェクトの共通言語>"
tone_instructions: "<チームのトーンに合わせた指示>"
```

**判断基準:**
- `language`: チームの共通言語。日本語チームなら `"ja"`
- `tone_instructions`: 250文字以内。具体的で建設的なトーンを指定

### 2b. reviews設定

| 設定 | 推奨 | 理由 |
|------|------|------|
| profile | `"chill"` | 細かすぎる指摘を抑制 |
| high_level_summary | `true` | PR概要の自動生成 |
| collapse_walkthrough | `true` | PR本文のノイズ削減 |
| poem | `false` | 実用性優先 |
| assess_linked_issues | `true` | Issue駆動開発との整合性チェック |
| reviews.auto_review.auto_incremental_review | `true` | push毎のレビュー |
| reviews.auto_review.drafts | `false` | WIP PRへの不要レビュー防止 |

### 2c. path_filters（最重要: 除外設定）

以下に該当するファイルを `!` プレフィックスで除外:

- ビルド成果物: `!dist/**`, `!build/**`, `!.next/**`
- minified/vendored: `!**/*.min.js`, `!**/vendor/**`
- lockファイル: 依存更新レビューが不要な場合のみ `!**/*.lock`
- バイナリ/アーカイブ: プロジェクトに存在するバイナリ形式を検出して除外（例: `!**/*.zip`）
- 自動生成コード: `!**/*.generated.*`, `!**/*.g.dart`

### 2d. path_instructions（最大の価値）

プロジェクトの各レイヤーに合わせた具体的なレビュー指示を生成する。

**生成ルール:**
1. プロジェクトの実際のディレクトリ構造からパターンを導出する
2. 各パターンの指示は検証可能な具体的チェック項目にする
3. 曖昧な指示（「きれいに書いて」等）は使わない
4. フレームワーク固有の規約を反映する

**典型パターン:**

| パス | チェック観点 |
|------|-------------|
| `**/*.ts` / `**/*.tsx` | any型回避、型安全性、null安全 |
| `**/api/**` / `**/routes/**` | 認証チェック、エラーハンドリング、バリデーション |
| `**/*.test.*` / `**/*.spec.*` | AAA パターン、エッジケース、モック適切性 |
| `**/migrations/**` | 破壊的変更の検出、ロールバック可能性 |
| `**/*.md` | リンク切れ、コード例の正確性 |
| `**/config/**` / `**/*.yaml` | 機密情報の露出、デフォルト値の妥当性 |

プロジェクト固有のパターンも追加する（例: スキルのSKILL.mdフロントマター検証等）。

### 2e. knowledge_base設定

```yaml
knowledge_base:
  code_guidelines:
    enabled: true
    filePatterns: []  # 1aで見つけたガイドラインファイルを列挙
```

### 2f. tools設定

- プロジェクトで使用している言語のlinterのみ有効化
- 未使用言語のツールは `enabled: false` で明示的に無効化
- 既存のlint設定ファイルがあればそのパスを指定

### 2g. auto_review設定

```yaml
reviews:
  auto_review:
    enabled: true
    drafts: false
    ignore_title_keywords: ["WIP", "DO NOT REVIEW"]
    base_branches: []  # デフォルトブランチ以外に追加する場合（例: ["develop", "release/*"]）
```

### 2h. pre_merge_checks（オプション）

プロジェクト固有の必須チェックがあれば `custom_checks` として提案。

## Phase 3: Confirm（ユーザー確認）

提案内容をユーザーに提示し、以下を確認:

1. 基本設定（言語、トーン）は適切か
2. path_instructionsの内容は妥当か
3. 除外すべきパスに漏れはないか
4. 追加したいカスタムチェックはあるか

AskUserQuestion を使って確認する。一度に多くの質問をしない。

## Phase 4: Generate / Update（生成・更新）

確認された設定で `.coderabbit.yaml` をプロジェクトルートに書き出す。

**出力規則:**
- スキーマ宣言を先頭に含める: `# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json`
- デフォルト値と同じ設定は省略してコンパクトに保つ
- セクションごとにコメントで意図を明記
- 既存ファイルの更新時は差分を提示してから書き込む
- 書き出し前にYAMLの階層構造が正しいか検証する（特に `reviews.auto_review`, `reviews.tools`, `reviews.pre_merge_checks` 等はreviews配下）

## 設定オプションリファレンス

主要な設定オプション一覧は references/config-reference.md を参照。最新の網羅情報は公式ドキュメントを確認。

## アンチパターン

| NG | 理由 |
|----|------|
| デフォルト値を全て明示的に書く | 冗長で保守コスト増 |
| path_instructionsに曖昧な指示 | AIが判断に迷い品質低下 |
| 全ツールを有効化 | 未使用言語のlintはノイズ |
| path_filtersなしで運用 | 自動生成ファイルがレビュー対象に |
| knowledge_baseの code_guidelines 未設定 | 既存規約が活用されない |
