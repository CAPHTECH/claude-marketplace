# 優先順位スコアリング

指摘と矛盾に優先順位を付けるためのスコアリング詳細。

---

## スコア計算式

```
Priority = Severity x Likelihood x (1 / Detectability) x Quality_Weight
```

## 各要素の定義

| 要素 | 説明 | スケール |
|------|------|---------|
| Severity | 発生時の影響度 | critical=4, high=3, medium=2, low=1 |
| Likelihood | 発生確率 | high=3, medium=2, low=1 |
| Detectability | 検出容易性（逆数を取る） | easy=1, medium=2, hard=3 |
| Quality_Weight | プロジェクト品質優先順位から | 1位=5, 2位=4, 3位=3, 4位=2, 5位=1 |

## 優先順位カテゴリ

| カテゴリ | スコア | 対応 |
|---------|--------|------|
| P0 - Blocker | 36+ | 即時対応（リリース不可） |
| P1 - Critical | 24-35 | 今スプリント内 |
| P2 - High | 12-23 | 次スプリント |
| P3 - Medium | 6-11 | バックログ |
| P4 - Low | 1-5 | 技術的負債 |

## スコアリング例

```yaml
scoring_example:
  finding_id: EDGE-001
  severity: critical  # 4
  likelihood: high    # 3
  detectability: hard # 3 -> 1/3 ではなく 3 を乗算
  quality: reliability  # 1位 -> 5

  # 4 x 3 x 3 x 5 = 180 ... ではなく
  # Detectability は逆数: easy=1(÷1), medium=2(÷2), hard=3(÷3) ではなく
  # 「検出しにくいほど危険」なので (1/Detectability) を反転して使う:
  #   easy -> 1/1 = 1, medium -> 1/(1/2) = 2, hard -> 1/(1/3) = 3
  # つまり: 4 x 3 x 3 x 5 = 180 → P0

  # 簡略計算: Severity x Likelihood x Detectability_inv x Quality_Weight
  score: 180
  priority: P0
```

**注意**: Detectability は「検出が難しいほどスコアが高くなる」方向。easy=1, medium=2, hard=3 をそのまま乗算する。

## プロジェクト特性の定義例

```yaml
project_characteristics:
  name: "ECサイト リニューアルプロジェクト"
  quality_priorities:  # 1が最優先
    1: reliability      # 信頼性（決済を落とせない）
    2: security         # セキュリティ（PCI-DSS準拠）
    3: performance      # 性能（UX）
    4: changeability    # 変更容易性
    5: observability    # 観測性
  constraints:
    - リリース日は固定（3ヶ月後）
    - チームは5名
    - レガシーDBとの互換性必須
  risk_tolerance:
    - 決済障害: 極めて低い（ゼロ許容）
    - 表示遅延: 中程度（500ms以下）
    - 技術的負債: 高い（リリース後に対応可）
```

## 出力形式: prioritized_actions

```yaml
prioritized_actions:
  - priority: P0
    items:
      - finding_id: EDGE-001
        score: 180
        action: payment-serviceタイムアウト整合
  - priority: P1
    items:
      - finding_id: CROSS-001
        score: 30
        action: 認可チェックの追加
  - priority: P2
    items: []
```

## deferred_items と missing_adrs

```yaml
deferred_items:
  - finding_id: COMP-001
    reason: 優先度が低い（changeability）
    revisit: リリース後のスプリント1

missing_adrs:
  - topic: サービス間タイムアウト戦略
    related_findings: [EDGE-001, EDGE-003]
    recommendation: ADR作成を推奨
```
