# 意思決定追跡ワークフロー

## 概要

ADR（Architecture Decision Record）や重要な意思決定を追跡し、決定間の整合性を検証するワークフロー。

## 決定の登録

### ADR形式での登録

```
pce_memory_upsert(
  text="ADR-XXXX: [タイトル]\n状態: 承認\n決定: [決定内容]\n理由: [理由]",
  kind="policy_hint",
  scope="project",
  boundary_class="internal",
  content_hash="sha256:...",
  provenance={
    at: "2025-01-01T00:00:00Z",
    actor: "決定者",
    note: "決定の背景"
  },
  entities=[
    {id: "adr-xxxx", type: "Event", name: "ADR-XXXX"}
  ]
)
```

### shirushi Doc-IDとの連携

ADRにはshirushiでDoc-IDを付与:

```markdown
<!-- Doc-ID: ADR-ADR-0019-X -->
# ADR-0019: 状態管理ライブラリの選定
```

## 決定間の関係追跡

### 依存関係の登録

```
pce_memory_upsert_relation(
  id: "adr-dep-1",
  src_id: "adr-0020",
  dst_id: "adr-0015",
  type: "SUPERSEDES"
)
```

### 関係タイプ

| タイプ | 意味 |
|--------|------|
| SUPERSEDES | 置き換え（旧決定を無効化）|
| DEPENDS_ON | 依存（前提として必要）|
| CONFLICTS_WITH | 競合（同時適用不可）|
| EXTENDS | 拡張（追加的決定）|
| IMPLEMENTS | 実装（上位決定の具体化）|

## 競合検出

### 検出手順

1. 新決定のドメインを特定
2. 同一ドメインの既存決定を検索
3. 論理的競合をチェック

```
pce_memory_activate(
  scope=["project"],
  q="[ドメインキーワード] 決定 policy ADR",
  top_k=10
)
```

### 競合パターン

- **直接競合**: 同一事項に対する異なる決定
- **暗黙的競合**: 前提条件の矛盾
- **スコープ競合**: 適用範囲の重複
- **時系列競合**: 古い決定と新しい決定の矛盾

## 決定の検証チェックリスト

- [ ] 既存決定との整合性を確認したか？
- [ ] 影響を受ける他の決定を特定したか？
- [ ] 必要に応じてSUPERSEDES関係を登録したか？
- [ ] shirushi Doc-IDを付与したか？
- [ ] pce-memoryに登録したか？

## 報告形式

```markdown
## 意思決定整合性レポート

### 新規決定
- **Doc-ID**: ADR-ADR-0020-Y
- **タイトル**: [決定タイトル]
- **状態**: 承認

### 関連する既存決定
| Doc-ID | タイトル | 関係 |
|--------|---------|------|
| ADR-ADR-0015-X | [タイトル] | DEPENDS_ON |
| ADR-ADR-0010-Z | [タイトル] | SUPERSEDES |

### 競合チェック結果
- ✅ 直接競合なし
- ⚠️ ADR-0010との暗黙的競合の可能性（要確認）
```
