---
name: review-report-generator
context: fork
description: |
  アーキテクチャレビューの結果を意思決定に耐える形式のレポートに整形するスキル。
  網羅的な指摘リストではなく、優先順位・対応案・受け入れ条件を明確にした実行可能な形式を生成する。

  使用タイミング:
  - 「レビューレポートを作成して」「報告書を生成して」
  - 「意思決定用にまとめて」「PRレビュー用にまとめて」
  - architecture-review/*/synthesis.yaml が存在する時
  - ステークホルダーへの報告や、PR作成前の確認
---

# Review Report Generator

レビュー結果を意思決定に耐える形式のレポートに整形する。

**核心**: 網羅的な指摘より「意思決定に必要な形」を優先。

## 前提条件

必須:
- `architecture-review/*/synthesis.yaml` - 統合済み分析結果

推奨:
- `architecture-review/*/findings.yaml` - 元の指摘
- `system-map/invariants.yaml` - 不変条件

## 指摘の標準形式

各指摘は以下の形式に固定:

```yaml
finding:
  id: FINDING-001
  title: payment-serviceタイムアウト不整合

  # 1. 影響範囲
  scope:
    type: interaction  # component/interaction/crosscutting
    affected:
      - order-service -> payment-service

  # 2. 何が成立しなくなるか
  failure_mode:
    description: |
      order-serviceがタイムアウトしてもpayment-serviceは処理を続行。
      二重課金が発生する可能性がある。
    impact:
      - ユーザーへの影響: 二重請求
      - ビジネスへの影響: 返金対応コスト、信頼低下
      - システムへの影響: 不整合データの発生

  # 3. 発生条件
  trigger_conditions:
    - 高負荷時（>500 RPS）
    - payment-gateway遅延時（>20s）
    - ネットワーク不安定時

  # 4. 根拠（推測禁止）
  evidence:
    - source: component-dossiers/order-service.yaml
      field: failure_modes[0].trigger
      value: "25s timeout"
    - source: component-dossiers/payment-service.yaml
      field: non_functional.performance.timeout
      value: "30s"
    - note: order-service(25s) < payment-service(30s) で不整合

  # 5. 対応案とトレードオフ
  options:
    - id: A
      action: order-serviceタイムアウトを35sに延長
      pros:
        - 実装が簡単（設定変更のみ）
        - 既存の契約を維持
      cons:
        - ユーザー体験悪化（待ち時間増加）
        - 他の依存先にも影響
      effort: 小（1日）

    - id: B
      action: 冪等キーを導入して二重課金を防止
      pros:
        - 根本解決
        - タイムアウトを短縮可能
      cons:
        - 実装コストが高い
        - payment-serviceの改修も必要
      effort: 中（1週間）

    - id: C
      action: 非同期処理に変更（イベント駆動）
      pros:
        - スケーラビリティ向上
        - タイムアウト問題を回避
      cons:
        - アーキテクチャの大幅変更
        - ADR-003との整合性確認が必要
      effort: 大（2週間）

  # 6. 優先度
  priority:
    category: P0  # P0/P1/P2/P3/P4
    score: 48
    breakdown:
      severity: critical (4)
      likelihood: high (3)
      detectability: hard (3)
      quality_weight: reliability (5)
    rationale: 決済障害はリスク許容度ゼロ

  # 7. 実施単位
  implementation:
    recommended_option: B
    pr_breakdown:
      - pr: "feat: Add idempotency key to payment request"
        scope: order-service
        size: S
      - pr: "feat: Support idempotency key validation"
        scope: payment-service
        size: M
    adr_needed: true
    adr_topic: "サービス間タイムアウトと冪等性戦略"

  # 8. 受け入れ条件
  acceptance_criteria:
    tests:
      - 同一リクエストを3回送信して課金が1回のみ
      - タイムアウト発生時にリトライが正常動作
    metrics:
      - 二重課金率 = 0%
      - payment成功率 >= 99.9%
    logs:
      - idempotency_key_duplicate イベントが記録される
    contract:
      - OpenAPI に X-Idempotency-Key ヘッダーを追加
```

## レポート形式

### エグゼクティブサマリー

```markdown
# アーキテクチャレビュー報告書

**レビュー日**: 2024-01-21
**対象**: order-service, payment-service, inventory-service
**レビュアー**: Claude + 担当者名

## サマリー

| カテゴリ | 件数 | 対応状況 |
|---------|------|---------|
| P0 (Blocker) | 2 | 即時対応必須 |
| P1 (Critical) | 3 | 今スプリント |
| P2 (High) | 5 | 次スプリント |
| P3/P4 | 8 | バックログ |

### 即時対応が必要な項目

1. **FINDING-001**: payment-serviceタイムアウト不整合
   - 二重課金リスク
   - 推奨: 冪等キー導入（Option B）

2. **FINDING-002**: 認可チェックの欠落
   - 他ユーザーデータアクセス可能
   - 推奨: 所有権チェック追加
```

### 詳細セクション

```markdown
## P0: 即時対応

### FINDING-001: payment-serviceタイムアウト不整合

**影響**: order-service -> payment-service 間

**問題**:
order-service(25s) < payment-service(30s) でタイムアウト不整合。
二重課金のリスクあり。

**発生条件**:
- 高負荷時（>500 RPS）
- payment-gateway遅延時

**根拠**:
- `component-dossiers/order-service.yaml` failure_modes[0].trigger: "25s"
- `component-dossiers/payment-service.yaml` timeout: "30s"

**対応案**:

| 案 | 内容 | 工数 | 推奨 |
|----|------|------|------|
| A | タイムアウト延長 | 小 | |
| B | 冪等キー導入 | 中 | ✓ |
| C | 非同期化 | 大 | |

**推奨**: Option B（冪等キー導入）

**PR分割**:
1. `feat: Add idempotency key to payment request` (order-service, S)
2. `feat: Support idempotency key validation` (payment-service, M)

**受け入れ条件**:
- [ ] 同一リクエスト3回で課金1回のテスト
- [ ] 二重課金率 = 0% のメトリクス確認
- [ ] OpenAPI更新

**ADR**: 要作成「サービス間タイムアウトと冪等性戦略」
```

## 出力ファイル

```
architecture-review/{timestamp}/
├── findings.yaml      # Phase 4 の出力
├── synthesis.yaml     # Phase 5 の出力
└── report/            # Phase 6 の出力
    ├── summary.md     # エグゼクティブサマリー
    ├── p0-blockers.md # P0詳細
    ├── p1-critical.md # P1詳細
    ├── p2-high.md     # P2詳細
    ├── backlog.md     # P3/P4
    └── adrs-needed.md # 必要なADR一覧
```

## フォーマット選択

| 用途 | 推奨フォーマット |
|------|-----------------|
| ステークホルダー報告 | summary.md のみ |
| 開発チーム共有 | 全ファイル |
| PR作成 | p0-blockers.md + PR分割情報 |
| バックログ追加 | backlog.md をIssue化 |

## 注意事項

- **推測禁止**: evidence がない指摘は含めない
- **実行可能な形式**: 「問題がある」だけでなく「何をするか」まで
- **PR単位まで分割**: 「改善する」ではなく「このPRを作る」
- **受け入れ条件の明示**: 完了判定ができる形で記載
