# 出力テンプレート集

## 成果物一覧

| 成果物 | 用途 | 更新頻度 |
|--------|------|---------|
| Codebase Map | 全体像把握 | 構造変更時 |
| 代表フロー | 重要処理の理解 | フロー変更時 |
| Change Playbook | 変更時の確認 | 依存関係変更時 |
| 設定/外部I/F台帳 | 環境構築・運用 | 設定追加時 |
| Fact Index | 参照用索引 | シンボル変更時 |
| 検証レポート | 品質記録 | 生成時 |

---

## 1. Codebase Map

```markdown
# Codebase Map: [プロジェクト名]

生成日: YYYY-MM-DD
対象コミット: [hash]

## システム概要

[1-2文でシステムの目的を説明]

## モジュール構成

| モジュール | 責務 | 主要依存 | 備考 |
|-----------|------|---------|------|
| src/api/ | HTTPハンドラ、ルーティング | services | REST API定義 |
| src/services/ | ビジネスロジック | repositories | トランザクション境界 |
| src/repositories/ | データアクセス | db | SQL発行 |
| src/events/ | イベント発行・購読 | services | 非同期処理 |
| src/jobs/ | バッチ処理 | services | スケジューラ連携 |

## エントリポイント

| 種類 | 場所 | 起動方法 | 備考 |
|------|------|---------|------|
| HTTP | src/api/server.ts | `npm run start` | ポート: 3000 |
| CLI | src/cli/main.ts | `npm run cli -- <cmd>` | 管理操作用 |
| Worker | src/worker/index.ts | `npm run worker` | ジョブ処理 |
| Consumer | src/events/consumer.ts | `npm run consumer` | イベント購読 |

## 主要データ

| エンティティ | テーブル | 責務 | 関連 |
|-------------|---------|------|------|
| User | users | ユーザー情報 | sessions, orders |
| Session | sessions | ログインセッション | users |
| Order | orders | 注文情報 | users, items |

## 外部境界

| 外部システム | 用途 | 設定キー | 障害時の挙動 |
|-------------|------|---------|-------------|
| PostgreSQL | 永続化 | DATABASE_URL | 503エラー返却 |
| Redis | セッション/キャッシュ | REDIS_URL | DBフォールバック |
| SendGrid | メール送信 | SENDGRID_API_KEY | キューイング |
| Stripe | 決済 | STRIPE_SECRET_KEY | リトライ後失敗 |

## ディレクトリ構造

```
src/
├── api/           # HTTPハンドラ
│   ├── routes/    # ルート定義
│   └── middleware/ # ミドルウェア
├── services/      # ビジネスロジック
├── repositories/  # データアクセス
├── models/        # ドメインモデル
├── events/        # イベント処理
├── jobs/          # バッチ処理
└── config/        # 設定
```
```

---

## 2. 代表フロー

```markdown
# 代表フロー: [フロー名]

## 概要

**目的**: [何を達成するフローか]
**選定理由**: [なぜ代表フローに選んだか]
  - 変更頻度: [高/中/低]
  - 境界カバー: [認証/DB/非同期/外部連携/削除]

## 成功シナリオ

### シーケンス

```
[Client] → POST /api/users
    ↓
[UsersController.create] (src/api/users.ts:45)
    ↓ validate
[UserService.register] (src/services/user.ts:78)
    ↓ hash password
[UserRepository.insert] (src/repositories/user.ts:34)
    ↓ INSERT users
[EventPublisher.emit] (src/events/publisher.ts:12)
    ↓ user.created
[201 Created]
```

### 入出力

**入力**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**出力**
```json
{
  "id": "usr_xxx",
  "email": "user@example.com",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### 副作用

| 種類 | 詳細 | 根拠 |
|------|------|------|
| DB | INSERT users | (UserRepository.ts:34) |
| Event | user.created | (EventPublisher.ts:12) |
| Log | INFO user_registered | (UserService.ts:92) |

### 検証ポイント

- [ ] 201 Created が返却される
- [ ] users テーブルにレコードが作成される
- [ ] user.created イベントが発行される
- [ ] パスワードがハッシュ化されている

## 失敗シナリオ1: 重複メールアドレス

### 条件
既存ユーザーと同一のメールアドレスで登録を試みた場合

### 発生箇所
UserService.register:92 (src/services/user.ts:92)

### シーケンス

```
[UserService.register]
    ↓ check email exists
    ↓ email already exists
[DuplicateEmailError]
    ↓
[409 Conflict]
```

### 出力
```json
{
  "error": "DUPLICATE_EMAIL",
  "message": "Email already registered"
}
```

### 副作用
- DB: なし（ロールバック）
- Log: WARN duplicate_email_attempt

## 失敗シナリオ2: DB接続エラー

### 条件
PostgreSQLへの接続がタイムアウトした場合

### 発生箇所
UserRepository.insert:34 (src/repositories/user.ts:34)

### シーケンス

```
[UserRepository.insert]
    ↓ connection timeout
[DatabaseConnectionError]
    ↓ retry 3 times
    ↓ all retries failed
[500 Internal Server Error]
```

### 出力
```json
{
  "error": "INTERNAL_ERROR",
  "message": "Service temporarily unavailable"
}
```

### 副作用
- DB: なし
- Log: ERROR db_connection_failed
- Alert: PagerDuty通知

## 不変条件

| 条件 | 説明 | 検証 | 根拠 |
|------|------|------|------|
| メール一意性 | システム内でメールは一意 | UNIQUE制約 | (migrations/001.sql:12) |
| パスワード非平文 | パスワードは必ずハッシュ化 | bcrypt適用 | (UserService.ts:85) |
| 監査ログ | 登録操作は必ずログ記録 | INFO出力 | (UserService.ts:92) |

## 関連テスト

| テスト | ファイル | カバー範囲 |
|--------|---------|-----------|
| ユニット | tests/services/user.test.ts | ビジネスロジック |
| 統合 | tests/integration/user_registration.test.ts | DB連携 |
| E2E | tests/e2e/signup.spec.ts | 全フロー |
```

---

## 3. Change Playbook

```markdown
# Change Playbook: [変更対象]

## 影響範囲マップ

```
[変更対象: UserService]
  ├── 直接依存
  │   ├── UsersController (src/api/users.ts)
  │   ├── AuthService (src/services/auth.ts)
  │   └── NotificationService (src/services/notification.ts)
  └── 間接依存
      ├── SessionService (via AuthService)
      └── EmailService (via NotificationService)
```

## 変更パターン

### パターン1: メソッド追加

**確認事項**
- [ ] 既存インターフェースとの整合性
- [ ] 依存サービスへの影響なし
- [ ] テスト追加済み

**必須テスト**
- tests/services/user.test.ts

### パターン2: シグネチャ変更

**確認事項**
- [ ] 呼び出し元をすべて更新
- [ ] 後方互換性の検討
- [ ] 関連ドキュメント更新

**必須テスト**
- tests/services/user.test.ts
- tests/api/users.test.ts
- tests/integration/user_*.test.ts

### パターン3: 外部連携変更

**確認事項**
- [ ] 障害時挙動の更新
- [ ] リトライ設定の確認
- [ ] タイムアウト設定の確認
- [ ] アラート設定の確認

**必須テスト**
- tests/integration/user_external.test.ts

## 破壊的変更の境界

| 変更 | 影響範囲 | 対策 |
|------|---------|------|
| User エンティティ変更 | 全API | マイグレーション必須 |
| 認証トークン形式変更 | 全クライアント | バージョニング |
| イベントペイロード変更 | 購読者全体 | 段階的移行 |

## レビュー観点

### 必須確認

- [ ] 後方互換性は維持されているか
- [ ] 既存テストは通るか
- [ ] 新規テストは追加されているか
- [ ] 不変条件は維持されているか

### セキュリティ

- [ ] 認証・認可に影響がないか
- [ ] 入力バリデーションは適切か
- [ ] 機密情報の扱いは適切か

### 運用

- [ ] ログ出力は適切か
- [ ] メトリクスへの影響は考慮されているか
- [ ] ロールバック可能か
```

---

## 4. 設定/外部I/F台帳

```markdown
# 設定/外部I/F台帳

## 環境変数

| キー | 用途 | 必須 | デフォルト | 例 |
|------|------|:----:|-----------|-----|
| DATABASE_URL | DB接続 | ✓ | - | postgres://... |
| REDIS_URL | Redis接続 | ✓ | - | redis://... |
| JWT_SECRET | JWT署名 | ✓ | - | [32文字以上] |
| LOG_LEVEL | ログレベル | | info | debug/info/warn/error |
| PORT | HTTPポート | | 3000 | 3000 |

## 外部API

| サービス | 用途 | エンドポイント | 認証 | タイムアウト |
|---------|------|--------------|------|-------------|
| SendGrid | メール送信 | api.sendgrid.com | API Key | 30s |
| Stripe | 決済 | api.stripe.com | Secret Key | 60s |
| S3 | ファイル保存 | s3.amazonaws.com | IAM Role | 30s |

## 外部システム障害時挙動

| システム | 障害検知 | 挙動 | 復旧 |
|---------|---------|------|------|
| PostgreSQL | 接続タイムアウト | 503返却 | 自動再接続 |
| Redis | 接続エラー | DBフォールバック | 自動再接続 |
| SendGrid | 4xx/5xx | キューイング | リトライ |
| Stripe | タイムアウト | リトライ3回後失敗 | 手動確認 |

## イベント

### 発行

| イベント名 | 発行元 | ペイロード | 根拠 |
|-----------|--------|-----------|------|
| user.created | UserService | `{userId, email}` | (publisher.ts:12) |
| order.placed | OrderService | `{orderId, userId, items}` | (publisher.ts:45) |

### 購読

| イベント名 | 購読者 | 処理 | 根拠 |
|-----------|--------|------|------|
| user.created | NotificationService | ウェルカムメール送信 | (consumer.ts:23) |
| order.placed | InventoryService | 在庫引当 | (consumer.ts:56) |
```

---

## 5. 検証レポート

```markdown
# 検証レポート

生成日: YYYY-MM-DD
対象: [ドキュメント名]

## サマリー

| ゲート | 結果 | 詳細 |
|--------|:----:|------|
| Evidence Gate | ⚠️ | 3件の表現弱め、2件の隔離 |
| Consistency Gate | ✅ | 矛盾なし |
| Task-based | ⚠️ | 2件の追記必要 |

## Evidence Gate

### 弱めた断定 (3件)

1. **キャッシュ導入理由**
   - 元: 「性能最適化のために導入された」
   - 後: 「キャッシュが存在する（導入理由は未確認）」

2. **リトライ回数**
   - 元: 「最適値として3回に設定」
   - 後: 「リトライ回数は3回（config.ts:45）」

3. **タイムアウト値**
   - 元: 「SLO基準で30秒」
   - 後: 「タイムアウトは30秒（config.ts:52）」

### 隔離した事項 (2件)

- キャッシュTTL設計の意図
- レート制限値の根拠

## Consistency Gate

矛盾なし

## Task-based Verification

### 要追記 (2件)

1. **Redis起動方法**
   - 場所: Codebase Map > 外部境界
   - 追記: `docker-compose up redis`

2. **テスト実行方法**
   - 場所: Change Playbook
   - 追記: `npm test`, `npm run test:integration`

## 次のアクション

- [ ] 隔離事項について開発者に確認依頼
- [ ] 要追記事項をドキュメントに反映
- [ ] 制約として constraints.md に記録
```
