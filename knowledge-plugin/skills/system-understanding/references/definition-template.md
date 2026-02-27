# システムマップ定義ファイルの作成方法

## 目次

- [概要](#概要)
- [テンプレート](#テンプレート)
  - 基本項目: components, dependencies, data-flow, boundaries, runtime
  - 追加項目: auth-flow, api-contracts, state-management, environments, observability, secrets-config, failure-modes, graph-vector
- [作成手順](#作成手順)
- [カスタマイズのポイント](#カスタマイズのポイント)

## 概要

`system-map/definition.yaml` は、収集するシステムマップ項目とその概要を定義するファイル。
プロジェクトごとに作成し、システムマップ収集の基準とする。

## テンプレート

```yaml
# system-map/definition.yaml
version: "1.0"
project: <プロジェクト名>
created_at: <作成日時 ISO8601>
updated_at: <更新日時 ISO8601>

# 収集項目一覧
items:
  # === 基本項目（推奨） ===

  - id: components
    name: コンポーネント一覧
    description: |
      システムを構成するコンポーネント（モジュール、サービス、パッケージ）の一覧。
      各コンポーネントの責務、所有データ、外部インターフェースを記述する。
    scope:
      - フロントエンド（React/Next.js コンポーネント）
      - バックエンド（API Routes、Lambda関数）
      - インフラ（AWS CDK Constructs）
      - 共有ライブラリ（lib/、utils/）
    output_fields:
      - id: コンポーネントID
      - name: コンポーネント名
      - type: 種別（frontend/backend/infrastructure/shared）
      - responsibility: 責務
      - owned_data: 所有データ
      - external_interfaces: 外部I/F（API、イベント、ファイル）
      - location: ファイルパス

  - id: dependencies
    name: 依存関係
    description: |
      コンポーネント間の呼び出し関係。方向付きで記述する。
      静的依存（import）と動的依存（API呼び出し、イベント）を区別する。
    scope:
      - モジュール間import
      - API呼び出し（REST、WebSocket）
      - イベント発行・購読
      - データベースアクセス
    output_fields:
      - from: 呼び出し元
      - to: 呼び出し先
      - type: 依存種別（import/api/event/db）
      - description: 説明

  - id: data-flow
    name: データフロー
    description: |
      データがシステム内をどう流れるか。
      入力元、変換処理、出力先、永続化の責任を明確にする。
    scope:
      - ユーザー入力フロー
      - API通信フロー
      - 状態管理フロー（React Query、XState、Valtio）
      - 永続化フロー（DB、ファイル）
    output_fields:
      - id: フローID
      - name: フロー名
      - source: 入力元
      - transformations: 変換処理
      - destination: 出力先
      - persistence: 永続化担当
      - data_types: データ型

  - id: boundaries
    name: 境界
    description: |
      システム内の各種境界を特定する。
      信頼境界、権限境界、ネットワーク境界、プロセス境界を区別する。
    scope:
      - 信頼境界（認証・認可）
      - 権限境界（ロール・パーミッション）
      - ネットワーク境界（VPC、サブネット、セキュリティグループ）
      - プロセス境界（コンテナ、Lambda、ブラウザ）
    output_fields:
      - id: 境界ID
      - name: 境界名
      - type: 境界種別（trust/permission/network/process）
      - inside: 内側のコンポーネント
      - outside: 外側のコンポーネント
      - crossing_rules: 境界を超える際のルール

  - id: runtime
    name: ランタイム要素
    description: |
      実行時に動作する非同期・バックグラウンド要素。
      キュー、ジョブ、スケジューラ、リトライ、キャッシュを含む。
    scope:
      - メッセージキュー（SQS）
      - バックグラウンドジョブ（Lambda）
      - スケジューラ（EventBridge）
      - リトライポリシー
      - キャッシュ（React Query、ブラウザ）
    output_fields:
      - id: 要素ID
      - name: 要素名
      - type: 種別（queue/job/scheduler/retry/cache）
      - configuration: 設定
      - triggers: トリガー
      - handlers: ハンドラー

  # === 追加項目（必要に応じて） ===

  - id: auth-flow
    name: 認証・認可フロー
    description: |
      ユーザー認証とアクセス制御の流れ。
      トークンライフサイクル、権限チェックポイントを含む。
    scope:
      - 認証プロバイダー（Cognito）
      - トークン管理（JWT）
      - セッション管理（NextAuth）
      - 権限チェック
    output_fields:
      - id: フローID
      - name: フロー名
      - steps: ステップ一覧
      - tokens: 使用トークン
      - checkpoints: チェックポイント

  - id: api-contracts
    name: API契約
    description: |
      REST/WebSocket APIのエンドポイント一覧と仕様。
    scope:
      - REST API
      - WebSocket API
      - 内部API
    output_fields:
      - id: エンドポイントID
      - method: HTTPメソッド
      - path: パス
      - description: 説明
      - request_schema: リクエストスキーマ
      - response_schema: レスポンススキーマ
      - auth_required: 認証要否

  - id: state-management
    name: 状態管理
    description: |
      フロントエンドの状態管理アーキテクチャ。
      各ライブラリの責務分担、状態遷移を含む。
    scope:
      - サーバー状態（React Query）
      - 複雑な遷移（XState）
      - 軽量UI状態（Valtio）
    output_fields:
      - id: 状態ID
      - name: 状態名
      - library: 使用ライブラリ
      - scope: スコープ（global/component/page）
      - transitions: 遷移（XStateの場合）

  - id: environments
    name: 環境・デプロイメント
    description: |
      各環境の構成と差異。
    scope:
      - 開発環境
      - ステージング環境
      - 本番環境
      - サンドボックス環境
    output_fields:
      - id: 環境ID
      - name: 環境名
      - branch: ブランチ
      - infrastructure: インフラ構成
      - configuration: 設定差分

  - id: observability
    name: 可観測性
    description: |
      ログ、メトリクス、トレーシングの構成。
    scope:
      - ロギング
      - メトリクス
      - トレーシング
      - アラート
    output_fields:
      - id: 要素ID
      - name: 要素名
      - type: 種別（log/metric/trace/alert）
      - location: 収集場所
      - retention: 保持期間

  - id: secrets-config
    name: シークレット・設定
    description: |
      シークレットと設定の管理方法。
    scope:
      - 環境変数
      - シークレット管理（Secrets Manager）
      - 設定ファイル
    output_fields:
      - id: 設定ID
      - name: 設定名
      - type: 種別（env/secret/config）
      - source: 取得元
      - usage: 使用箇所

  - id: failure-modes
    name: 障害モード・回復
    description: |
      各コンポーネントの障害時挙動と回復戦略。
    scope:
      - タイムアウト
      - 接続エラー
      - データ不整合
      - リソース枯渇
    output_fields:
      - id: 障害ID
      - name: 障害名
      - component: 対象コンポーネント
      - symptoms: 症状
      - recovery: 回復戦略
      - prevention: 予防策

  - id: graph-vector
    name: グラフ・ベクトル検索
    description: |
      グラフDB（Apache AGE）とベクトル検索（pgvector）の構成。
    scope:
      - グラフスキーマ
      - ベクトル埋め込み
      - クエリパターン
    output_fields:
      - id: 要素ID
      - name: 要素名
      - type: 種別（graph/vector）
      - schema: スキーマ
      - queries: 代表的クエリ

# カスタム項目を追加する場合のテンプレート
# - id: custom-item
#   name: カスタム項目名
#   description: |
#     項目の説明
#   scope:
#     - スコープ1
#     - スコープ2
#   output_fields:
#     - field1: フィールド説明
#     - field2: フィールド説明
```

## 作成手順

1. プロジェクトに `system-map/` ディレクトリを作成
2. 上記テンプレートをコピーして `definition.yaml` を作成
3. プロジェクトに合わせて項目を取捨選択・カスタマイズ
4. 不要な項目は削除、必要な項目は追加

## カスタマイズのポイント

### 項目の取捨選択

- 小規模プロジェクト: `components`, `dependencies`, `data-flow` のみで十分
- 大規模プロジェクト: すべての項目 + カスタム項目
- マイクロサービス: `api-contracts`, `boundaries` を重視
- フロントエンド中心: `state-management`, `components` を重視

### スコープの調整

プロジェクト構造に合わせてスコープを具体化する。

```yaml
# 例: Next.js プロジェクトの場合
- id: components
  scope:
    - src/app/（App Router）
    - src/components/（UIコンポーネント）
    - src/hooks/（カスタムフック）
    - src/lib/（ユーティリティ）
```

### output_fieldsの拡張

必要に応じてフィールドを追加する。

```yaml
output_fields:
  - id: コンポーネントID
  - name: コンポーネント名
  - owner: 担当者  # 追加
  - sla: SLA要件   # 追加
```
