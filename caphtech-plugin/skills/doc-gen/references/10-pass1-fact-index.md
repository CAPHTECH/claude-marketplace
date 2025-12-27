# Pass 1: 事実索引（Fact Index）

## 目的

コードから**根拠付きの事実**を抽出し、索引化する。
推測・意図は分離して扱う。

## 入力整形

### エントリポイント特定

以下を優先的に特定:

| 種類 | 例 |
|------|-----|
| HTTPハンドラ | Express routes, FastAPI endpoints |
| CLI | argparse, commander, cobra |
| イベント購読 | Kafka consumer, SQS listener |
| ジョブ起点 | cron, celery task, sidekiq |
| gRPC | protobuf service definitions |

### シンボル単位チャンク化

```
❌ 悪い例: 500行ごとに分割
  → 文脈が切れて誤解が増える

✅ 良い例: 意味単位で分割
  - 関数/メソッド
  - クラス/モジュール
  - エンドポイント
  - 設定ブロック
```

### 静的解析・メタデータ優先

AIに抽出させるのではなく、機械抽出を優先:

| 対象 | ツール/ファイル |
|------|----------------|
| API定義 | OpenAPI, GraphQL schema |
| DB構造 | マイグレーション, Prisma schema |
| 設定 | .env.example, config/*.yaml |
| 依存関係 | package.json, requirements.txt |
| テスト一覧 | test files, jest config |

## 事実抽出ルール

### 断定可能（Fact）

| カテゴリ | 例 |
|----------|-----|
| シグネチャ | `function createUser(email: string, password: string): User` |
| HTTPパス | `POST /api/v1/users` |
| 例外型 | `throws DuplicateEmailError, ValidationError` |
| 設定キー | `DATABASE_URL`, `REDIS_HOST` |
| 依存先 | `UserRepository`, `EmailService` |
| 戻り値型 | `Promise<User>`, `Result<User, Error>` |

### 断定不可（Hypothesis）

| カテゴリ | 扱い方 |
|----------|--------|
| 意図・理由 | 「不明」または「推測:」プレフィックス |
| 性能特性 | 「測定が必要」と明記 |
| 稀なパス | 「未検証」としてマーク |

## 根拠参照フォーマット

```markdown
# 必須形式
(ファイルパス:行範囲)

# 例
UserService.createUser (src/services/user.ts:45-78)
  - 入力: email, password
  - 出力: User | DuplicateEmailError
  - 副作用: DB INSERT users, Event user.created
```

## 副作用リスト（継続性の急所）

以下を必ず列挙:

| 副作用 | 記録すべき情報 |
|--------|---------------|
| DB書込み | テーブル名, 操作(INSERT/UPDATE/DELETE) |
| 外部API呼出し | エンドポイント, リトライ方針 |
| イベント発行 | イベント名, ペイロード構造 |
| ジョブ投入 | キュー名, 遅延設定 |
| キャッシュ更新 | キー, TTL, 無効化条件 |
| ファイルI/O | パス, 権限 |
| 外部サービス | SDK名, タイムアウト |

## 出力フォーマット

```markdown
# Fact Index: [モジュール名]

## シンボル一覧

### [シンボル名] (ファイル:行)
- **種類**: function | class | endpoint | config
- **シグネチャ**: `具体的な型情報`
- **入力**: パラメータ一覧
- **出力**: 戻り値型
- **例外**: スロー可能な例外
- **副作用**:
  - DB: [テーブル] [操作]
  - Event: [イベント名]
  - External: [サービス名]

### [次のシンボル]
...

## 依存関係

| 依存元 | 依存先 | 種類 |
|--------|--------|------|
| UserService | UserRepository | inject |
| UserService | EmailService | method call |

## 設定キー

| キー | 用途 | デフォルト | 必須 |
|------|------|-----------|------|
| DATABASE_URL | DB接続 | - | ✓ |

## 未確認事項

- [ ] XxxService の導入理由（ADR未発見）
- [ ] キャッシュTTL の根拠
```

## チェックリスト

```markdown
### 入力整形
- [ ] エントリポイントを特定したか
- [ ] シンボル単位でチャンク化したか
- [ ] 静的解析結果を優先収集したか

### 事実抽出
- [ ] Fact と Hypothesis を分離したか
- [ ] 根拠参照を付けたか
- [ ] 意図の断定を避けたか

### 副作用
- [ ] DB操作を列挙したか
- [ ] 外部API呼出しを列挙したか
- [ ] イベント発行を列挙したか
- [ ] ジョブ投入を列挙したか
- [ ] キャッシュ更新を列挙したか
```
