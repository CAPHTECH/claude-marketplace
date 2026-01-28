---
name: synthesis-analyzer
context: fork
description: |
  アーキテクチャレビューの結果を再統合し、矛盾の検出と優先順位付けを行うスキル。
  改善案の大量生成よりも「矛盾の検出」に価値を置き、プロジェクト特性に応じた優先順位を決定する。

  使用タイミング:
  - 「矛盾を検出して」「優先順位を付けて」
  - 「レビュー結果を統合して」「トレードオフを分析して」
  - architecture-review/*/findings.yaml が存在する時
  - 複数の改善案の中から優先順位を決めたい時
---

# Synthesis Analyzer

アーキテクチャレビューの結果を再統合し、矛盾検出と優先順位付けを行う。

**核心**: 改善案の大量生成より「矛盾の検出」に価値がある。

## 前提条件

必須:
- `architecture-review/*/findings.yaml` - レビュー結果
- `system-map/invariants.yaml` - 不変条件

推奨:
- プロジェクト特性の定義（品質優先順位）
- 既存ADR（アーキテクチャ決定記録）

## ワークフロー

```
1. 指摘の収集 → 2. 矛盾検出 → 3. プロジェクト特性適用 → 4. 優先順位付け → 5. 出力
```

## Phase 1: 矛盾の4類型

### 類型1: 改善案間の矛盾

改善案Aは品質Xを改善するが、品質Yを損なう。

```yaml
conflict_type: improvement_tradeoff
findings:
  - finding_a:
      id: COMP-001
      recommendation: PaymentServiceへの依存を抽象化する
      improves: [changeability, testability]
  - finding_b:
      id: EDGE-003
      recommendation: PaymentServiceとの直接通信でレイテンシを削減
      improves: [performance]
conflict:
  description: |
    COMP-001の抽象化はCOMP-003の直接通信と矛盾する。
    抽象化するとレイテンシが増加し、直接通信すると結合度が上がる。
  affected_qualities:
    improves_if_a: [changeability, testability]
    degrades_if_a: [performance]
    improves_if_b: [performance]
    degrades_if_b: [changeability, testability]
```

### 類型2: コンポーネント間の前提破壊

コンポーネントiの改善は、依存先jの前提を破壊する。

```yaml
conflict_type: assumption_violation
findings:
  - finding_i:
      id: COMP-005
      component: order-service
      recommendation: リトライ回数を5回に増やす
  - assumption_j:
      component: payment-service
      assumption: "呼び出し元は最大3回リトライする"
      source: component-dossiers/payment-service.yaml#assumptions
conflict:
  description: |
    order-serviceのリトライ増加により、payment-serviceの想定を超える。
    payment-serviceは3回を前提にタイムアウトを設計しているため、
    5回リトライすると処理時間が想定の1.7倍になる。
  impact:
    - payment-serviceのSLO違反リスク
    - 二重課金リスクの増加
```

### 類型3: 不変条件との食い違い

不変条件と実装方針が食い違っている。

```yaml
conflict_type: invariant_violation
invariant:
  id: INV-SEC-001
  statement: 認可チェックは必ずAPI Gateway層で完結する
finding:
  id: CROSS-002
  recommendation: 各サービスで所有権チェックを追加する
conflict:
  description: |
    CROSS-002の推奨は、INV-SEC-001と直接矛盾する。
    不変条件は「境界で完結」と定めているが、
    推奨は「各サービスで追加」と言っている。
  resolution_options:
    - option: 不変条件を維持
      action: API Gatewayで所有権チェックを実装
      tradeoff: Gateway の複雑化
    - option: 不変条件を更新
      action: INV-SEC-001を「境界 + 深層防御」に改訂
      tradeoff: ADR更新が必要
```

### 類型4: ADRとの矛盾

既存ADRと矛盾している、またはADRが欠落している。

```yaml
conflict_type: adr_inconsistency
adr:
  id: ADR-003
  title: イベント駆動アーキテクチャの採用
  decision: サービス間通信はイベントで行う
finding:
  id: EDGE-007
  recommendation: inventory-serviceへの同期API呼び出しを追加
conflict:
  description: |
    EDGE-007の同期API追加は、ADR-003のイベント駆動方針と矛盾する。
  resolution_options:
    - option: ADRを維持
      action: イベント経由で在庫確認を行う
      tradeoff: レイテンシ増加（非同期化）
    - option: ADRを例外として更新
      action: ADR-003に「在庫確認は同期許可」を追記
      tradeoff: 一貫性の低下
    - option: ADRを廃止
      action: ADR-003を廃止し、ハイブリッド方式に移行
      tradeoff: 大規模な方針転換
```

## Phase 2: プロジェクト特性の適用

**同じ問題でも、プロジェクト特性で優先順位が変わる。**

### 特性の定義

```yaml
project_characteristics:
  name: "ECサイト リニューアルプロジェクト"

  quality_priorities:  # 優先順位（1が最優先）
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

### 特性に基づく判定

```yaml
# 矛盾の解決方針
conflict_resolution:
  - conflict_id: CONF-001
    type: improvement_tradeoff
    affected_qualities: [changeability, performance]

    project_decision:
      winner: performance  # 優先順位3 > 4
      rationale: |
        プロジェクト特性でperformance(3) > changeability(4)。
        レイテンシ削減を優先し、結合度の問題はリリース後に対処。

    action:
      immediate: EDGE-003の直接通信を採用
      deferred: COMP-001の抽象化は技術的負債として記録
```

## Phase 3: 優先順位付け

### スコアリング

```
Priority = Severity × Likelihood × (1/Detectability) × Quality_Weight
```

| 要素 | 説明 | スケール |
|------|------|---------|
| Severity | 発生時の影響度 | critical=4, high=3, medium=2, low=1 |
| Likelihood | 発生確率 | high=3, medium=2, low=1 |
| Detectability | 検出容易性 | easy=1, medium=2, hard=3 |
| Quality_Weight | 品質優先順位から | 1位=5, 2位=4, 3位=3, 4位=2, 5位=1 |

### 優先順位カテゴリ

| カテゴリ | スコア | 対応 |
|---------|--------|------|
| P0 - Blocker | 36+ | 即時対応（リリース不可） |
| P1 - Critical | 24-35 | 今スプリント内 |
| P2 - High | 12-23 | 次スプリント |
| P3 - Medium | 6-11 | バックログ |
| P4 - Low | 1-5 | 技術的負債 |

## 出力形式

`architecture-review/*/synthesis.yaml` に出力:

```yaml
id: synthesis
analyzed_at: "2024-01-21T11:00:00+09:00"
source_review: architecture-review/2024-01-21/findings.yaml

project_characteristics:
  quality_priorities: [reliability, security, performance, changeability]
  risk_tolerance: conservative

conflicts:
  total: 8
  by_type:
    improvement_tradeoff: 3
    assumption_violation: 2
    invariant_violation: 2
    adr_inconsistency: 1

  items:
    - id: CONF-001
      type: improvement_tradeoff
      findings: [COMP-001, EDGE-003]
      description: 抽象化 vs 直接通信のトレードオフ
      resolution:
        decision: performance優先（EDGE-003採用）
        rationale: プロジェクト特性でperformance > changeability
        deferred_action: COMP-001は技術的負債として記録

prioritized_actions:
  - priority: P0
    items:
      - finding_id: EDGE-001
        score: 48
        action: payment-serviceタイムアウト整合

  - priority: P1
    items:
      - finding_id: CROSS-001
        score: 30
        action: 認可チェックの追加

  - priority: P2
    items: [...]

deferred_items:
  - finding_id: COMP-001
    reason: 優先度が低い（changeability）
    revisit: リリース後のスプリント1

missing_adrs:
  - topic: サービス間タイムアウト戦略
    related_findings: [EDGE-001, EDGE-003]
    recommendation: ADR作成を推奨
```

## 注意事項

- **矛盾検出が本丸**: 改善案の列挙より、矛盾の発見と解決に注力
- **プロジェクト特性を必ず適用**: 同じ問題でも優先順位が変わる
- **ADR欠落の検出**: 重要な決定にADRがなければ指摘
- **推測禁止**: 矛盾の根拠は必ずfindingsから引用

## 次のステップ

統合結果は `review-report-generator` スキルで意思決定用レポートに整形する。
