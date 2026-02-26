# 6つの情報源 — 調査手法と検出パターン

## 目次

1. [ディレクトリ構造](#1-ディレクトリ構造)
2. [依存関係・外部サービス](#2-依存関係外部サービス)
3. [コードパターン](#3-コードパターン)
4. [設定・インフラ](#4-設定インフラ)
5. [テスト構成](#5-テスト構成)
6. [ドキュメント](#6-ドキュメント)

---

## 1. ディレクトリ構造

機能ドメインの境界を発見する。

### 調査手法

```bash
# feature別ディレクトリの発見
find . -type d -maxdepth 3 | grep -v node_modules | grep -v .git

# 各ディレクトリのファイル数で重量感を把握
find ./src -type f -name "*.ts" | cut -d/ -f3 | sort | uniq -c | sort -rn
```

### 検出パターン

| ディレクトリ構造 | Skill候補 | 根拠 |
|---|---|---|
| `src/payments/`, `src/billing/` | `payment-patterns` | 決済ドメインが独立モジュール |
| `src/auth/`, `src/middleware/auth*` | `auth-flow` | 認証が複数箇所にまたがる |
| `src/notifications/` | `notification-patterns` | 通知チャネル（email/push/slack）の設計 |
| `src/integrations/<service>/` | `<service>-integration` | 外部サービス連携が独立 |
| `src/admin/`, `src/backoffice/` | `admin-conventions` | 管理画面固有の規約 |

### Skill化の判断基準

- ファイル5個超 → そのドメインの規約・パターンをSkill化する価値あり
- 独自のユーティリティやヘルパーが存在 → ドメイン固有の知識がある証拠
- サブディレクトリにCLAUDE.mdが既にある → Skillに昇格する候補

## 2. 依存関係・外部サービス

プロジェクト固有の連携パターンを発見する。

### 調査手法

```bash
# JS/TS
cat package.json | grep -E '"(stripe|aws-sdk|@aws-sdk|firebase|supabase|prisma|drizzle|@sentry|datadog|twilio|sendgrid)"'

# Python
grep -E '(stripe|boto3|firebase|supabase|sentry|celery|redis)' requirements.txt pyproject.toml 2>/dev/null

# 実際の使用箇所
grep -r "import.*stripe\|require.*stripe" src/ --include="*.ts" --include="*.js" -l
```

### 検出パターン

| 依存 | Skill候補 | Skill化すべき知識 |
|------|----------|-----------------|
| stripe | `stripe-integration` | Webhook処理、冪等性、テストモック |
| @supabase/supabase-js | `supabase-patterns` | RLSポリシー設計、リアルタイム購読、Edge Functions |
| prisma / drizzle | `db-patterns` | マイグレーション手順、クエリパターン、シード |
| @sentry/* | `error-monitoring` | エラー分類、コンテキスト付与、アラート設計 |
| aws-sdk / @aws-sdk | `aws-patterns` | IAMポリシー、S3操作、Lambda連携 |
| next-auth / lucia | `auth-patterns` | セッション管理、プロバイダ設定、ミドルウェア |

### Skill化の判断基準

- 使用箇所が3ファイル以上 → 連携パターンにSkill価値あり
- ラッパー関数やユーティリティが存在 → プロジェクト固有の使い方がある
- 環境変数でAPI鍵を設定 → セットアップ手順をSkill化

## 3. コードパターン

繰り返し出現する構造やプロジェクト固有の規約を発見する。

### 調査手法

```bash
# エラーハンドリングパターン
grep -rn "catch\|throw\|Error\|Result<\|Result\.err" src/ --include="*.ts" -l | head -20

# カスタムフック/ユーティリティ
find src/ -name "use*.ts" -o -name "use*.tsx" | head -20
find src/ -name "*util*" -o -name "*helper*" | head -20

# バリデーションパターン
grep -rn "zod\|yup\|joi\|validate\|schema" src/ --include="*.ts" -l | head -20

# ミドルウェア/デコレータ
grep -rn "middleware\|@Guard\|@Auth\|@Role" src/ --include="*.ts" -l | head -20
```

### 検出パターン

| コードパターン | Skill候補 | Skill化すべき知識 |
|---|---|---|
| カスタムErrorクラス群 | `error-handling` | エラー階層、レスポンス変換、ログ規約 |
| zodスキーマ定義が多数 | `validation-patterns` | スキーマ定義規約、共通バリデータ |
| カスタムフック群 | `custom-hooks-guide` | フック設計方針、状態管理パターン |
| ミドルウェアチェーン | `middleware-patterns` | 実行順序、エラー伝播、認可チェック |
| Repository/Service層 | `layered-architecture` | 層間のルール、DI方針、トランザクション |

### Skill化の判断基準

- 同じパターンが5箇所以上 → 規約として明文化する価値あり
- パターン逸脱箇所がある → Skillで正しいパターンを示すことで防止
- 新規実装時に「既存コードを参考に」が必要 → Skillで手順化

## 4. 設定・インフラ

デプロイ・運用の暗黙知を発見する。

### 調査手法

```bash
# CI/CD設定
ls .github/workflows/ 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | head -100

# Docker/インフラ
ls Dockerfile docker-compose.yml 2>/dev/null
ls terraform/ cdk/ pulumi/ 2>/dev/null

# 環境変数
cat .env.example .env.local.example 2>/dev/null
grep -rn "process.env\|os.environ\|env::" src/ --include="*.ts" --include="*.py" | head -20
```

### 検出パターン

| 設定ファイル | Skill候補 | Skill化すべき知識 |
|---|---|---|
| 複数のCI workflowファイル | `ci-workflow` | ワークフロー分岐、キャッシュ戦略、シークレット管理 |
| Dockerfile + docker-compose | `local-dev-setup` | 開発環境構築手順、ボリュームマウント規約 |
| 環境変数が10個超 | `env-configuration` | 環境変数の意味、設定手順、環境間差異 |
| terraform/等のIaCディレクトリ | `infrastructure` | リソース構成、命名規則、変更手順 |
| 複数環境（staging/production） | `deploy-procedure` | デプロイフロー、ロールバック手順 |

## 5. テスト構成

テスト戦略の暗黙知を発見する。

### 調査手法

```bash
# テストファイル構成
find . -name "*.test.*" -o -name "*.spec.*" -o -name "*_test.*" | head -30

# テストヘルパー・フィクスチャ
find . -path "*/test*" -name "*helper*" -o -path "*/test*" -name "*fixture*" -o -path "*/test*" -name "*factory*" | head -20

# テスト設定
ls jest.config* vitest.config* playwright.config* cypress.config* 2>/dev/null
```

### 検出パターン

| テスト構成 | Skill候補 | Skill化すべき知識 |
|---|---|---|
| テストヘルパー/ファクトリが充実 | `test-patterns` | ファクトリ使用法、ヘルパーAPI、データ生成 |
| E2E設定が存在 | `e2e-testing` | E2E実行手順、セレクタ規約、テストデータ管理 |
| モック/スタブのユーティリティ | `test-mocking` | モック方針、何をモックするか、スタブ管理 |
| 複数テストレイヤー（unit/integration/e2e） | `test-strategy` | レイヤー判断基準、カバレッジ方針 |

## 6. ドキュメント

文書化された設計判断・業務ルールを発見する。

### 調査手法

```bash
# ドキュメント
ls docs/ doc/ 2>/dev/null
find . -name "*.md" -not -path "*/node_modules/*" -not -name "CLAUDE*" | head -20

# ADR（Architecture Decision Records）
ls docs/adr/ docs/decisions/ 2>/dev/null

# OpenAPI/スキーマ定義
find . -name "openapi*" -o -name "swagger*" -o -name "*.graphql" -o -name "schema.prisma" | head -10

# コード内の重要コメント
grep -rn "IMPORTANT\|HACK\|WORKAROUND\|NOTE:\|TODO:" src/ --include="*.ts" | head -20
```

### 検出パターン

| ドキュメント | Skill候補 | Skill化すべき知識 |
|---|---|---|
| ADRが存在 | `architecture-decisions` | 設計判断の背景、制約、トレードオフ |
| OpenAPI定義 | `api-conventions` | エンドポイント命名、レスポンス形式、認証 |
| GraphQLスキーマ | `graphql-patterns` | スキーマ設計規約、リゾルバパターン |
| HACK/WORKAROUND コメント多数 | `known-workarounds` | 既知の制約と回避策 |
| ビジネスロジックの長いコメント | `business-rules` | ドメイン固有の業務ルール |
