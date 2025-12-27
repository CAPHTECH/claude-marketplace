# 出力テンプレート

## 層A: インターフェースspec（YAML）

### 基本構造

```yaml
# spec-gen: 層A インターフェースspec
# Generated: YYYY-MM-DD
# Target: [対象モジュール/エンドポイント]

version: "1.0"
spec_type: interface
layer: A
generated_at: "2024-01-15T10:30:00Z"

# メタ情報
meta:
  target: src/api/users.ts
  scope: user-management
  maintainer: Unknown

# エンドポイント一覧
endpoints:
  - id: get-user
    path: /api/users/{id}
    method: GET
    confidence: Observed
    evidence:
      file: src/api/routes.ts
      line: 23
      symbol: userRoutes

    request:
      params:
        id:
          type: string
          format: uuid
          required: true
          confidence: Verified
          evidence:
            file: tests/api/users.test.ts
            line: 45

      headers:
        Authorization:
          type: string
          required: true
          pattern: "Bearer .*"
          confidence: Observed
          evidence:
            file: src/middleware/auth.ts
            line: 12

    response:
      success:
        status: 200
        content_type: application/json
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string
            email:
              type: string
            created_at:
              type: string
              format: date-time
        confidence: Observed
        evidence:
          file: src/api/users.ts
          line: 52-60

      errors:
        - status: 401
          code: UNAUTHORIZED
          message: "認証が必要"
          confidence: Observed
          evidence:
            file: src/middleware/auth.ts
            line: 25

        - status: 404
          code: USER_NOT_FOUND
          message: "ユーザーが見つからない"
          confidence: Observed
          evidence:
            file: src/api/users.ts
            line: 48
```

### 複数エンドポイント版

```yaml
# 複数エンドポイントをまとめる場合
endpoints:
  - id: create-user
    path: /api/users
    method: POST
    # ... 詳細

  - id: get-user
    path: /api/users/{id}
    method: GET
    # ... 詳細

  - id: update-user
    path: /api/users/{id}
    method: PUT
    # ... 詳細

  - id: delete-user
    path: /api/users/{id}
    method: DELETE
    # ... 詳細
```

## 層B: 振る舞いspec（YAML）

### 基本構造

```yaml
# spec-gen: 層B 振る舞いspec
# Generated: YYYY-MM-DD
# Target: [対象機能/ユースケース]

version: "1.0"
spec_type: behavior
layer: B
generated_at: "2024-01-15T10:30:00Z"

meta:
  target: user-registration
  scope: user-management
  related_interface: get-user

# 振る舞い定義
behavior:
  # 前提条件
  preconditions:
    - id: pre-01
      condition: "リクエストが認証済み"
      confidence: Observed
      evidence:
        file: src/middleware/auth.ts
        line: 12-25

    - id: pre-02
      condition: "ユーザーIDが有効なUUID形式"
      confidence: Verified
      evidence:
        file: tests/api/users.test.ts
        line: 78

  # 事後条件
  postconditions:
    - id: post-01
      condition: "ユーザー情報が返却される"
      confidence: Verified
      evidence:
        file: tests/api/users.test.ts
        line: 85

    - id: post-02
      condition: "アクセスログが記録される"
      confidence: Observed
      evidence:
        file: src/middleware/logging.ts
        line: 34

  # 禁止条件
  prohibitions:
    - id: prohib-01
      condition: "削除済みユーザーの情報は返さない"
      confidence: Observed
      evidence:
        file: src/services/user.ts
        line: 45

  # 副作用
  side_effects:
    database:
      - type: read
        table: users
        confidence: Observed
        evidence:
          file: src/repositories/user.ts
          line: 23

    external:
      - type: none
        note: "外部API呼び出しなし"
        confidence: Observed

    async:
      - type: none
        note: "非同期処理なし"
        confidence: Observed

    cache:
      - type: read
        key: "user:{id}"
        confidence: Assumed
        evidence:
          file: src/services/user.ts
          line: 30
        note: "キャッシュ実装が不明確"

  # 状態遷移（該当する場合）
  state_transitions:
    - id: st-01
      from: null
      to: null
      trigger: "GET /api/users/{id}"
      note: "読み取り専用、状態変更なし"
      confidence: Observed

  # 不変条件
  invariants:
    - id: inv-01
      statement: "同一IDで常に同一ユーザーが返る（キャッシュ期間内）"
      confidence: Assumed
      evidence: null
      note: "明示的な保証がコードにない"

  # エラーモデル
  error_model:
    - condition: "ユーザーが存在しない"
      error_code: USER_NOT_FOUND
      http_status: 404
      retryable: false
      confidence: Observed
      evidence:
        file: src/api/users.ts
        line: 48

    - condition: "認証トークンが無効"
      error_code: UNAUTHORIZED
      http_status: 401
      retryable: true
      retry_hint: "新しいトークンで再試行"
      confidence: Observed
      evidence:
        file: src/middleware/auth.ts
        line: 25
```

### 状態機械がある場合

```yaml
state_machine:
  name: order-status
  initial: draft
  states:
    - name: draft
      description: "下書き状態"
    - name: pending
      description: "確認待ち"
    - name: confirmed
      description: "確定済み"
    - name: shipped
      description: "発送済み"
    - name: delivered
      description: "配達完了"
    - name: cancelled
      description: "キャンセル"

  transitions:
    - from: draft
      to: pending
      trigger: submit
      confidence: Observed
      evidence:
        file: src/services/order.ts
        line: 45

    - from: pending
      to: confirmed
      trigger: confirm
      guard: "支払い完了"
      confidence: Observed
      evidence:
        file: src/services/order.ts
        line: 67

    - from: [draft, pending]
      to: cancelled
      trigger: cancel
      confidence: Observed
      evidence:
        file: src/services/order.ts
        line: 89
```

## 層C: 業務意味spec（Markdown）

### 基本構造

```markdown
# 業務意味spec: [機能名]

> **注意**: この層はコードから直接導出困難。草案として扱い、人間レビュー必須。

## 概要

[Assumed] [機能の概要を1-2文で記述]

## 目的

[Unknown] 具体的なビジネス目的は不明。以下は推測:

- ユーザー管理機能の一部として提供
- 認証済みユーザーによる情報参照を可能にする

## 使用コンテキスト

[Assumed] 以下のシナリオで使用される可能性:

1. ユーザープロフィール画面での表示
2. 管理画面でのユーザー確認
3. 他サービスからのユーザー情報参照

## 設計判断

[Unknown] 以下の設計判断の理由は不明:

- なぜRESTful APIとして実装されたか
- なぜキャッシュ戦略がこうなっているか
- なぜ特定のエラーコード体系を採用したか

## トレードオフ

[Assumed] 推測されるトレードオフ:

| 選択 | 優先したもの | 犠牲にしたもの |
|------|------------|--------------|
| 同期API | シンプルさ | スケーラビリティ |
| UUIDベースID | 分散生成 | 順序性 |

## 非機能要件

[Unknown] 以下は測定または確認が必要:

- 性能目標: 不明
- 可用性目標: 不明
- セキュリティ要件: 認証必須（Observed）

## 関連ドキュメント

[Unknown] 関連するADRやドキュメントは未発見

---

## レビュー依頼

この層の内容は人間による確認が必要です:

- [ ] 目的の正確性を確認
- [ ] 使用コンテキストの網羅性を確認
- [ ] 設計判断の理由を補完
- [ ] 非機能要件を明確化
```

## ファイル命名規則

```
specs/
├── layer-a/
│   ├── users-api.yaml
│   ├── orders-api.yaml
│   └── auth-api.yaml
├── layer-b/
│   ├── user-registration.yaml
│   ├── order-processing.yaml
│   └── payment-flow.yaml
└── layer-c/
    ├── user-management.md
    ├── order-management.md
    └── payment-system.md
```

## 統合spec（全層まとめ）

必要に応じて、1ファイルにまとめる場合:

```yaml
# spec-gen: 統合spec
# Target: user-get

meta:
  version: "1.0"
  generated_at: "2024-01-15T10:30:00Z"
  target: user-get

layer_a:
  # ... インターフェースspec

layer_b:
  # ... 振る舞いspec

layer_c:
  # Markdownをembedded stringで
  content: |
    # 業務意味spec
    ...
```
