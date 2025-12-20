# Grounding（接地）ガイド

## 概要

Lawの接地とは、各Lawに対して以下を最低1つずつ設定すること：
- **検証手段**: Test または Runtime Check
- **観測手段**: Telemetry または Log/Event

## Grounding Mapテンプレート

```md
| Law ID | Type | Test | Runtime Check | Telemetry | Notes |
|--------|------|------|---------------|-----------|-------|
| LAW-inv-available-balance | Invariant | prop_inventory_balance | assert_balance | law.inventory.balance.* | バッチは遅延あり |
| LAW-pre-order-limit | Pre | test_order_limit | validate_order | law.order.limit.* | - |
```

## テスト戦略

### 例示テスト（Example-based）が向いているケース

- 重要な具体例（仕様例・回帰ケース）
- UIや外部I/Fの振る舞い
- 例外処理の分岐が少ない領域

### Property-based Testing（PBT）が向いているケース

- **Invariant**（状態制約）
- 代数的性質が明確な操作（結合律・単位元など）
- 入力パターンが多様で、例示では漏れやすい領域

### PBT運用の要点

1. 反例は固定化して回帰テストへ昇格（PBTに任せきりにしない）
2. seedを記録して再現性を確保
3. arbitraryは「意味のある範囲」に限定し、ドメイン生成器を育てる

## Telemetry命名規約

```
law.<domain>.<law_name>.(applied|violated|latency_ms|coverage)
```

### 最低限（S0/S1）

| メトリクス | 説明 |
|-----------|------|
| `applied_total` | Law適用回数 |
| `violated_total` | Law違反回数 |
| `violation_rate` | 違反率 |
| `p95_latency_ms` | 95パーセンタイル遅延 |

## 収集方針

| トラック | 方針 |
|----------|------|
| Simple | サンプリング中心（コスト・プライバシー優先） |
| Standard | 主要Lawは全量（違反率の把握を優先） |
| Complex | 全量 + 反例スナップショット（監査・再発防止） |

## 過接地（Over-Grounding）を避ける

観測は「検証可能性」を高める一方で、コスト・遅延・プライバシー影響を増やす。

- まずは **重要Lawの最小観測** から開始
- "スコアを上げるために観測する" を禁止する（目的の逆転）
