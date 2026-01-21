# コンポーネントカード テンプレート

各セクションの詳細な説明とガイドライン。

## 目次

- [ヘッダー](#ヘッダー)
- [purpose（目的・責務）](#purpose)
- [contracts（入出力と契約）](#contracts)
- [owned_data（所有データ）](#owned_data)
- [dependencies（依存関係）](#dependencies)
- [failure_modes（失敗モード）](#failure_modes)
- [state（状態管理）](#state)
- [non_functional（非機能要件）](#non_functional)
- [test_strategy（テスト戦略）](#test_strategy)
- [unknowns / assumptions](#unknowns--assumptions)

---

## ヘッダー

```yaml
id: order-service           # 一意のID（kebab-case）
name: 注文サービス           # 人間が読む名前
collected_at: "2024-01-21T10:00:00+09:00"  # ISO8601
confidence: high            # high/medium/low
source_files:               # 調査したファイル
  - src/services/order/
  - src/api/orders/
```

### confidence の判定基準

| レベル | 判定基準 |
|--------|----------|
| high | コードを直接読み、テストも確認した |
| medium | コードを読んだが、一部は推測や仮定を含む |
| low | ドキュメントのみ、またはコードを十分に確認できていない |

---

## purpose

**何をするか、何をしないかを明確に分ける。**

```yaml
purpose:
  does:
    - 注文の作成・更新・キャンセル
    - 注文ステータスの管理
    - 注文履歴の保持
  does_not:
    - 決済処理（payment-serviceに委譲）
    - 在庫確認・引当（inventory-serviceに委譲）
    - ユーザー認証（auth-serviceに委譲）
```

### 記載のコツ

- `does_not` は「やらないこと」ではなく「他に委譲していること」を書く
- 曖昧な表現（「〜を管理」）は避け、具体的な操作を書く

---

## contracts

**外部との契約（API、イベント、DBスキーマ）を明記。**

```yaml
contracts:
  apis:
    - method: POST
      path: /api/orders
      description: 注文作成
      auth: required
      idempotency_key: X-Idempotency-Key
    - method: GET
      path: /api/orders/{id}
      description: 注文取得
      auth: required
    - method: PATCH
      path: /api/orders/{id}/cancel
      description: 注文キャンセル
      auth: required

  events_published:
    - name: order.created
      payload: { orderId, userId, items, totalAmount }
      trigger: 注文作成成功時
    - name: order.cancelled
      payload: { orderId, reason }
      trigger: 注文キャンセル時

  events_subscribed:
    - name: payment.completed
      action: 注文ステータスをpaidに更新
    - name: inventory.reserved
      action: 注文ステータスをconfirmedに更新

  db_tables:
    - name: orders
      columns: [id, user_id, status, total_amount, created_at]
      indexes: [user_id, status, created_at]
    - name: order_items
      columns: [id, order_id, product_id, quantity, price]
      indexes: [order_id]
```

### 調査方法

| 契約タイプ | 調査先 |
|-----------|--------|
| API | ルーティング定義、OpenAPI、型定義 |
| イベント発行 | `emit`, `publish`, `dispatch` の検索 |
| イベント購読 | `on`, `subscribe`, `handle` の検索 |
| DB | マイグレーション、ORM定義、スキーマ |

---

## owned_data

**Source of Truth（SoT）を明確にする。**

```yaml
owned_data:
  source_of_truth:
    - orders        # このコンポーネントが権威を持つ
    - order_items   # このコンポーネントが権威を持つ
  reads_from:
    - products      # 参照のみ（所有していない）
    - users         # 参照のみ（所有していない）
  caches:
    - user_info     # キャッシュ（SoTはuser-service）
```

### 重要な原則

- **SoTは1箇所**: 同じデータのSoTが複数あると整合性問題が発生
- **reads_from は所有していない**: 直接書き込むことはない
- **caches は一時的**: 無効化戦略が必要

---

## dependencies

**依存関係を双方向で記録。**

```yaml
dependencies:
  depends_on:
    - name: payment-service
      type: sync  # sync/async
      protocol: REST
      critical: true  # 障害時に機能停止するか
    - name: inventory-service
      type: async
      protocol: SQS
      critical: false
    - name: PostgreSQL
      type: sync
      protocol: TCP
      critical: true

  depended_by:
    - name: notification-service
      type: async
      protocol: SNS
    - name: analytics-service
      type: async
      protocol: Kinesis
```

### critical の判定

| critical | 意味 |
|----------|------|
| true | この依存先が落ちると、このコンポーネントも機能停止 |
| false | フォールバックや遅延処理で対応可能 |

---

## failure_modes

**障害パターンと対処法を明記。**

```yaml
failure_modes:
  - trigger: payment-service timeout (30s)
    behavior: 注文をpending状態に保持
    recovery: |
      1. 3回リトライ（exponential backoff）
      2. 失敗時はDLQに送信
      3. 手動介入で再処理または返金

  - trigger: inventory-service 不整合
    behavior: 409 Conflictを返却
    recovery: ユーザーに再試行を促す

  - trigger: PostgreSQL 接続エラー
    behavior: 503 Service Unavailableを返却
    recovery: |
      1. コネクションプール再接続
      2. 回復しない場合はサーキットブレーカー発動

  - trigger: 高負荷（>1000 RPS）
    behavior: レート制限（429）
    recovery: オートスケーリングで対応
```

### 調査方法

- `try-catch`, `rescue`, `except` ブロックを検索
- タイムアウト設定を確認
- リトライロジックを確認
- サーキットブレーカーの有無を確認

---

## state

**ステートフル/ステートレスと永続化戦略。**

```yaml
state:
  type: stateful  # stateful/stateless

  persistence:
    type: PostgreSQL
    connection_pool: 20
    read_replica: true

  cache:
    type: Redis
    ttl: 300  # 秒
    invalidation:
      - order更新時に該当キーを削除
      - 日次バッチで全キー再構築
    fallback: キャッシュミス時はDBから取得

  session:
    type: none  # JWT認証のためセッションレス
```

### ステートレスの判定

- リクエスト間で状態を保持しない
- どのインスタンスでも処理可能
- 水平スケーリングが容易

---

## non_functional

**性能、可用性、セキュリティ、可観測性。**

```yaml
non_functional:
  performance:
    p50_latency: 50ms
    p99_latency: 200ms
    throughput: 1000 RPS
    batch_size: 100  # バッチ処理の場合

  availability:
    target: 99.9%
    redundancy: 3 replicas
    failover: automatic

  security:
    authentication: JWT (Cognito)
    authorization: RBAC (owner/admin/viewer)
    encryption:
      at_rest: AES-256
      in_transit: TLS 1.3
    secrets: AWS Secrets Manager

  observability:
    metrics:
      platform: DataDog
      custom: [order_count, payment_success_rate]
    logging:
      format: structured JSON
      level: INFO (production)
      retention: 30 days
    tracing:
      platform: OpenTelemetry
      sampling: 10%
    alerting:
      - condition: error_rate > 1%
        action: PagerDuty
```

---

## test_strategy

**テストの種類とカバレッジ。**

```yaml
test_strategy:
  unit:
    framework: Jest
    coverage: 80%
    location: src/__tests__/

  integration:
    framework: Testcontainers
    scope: DB + Redis
    location: tests/integration/

  contract:
    framework: Pact
    consumer: [notification-service, analytics-service]
    provider: order-service

  e2e:
    framework: Playwright
    scope: 注文フロー全体
    location: e2e/

  load:
    framework: k6
    target: 1000 RPS
    duration: 10min
    location: tests/load/

  mutation:
    framework: Stryker
    threshold: 70%
```

### テストがない場合

```yaml
test_strategy:
  unit:
    framework: なし
    coverage: 0%
    note: "テスト未整備（unknownsに記載）"
```

---

## unknowns / assumptions

**最も重要なセクション。正直に記録する。**

```yaml
unknowns:
  - inventory-service障害時のフォールバック戦略が未定義
  - キャッシュ無効化の伝播メカニズムが不明
  - 高負荷時のオートスケーリング閾値が未確認
  - payment-serviceとの間のリトライ上限が未確認

assumptions:
  - payment-serviceは冪等性を保証していると仮定
  - inventory.reservedイベントは必ずorder.created後に到着すると仮定
  - PostgreSQLのread replicaは1秒以内に同期されると仮定
  - Redisキャッシュは最終整合性で許容されると仮定
```

### unknowns の記載基準

- コードに書かれていない
- ドキュメントにも記載がない
- 調査時間内に確認できなかった

### assumptions の記載基準

- 明示的な仕様がないが、動作から推測した
- 他のコンポーネントの挙動に依存している
- 将来変更される可能性がある

---

## 最小限のカード

すべてのセクションが必須ではない。最小限のカードは以下:

```yaml
id: simple-component
name: シンプルコンポーネント
collected_at: "2024-01-21T10:00:00+09:00"
confidence: medium

purpose:
  does:
    - 単一の責務を実行
  does_not:
    - 他への委譲内容

contracts:
  apis:
    - method: GET
      path: /api/simple
      description: 基本操作

dependencies:
  depends_on: []
  depended_by: []

unknowns:
  - 詳細調査が未完了
```
