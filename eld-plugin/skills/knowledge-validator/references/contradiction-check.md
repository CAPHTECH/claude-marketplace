# 矛盾チェック詳細手順

## 前提条件

- pce-memoryがReady状態であること
- 対象ドキュメントがClaim化済み、または読み取り可能であること

## ステップ1: 対象情報の収集

### 既存Claimから収集

```
pce_memory_activate(
  scope=["project", "principle"],
  allow=["*"],
  q="対象ドメインのキーワード",
  top_k=20
)
```

### 新規ドキュメントをClaim化

```
pce_memory_upsert(
  text="ドキュメントの要点",
  kind="fact",
  scope="project",
  boundary_class="internal",
  content_hash="sha256:...",
  entities=[{id, type, name}],
  provenance={at: "ISO8601", url: "ソースURL"}
)
```

## ステップ2: 関係性の構築

### Entity登録

```
pce_memory_upsert_entity(
  id="doc-A",
  type="Artifact",
  name="設計書A"
)
```

### Relation登録

```
pce_memory_upsert_relation(
  id="rel-1",
  src_id="doc-A",
  dst_id="doc-B",
  type="DEPENDS_ON"
)
```

## ステップ3: 矛盾検出パターン

### パターン1: 定義の不一致

- 同一概念に対する異なる定義
- 例: 「ユーザーID」がドキュメントAではUUID、BではintegerID

### パターン2: 前提条件の競合

- ドキュメントAの前提がBの結論と矛盾
- 例: A「認証必須」vs B「匿名アクセス可能」

### パターン3: 時系列の不整合

- 古い情報と新しい情報の混在
- provenance.atで時系列を確認

### パターン4: shirushi Doc-IDの不整合

- 同一Doc-IDに異なる内容
- `shirushi lint`で検出可能

## ステップ4: 報告形式

```markdown
## 矛盾チェック報告

### 検出された矛盾

#### 矛盾1: [タイトル]
- **ソースA**: [引用] (Claim ID: xxx / Doc-ID: YYY)
- **ソースB**: [引用] (Claim ID: yyy / Doc-ID: ZZZ)
- **矛盾内容**: [説明]
- **推奨対応**: [解決策]

### 整合性確認済み項目
- [項目1]: ✅ 一貫性あり
- [項目2]: ✅ 一貫性あり
```

## ステップ5: フィードバック

矛盾発見時:

```
pce_memory_feedback(
  claim_id="古い/誤ったClaimのID",
  signal="outdated"
)
```
