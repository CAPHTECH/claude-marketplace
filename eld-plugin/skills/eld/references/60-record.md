# Record（記録）フェーズ

Context Deltaをpce-memory/ADR/Catalogへ反映する。Context Engineering統合。

> v2.3: Context Engineering統合。3層メモリ+TTL、動的アクション（KEEP/SUMMARIZE/DISCARD）、
> claim schema、source auto-tagging、epistemic auto-downgrade を導入。
> compact/maintenance サブモードを統合。

## 目的

- 意思決定の痕跡を残す
- 知識を構造化して再利用可能にする
- 次のサイクルへの引き継ぎを準備
- Context Rotを防ぐ（動的メモリポリシー）

## サブモード（v2.3）

| モード | 説明 | 起動方法 |
|--------|------|----------|
| **record**（デフォルト） | Context Delta収集・保存 | `/eld-record` |
| **compact** | 履歴圧縮 | `/eld-record compact` |
| **maintenance** | 知識メンテナンス | `/eld-record maintenance` |

## Claim Schema（v2.3）

全ての知識はclaim（主張）として構造化される:

```json
{
  "claim_id": "clm_xxx",
  "content": "CacheServiceはインメモリLRUキャッシュを使用",
  "source": ["file:src/services/CacheService.ts:15", "test:test_cache_lru"],
  "epistemic_status": "verified",
  "last_verified_at": "2026-02-28T10:00:00Z",
  "ttl": "7d",
  "importance": "S2"
}
```

**validation rules**:
- `verified`は`source`が1つ以上必須（なければ自動降格→`inferred`）
- `S0/S1`は`DISCARD`不可
- `ttl`超過で自動降格（verified→inferred→unknown）

### Source Auto-Tagging

claimの出典を自動的にタグ付け:
- コード参照 → `file:<path>:<line>`
- テスト結果 → `test:<test_name>`
- コミット → `commit:<hash>`
- レビュー → `review:<reviewer>`

### Epistemic Auto-Downgrade

```
verified (source変更検知) → inferred (TTL超過) → unknown
```

- 出典ファイルのgit変更を検知 → `verified`を`inferred`に降格
- `last_verified_at` + `ttl` < 現在時刻 → `inferred`を`unknown`に降格
- 手動で再検証するまで昇格しない

## 動的メモリポリシー（Context Engineering）

### 3層メモリモデル

| Layer | 内容 | TTL | scope |
|-------|------|-----|-------|
| **Working** | 現セッションの作業コンテキスト | session終了まで | `session` |
| **Short-term** | 最近のclaim、まだ検証途中 | 24h | `session` |
| **Long-term** | 検証済みclaim、ADR、Law/Term | 無期限（鮮度チェック付き） | `project` |

### 動的アクション

重要度と鮮度に基づきclaimを自動分類:

| アクション | 条件 | 処理 |
|-----------|------|------|
| **KEEP** | 高重要度(S0/S1) + 高鮮度 | Long-term保持 |
| **SUMMARIZE** | 高重要度(S0/S1) + 低鮮度 | 要約してLong-term |
| **DISCARD** | 低重要度(S2/S3) + 低鮮度 | 破棄 |

**制約**: S0/S1はDISCARD不可。最低でもSUMMARIZE。

**鮮度判定**: `last_verified_at`からの経過時間

```
鮮度 = now - last_verified_at
高鮮度: 鮮度 < ttl
低鮮度: 鮮度 ≥ ttl
```

## Context Delta（文脈差分）

作業中に発生した知見・決定の差分:

### 収集対象

| カテゴリ | 内容 | 例 |
|----------|------|-----|
| **意思決定** | なぜその選択をしたか | 「Redisではなくメモリキャッシュを選択」 |
| **学び/パターン** | 今後に活かせること | 「この形式のエラーはX型の問題」 |
| **再発防止** | 追加したテスト/不変条件 | 「境界値テスト追加」 |
| **発見したLaw/Term** | 新しく特定した法則/語彙 | 「LAW-cache-ttl候補」 |
| **技術的負債** | 将来の改善点 | 「リファクタリング候補」 |

### 収集タイミング

- 設計判断を下した時
- 問題を解決した時
- 新しいパターンを発見した時
- テスト/不変条件を追加した時
- 作業を中断/完了する時

## 出力先

### 1. pce-memory（即時）

セッション中の知識をclaim schemaで保存:

```typescript
// claim形式での保存
pce.memory.upsert({
  text: JSON.stringify({
    claim_id: "clm_cache_strategy",
    content: "CacheServiceはインメモリLRUキャッシュを使用",
    source: ["file:src/services/CacheService.ts:15"],
    epistemic_status: "verified",
    last_verified_at: new Date().toISOString(),
    ttl: "7d",
    importance: "S2"
  }),
  kind: "fact",
  scope: "project",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    actor: "eld-record"
  }
});
```

### 2. ADR（Architecture Decision Records）

重要なアーキテクチャ決定を記録:

```markdown
# ADR-007: キャッシュ戦略

## ステータス
承認済み

## 背景
ユーザー情報の取得が頻繁で、DBへの負荷が高い。

## 決定
インメモリLRUキャッシュを採用する。

## 理由
- Redisはインフラ追加が必要
- 現時点のトラフィックではメモリキャッシュで十分

## 関連
- LAW-cache-ttl: キャッシュTTLは環境変数で設定
- TERM-cache-entry: キャッシュエントリの構造
```

### 3. Law/Term Catalog

新しいLaw/Termを正式登録。

## Compact サブモード（v2.3: 統合）

履歴圧縮を実行:

```
/eld-record compact
```

**処理内容**:
1. 全claimの鮮度チェック
2. 動的アクション適用（KEEP/SUMMARIZE/DISCARD）
3. 圧縮レポート出力

## Maintenance サブモード（v2.3: 統合）

知識メンテナンスを実行:

```
/eld-record maintenance
```

**処理内容**:
1. 孤立claimの検出
2. 矛盾する claim の検出・解決
3. 品質スコア算出
4. フィードバックの反映

## フィードバックループ

記憶の有用性を追跡:

```typescript
// 記憶が役立った場合
pce.memory.feedback({ claim_id: "clm_xxx", signal: "helpful" });

// 記憶が古かった場合
pce.memory.feedback({ claim_id: "clm_xxx", signal: "outdated" });

// 記憶が誤解を招いた場合
pce.memory.feedback({ claim_id: "clm_xxx", signal: "harmful" });
```

## Evidence Pack出力

PRに添付する証拠パック（→ `pr-template.md` 参照）。

## チェックリスト

### 収集
- [ ] 意思決定の理由を記録したか
- [ ] 発見したパターンを記録したか
- [ ] 新しいLaw/Term候補を列挙したか
- [ ] source auto-taggingが正しく付与されているか

### 構造化
- [ ] 重要な意思決定はADRに記録したか
- [ ] claimがclaim schemaに準拠しているか
- [ ] epistemic_statusが正しく設定されているか
- [ ] Law/Term CatalogとLink Mapを更新したか

### Context Engineering（v2.3）
- [ ] 動的アクション（KEEP/SUMMARIZE/DISCARD）を適用したか
- [ ] S0/S1のclaimがDISCARDされていないか
- [ ] TTL超過claimの自動降格が実行されているか

### 引き継ぎ
- [ ] 未完了タスクを明記したか
- [ ] 次回への引き継ぎ事項を記録したか
