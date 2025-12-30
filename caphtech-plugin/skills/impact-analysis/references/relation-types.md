# Relation Types（関係タイプ一覧）

コード依存の関係タイプとその検出方法。

## Direct Relations（直接関係）

### caller

対象を直接呼び出している。

```typescript
// auth.ts から login.ts の authenticateUser を呼び出し
function handleLogin() {
  authenticateUser(credentials);  // caller関係
}
```

**検出**: 関数呼び出し、メソッド呼び出し

### callee

対象から呼び出されている。

```typescript
// login.ts の authenticateUser から validatePassword を呼び出し
function authenticateUser() {
  validatePassword(password);  // validatePassword は callee
}
```

**検出**: 関数内の呼び出し先

### importer

対象をimport/requireしている。

```typescript
import { authenticateUser } from '../auth/login';  // importer関係
const auth = require('./auth');  // importer関係
```

**検出**: import文、require文

### override

対象メソッドをオーバーライドしている。

```typescript
class CustomAuth extends BaseAuth {
  authenticateUser() {  // BaseAuth.authenticateUser を override
    // カスタム実装
  }
}
```

**検出**: クラス継承、メソッドオーバーライド

### implements

対象インターフェースを実装している。

```typescript
class AuthService implements IAuthService {
  authenticateUser() {  // IAuthService.authenticateUser を implements
    // 実装
  }
}
```

**検出**: implements宣言

### type_depends

型として依存している。

```typescript
function processUser(user: User): AuthResult {  // User, AuthResult に type_depends
  // ...
}

const config: AuthConfig = { ... };  // AuthConfig に type_depends
```

**検出**: 型注釈、ジェネリクス

## Runtime Relations（ランタイム関係）

### route_maps_to

ルーティング設定で対応している。

```typescript
// Express
app.post('/login', loginHandler);  // '/login' が loginHandler に route_maps_to

// NestJS
@Post('/login')
async login() { ... }  // デコレータで route_maps_to
```

**検出**: ルーティング設定、デコレータ

### di_binds_to

DIコンテナでバインドされている。

```typescript
// NestJS
@Injectable()
class AuthService {
  constructor(private userRepo: UserRepository) { }  // DIバインド
}

// 手動DI
container.bind(IAuthService).to(AuthServiceImpl);  // di_binds_to
```

**検出**: DIコンテナ設定、コンストラクタインジェクション

**注意**: DI関係は静的解析が困難なため、confidence を下げて報告。

## Transitive Relations（間接関係）

### depends_on_caller

直接のcallerを経由して依存。

```
A → B → C
AがBを呼び出し、BがCを呼び出す場合:
A は C に depends_on_caller（depth=2）
```

### fanout_from_entrypoint

エントリポイントからの波及。

```
/login → authMiddleware → authenticateUser → ...
エントリポイントからのファンアウト
```

### shared_middleware

共有ミドルウェア経由の関係。

```typescript
// 複数ルートが同じミドルウェアを使用
app.use('/api/*', authMiddleware);

// /api/users と /api/orders は shared_middleware
```

## 関係の強さ

| relation | 強さ | 説明 |
|----------|------|------|
| `caller` | 高 | 直接呼び出し、変更が即座に影響 |
| `importer` | 高 | import変更でエラー |
| `override` | 高 | 振る舞いの変更が影響 |
| `type_depends` | 中 | 型変更でコンパイルエラー |
| `route_maps_to` | 中 | ルーティング変更で影響 |
| `di_binds_to` | 中 | DI設定次第で影響 |
| `depends_on_caller` | 低 | 間接的影響 |

## 不確実性

静的解析で追跡困難な関係:

| パターン | 理由 | 対処 |
|----------|------|------|
| DI | 実行時にバインド決定 | DI設定の確認を推奨 |
| 動的ディスパッチ | 実行時に型決定 | 基底クラスの実装を確認 |
| 文字列ルーティング | パターンマッチが必要 | ルーティング設定を確認 |
| リフレクション | 実行時に解決 | ログで確認を推奨 |
| eval/動的require | 静的解析不可 | unknownsに記載 |

```yaml
# 不確実な関係の報告例
- ref: "src/services/*.ts"
  relation: "di_binds_to"
  confidence: 0.4
  evidence:
    - "DIコンテナ経由のバインドが存在する可能性"
    - "静的解析では追跡不能"
```
