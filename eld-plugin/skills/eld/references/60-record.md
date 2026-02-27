# Record（記録）フェーズ

Context Deltaをpce-memory/ADR/Catalogへ反映する。

## 目的

- 意思決定の痕跡を残す
- 知識を構造化して再利用可能にする
- 次のサイクルへの引き継ぎを準備

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

セッション中の知識を即座に保存:

```typescript
// Fact層（高頻度更新）
pce.memory.upsert({
  text: JSON.stringify({
    entity_id: "src/services/CacheService.ts:get",
    type: "function",
    last_verified_commit: "a1b2c3d",
    facts: {
      signature: "get(key: string): Promise<T | null>",
      returnType: "Promise<T | null>"
    }
  }),
  kind: "fact",
  scope: "session",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    actor: "eld-record"
  }
});

// Semantic層（中頻度更新）
pce.memory.upsert({
  text: "CacheServiceはインメモリLRUキャッシュを使用。TTLは環境変数CACHE_TTL_SECで設定。",
  kind: "fact",
  scope: "project",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    actor: "eld-record",
    note: "コード調査から判明"
  }
});

// Relational層（低頻度更新）
pce.memory.upsert({
  text: JSON.stringify({
    source: "src/services/UserService.ts",
    target: "src/services/CacheService.ts",
    relation: "uses",
    note: "ユーザー情報のキャッシュに使用"
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
- シンプルさを優先

## 影響
- 水平スケール時はキャッシュ同期が課題になる
- 将来的にRedis移行の可能性を残す

## 関連
- LAW-cache-ttl: キャッシュTTLは環境変数で設定
- TERM-cache-entry: キャッシュエントリの構造
```

### 3. Law/Term Catalog

新しいLaw/Termを正式登録:

```yaml
# law-catalog.md に追記
| ID | Type | Statement | Severity | Owner |
|----|------|-----------|----------|-------|
| LAW-cache-ttl | Policy | キャッシュTTLは環境変数で設定可能 | S2 | @team |
```

### 4. セッションノート

長期セッションの引き継ぎ用:

```markdown
# セッションノート 2024-01-15

## 完了タスク
- [ ] ユーザーキャッシュ機能実装
- [ ] LAW-cache-ttl定義・接地

## 未完了タスク
- キャッシュ無効化のE2Eテスト
- 本番Telemetry設定

## 学び
- LRUキャッシュはnode-lru-cacheが使いやすい
- TTLのデフォルト値は300秒で十分

## 次回への引き継ぎ
1. E2Eテストを追加
2. Grafanaダッシュボード設定
```

## 構造化プロセス

### Step 1: 差分の収集

作業中に発生した差分を列挙:

```markdown
## 今回の変更で得た知見

### 意思決定
- キャッシュ実装にnode-lru-cacheを選択
  - 理由: シンプル、TTL対応、型サポート良好

### 発見したパターン
- 環境変数でTTLを設定するパターンは汎用的

### 新しいLaw/Term候補
- LAW-cache-ttl: TTLは環境変数で設定
- TERM-cache-entry: { key, value, ttl }

### 再発防止
- test_cache_expiration追加
```

### Step 2: 分類と配置

```
意思決定（重要） → ADR + pce-memory
意思決定（軽微） → pce-memory
パターン → pce-memory + CLAUDE.md
Law/Term候補 → Catalog + pce-memory
再発防止 → コミットメッセージ + pce-memory
```

### Step 3: 保存

各出力先に適切な形式で保存。

## フィードバックループ

記憶の有用性を追跡:

```typescript
// 記憶が役立った場合
pce.memory.feedback({
  claim_id: "clm_xxx",
  signal: "helpful"
});

// 記憶が古かった場合
pce.memory.feedback({
  claim_id: "clm_xxx",
  signal: "outdated"
});

// 記憶が誤解を招いた場合
pce.memory.feedback({
  claim_id: "clm_xxx",
  signal: "harmful"
});
```

## Evidence Pack出力

PRに添付する証拠パック:

```markdown
## Evidence Pack

### 因果関係（Causality）
ユーザー情報取得の高頻度アクセスによるDB負荷を
インメモリキャッシュで軽減する。

### 証拠の梯子（Evidence Ladder）

#### L0: 静的整合
- [x] 型チェック通過
- [x] lint通過

#### L1: ユニットテスト
- [x] test_cache_get_set
- [x] test_cache_expiration
- [x] test_cache_lru_eviction

#### L2: 統合テスト
- [x] test_user_service_with_cache

#### L3: 失敗注入
- [ ] TODO: キャッシュ障害時のフォールバック

#### L4: 本番Telemetry
- [ ] TODO: cache.hit_rate メトリクス設定

### 証拠レベル達成
- 達成レベル: L2
- 理由: 統合テストまで完了、L3/L4は次フェーズ

### 関連Law
| Law ID | 接地状況 | 検証手段 |
|--------|----------|----------|
| LAW-cache-ttl | 接地済 | test_cache_expiration |

### 関連Term
| Term ID | 境界検証 | 観測手段 |
|---------|----------|----------|
| TERM-cache-entry | 検証済 | CacheEntry型定義 |
```

## チェックリスト

### 収集
- [ ] 意思決定の理由を記録したか
- [ ] 発見したパターンを記録したか
- [ ] 新しいLaw/Term候補を列挙したか
- [ ] 再発防止策を記録したか

### 構造化
- [ ] 重要な意思決定はADRに記録したか
- [ ] pce-memoryに適切なスコープで保存したか
- [ ] Law/Term CatalogとLink Mapを更新したか

### Evidence Pack
- [ ] 因果関係を明記したか
- [ ] 証拠の梯子の達成レベルを評価したか
- [ ] 関連Law/Termの接地状況を確認したか

### 引き継ぎ
- [ ] 未完了タスクを明記したか
- [ ] 次回への引き継ぎ事項を記録したか
