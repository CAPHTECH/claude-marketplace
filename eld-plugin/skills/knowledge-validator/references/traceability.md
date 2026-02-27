# トレーサビリティ検証ワークフロー

## 概要

shirushiのDoc-IDとコードの参照関係を検証し、要件からコードへの双方向トレーサビリティを確保するワークフロー。

## shirushi Doc-ID形式

### ID構造

`.shirushi.yml`で定義されたID形式:

```
{COMP}-{KIND}-{SER4}-{CHK1}

例: DOC-REQ-0001-A
│    │    │    └─ チェックサム（mod26AZ）
│    │    └────── 連番（スコープ内で自動採番）
│    └─────────── 種別（REQ/SPEC/ADR/GUIDE等）
└──────────────── コンポーネント（DOC/ADR/COMP等）
```

### ドキュメント内での記述

```markdown
<!-- Doc-ID: DOC-REQ-0001-A -->
# 認証要件

...
```

## コード内参照形式

### 基本形式

```typescript
// @shirushi DOC-REQ-0001-A
export function authenticate() { ... }
```

### 複数参照

```typescript
// @shirushi DOC-REQ-0001-A
// @shirushi DOC-SPEC-0002-B
export function authenticate() { ... }
```

### 各言語での形式

```python
# @shirushi DOC-REQ-0001-A
def authenticate():
    pass
```

```go
// @shirushi DOC-REQ-0001-A
func Authenticate() { }
```

```java
// @shirushi DOC-REQ-0001-A
public void authenticate() { }
```

## 検証フロー

### 1. shirushi lint実行

```bash
shirushi lint --base main
```

出力:
- Doc-ID形式違反
- 重複Doc-ID
- チェックサムエラー

### 2. コード内参照の収集

```bash
python3 scripts/trace_doc_code.py \
  --src-dir src \
  --docs-dir docs \
  --output report.json
```

### 3. 照合マトリクス生成

```markdown
## Doc-ID ↔ Code 照合マトリクス

| Doc-ID | ドキュメント | コード参照 | 状態 |
|--------|-------------|-----------|------|
| DOC-REQ-0001-A | docs/req/auth.md | src/auth.ts:15 | ✅ |
| DOC-REQ-0002-B | docs/req/api.md | - | ⚠️ 未実装 |
| - | - | src/old.ts:10 | ❌ 孤立参照 |
```

### 4. pce-memory Relation登録

```
# Entity登録
pce_memory_upsert_entity(
  id="DOC-REQ-0001-A",
  type="Artifact",
  name="認証要件",
  attrs={file: "docs/req/auth.md", doc_type: "requirement"}
)

pce_memory_upsert_entity(
  id="CODE-auth-ts-15",
  type="Artifact",
  name="authenticate関数",
  attrs={file: "src/auth.ts", line: 15}
)

# Relation登録
pce_memory_upsert_relation(
  id="trace-req-0001",
  src_id="DOC-REQ-0001-A",
  dst_id="CODE-auth-ts-15",
  type="IMPLEMENTED_BY"
)
```

## 検証レポート形式

```markdown
## トレーサビリティ検証レポート

### サマリ
- 総Doc-ID数: N
- コード参照あり: X (XX%)
- コード参照なし: Y (YY%)
- 孤立参照: Z件

### shirushi lint結果
- 形式エラー: 0件
- 重複: 0件
- チェックサムエラー: 0件

### 未実装Doc-ID
| Doc-ID | ドキュメント | 理由 |
|--------|-------------|------|
| DOC-REQ-0002-B | docs/req/api.md | 未着手 |

### 孤立参照（要修正）
| ファイル | 参照 | 問題 |
|---------|------|------|
| src/old.ts:10 | DOC-REQ-9999-X | Doc-ID不存在 |

### 影響分析
Doc-ID変更時の影響を受けるファイル:
- DOC-REQ-0001-A → src/auth.ts, src/login.ts
```

## CI統合

### GitHub Actions例

```yaml
- name: Validate traceability
  run: |
    shirushi lint --base ${{ github.event.pull_request.base.sha }}
    python3 scripts/trace_doc_code.py --check
```

## 関係タイプ

| タイプ | 方向 | 意味 |
|--------|------|------|
| IMPLEMENTED_BY | Doc → Code | ドキュメントがコードで実装される |
| DOCUMENTS | Code → Doc | コードがドキュメントで説明される |
| TESTS | Test → Doc | テストがドキュメントを検証する |
| DERIVED_FROM | Doc → Doc | ドキュメントが別のドキュメントから派生 |
