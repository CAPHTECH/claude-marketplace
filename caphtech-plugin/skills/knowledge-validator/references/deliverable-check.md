# 成果物検証ワークフロー

## 概要

成果物が要件を満たしているかを検証するワークフロー。shirushiのDoc-IDを活用したトレーサビリティ検証を含む。

## ステップ1: 要件の収集

### pce-memoryから要件を取得

```
pce_memory_activate(
  scope=["project"],
  q="要件 仕様 spec requirement",
  top_k=30
)
```

### shirushiインデックスから要件Doc-IDを取得

```bash
shirushi scan --format json | jq '.[] | select(.kind == "REQ")'
```

### 要件リストの整理

```markdown
| Doc-ID | 要件 | 優先度 | ソース |
|--------|------|--------|--------|
| DOC-REQ-0001-A | [要件内容] | 高 | docs/requirements/auth.md |
| DOC-REQ-0002-B | [要件内容] | 中 | docs/requirements/api.md |
```

## ステップ2: 成果物との照合

### コード内参照の収集

```bash
python3 scripts/trace_doc_code.py --src-dir src --docs-dir docs
```

### 照合マトリクス

```markdown
| Doc-ID | 成果物 | 状態 | 検証方法 | 備考 |
|--------|--------|------|----------|------|
| DOC-REQ-0001-A | src/auth.ts | ✅ | テスト通過 | @shirushi参照あり |
| DOC-REQ-0002-B | src/api.ts | ⚠️ | 部分実装 | 残タスクあり |
| DOC-REQ-0003-C | - | ❌ | 未着手 | |
```

## ステップ3: カバレッジ計算

```
カバレッジ = (✅の数) / (全要件数) × 100%

結果:
- 完了: X件
- 部分的: Y件
- 未着手: Z件
- カバレッジ: XX%
```

### カバレッジレポート形式

```markdown
## 成果物カバレッジレポート

### サマリ
- 総要件数: N
- 完了: X (XX%)
- 部分的: Y (YY%)
- 未着手: Z (ZZ%)

### 詳細

#### ✅ 完了
| Doc-ID | 成果物 | 検証結果 |
|--------|--------|---------|
| DOC-REQ-0001-A | src/auth.ts:15 | テスト通過 |

#### ⚠️ 部分的
| Doc-ID | 成果物 | 残作業 |
|--------|--------|--------|
| DOC-REQ-0002-B | src/api.ts | エラーハンドリング未実装 |

#### ❌ 未着手
| Doc-ID | 要件 | 理由 |
|--------|------|------|
| DOC-REQ-0003-C | [要件内容] | スコープ外 |
```

## ステップ4: ギャップ分析

### 未対応要件の分析

```markdown
## 未対応要件分析

### DOC-REQ-0003-C: [要件内容]
- **理由**: [未対応の理由]
- **影響**: [ビジネス影響]
- **対応案**: [解決策]
- **優先度**: [対応優先度]
```

### 孤立参照の検出

コード内に存在するが、ドキュメントに存在しないDoc-ID参照:

```markdown
## 孤立参照

| ファイル | 参照Doc-ID | 問題 |
|---------|-----------|------|
| src/old.ts:10 | DOC-REQ-9999-X | Doc-IDが存在しない |
```

## ステップ5: 検証結果の記録

### pce-memoryへの記録

```
pce_memory_upsert(
  text="成果物検証結果: カバレッジXX%、未対応X件",
  kind="fact",
  scope="project",
  boundary_class="internal",
  content_hash="sha256:...",
  provenance={at: "ISO8601"}
)
```

### Relationの登録

```
pce_memory_upsert_relation(
  id="impl-req-0001",
  src_id="DOC-REQ-0001-A",
  dst_id="CODE-auth-ts-authenticate",
  type="IMPLEMENTED_BY"
)
```
