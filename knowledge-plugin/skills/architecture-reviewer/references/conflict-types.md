# 矛盾の4類型

矛盾検出フェーズで使用する4つの類型の詳細説明とYAML例。
各類型の定義を理解し、findings から矛盾を特定する際に参照する。

---

## 類型1: improvement_tradeoff（改善案間の矛盾）

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
    COMP-001の抽象化はEDGE-003の直接通信と矛盾する。
    抽象化するとレイテンシが増加し、直接通信すると結合度が上がる。
  affected_qualities:
    improves_if_a: [changeability, testability]
    degrades_if_a: [performance]
    improves_if_b: [performance]
    degrades_if_b: [changeability, testability]
```

---

## 類型2: assumption_violation（コンポーネント間の前提破壊）

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

---

## 類型3: invariant_violation（不変条件との食い違い）

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

---

## 類型4: adr_inconsistency（ADRとの矛盾）

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

---

## 矛盾解決の方針決定

プロジェクト特性の `quality_priorities` を参照し、優先順位の高い品質を勝たせる。

```yaml
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
