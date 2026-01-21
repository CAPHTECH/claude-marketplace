# 不変条件抽出パターン

カテゴリ別の抽出パターンと具体例。

## 目次

- [Security（セキュリティ境界）](#security)
- [Data Ownership（データ所有権）](#data-ownership)
- [Audit（監査）](#audit)
- [Idempotency（冪等性）](#idempotency)
- [Architecture（アーキテクチャ）](#architecture)
- [API Contract（API契約）](#api-contract)
- [Failure（障害・回復）](#failure)
- [Environment（環境）](#environment)

---

## Security

### 抽出元
- `boundaries.yaml` (type: trust)
- `auth-flow.yaml`

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| trust境界にcrossing_rulesがある | 「境界を超える際は{rules}を満たす」 |
| checkpointsが特定層に集中 | 「認可は{layer}層で完結する」 |
| 内部コンポーネントにcheckpointがない | 「内部は信頼済み前提で動作する」 |

### 抽出例

```yaml
# boundaries.yaml の入力
- id: boundary-001
  type: trust
  inside: [internal-services]
  outside: [public-internet]
  crossing_rules:
    - JWTトークン検証
    - Rate limiting
  checkpoints:
    - api-gateway

# 抽出される不変条件
- id: INV-SEC-001
  category: security
  statement: 認可チェックは必ずAPI Gateway層で完結する
  rationale: 内部サービスにはcheckpointがなく、境界での検証に依存している
```

### 典型的な不変条件

1. 認可は境界で完結し、内部は信頼前提に寄らない
2. 境界を超えるリクエストは必ずトークン検証を通過する
3. セッショントークンは有効期限を持ち、期限切れ時は再認証を強制
4. ロール昇格は監査証跡を残し、自己昇格は禁止
5. シークレットはコードにハードコードせず、Secrets Manager経由

---

## Data Ownership

### 抽出元
- `components.yaml` (owned_data)
- `data-flow.yaml` (persistence)
- `dependencies.yaml` (type: db)

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| owned_dataが明示されている | 「{data}の書込責任は{component}が持つ」 |
| persistence.responsibleが単一 | 「永続化責任は{component}に集約」 |
| 複数コンポーネントが同一DBに依存 | ⚠️ ギャップ：データ所有権が曖昧 |

### 抽出例

```yaml
# components.yaml の入力
- id: order-service
  owned_data:
    - orders
    - order_items

# data-flow.yaml の入力
- id: flow-001
  persistence:
    responsible: order-service
    table: orders

# 抽出される不変条件
- id: INV-DATA-001
  category: data_ownership
  statement: ordersテーブルへの書込はorder-serviceのみが行う
  rationale: owned_dataとpersistence.responsibleが一致
```

### 典型的な不変条件

1. データ所有者以外は直接DBを書かない（所有者経由のAPIを使用）
2. 永続化責任は単一コンポーネントに集約する
3. 整合モデル（最終整合/強整合）を明示し、画面挙動と一致させる
4. 書き込み順序依存がある場合はトランザクション境界を明示する

---

## Audit

### 抽出元
- `observability.yaml` (type: log)
- `api-contracts.yaml` (method: POST/PUT/DELETE)
- `auth-flow.yaml`

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| 重要操作にlogが紐付いている | 「{operation}は監査ログ必須」 |
| correlation_idが設定されている | 「リクエストは追跡可能」 |
| 認証イベントにログがある | 「認証失敗は記録される」 |

### 抽出例

```yaml
# observability.yaml の入力
- id: audit-001
  type: log
  location: order-service
  events:
    - order.created
    - order.deleted
  retention: 7years

# 抽出される不変条件
- id: INV-AUDIT-001
  category: audit
  statement: 注文の作成・削除は監査ログに記録し、7年間保持する
```

### 典型的な不変条件

1. 重要操作（作成/削除/権限変更）は監査ログ必須
2. ログにはcorrelation IDを含め、リクエスト追跡可能にする
3. 認証失敗は記録し、一定回数でロックアウトする
4. 障害発生時はアラートを発報し、人間が介入可能にする

---

## Idempotency

### 抽出元
- `runtime.yaml` (type: queue/job)
- `api-contracts.yaml` (method: POST/PUT)

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| queueにretry_policyがある | 「キュー処理は冪等キー必須」 |
| visibility_timeoutが設定されている | 「at-least-once前提の設計」 |
| idempotency_keyがスキーマにある | 「冪等性が保証されている」 |

### 抽出例

```yaml
# runtime.yaml の入力
- id: queue-001
  type: queue
  configuration:
    service: SQS FIFO
    visibility_timeout: 300
  retry_policy:
    max_attempts: 3

# 抽出される不変条件
- id: INV-IDEM-001
  category: idempotency
  statement: SQSキュー処理は冪等キーを持ち、3回までリトライ可能
  verification:
    type: test
    method: 同一メッセージを複数回処理して副作用が1回のみであることを確認
```

### 典型的な不変条件

1. リトライ可能な操作は冪等キーを持つ
2. 副作用を伴う操作はat-least-onceを前提に設計する
3. POST/PUT/DELETEは冪等性を保証するか、明示的に禁止する
4. メッセージ処理は順序保証の有無を明示する

---

## Architecture

### 抽出元
- `dependencies.yaml`
- `components.yaml` (type)

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| 依存グラフに循環がない | 「循環依存は禁止」 |
| frontend→infrastructureの直接依存がない | 「レイヤー違反禁止」 |
| sharedの外部依存が少ない | 「共有ライブラリは外部依存最小化」 |

### 抽出例

```yaml
# dependencies.yaml の入力
- from: src/app/
  to: src/lib/
  type: import
- from: src/lib/
  to: src/domain/
  type: import
# 循環なし

# 抽出される不変条件
- id: INV-ARCH-001
  category: architecture
  statement: 依存方向はapp→lib→domainであり、逆方向の依存は禁止
  verification:
    type: static
    method: eslint-plugin-import/no-cycle
```

### 典型的な不変条件

1. 循環依存は禁止
2. レイヤー違反禁止（presentation → infrastructure への直接依存）
3. sharedライブラリは外部依存を最小化する
4. フロントエンドはバックエンドの内部実装に依存しない

---

## API Contract

### 抽出元
- `api-contracts.yaml`

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| versionがパスに含まれている | 「バージョニングルールが存在」 |
| request_schemaが定義されている | 「入力バリデーション必須」 |
| errorsが統一フォーマット | 「エラーレスポンス統一」 |

### 抽出例

```yaml
# api-contracts.yaml の入力
- id: api-001
  path: /v1/orders
  request_schema:
    body:
      quantity: number (required, min: 1)
  errors:
    - code: 400
      format: { error: string, details: object }

# 抽出される不変条件
- id: INV-API-001
  category: api_contract
  statement: APIリクエストは必ずスキーマバリデーションを通過する
  verification:
    type: test
    method: 不正な入力でバリデーションエラーが返ることを確認
```

### 典型的な不変条件

1. 公開APIは後方互換性を維持する（破壊的変更はバージョンを上げる）
2. エラーレスポンスは統一フォーマットに従う
3. 入力は必ずバリデーションを通過してから処理する
4. レート制限を設け、DoS攻撃に耐える

---

## Failure

### 抽出元
- `failure-modes.yaml`
- `runtime.yaml` (retry_policy, timeout)

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| timeoutが設定されている | 「タイムアウト必須」 |
| recoveryが定義されている | 「障害回復戦略が存在」 |
| circuit_breakerがある | 「カスケード障害を防止」 |

### 抽出例

```yaml
# failure-modes.yaml の入力
- id: failure-001
  component: payment-gateway
  symptoms: タイムアウト
  recovery: リトライ後にフォールバック決済

# runtime.yaml の入力
- id: job-001
  configuration:
    timeout: 30000

# 抽出される不変条件
- id: INV-FAIL-001
  category: failure
  statement: 外部サービス呼び出しは30秒でタイムアウトし、フォールバック戦略を持つ
```

### 典型的な不変条件

1. 外部サービス障害時のフォールバック戦略を持つ
2. タイムアウトは必ず設定し、無限待機を禁止する
3. キャッシュ不整合時の自動回復策を持つ（TTL/invalidation）
4. 部分障害時もシステム全体は継続稼働する（graceful degradation）

---

## Environment

### 抽出元
- `environments.yaml`
- `secrets-config.yaml`

### パターン

| シグナル | 抽出する不変条件 |
|---------|-----------------|
| 本番環境に踏み台が設定されている | 「本番直接アクセス禁止」 |
| migration必須フラグがある | 「スキーマ差分禁止」 |
| env変数にデフォルト値がない | 「明示的設定必須」 |

### 抽出例

```yaml
# environments.yaml の入力
- id: production
  access:
    method: bastion
    direct_access: false

# 抽出される不変条件
- id: INV-ENV-001
  category: environment
  statement: 本番環境への直接アクセスは禁止（踏み台経由必須）
  verification:
    type: runtime
    method: セキュリティグループで直接アクセスがブロックされていることを確認
```

### 典型的な不変条件

1. 本番環境への直接アクセスは禁止（踏み台経由）
2. 環境間でスキーマ差分を許容しない（migration必須）
3. 環境変数はデフォルト値を持たない（明示的に設定必須）
