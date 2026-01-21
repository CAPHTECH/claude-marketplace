---
name: invariant-extractor
description: |
  system-map-collectorで作成したシステムマップからInvariants（不変条件）とGlobal Rules（全体ルール）を抽出するスキル。
  コンポーネント、境界、データフロー、ランタイム要素等からシステム全体で守るべき制約を発見し、検証可能性を分類する。

  使用タイミング:
  - 「不変条件を抽出して」「Global Rulesを作成して」
  - 「システムマップからルールを発見して」「守るべき制約を整理して」
  - system-map/*.yaml が存在する状態で全体ルールを整理したい時
  - アーキテクチャ品質を担保するルールを明文化したい時
---

# Invariant Extractor

system-map/*.yaml からシステム全体の不変条件（Invariants）とグローバルルール（Global Rules）を抽出する。

## 前提条件

- `system-map/` ディレクトリが存在すること
- 最低限 `components.yaml`, `boundaries.yaml` が収集済みであること

## ワークフロー

```
1. システムマップ読込 → 2. カテゴリ別抽出 → 3. ギャップ分析 → 4. YAML出力
```

## Phase 1: システムマップ読込

```bash
ls system-map/*.yaml
```

必須ファイルを確認:
- `components.yaml` - コンポーネント一覧
- `boundaries.yaml` - 境界定義

推奨ファイル:
- `dependencies.yaml`, `data-flow.yaml`, `runtime.yaml`
- `auth-flow.yaml`, `api-contracts.yaml`, `failure-modes.yaml`

## Phase 2: カテゴリ別抽出

8カテゴリから不変条件を抽出する。詳細は [references/extraction-patterns.md](references/extraction-patterns.md) を参照。

| カテゴリ | 抽出元 | 典型的な不変条件 |
|---------|--------|-----------------|
| Security | boundaries (trust) | 認可は境界で完結、内部信頼前提禁止 |
| Data Ownership | components, data-flow | データ所有者以外は直接DB書込禁止 |
| Audit | observability | 重要操作は監査ログ必須 |
| Idempotency | runtime (queue/job) | リトライ可能操作は冪等キー必須 |
| Architecture | dependencies | 循環依存禁止、レイヤー違反禁止 |
| API Contract | api-contracts | 後方互換性維持、入力バリデーション必須 |
| Failure | failure-modes, runtime | タイムアウト必須、graceful degradation |
| Environment | environments | 本番直接アクセス禁止 |

### 抽出プロセス

各カテゴリについて:

1. 該当するシステムマップファイルを読込
2. パターンマッチで候補を抽出
3. confidence（high/medium/low）を判定
4. 関連コンポーネント・境界を紐付け

```yaml
# 抽出例
invariant_candidate:
  id: INV-SEC-001
  category: security
  statement: 認可チェックは必ずAPI Gateway層で完結する
  source:
    file: boundaries.yaml
    item_id: boundary-001
  related:
    components: [api-gateway, auth-service]
    boundaries: [trust-boundary-001]
  confidence: high
  verification:
    type: static  # static/test/runtime/manual
    method: middleware検査でAuthorizationヘッダー検証を確認
```

## Phase 3: ギャップ分析

抽出した不変条件の品質をチェック:

| チェック項目 | 内容 |
|-------------|------|
| 未定義境界 | boundariesにcrossing_rulesが未定義 |
| 監査漏れ | 重要操作でobservabilityが未設定 |
| 冪等性未定義 | queueがあるがidempotency_keyが未定義 |
| 障害対策なし | 外部連携でfailure-modesが未定義 |

## Phase 4: 出力

`system-map/invariants.yaml` に出力:

```yaml
id: invariants
name: 不変条件・グローバルルール
collected_at: "2024-01-21T10:00:00+09:00"
source_maps:
  - components.yaml
  - boundaries.yaml
  - runtime.yaml

summary:
  total: 24
  by_category:
    security: 5
    data_ownership: 3
    audit: 4
    idempotency: 2
    architecture: 4
    api_contract: 3
    failure: 2
    environment: 1
  by_confidence:
    high: 15
    medium: 7
    low: 2
  by_verification:
    static: 8
    test: 10
    runtime: 4
    manual: 2

items:
  - id: INV-SEC-001
    category: security
    statement: 認可チェックは必ずAPI Gateway層で完結する
    rationale: 内部サービスは信頼済み前提で動作し、個別認可を持たない
    source:
      file: boundaries.yaml
      item_id: boundary-001
    related:
      components: [api-gateway, auth-service]
      boundaries: [trust-boundary-001]
    confidence: high
    verification:
      type: static
      method: middleware検査でAuthorizationヘッダー検証を確認
      implementable: true

gaps:
  - type: missing_crossing_rules
    location: boundaries.yaml#boundary-003
    severity: high
    recommendation: VPC境界のcrossing_rulesを定義する
```

## 検証可能性の分類

| 分類 | 検証方法 | 例 |
|------|---------|-----|
| static | lint/型チェック/静的解析 | 循環依存検出、import制約 |
| test | 単体/結合テスト | 冪等性テスト、境界テスト |
| runtime | ログ/メトリクス監視 | 監査ログ出力、タイムアウト監視 |
| manual | レビュー/監査 | 設計レビュー、セキュリティ監査 |

## 注意事項

- 推測で不変条件を作成しない（ソースファイルに根拠がない場合はconfidence: lowで記録）
- 既存の `system-map/invariants.yaml` がある場合は差分更新
- 1セッションで全カテゴリを網羅しようとしない（重要度の高いカテゴリから順に）
