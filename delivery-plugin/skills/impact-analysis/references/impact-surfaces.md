# Impact Surfaces（影響面の詳細定義）

8つの影響面の詳細な分析対象と検出方法。

## 1. code（コード依存）

呼び出し関係・import・型依存などの静的コード依存。

### 分析対象

| 対象 | 説明 |
|------|------|
| 呼び出しグラフ | 関数/メソッドの呼び出し関係 |
| import/require | モジュールのインポート関係 |
| 継承/実装 | クラス継承、インターフェース実装 |
| 型依存 | 型定義への依存 |

### 検出パターン

```typescript
// caller: 対象を呼び出している
authenticateUser(credentials);

// importer: 対象をimportしている
import { authenticateUser } from '../auth/login';

// type_depends: 型として依存
function process(user: User): AuthResult { ... }

// override: オーバーライド
class CustomAuth extends BaseAuth {
  authenticateUser() { ... }  // override
}
```

### direct vs transitive

- **direct**: 直接の参照・呼び出し（depth=1）
- **transitive**: 間接的な依存（depth>1）

transitive の追跡は `max_graph_depth` で制限。

## 2. interface（公開インターフェース）

外部に公開されているAPIや型定義の変更。

### 分析対象

| 対象 | 説明 |
|------|------|
| export | エクスポートされた関数/クラス/定数 |
| REST API | HTTPエンドポイント |
| GraphQL | スキーマ/リゾルバ |
| イベント | 発行/購読するイベント |
| 型定義 | 公開型の変更 |

### 互換性判定

| compatibility | 条件 |
|---------------|------|
| `breaking` | シグネチャ変更、必須パラメータ追加、戻り値型変更 |
| `non_breaking` | オプショナルパラメータ追加、内部実装のみ変更 |
| `unknown` | 判定不能 |

### 検出パターン

```typescript
// exported_function
export function authenticateUser(...) { ... }

// api_endpoint
@Post('/login')
async login(@Body() dto: LoginDto) { ... }

// type
export interface User {
  id: string;
  email: string;  // フィールド追加→breaking可能性
}
```

## 3. data（データストア）

データベース、キャッシュ、ファイルシステムへの操作。

### 分析対象

| store | 説明 |
|-------|------|
| `postgres`/`mysql` | RDBMSへのCRUD |
| `redis` | キャッシュ/セッション操作 |
| `dynamodb`/`mongodb` | NoSQL操作 |
| `filesystem` | ファイルI/O |

### 操作種別

| operation | リスク | 説明 |
|-----------|--------|------|
| `read` | low | 読み取りのみ |
| `write` | high | 新規作成 |
| `upsert` | high | 更新または作成 |
| `delete` | high | 削除 |
| `migrate` | critical | スキーマ変更 |

### 検出パターン

```typescript
// SQL
await db.query('SELECT * FROM users WHERE id = $1', [userId]);
await db.query('UPDATE sessions SET expires_at = $1', [newExpiry]);

// ORM
const user = await userRepository.findOne({ id });
await sessionRepository.save(session);

// Redis
await redis.set(`session:${id}`, data);
await redis.del(`session:${id}`);
```

## 4. external（外部依存）

外部サービス、SaaS、メッセージングへの依存。

### 分析対象

| 種別 | 例 |
|------|-----|
| 外部API | Stripe, SendGrid, Slack |
| キャッシュ | Redis, Memcached |
| メッセージング | Kafka, RabbitMQ, SQS |
| ストレージ | S3, GCS |
| 認証 | Auth0, Firebase Auth |

### 障害モード

外部依存には必ず障害モードを検討:

```yaml
failure_modes:
  - "タイムアウト時: リトライ3回後にエラー"
  - "接続断時: フォールバックキャッシュを使用"
  - "レート制限時: 429を返却"
```

## 5. config（設定・環境）

環境変数、Feature Flag、権限設定など。

### 分析対象

| 種別 | 例 |
|------|-----|
| 環境変数 | `AUTH_JWT_TTL`, `DATABASE_URL` |
| Feature Flag | `ENABLE_NEW_AUTH` |
| 権限設定 | IAM, RBAC |
| タイムアウト | 接続/リクエストタイムアウト |
| リトライ | リトライ回数/間隔 |

### 検出パターン

```typescript
// 環境変数
const ttl = process.env.AUTH_JWT_TTL || '3600';

// Feature Flag
if (featureFlags.isEnabled('NEW_AUTH_FLOW')) { ... }

// 設定ファイル
const config = require('./config.json');
```

## 6. runtime_quality（実行時品質）

性能と可用性への影響。

### 性能（performance）

| リスクパターン | 説明 |
|----------------|------|
| N+1クエリ追加 | ループ内でのDB呼び出し |
| 同期ブロック追加 | 外部API呼び出しの追加 |
| メモリ増加 | 大量データのロード |
| CPU負荷増加 | 計算量の増加 |

### 可用性（availability）

| リスクパターン | 説明 |
|----------------|------|
| SPOF追加 | 単一障害点の導入 |
| 必須依存追加 | 外部サービスが必須に |
| タイムアウト増加 | 全体レイテンシの増加 |

## 7. security_privacy（セキュリティ・プライバシー）

セキュリティとプライバシーへの影響。

### 懸念タイプ

| type | 説明 |
|------|------|
| `authn` | 認証に関する変更 |
| `authz` | 認可に関する変更 |
| `session` | セッション管理 |
| `pii` | 個人情報の取り扱い |
| `injection` | インジェクションリスク |
| `logging_sensitive` | 機密情報のログ出力 |
| `rate_limit` | レート制限 |
| `csrf` | CSRF対策 |

### 検出観点

- 認証/認可ロジックの変更
- 資格情報の取り扱い
- ユーザー入力の処理
- ログ出力内容
- エラーメッセージの内容

## 8. observability（観測性）

ログ、メトリクス、トレースへの影響。

### 分析対象

| 対象 | 確認事項 |
|------|----------|
| ログ | 新しいログポイントが必要か |
| メトリクス | 新しいメトリクスが必要か |
| トレース | スパンの追加が必要か |
| アラート | 閾値の見直しが必要か |

### 設計観点

- 障害検知に十分なログが出るか
- 性能監視に必要なメトリクスがあるか
- 分散トレースで追跡可能か
- 既存ダッシュボードへの影響
