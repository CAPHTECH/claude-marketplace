# プロジェクト情報収集ガイド

CLAUDE.mdに記述すべき情報をプロジェクトから収集する手順。

## 収集の原則

| 判定 | 基準 |
|------|------|
| **書く** | Claudeが推測すると間違えやすい情報（推測ミスのコスト > 記載コスト） |
| **書かない** | コードや設定ファイルから一意に確定できる情報 |
| **要約のみ** | 重要だが詳細を書くと肥大化する情報（参照先パスを添える） |

## 収集手順

### 1. 実行コマンドの収集（High）

```bash
# package.json scripts
cat package.json | jq '.scripts'

# Makefile
head -50 Makefile

# CI設定からのコマンド抽出
cat .github/workflows/*.yml | grep -A2 'run:'
```

**CLAUDE.mdに書くべき情報**:
- dev/test/build/lint/typecheck の各コマンド
- 単一テスト実行のコマンド（パス指定方法）
- CI固有の前提条件（環境変数、事前セットアップ）

**書かない**: package.jsonのscripts一覧をそのまま転記

### 2. テスト方法の収集（High）

確認するファイル:
- テスト設定: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `.rspec`等
- テストディレクトリ構造: `__tests__/`, `test/`, `spec/`, `*_test.go`等
- CIでのテスト実行コマンド

**CLAUDE.mdに書くべき情報**:
- テストフレームワーク名と実行コマンド
- テストファイルの配置規約（colocate vs 分離）
- テスト命名規約（`*.test.ts` vs `*.spec.ts`等）
- モック/フィクスチャの作法（プロジェクト固有のもの）

**書かない**: テストフレームワークの使い方の説明

### 3. 安全制約・必須ルールの収集（High）

確認するファイル:
- `.gitignore`（機密ファイルのパターン）
- CI checks（pre-commit hooks, required checks）
- `.claude/settings.json`（既存Hooks）
- セキュリティ関連設定

**CLAUDE.mdに書くべき情報**:
- コミット前に必ず実行すべきチェック
- 触ってはいけないファイル・ディレクトリ
- 環境変数の取り扱いルール
- デプロイ・リリースに関する制約

### 4. 技術スタック概要の収集（Med）

確認するファイル:
- `package.json`/`Cargo.toml`/`go.mod`/`requirements.txt`等
- フレームワーク設定: `next.config.*`, `vite.config.*`等
- DB設定: `prisma/schema.prisma`, `drizzle.config.*`等
- インフラ設定: `Dockerfile`, `docker-compose.yml`, `terraform/`等

**CLAUDE.mdに書くべき情報**:
- 主要フレームワーク・ランタイム（名前とバージョン制約）
- DB/キャッシュ/メッセージキュー等のインフラ構成
- モノレポの場合、各パッケージの役割

**書かない**: 全依存パッケージの一覧、設定ファイルの詳細

### 5. アーキテクチャ・責務境界の収集（Med）

確認する情報源:
- トップレベルディレクトリ構造
- README.md, ARCHITECTURE.md, docs/
- モノレポのワークスペース設定

**CLAUDE.mdに書くべき情報**:
- 主要ディレクトリの役割（コードから自明でないもの）
- レイヤー構造や依存方向のルール
- 共有コードの配置ルール
- 「なぜこの構造なのか」の設計意図（簡潔に）

**書かない**: 全ディレクトリの説明、ファイル一覧

### 6. 命名規約・コードスタイルの収集（Med）

確認するファイル:
- `.eslintrc*`, `.prettierrc*`, `biome.json`等
- 既存コードのパターン（サンプリング3-5ファイル）
- CONTRIBUTING.md

```bash
# linter設定のカスタムルール確認
cat .eslintrc* | grep -A5 'rules'
```

**CLAUDE.mdに書くべき情報**:
- linterで強制されない慣習（ファイル命名、エクスポートパターン等）
- プロジェクト固有の命名規約（コンポーネント名、API命名等）
- コメント規約（あれば）

**書かない**: linter/formatterで自動強制されるルール

### 7. 設計判断の背景の収集（Low）

確認する情報源:
- ADR（Architecture Decision Records）
- README内の設計セクション
- 重要なPRの説明文

**CLAUDE.mdに書くべき情報**:
- 重要な技術選定の理由（1行要約 + 詳細への参照パス）
- 「なぜXではなくYを使うのか」系の判断

### 8. ワークフローの収集（Low）

確認する情報源:
- CONTRIBUTING.md
- PR template
- git branching model（git branchのパターン）
- CI/CDパイプライン設定

**CLAUDE.mdに書くべき情報**:
- ブランチ戦略（あれば）
- PR作成・マージの方針
- リリース手順（あれば）

## 暗黙知の発見

コード・設定ファイルだけでは読み取れない「暗黙の規約」を発見するアプローチ。

### git履歴からのパターン発見

```bash
# コミットメッセージの規約を推測
git log --oneline -30

# よく修正されるファイル（ホットスポット）
git log --pretty=format: --name-only -100 | sort | uniq -c | sort -rn | head -20
```

- コミットメッセージに一貫したフォーマットがあるか（conventional commits等）
- 特定パターンの修正が繰り返されていないか（= ルール化すべき）

### ユーザーへの確認質問

収集だけでは判断できない場合、以下の質問をユーザーに投げる:

1. 「このプロジェクトでClaudeが間違えやすいことは何ですか？」
2. 「新メンバーが最初に躓くポイントは？」
3. 「コードレビューで繰り返し指摘することは？」

これらの回答はCLAUDE.mdの Known Gotchas セクションに直結する。

## サブディレクトリCLAUDE.md提案の判断フロー

```
ディレクトリを評価
  ├─ ルートと技術スタックが異なる？ → Yes → 提案
  ├─ ルートにない独自ルールがある？ → Yes → 提案
  ├─ セキュリティ/課金等の高影響領域？ → Yes → 提案
  ├─ ルートCLAUDE.mdの該当セクションが50行超？ → Yes → 分離を提案
  └─ いずれもNo → 提案しない
```

サブディレクトリCLAUDE.mdの内容:
- そのディレクトリ固有の規約・コマンド・注意点のみ
- ルートと共通の情報は書かない（継承される）
- 20-50行程度が目安
