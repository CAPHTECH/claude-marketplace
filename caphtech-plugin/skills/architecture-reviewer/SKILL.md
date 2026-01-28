---
name: architecture-reviewer
context: fork
description: |
  3種類のアーキテクチャ分析を並行実行し、単体・相互作用・横断的観点から問題を検出するスキル。
  「単体は良いのに全体として成立しない」問題を防ぐため、必ず3視点を同時に適用する。

  使用タイミング:
  - 「アーキテクチャレビューして」「設計をレビューして」
  - 「コンポーネント分析して」「依存関係を分析して」
  - component-dossiers/*.yaml と system-map/invariants.yaml が存在する時
  - PR前の設計確認、リファクタリング前の影響分析
---

# Architecture Reviewer

3種類の分析を並行実行し、アーキテクチャの問題を多角的に検出する。

**重要**: 3種類すべてを実行すること。単体分析だけで終わらせない。

## 前提条件

必須:
- `system-map/invariants.yaml` - 不変条件
- `component-dossiers/*.yaml` - コンポーネントカード

推奨:
- `system-map/dependencies.yaml` - 依存グラフ
- `system-map/boundaries.yaml` - 境界定義

## 3種類の分析

```
┌─────────────────────────────────────────────────────────┐
│  必ず3つとも実行する（単体だけで終わらせない）           │
├─────────────────────────────────────────────────────────┤
│  ① コンポーネント内レビュー ─ ノード（局所の健全性）    │
│  ② インタラクションレビュー ─ エッジ（依存の整合性）    │
│  ③ クロスカッティングレビュー ─ 縦串（横断的品質）      │
└─────────────────────────────────────────────────────────┘
```

## 分析1: コンポーネント内レビュー（ノード）

各コンポーネントの局所的な健全性を検証。

### 評価観点

| 観点 | チェック内容 |
|------|-------------|
| 責務 | 過多（God Object）/ 不足（Anemic）はないか |
| 境界 | 境界を逸脱した処理をしていないか |
| データ所有 | owned_data以外を直接書き込んでいないか |
| 例外設計 | 例外の握りつぶし、過剰なcatch-allはないか |
| テスト可能性 | 依存注入、モック可能性は確保されているか |

### 評価基準

**必ず不変条件（invariants.yaml）に照らして評価する。**

```yaml
# 指摘の形式
component_findings:
  - component_id: order-service
    finding_id: COMP-001
    category: responsibility  # responsibility/boundary/data_ownership/exception/testability
    severity: high
    description: |
      PaymentServiceへの直接依存があり、payment-serviceの内部実装に結合している
    evidence:
      file: src/services/order/OrderService.ts
      line: 45
      code: "await paymentService.chargeInternal(amount)"
    violated_invariant: INV-ARCH-002  # 関連する不変条件
    recommendation: PaymentServiceの公開APIを使用する
```

## 分析2: インタラクションレビュー（エッジ）

依存グラフの「辺」ごとに検証。**全体性の本丸。**

### 評価観点

| 観点 | チェック内容 |
|------|-------------|
| 契約整合 | スキーマ、バージョン、後方互換性 |
| エラー伝播 | リトライ連鎖、サーキットブレーカ、タイムアウト整合 |
| 冪等性 | リトライ時の副作用、重複処理 |
| 順序性 | イベント順序の前提、順序逆転時の挙動 |
| 整合モデル | 結果整合/強整合の前提が一致しているか |
| セキュリティ | 認証・認可・秘密情報の境界超え |

### 評価方法

依存グラフの各辺（A → B）について:

```yaml
# 辺ごとの分析
interaction_findings:
  - edge_id: order-service -> payment-service
    finding_id: EDGE-001
    category: error_propagation  # contract/error_propagation/idempotency/ordering/consistency/security
    severity: critical
    description: |
      payment-serviceのタイムアウト(30s)がorder-serviceのタイムアウト(25s)より長い。
      order-serviceがタイムアウトしてもpayment-serviceは処理を続行し、
      二重課金のリスクがある。
    evidence:
      source:
        file: component-dossiers/order-service.yaml
        field: failure_modes[0].trigger
        value: "25s timeout"
      target:
        file: component-dossiers/payment-service.yaml
        field: non_functional.performance.timeout
        value: "30s"
    violated_invariant: INV-IDEM-001
    recommendation: |
      1. order-serviceのタイムアウトをpayment-serviceより長くする
      2. または冪等キーを導入して二重課金を防止
```

### エラー伝播の連鎖分析

```
A → B → C の場合：
- AのタイムアウトはBより長いか？
- BのタイムアウトはCより長いか？
- Bが失敗した時、Aはどうリトライするか？
- リトライの連鎖で指数的爆発は起きないか？
```

## 分析3: クロスカッティングレビュー（縦串）

システム横断的な品質を検証。

### 評価観点

| 縦串 | チェック内容 |
|------|-------------|
| セキュリティ | 脅威モデルとの整合、境界の一貫性 |
| 信頼性 | SLO/SLI定義、障害分離、リカバリ戦略 |
| 観測性 | ログ・メトリクス・トレースが責務境界と一致 |
| 変更容易性 | モジュール結合度、影響範囲、ADR整合 |

### 評価方法

```yaml
crosscutting_findings:
  - aspect: security  # security/reliability/observability/changeability
    finding_id: CROSS-001
    severity: high
    description: |
      認証境界（API Gateway）を超えた後、内部サービス間で認可チェックが
      行われていない。order-serviceはuser_idの所有権を検証せずに
      他ユーザーの注文を操作可能。
    affected_components:
      - order-service
      - inventory-service
    evidence:
      - file: component-dossiers/order-service.yaml
        field: non_functional.security
        note: "JWT認証必須"とあるが認可ロジックが未記載
    violated_invariant: INV-SEC-001
    recommendation: |
      各サービスで所有権チェックを実装、または認可サービスを導入
```

詳細は [references/crosscutting-checklist.md](references/crosscutting-checklist.md) を参照。

## 出力形式

`architecture-review/{timestamp}/findings.yaml` に出力:

```yaml
id: architecture-review
reviewed_at: "2024-01-21T10:00:00+09:00"
reviewed_scope:
  components: 15
  interactions: 23
  invariants_checked: 24

summary:
  total_findings: 12
  by_category:
    component: 4
    interaction: 5
    crosscutting: 3
  by_severity:
    critical: 2
    high: 4
    medium: 5
    low: 1

component_findings:
  - ...

interaction_findings:
  - ...

crosscutting_findings:
  - ...
```

## 注意事項

- **3種類すべてを実行**: 単体分析だけで終わらせると全体性を見落とす
- **不変条件に拘束**: 評価基準は invariants.yaml から導出
- **推測禁止**: 根拠がない指摘はしない。evidenceを必ず記載
- **severity は客観的に**: 影響範囲と発生確率で判定

## 次のステップ

分析結果は `synthesis-analyzer` スキルで矛盾検出・優先順位付けを行う。
