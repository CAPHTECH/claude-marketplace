# リアルタイム検証ワークフロー

## 概要

作業進行中に継続的に整合性を確認するワークフロー。マイルストーンごとに期待値との乖離を検出する。

## セットアップ

### 1. 期待値の登録

作業開始前に期待される状態を登録:

```
pce_memory_upsert(
  text="期待値: [具体的な期待状態]",
  kind="task",
  scope="session",
  boundary_class="internal",
  content_hash="sha256:...",
  provenance={at: "ISO8601"}
)
```

### 2. 関連要件の収集

```
pce_memory_activate(
  scope=["project"],
  q="要件 仕様 制約",
  top_k=10
)
```

### 3. shirushi Doc-IDの確認

作業対象に関連するDoc-IDを特定:

```bash
shirushi scan --format table | grep "対象キーワード"
```

## 作業中の記録

### マイルストーン記録

各マイルストーンで現状を記録:

```
pce_memory_observe(
  source_type="tool",
  content="マイルストーン1完了: [状態の詳細]",
  tags=["milestone", "validation", "checkpoint"],
  ttl_days=7
)
```

### 状態変化の記録

重要な状態変化があった場合:

```
pce_memory_observe(
  source_type="chat",
  content="状態変化: [変化内容]",
  tags=["state-change"],
  ttl_days=7
)
```

## 検証ポイント

### マイルストーン検証

```
1. pce_memory_activate(scope=["session"], q="期待値 マイルストーン")
2. 現状と期待値を比較
3. 逸脱があれば即時報告
```

### 検証チェックリスト

作業中に以下を定期確認:

- [ ] 要件との整合性
- [ ] 既存決定（ADR）との整合性
- [ ] コーディング規約との整合性
- [ ] テスト要件との整合性
- [ ] shirushi Doc-IDの参照整合性

## 逸脱検出時の対応

### 逸脱報告形式

```markdown
## ⚠️ 逸脱検出

**検出時点**: マイルストーン X
**期待値**: [期待していた状態]
**現状**: [実際の状態]
**逸脱内容**: [差異の説明]
**関連Doc-ID**: [影響を受けるDoc-ID]
**推奨対応**: [修正案]
```

### 逸脱の記録

```
pce_memory_observe(
  source_type="tool",
  content="逸脱検出: [詳細]",
  tags=["deviation", "alert"],
  ttl_days=30
)
```

## 作業完了時

### 最終検証

```
1. 全マイルストーンの記録を確認
2. 逸脱の解消状況を確認
3. 最終状態と期待値を照合
4. 成果物チェックワークフローへ移行
```

### 知見の永続化

重要な知見があれば永続化:

```
pce_memory_upsert(
  text="学習した知見: [内容]",
  kind="fact",
  scope="project",
  boundary_class="internal",
  content_hash="sha256:...",
  provenance={at: "ISO8601", note: "作業中に発見"}
)
```
