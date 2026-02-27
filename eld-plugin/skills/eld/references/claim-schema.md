# Claim Schema 仕様

ELD v2.3 の知識管理における最小単位「claim（主張）」のスキーマ定義。

## 最小スキーマ

```json
{
  "claim_id": "clm_<uuid_short>",
  "content": "string",
  "source": ["file:<path>:<line>", "test:<name>", "commit:<hash>"],
  "epistemic_status": "verified | inferred | unknown",
  "last_verified_at": "ISO8601",
  "ttl": "duration (e.g., 7d, 24h, 30d)",
  "importance": "S0 | S1 | S2 | S3"
}
```

## フィールド定義

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `claim_id` | string | Yes | 一意識別子。`clm_`プレフィックス |
| `content` | string | Yes | 主張の内容。自然言語 |
| `source` | string[] | 条件付き | 出典リスト。`verified`時は1つ以上必須 |
| `epistemic_status` | enum | Yes | 認識論的状態 |
| `last_verified_at` | ISO8601 | Yes | 最終検証日時 |
| `ttl` | duration | Yes | 有効期間 |
| `importance` | enum | Yes | 重要度（Severity準拠） |

## Source タグ形式

| タグ | 形式 | 例 |
|------|------|-----|
| ファイル参照 | `file:<path>:<line>` | `file:src/auth/login.ts:42` |
| テスト参照 | `test:<test_name>` | `test:test_login_success` |
| コミット参照 | `commit:<hash>` | `commit:a1b2c3d` |
| レビュー参照 | `review:<reviewer>` | `review:@alice` |
| ADR参照 | `adr:<id>` | `adr:ADR-007` |

## Validation Rules

### 1. Source必須化

```
if epistemic_status == "verified":
  assert len(source) >= 1
  // sourceが空の場合 → 自動降格: verified → inferred
```

### 2. DISCARD不可制約

```
if importance in ["S0", "S1"]:
  assert action != "DISCARD"
  // S0/S1は最低でもSUMMARIZEに回す
```

### 3. TTL超過チェック

```
if now > last_verified_at + ttl:
  if epistemic_status == "verified":
    epistemic_status = "inferred"  // 自動降格
  elif epistemic_status == "inferred":
    epistemic_status = "unknown"   // 自動降格
```

### 4. Source変更検知

```
for s in source:
  if s.startsWith("file:"):
    path, line = parse(s)
    if git.hasChanged(path, since=last_verified_at):
      epistemic_status = "inferred"  // 自動降格
```

## Auto-Tagging 動作

claimの保存時にsourceを自動的にタグ付けする:

### 自動タグ付けルール

1. **コード参照**: `Read`ツールで読んだファイルの行を自動的に`file:<path>:<line>`でタグ付け
2. **テスト結果**: テスト実行結果を`test:<name>`でタグ付け
3. **コミット**: 変更をコミットした際に`commit:<hash>`でタグ付け

### 自動タグ付けフロー

```
claim作成
  ↓
sourceフィールドが空?
  ├─ Yes: epistemic_statusを"inferred"に設定
  └─ No: 各sourceの形式を検証
          ├─ 有効 → そのまま保持
          └─ 無効 → 警告を出力、sourceから除外
```

## Auto-Downgrade（自動降格）

### 降格フロー

```
verified ──[source変更検知]──→ inferred ──[TTL超過]──→ unknown
    ↑                                                      │
    └────────────[手動再検証]───────────────────────────────┘
```

### 降格条件サマリ

| 現在のstatus | 条件 | 降格先 |
|-------------|------|--------|
| verified | sourceファイルがgit変更された | inferred |
| verified | sourceが空になった | inferred |
| verified | TTL超過 | inferred |
| inferred | TTL超過 | unknown |
| unknown | - | （最低レベル、これ以上降格しない） |

### 昇格条件

| 現在のstatus | 条件 | 昇格先 |
|-------------|------|--------|
| unknown | 手動で再検証 + source付与 | verified |
| inferred | source付与 + last_verified_at更新 | verified |

## 動的メモリポリシーとの連携

```
importance × 鮮度 → アクション

鮮度 = now - last_verified_at

高重要度(S0/S1) + 高鮮度(< ttl)  → KEEP
高重要度(S0/S1) + 低鮮度(≥ ttl)  → SUMMARIZE
低重要度(S2/S3) + 高鮮度(< ttl)  → KEEP
低重要度(S2/S3) + 低鮮度(≥ ttl)  → DISCARD
```

## 使用例

### 検証済みclaim

```json
{
  "claim_id": "clm_auth_jwt",
  "content": "認証はJWTベース。有効期限は1時間。リフレッシュトークンは7日",
  "source": [
    "file:src/auth/jwt.ts:15",
    "test:test_jwt_expiration",
    "adr:ADR-003"
  ],
  "epistemic_status": "verified",
  "last_verified_at": "2026-02-28T10:00:00Z",
  "ttl": "30d",
  "importance": "S0"
}
```

### 推論claimn

```json
{
  "claim_id": "clm_cache_pattern",
  "content": "キャッシュはLRUパターンを使用している模様",
  "source": [],
  "epistemic_status": "inferred",
  "last_verified_at": "2026-02-25T10:00:00Z",
  "ttl": "7d",
  "importance": "S2"
}
```
