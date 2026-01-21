---
name: component-dossier-builder
description: |
  各コンポーネントの詳細情報を構造化した「ドシエ（調査書）」を作成するスキル。
  system-map/components.yamlを入力として、RAG検索の核となるコンポーネントカードを生成する。
  LLMにコード全文を渡す代わりに、構造化されたカードで本質を伝える。

  使用タイミング:
  - 「コンポーネントドシエを作成して」「コンポーネントカードを作って」
  - 「各コンポーネントの詳細を調査して」「RAG用のコンテキストを作成して」
  - system-map/components.yaml が存在し、各コンポーネントの深掘りが必要な時
  - コードベースの知識をLLM検索可能な形式で蓄積したい時
---

# Component Dossier Builder

system-map/components.yaml から各コンポーネントの詳細な「ドシエ（調査書）」を作成する。

**重要ルール**: 推測で埋めない。不明点は `unknowns` に、仮定は `assumptions` に明示する。

## 前提条件

- `system-map/components.yaml` が存在すること
- 推奨: `dependencies.yaml`, `api-contracts.yaml`, `failure-modes.yaml` も存在

## ワークフロー

```
1. components.yaml読込 → 2. 対象選択 → 3. 深掘り調査 → 4. カード出力 → 5. 次のコンポーネントへ
```

## Phase 1: 対象コンポーネント選択

```bash
ls component-dossiers/*.yaml 2>/dev/null || echo "未作成"
```

`system-map/components.yaml` を読み、未作成のコンポーネントを1つ選択する。

優先順位:
1. 依存される側が多いコンポーネント（影響範囲が大きい）
2. 境界に位置するコンポーネント（API Gateway、認証など）
3. 障害モードが定義されているコンポーネント

## Phase 2: 深掘り調査

Exploreエージェントまたはkiri MCPで調査:

```
Task(subagent_type="Explore", prompt="
{component_name}について以下を調査して:
1. 責務（何をするか、何をしないか）
2. 公開API/イベント/DBスキーマ
3. 依存先と依存される側
4. エラーハンドリングとリトライ戦略
5. 状態管理（ステートフル/ステートレス、キャッシュ）
6. テストの有無と種類
")
```

### 調査対象ファイル

| 情報 | 調査先 |
|------|--------|
| 責務 | コード本体、README、コメント |
| API契約 | OpenAPI、型定義、ルーティング |
| イベント | イベント発行/購読コード |
| 失敗モード | try-catch、リトライロジック、タイムアウト設定 |
| 状態管理 | DB接続、キャッシュ設定、セッション |
| テスト | テストファイル、CI設定 |

## Phase 3: カード出力

`component-dossiers/{component-id}.yaml` に出力。

テンプレートは [references/card-template.md](references/card-template.md) を参照。

```yaml
id: order-service
name: 注文サービス
collected_at: "2024-01-21T10:00:00+09:00"
confidence: high  # high/medium/low
source_files:
  - src/services/order/
  - src/api/orders/

purpose:
  does:
    - 注文の作成・更新・キャンセル
    - 注文ステータスの管理
  does_not:
    - 決済処理（payment-serviceに委譲）
    - 在庫管理（inventory-serviceに委譲）

contracts:
  apis:
    - method: POST
      path: /api/orders
      description: 注文作成
    - method: GET
      path: /api/orders/{id}
      description: 注文取得
  events_published:
    - order.created
    - order.cancelled
  events_subscribed:
    - payment.completed
    - inventory.reserved
  db_tables:
    - orders
    - order_items

owned_data:
  source_of_truth:
    - orders
    - order_items
  reads_from:
    - products  # 所有していない
    - users     # 所有していない

dependencies:
  depends_on:
    - payment-service
    - inventory-service
  depended_by:
    - notification-service
    - analytics-service

failure_modes:
  - trigger: payment-service timeout
    behavior: 注文をpending状態に保持
    recovery: 3回リトライ後に失敗、手動介入を要求
  - trigger: inventory不足
    behavior: 400エラーを即座に返却
    recovery: なし（ユーザーに再試行を促す）

state:
  type: stateful  # stateful/stateless
  persistence: PostgreSQL
  cache:
    type: Redis
    ttl: 300  # 秒
    invalidation: order更新時

non_functional:
  performance:
    p99_latency: 200ms
    throughput: 1000 RPS
  availability: 99.9%
  security:
    - JWT認証必須
    - 所有者のみアクセス可能
  observability:
    metrics: DataDog
    logging: structured JSON
    tracing: OpenTelemetry

test_strategy:
  unit:
    framework: Jest
    coverage: 80%
  integration:
    framework: Testcontainers
  contract:
    framework: Pact
  load:
    framework: k6
    target: 1000 RPS

unknowns:
  - inventory-service障害時のフォールバック戦略が未定義
  - キャッシュ無効化の伝播メカニズムが不明

assumptions:
  - payment-serviceは冪等性を保証していると仮定
  - inventory.reservedイベントは必ずorder.created後に到着すると仮定
```

## Phase 4: 進捗管理

`component-dossiers/progress.yaml` で進捗を管理:

```yaml
total_components: 15
completed: 3
items:
  - id: order-service
    status: completed
    file: order-service.yaml
    confidence: high
  - id: payment-service
    status: in_progress
  - id: user-service
    status: pending
```

## 品質ルール

### 絶対に守ること

1. **推測で埋めない**: コードに根拠がない情報は書かない
2. **不明は不明**: `unknowns` セクションに明示する
3. **仮定は仮定**: `assumptions` セクションに明示する
4. **confidence を正直に**: 調査が不十分なら `low` にする

### confidence の基準

| レベル | 基準 |
|--------|------|
| high | コードを直接確認、テストで検証済み |
| medium | コードを確認したが、一部推測を含む |
| low | ドキュメントのみ、またはコード未確認 |

## 注意事項

- 1セッションで1コンポーネントのみ調査（品質確保のため）
- 既存の `component-dossiers/*.yaml` を確認して重複を避ける
- 大きなコンポーネントは分割を検討（例: auth → auth-login, auth-session）
