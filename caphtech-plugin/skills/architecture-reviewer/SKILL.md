---
name: architecture-reviewer
context: fork
description: 3種類のアーキテクチャ分析（ノード/エッジ/縦串）を並行実行し、矛盾検出・優先順位付けまで一貫して行う。「アーキテクチャレビューして」「設計をチェックして」「矛盾を検出して」「優先順位を付けて」「トレードオフを分析して」と言われた時、またはcomponent-dossiers/*.yamlが存在する時に使用。
---

# Architecture Reviewer

3種類の分析を並行実行し、矛盾検出と優先順位付けまで一貫して行う。

**核心**: 単体分析で終わらせない。3視点の分析 → 矛盾検出 → 優先順位付けを必ず通す。

## ワークフロー

```
1. 3種類の分析（並行）→ 2. 矛盾検出（4類型）→ 3. 優先順位付け → 4. 出力
```

## 前提条件

### Full Mode（デフォルト）

必須:
- `system-map/invariants.yaml` - 不変条件
- `component-dossiers/*.yaml` - コンポーネントカード

推奨:
- `system-map/dependencies.yaml` - 依存グラフ
- `system-map/boundaries.yaml` - 境界定義
- 既存ADR（アーキテクチャ決定記録）
- プロジェクト特性の定義（品質優先順位）

### Lightweight Mode

system-map が存在しない場合、`scripts/collect_artifacts.py` でプロジェクトをスキャンし、D2/D3/D5 の検証のみを実行する。

```bash
python3 scripts/collect_artifacts.py <project_root> -o /tmp/dcc-manifest.json
```

## Phase 1: 3種類の分析

```
┌─────────────────────────────────────────────────────────┐
│  必ず3つとも実行する（単体だけで終わらせない）           │
├─────────────────────────────────────────────────────────┤
│  (1) コンポーネント内レビュー ─ ノード（局所の健全性）   │
│  (2) インタラクションレビュー ─ エッジ（依存の整合性）   │
│  (3) クロスカッティングレビュー ─ 縦串（横断的品質）     │
└─────────────────────────────────────────────────────────┘
```

### 分析1: コンポーネント内レビュー（ノード）

各コンポーネントの局所的な健全性を検証する。不変条件（invariants.yaml）に照らして評価すること。

| 観点 | チェック内容 |
|------|-------------|
| 責務 | 過多（God Object）/ 不足（Anemic）はないか |
| 境界 | 境界を逸脱した処理をしていないか |
| データ所有 | owned_data以外を直接書き込んでいないか |
| 例外設計 | 例外の握りつぶし、過剰なcatch-allはないか |
| テスト可能性 | 依存注入、モック可能性は確保されているか |
| テスト網羅性(D2) | 各不変条件・状態遷移・境界条件にテストがあるか |
| 障害モード網羅性(D5) | 各障害モードに処理コードとリカバリ戦略があるか |

指摘は `component_findings` として出力する。category は responsibility/boundary/data_ownership/exception/testability のいずれか。

### 分析2: インタラクションレビュー（エッジ）

依存グラフの「辺」ごとに検証する。**全体性の本丸。**

| 観点 | チェック内容 |
|------|-------------|
| 契約整合 | スキーマ、バージョン、後方互換性 |
| エラー伝播 | リトライ連鎖、サーキットブレーカ、タイムアウト整合 |
| 冪等性 | リトライ時の副作用、重複処理 |
| 順序性 | イベント順序の前提、順序逆転時の挙動 |
| 整合モデル | 結果整合/強整合の前提が一致しているか |
| セキュリティ | 認証・認可・秘密情報の境界超え |
| スキーマ実装一致(D3) | データスキーマとコードの型・フィールド・制約が一致しているか |

エラー伝播の連鎖分析: A -> B -> C の場合、タイムアウトの大小関係、リトライ連鎖の指数的爆発を確認する。

指摘は `interaction_findings` として出力する。category は contract/error_propagation/idempotency/ordering/consistency/security のいずれか。

### 分析3: クロスカッティングレビュー（縦串）

システム横断的な品質を検証する。

| 縦串 | チェック内容 |
|------|-------------|
| セキュリティ | 脅威モデルとの整合、境界の一貫性 |
| 信頼性 | SLO/SLI定義、障害分離、リカバリ戦略 |
| 観測性 | ログ・メトリクス・トレースが責務境界と一致 |
| 変更容易性 | モジュール結合度、影響範囲、ADR整合 |

指摘は `crosscutting_findings` として出力する。aspect は security/reliability/observability/changeability のいずれか。

各指摘のYAML例は [references/finding-examples.yaml](references/finding-examples.yaml) を参照。指摘を書くときのテンプレートとして使用する。

## Phase 2: 矛盾検出（4類型）

分析結果の指摘間、および指摘と不変条件/ADR間の矛盾を検出する。**改善案の列挙より矛盾の発見に注力する。**

### 4類型の概要

| 類型 | conflict_type | 内容 |
|------|---------------|------|
| 改善案間の矛盾 | improvement_tradeoff | 改善案Aは品質Xを改善するが品質Yを損なう |
| 前提破壊 | assumption_violation | コンポーネントiの改善が依存先jの前提を破壊 |
| 不変条件違反 | invariant_violation | 推奨アクションが不変条件と食い違う |
| ADR矛盾 | adr_inconsistency | 推奨がADRと矛盾、またはADRが欠落 |

### 検出手順

1. 全 findings の recommendation を品質属性でタグ付け
2. 同じ品質属性に対して逆方向の recommendation がないか走査
3. 各 recommendation が invariants.yaml の条件に違反しないか確認
4. 各 recommendation が既存ADRと矛盾しないか確認
5. 重要な決定にADRがなければ `missing_adrs` として記録

各類型の詳細説明とYAML例は [references/conflict-types.md](references/conflict-types.md) を参照。矛盾を特定する際のパターンマッチに使用する。

## Phase 3: 優先順位付け

### スコアリング

```
Priority = Severity x Likelihood x Detectability_inv x Quality_Weight
```

| 要素 | 説明 | スケール |
|------|------|---------|
| Severity | 発生時の影響度 | critical=4, high=3, medium=2, low=1 |
| Likelihood | 発生確率 | high=3, medium=2, low=1 |
| Detectability_inv | 検出困難なほど高い | easy=1, medium=2, hard=3 |
| Quality_Weight | プロジェクト品質優先順位 | 1位=5, 2位=4, 3位=3, 4位=2, 5位=1 |

### 優先順位カテゴリ

| カテゴリ | スコア | 対応 |
|---------|--------|------|
| P0 - Blocker | 36+ | 即時対応（リリース不可） |
| P1 - Critical | 24-35 | 今スプリント内 |
| P2 - High | 12-23 | 次スプリント |
| P3 - Medium | 6-11 | バックログ |
| P4 - Low | 1-5 | 技術的負債 |

プロジェクト特性が未定義の場合、Quality_Weight は全て 3（中央値）として計算する。

スコアリングの詳細計算例とプロジェクト特性の定義例は [references/priority-scoring.md](references/priority-scoring.md) を参照。スコア算出に迷った時に使用する。

## 出力形式

`architecture-review/{timestamp}/review.yaml` に統合出力する。

```yaml
id: architecture-review
reviewed_at: "2024-01-21T10:00:00+09:00"
mode: full  # full | lightweight

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

verification_summary:
  verdict: NEEDS_ATTENTION  # PASS | PASS_WITH_WARNINGS | NEEDS_ATTENTION | FAIL
  by_verdict: { pass: 18, warn: 4, fail: 2 }
  dimensions_checked: [D2_test_coverage, D3_schema_match, D5_failure_modes]

# Phase 1 の結果
component_findings: [...]     # finding-examples.yaml 参照
interaction_findings: [...]   # finding-examples.yaml 参照
crosscutting_findings: [...]  # finding-examples.yaml 参照

# Phase 2 の結果
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

# Phase 3 の結果
prioritized_actions:
  - priority: P0
    items:
      - finding_id: EDGE-001
        score: 180
        action: payment-serviceタイムアウト整合

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

- **3種類すべてを実行**: 単体分析だけで終わらせると全体性を見落とす
- **矛盾検出が本丸**: 改善案の列挙より、矛盾の発見と解決に注力
- **不変条件に拘束**: 評価基準は invariants.yaml から導出
- **プロジェクト特性を必ず適用**: 同じ問題でも優先順位が変わる
- **推測禁止**: 根拠がない指摘はしない。evidence を必ず記載
- **severity は客観的に**: 影響範囲と発生確率で判定
- **ADR欠落の検出**: 重要な決定にADRがなければ指摘

## 参照

- [references/finding-examples.yaml](references/finding-examples.yaml) - 3種類の分析指摘のYAML例。指摘を書くときのテンプレートとして使用
- [references/conflict-types.md](references/conflict-types.md) - 矛盾の4類型の詳細説明とYAML例。矛盾を特定する際に使用
- [references/priority-scoring.md](references/priority-scoring.md) - スコアリング詳細とプロジェクト特性の定義例。スコア算出時に使用
- [references/crosscutting-checklist.md](references/crosscutting-checklist.md) - クロスカッティング分析の詳細チェックリスト。縦串分析時に使用
- [references/verification-dimensions.md](references/verification-dimensions.md) - D2/D3/D5 検証次元の詳細。設計整合性チェック時に使用
- [references/report-verdicts.md](references/report-verdicts.md) - PASS/WARN/FAIL 判定基準。verdict 付与時に使用
- `scripts/collect_artifacts.py` - Lightweight Mode 用アーティファクト収集スクリプト
