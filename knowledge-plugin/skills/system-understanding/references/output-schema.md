# システムマップ出力YAMLスキーマ

## 目次

- [概要](#概要)
- [共通ヘッダー](#共通ヘッダー)
- [項目別スキーマ](#項目別スキーマ)
  - [components](#componentsコンポーネント一覧)
  - [dependencies](#dependencies依存関係)
  - [data-flow](#data-flowデータフロー)
  - [boundaries](#boundaries境界)
  - [runtime](#runtimeランタイム要素)
  - [auth-flow](#auth-flow認証認可フロー)
  - [api-contracts](#api-contractsapi契約)
- [進捗管理ファイル](#進捗管理ファイル)
- [出力のベストプラクティス](#出力のベストプラクティス)

## 概要

各項目の調査結果は `system-map/{item-id}.yaml` に出力する。
このドキュメントは各項目の出力スキーマを定義する。

## 共通ヘッダー

すべての出力ファイルに共通するヘッダー:

```yaml
id: <項目ID>
name: <項目名>
collected_at: <収集日時 ISO8601>
collector: <収集者（Claude/人間）>
source_files: <調査したファイル数>
confidence: <確信度 high/medium/low>
notes: <補足・注意事項>
```

---

## 項目別スキーマ

### components（コンポーネント一覧）

```yaml
id: components
name: コンポーネント一覧
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 150
confidence: high
notes: |
  - フロントエンド・バックエンド・インフラを網羅
  - 47個のReactコンポーネント、48個のLambda関数を確認

items:
  - id: comp-001
    name: EditorComponent
    type: frontend  # frontend/backend/infrastructure/shared
    responsibility: |
      BlockNoteエディタのラッパー。
      ページコンテンツの編集、自動保存、Y.js同期を担当。
    owned_data:
      - editor_state: エディタの現在状態
      - blocks: ブロックデータ
    external_interfaces:
      - api: "POST /api/pages/[id]/blocks"
      - websocket: "action: sync"
      - event: "onSave"
    location: src/components/editor/EditorComponent.tsx
    dependencies:
      - "@blocknote/react"
      - "src/hooks/useEditorState"
    tags:
      - core
      - editor
```

### dependencies（依存関係）

```yaml
id: dependencies
name: 依存関係
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 200
confidence: medium
notes: |
  - 静的依存（import）と動的依存（API）を区別
  - 循環依存なし

items:
  - from: src/components/editor/EditorComponent.tsx
    to: src/hooks/useEditorState.ts
    type: import  # import/api/event/db
    direction: unidirectional  # unidirectional/bidirectional
    description: エディタ状態管理フックを使用

  - from: src/app/api/pages/[id]/route.ts
    to: lambda/handlers/page-handler.ts
    type: api
    direction: unidirectional
    description: Lambda経由でページデータを取得
    protocol: REST
    endpoint: "GET /api/pages/[id]"

  - from: lambda/handlers/relationship-rebuild-handler.ts
    to: SQS:kakusill-relationship-rebuild
    type: event
    direction: unidirectional
    description: 関係再構築ジョブをキューに投入
```

### data-flow（データフロー）

```yaml
id: data-flow
name: データフロー
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 80
confidence: high
notes: |
  - 主要な5つのデータフローを特定
  - Y.js CRDTによるリアルタイム同期を含む

items:
  - id: flow-001
    name: ページ編集フロー
    description: ユーザーがページを編集し保存するまでの流れ
    source:
      type: user_input
      component: EditorComponent
    transformations:
      - step: 1
        component: editorMachine (XState)
        action: 状態遷移（editing → saving）
      - step: 2
        component: useEditorState
        action: debounce処理
      - step: 3
        component: React Query mutation
        action: APIリクエスト構築
    destination:
      type: database
      component: PostgreSQL pages table
    persistence:
      responsible: src/app/api/pages/[id]/route.ts
      method: PATCH
      table: pages
    data_types:
      - blocks: Block[]
      - metadata: PageMetadata

  - id: flow-002
    name: AIチャットフロー
    description: ユーザーのプロンプトからAI応答までの流れ
    source:
      type: user_input
      component: ChatInput
    transformations:
      - step: 1
        component: chatSessionMachine
        action: メッセージ追加、ストリーミング開始
      - step: 2
        component: WebSocket
        action: Lambda呼び出し
      - step: 3
        component: ask-agent Lambda
        action: Gemini API呼び出し
    destination:
      type: ui
      component: ChatMessages
    persistence:
      responsible: DynamoDB conversations table
      method: PUT
      table: conversations
    data_types:
      - prompt: string
      - response: StreamingResponse
```

### boundaries（境界）

```yaml
id: boundaries
name: 境界
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 50
confidence: high
notes: |
  - 4種類の境界を特定
  - Cognito認証が信頼境界の中心

items:
  - id: boundary-001
    name: 認証境界
    type: trust  # trust/permission/network/process
    description: Cognito認証による信頼境界
    inside:
      - 認証済みユーザーセッション
      - JWTトークン保持リクエスト
    outside:
      - 未認証リクエスト
      - 期限切れトークン
    crossing_rules:
      - rule: JWTトークンをAuthorizationヘッダーに付与
      - rule: トークン有効期限内であること
      - rule: Cognito sub (UUID) で識別
    checkpoints:
      - location: src/lib/auth/verify-token.ts
      - location: lambda/handlers/auth-handler.ts

  - id: boundary-002
    name: ワークスペース権限境界
    type: permission
    description: ワークスペースメンバーシップによるアクセス制御
    inside:
      - ワークスペースメンバー（owner/admin/member/viewer）
    outside:
      - 非メンバー
    crossing_rules:
      - rule: workspace_membershipsテーブルにレコードが存在すること
      - rule: ロールに応じた操作権限
    checkpoints:
      - location: lambda/services/access-control/

  - id: boundary-003
    name: VPCネットワーク境界
    type: network
    description: AWS VPCによるネットワーク分離
    inside:
      - EC2 (PostgreSQL)
      - Lambda (VPC内実行)
    outside:
      - インターネット
      - Vercel (Next.js)
    crossing_rules:
      - rule: セキュリティグループで許可されたポートのみ
      - rule: Elastic IP経由でのみ外部からアクセス可能
    checkpoints:
      - location: infrastructure/cdk/lib/constructs/
```

### runtime（ランタイム要素）

```yaml
id: runtime
name: ランタイム要素
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 30
confidence: high
notes: |
  - SQS FIFO、Lambda、React Queryキャッシュを特定

items:
  - id: runtime-001
    name: 関係再構築キュー
    type: queue  # queue/job/scheduler/retry/cache
    description: ページ間関係の非同期再構築用FIFOキュー
    configuration:
      service: SQS FIFO
      name: kakusill-relationship-rebuild-{stage}
      visibility_timeout: 300
      message_retention: 1209600  # 14日
    triggers:
      - ページ保存時
      - 要件更新時
    handlers:
      - lambda/handlers/relationship-rebuild-handler.ts

  - id: runtime-002
    name: AIジョブプロセッサ
    type: job
    description: 長時間AI処理のバックグラウンドジョブ
    configuration:
      service: Lambda
      timeout: 900  # 15分
      memory: 3008
    triggers:
      - WebSocket action: ask
      - WebSocket action: analyze
    handlers:
      - lambda/handlers/job-processor-handler.ts
    retry_policy:
      max_attempts: 3
      backoff: exponential

  - id: runtime-003
    name: React Queryキャッシュ
    type: cache
    description: サーバー状態のクライアントサイドキャッシュ
    configuration:
      stale_time: 5000
      cache_time: 300000
      refetch_on_window_focus: true
    scope:
      - ページリスト
      - ユーザー情報
      - ワークスペース設定
```

### auth-flow（認証・認可フロー）

```yaml
id: auth-flow
name: 認証・認可フロー
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 25
confidence: high
notes: |
  - Cognito + NextAuth統合
  - sub (UUID) を安定識別子として使用

items:
  - id: auth-001
    name: ログインフロー
    steps:
      - step: 1
        action: ユーザーが認証情報を入力
        component: /api/auth/signin
      - step: 2
        action: Cognito認証
        component: AWS Cognito User Pool
      - step: 3
        action: トークン発行
        component: Cognito (ID/Access/Refresh Token)
      - step: 4
        action: NextAuthセッション作成
        component: NextAuth.js
      - step: 5
        action: DBにユーザー情報保存/更新
        component: users table (cognito_id = sub)
    tokens:
      - name: ID Token
        lifetime: 1時間
        usage: ユーザー情報取得
      - name: Access Token
        lifetime: 1時間
        usage: API認証
      - name: Refresh Token
        lifetime: 30日
        usage: トークン更新
    checkpoints:
      - location: src/lib/auth/cognito.ts
      - location: src/app/api/auth/[...nextauth]/route.ts

  - id: auth-002
    name: WebSocket認証フロー
    steps:
      - step: 1
        action: 短命トークン取得
        component: /api/auth/websocket-token
      - step: 2
        action: WebSocket接続時にトークン送信
        component: WebSocket connect
      - step: 3
        action: Lambda Authorizerで検証
        component: lambda/handlers/auth-handler.ts
    tokens:
      - name: WebSocket Token
        lifetime: 15分
        usage: WebSocket接続認証
```

### api-contracts（API契約）

```yaml
id: api-contracts
name: API契約
collected_at: "2024-01-21T10:00:00+09:00"
collector: Claude
source_files: 60
confidence: high
notes: |
  - REST API 60+エンドポイント
  - WebSocket 4アクション

rest_apis:
  - id: api-001
    method: GET
    path: /api/pages
    description: ページ一覧取得
    auth_required: true
    request_schema:
      query:
        workspace_id: string (required)
        limit: number (optional, default: 50)
        offset: number (optional, default: 0)
    response_schema:
      pages: Page[]
      total: number
      has_more: boolean
    errors:
      - code: 401
        description: 未認証
      - code: 403
        description: ワークスペースへのアクセス権なし

  - id: api-002
    method: POST
    path: /api/pages
    description: ページ作成
    auth_required: true
    request_schema:
      body:
        workspace_id: string (required)
        title: string (required)
        parent_id: string (optional)
        blocks: Block[] (optional)
    response_schema:
      page: Page

websocket_apis:
  - id: ws-001
    action: ask
    description: AIチャット質問
    request_schema:
      pageId: string (required)
      prompt: string (required)
      context: object (optional)
    response_schema:
      type: data | error | complete
      data: StreamChunk
      error: ErrorInfo
```

---

## 進捗管理ファイル

`system-map/progress.yaml`:

```yaml
version: "1.0"
project: <プロジェクト名>
updated_at: "2024-01-21T10:00:00+09:00"

summary:
  total_items: 14
  completed: 5
  in_progress: 1
  pending: 8

items:
  - id: components
    status: completed  # completed/in_progress/pending/skipped
    file: components.yaml
    collected_at: "2024-01-21T09:00:00+09:00"
    confidence: high

  - id: dependencies
    status: completed
    file: dependencies.yaml
    collected_at: "2024-01-21T09:30:00+09:00"
    confidence: medium

  - id: data-flow
    status: in_progress
    file: null
    started_at: "2024-01-21T10:00:00+09:00"

  - id: boundaries
    status: pending
    file: null

  - id: runtime
    status: pending
    file: null

  # ... 他の項目
```

## 出力のベストプラクティス

1. **確信度を正直に記載**: 不明な点は `confidence: low` とし、notes に理由を記載
2. **ソースファイルを明記**: 調査したファイルパスを `location` に記載
3. **不明は「不明」**: 推測で埋めず、明示的に「不明」「要調査」と記載
4. **IDの一貫性**: コンポーネントIDは他の項目（dependencies等）で参照されるため、一貫性を保つ
