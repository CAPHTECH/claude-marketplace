---
name: eld-ground-law-monitor
context: fork
description: |
  実行時Law違反監視スキル。
  本番環境でのLaw違反を検知し、分析結果を記録して継続的改善を促す。
  使用タイミング: (1) 本番ログからLaw違反を分析する時、(2) 「Law違反を確認して」、
  (3) 運用中のLaw健全性をチェックする時、(4) 違反パターンから新Lawを発見する時
---

# Law Monitor

本番環境でのLaw違反を監視し、分析結果を記録する。

## 監視フロー

```
Telemetry/Log → 違反検知 → パターン分析 → 記録 → 改善提案
       ↓              ↓             ↓          ↓          ↓
  law.*.violated   分類・集計    根本原因分析   lessons.md  Law強化
```

## 監視対象

### Telemetryメトリクス

```
law.<domain>.<law_name>.violated_total   # 違反総数
law.<domain>.<law_name>.violation_rate   # 違反率
law.<domain>.<law_name>.p95_latency_ms   # 95パーセンタイル遅延
```

### Log/Event

```json
{
  "event": "law.violation",
  "law_id": "LAW-inv-balance",
  "severity": "S1",
  "context": {
    "expected": 100,
    "actual": -5,
    "diff": 105
  },
  "timestamp": "2024-12-21T10:30:00Z"
}
```

## 分析プロセス

### Step 1: 違反イベント収集

```bash
# ログから違反イベントを抽出
grep "law.violation" /var/log/app/*.log | jq -s 'group_by(.law_id)'
```

### Step 2: パターン分類

| パターン | 説明 | 対応 |
|---------|------|------|
| 単発 | 1回限りの違反 | 個別調査 |
| 周期的 | 定期的に発生 | 根本原因分析 |
| バースト | 短時間に集中 | 緊急対応 |
| 漸増 | 徐々に増加 | Law見直し |

### Step 3: 根本原因分析

```yaml
violation_analysis:
  law_id: LAW-inv-balance
  pattern: 漸増
  period: 2024-12-01 ~ 2024-12-21
  count: 47

  root_cause_candidates:
    - hypothesis: "並行処理での競合条件"
      confidence: high
      evidence: "複数リクエスト同時処理時に集中"
    - hypothesis: "バリデーション漏れ"
      confidence: medium
      evidence: "特定APIエンドポイントからのみ発生"

  affected_contexts:
    - endpoint: /api/orders
    - user_segment: enterprise
    - time_window: 10:00-12:00 JST
```

### Step 4: 改善提案

```yaml
recommendations:
  immediate:
    - action: "STMによる在庫更新のトランザクション化"
      priority: high
      effort: medium

  law_enhancement:
    - action: "LAW-inv-balance に並行制御要件を追加"
      new_statement: "在庫更新は原子的に行い、並行リクエスト間で整合性を保つ"

  new_law_candidate:
    - id: LAW-inv-concurrent-update
      type: Invariant
      statement: "同一商品への並行更新は順序付けて実行する"
```

## 出力形式

### Law Health Report

```markdown
# Law Health Report

## Period: 2024-12-15 ~ 2024-12-21

## Summary
| Severity | Total Laws | Violations | Health |
|----------|------------|------------|--------|
| S0 | 3 | 0 | 🟢 Healthy |
| S1 | 5 | 2 | 🟡 Degraded |
| S2 | 10 | 5 | 🟢 Healthy |

## S1 Violations (Attention Required)

### LAW-inv-balance
- **Violations**: 47
- **Trend**: 📈 Increasing
- **Pattern**: Burst (10:00-12:00 JST)
- **Root Cause**: Concurrency issue (high confidence)

**Recommended Actions**:
1. [Immediate] 在庫更新にトランザクション追加
2. [Law Enhancement] 並行制御要件を明文化
3. [New Law] LAW-inv-concurrent-update の追加検討

### LAW-pre-order-limit
- **Violations**: 12
- **Trend**: 📉 Decreasing
- **Pattern**: Single events
- **Root Cause**: Edge case in validation

**Recommended Actions**:
1. [Bug Fix] バリデーションのエッジケース修正
```

## 使用例

```
User: 今週のLaw違反を確認して

Claude:
## Law Health Check実行中...

### Telemetry/Log収集
- law.*.violated_total を集計中...
- 対象期間: 2024-12-15 ~ 2024-12-21

## Law Health Report

### Status: 🟡 Attention Required

| Law ID | Severity | Violations | Trend |
|--------|----------|------------|-------|
| LAW-inv-balance | S1 | 47 | 📈 +35% |
| LAW-pre-order | S1 | 12 | 📉 -20% |

### 詳細分析: LAW-inv-balance

**パターン**: バースト型（10:00-12:00に集中）
**根本原因候補**: 並行処理での競合条件（confidence: high）

**推奨アクション**:
1. 在庫更新処理にSTMを導入
2. Lawに並行制御要件を追加

→ 分析結果をtasks/lessons.mdに記録しました
→ 新Law候補を生成しますか？
```

---

## 品質優先原則（Superpowers統合）

### 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し、即時検証する
4. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
5. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 「速さより質」の実践

- 要件の曖昧さによる手戻りを根本から排除
- テストなし実装を許さない
- 観測不能な変更を防ぐ

### 完了の定義

- [ ] Evidence Ladder目標レベル達成
- [ ] Issue Contractの物差し満足
- [ ] Law/Termが接地している（Grounding Map確認）
- [ ] Link Mapに孤立がない
- [ ] ロールバック可能な状態

### 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小：

- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）
