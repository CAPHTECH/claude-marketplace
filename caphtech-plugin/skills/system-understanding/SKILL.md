---
name: system-understanding
context: fork
description: "システムマップ収集・不変条件抽出・コンポーネントカード作成を統合したスキル。コードベースを調査しアーキテクチャ知識をYAMLで構造化する。「システムマップを作成して」「不変条件を抽出して」「コンポーネントカードを作って」と指示された時、またはプロジェクトの全体像を把握したい時に使う。"
argument-hint: "[map|invariants|dossiers|all]"
---

# System Understanding

コードベースを調査し、アーキテクチャ知識を3段階で構造化する。

`$ARGUMENTS` でPhaseを指定する:
- `map` — Phase 1のみ
- `invariants` — Phase 2のみ
- `dossiers` — Phase 3のみ
- `all` または未指定 — Phase 1→2→3を順に実行

## Phase 1: システムマップ収集 → system-map/*.yaml

コードベースを調査し、アーキテクチャ情報をYAML形式で収集する。

**重要**: 品質確保のため、一度に1項目のみ収集する。

### 手順

1. `system-map/definition.yaml` を作成（テンプレートは [references/definition-template.md](references/definition-template.md) を参照）
2. 未収集項目を確認し、1つ選択
3. Exploreエージェントまたはkiri MCPで調査
4. 結果を `system-map/{item-id}.yaml` に出力
5. `system-map/progress.yaml` を更新

```bash
mkdir -p system-map
```

### 調査方法

```
Task(subagent_type="Explore", prompt="...")
# または
context_bundle(goal="...")
deps_closure(path="...", direction="both")
```

### 出力形式

[references/output-schema.md](references/output-schema.md) に項目別スキーマの詳細を記載。共通ヘッダー:

```yaml
id: <項目ID>
name: <項目名>
collected_at: <ISO8601>
confidence: high  # high/medium/low
items:
  - id: comp-001
    name: ...
```

### 進捗管理

`system-map/progress.yaml` で進捗を管理:

```yaml
total_items: 14
completed: 3
items:
  - id: components
    status: completed  # completed/in_progress/pending/skipped
    file: components.yaml
  - id: dependencies
    status: pending
```

### 注意事項

- 複数項目を同時に収集しない
- 既存の `system-map/*.yaml` を確認して重複を避ける
- 不明な点は推測せず「不明」と記載する

---

## Phase 2: 不変条件抽出 → system-map/invariants.yaml

system-map/*.yaml からシステム全体の不変条件（Invariants）とグローバルルール（Global Rules）を抽出する。

### 前提条件

- `system-map/` に最低限 `components.yaml`, `boundaries.yaml` が収集済み

### 手順

1. `system-map/*.yaml` を読み込む
2. 8カテゴリから不変条件を抽出
3. ギャップ分析を実施
4. `system-map/invariants.yaml` に出力

### 8カテゴリ

抽出パターンの詳細は [references/extraction-patterns.md](references/extraction-patterns.md) を参照。

| カテゴリ | 抽出元 | 典型的な不変条件 |
|---------|--------|-----------------|
| Security | boundaries, auth-flow | 認可は境界で完結 |
| Data Ownership | components, data-flow | データ所有者以外は直接DB書込禁止 |
| Audit | observability, api-contracts | 重要操作は監査ログ必須 |
| Idempotency | runtime (queue/job) | リトライ可能操作は冪等キー必須 |
| Architecture | dependencies | 循環依存禁止、レイヤー違反禁止 |
| API Contract | api-contracts | 後方互換性維持、入力バリデーション必須 |
| Failure | failure-modes, runtime | タイムアウト必須、graceful degradation |
| Environment | environments, secrets-config | 本番直接アクセス禁止 |

### 抽出プロセス

各カテゴリについて:
1. 該当するシステムマップファイルを読込
2. パターンマッチで候補を抽出
3. confidence（high/medium/low）を判定
4. 関連コンポーネント・境界を紐付け

### ギャップ分析

| チェック項目 | 内容 |
|-------------|------|
| 未定義境界 | boundariesにcrossing_rulesが未定義 |
| 監査漏れ | 重要操作でobservabilityが未設定 |
| 冪等性未定義 | queueがあるがidempotency_keyが未定義 |
| 障害対策なし | 外部連携でfailure-modesが未定義 |

### 出力形式

```yaml
id: invariants
name: 不変条件・グローバルルール
collected_at: "2024-01-21T10:00:00+09:00"
source_maps:
  - components.yaml
  - boundaries.yaml

summary:
  total: 24
  by_category: { security: 5, data_ownership: 3, ... }
  by_confidence: { high: 15, medium: 7, low: 2 }
  by_verification: { static: 8, test: 10, runtime: 4, manual: 2 }

items:
  - id: INV-SEC-001
    category: security
    statement: 認可チェックは必ずAPI Gateway層で完結する
    rationale: 内部サービスは信頼済み前提で動作する
    source: { file: boundaries.yaml, item_id: boundary-001 }
    related:
      components: [api-gateway, auth-service]
      boundaries: [trust-boundary-001]
    confidence: high
    verification:
      type: static  # static/test/runtime/manual
      method: middleware検査で検証

gaps:
  - type: missing_crossing_rules
    location: boundaries.yaml#boundary-003
    severity: high
    recommendation: crossing_rulesを定義する
```

### 検証可能性の分類

| 分類 | 検証方法 | 例 |
|------|---------|-----|
| static | lint/型チェック/静的解析 | 循環依存検出、import制約 |
| test | 単体/結合テスト | 冪等性テスト、境界テスト |
| runtime | ログ/メトリクス監視 | 監査ログ出力、タイムアウト監視 |
| manual | レビュー/監査 | 設計レビュー、セキュリティ監査 |

### 注意事項

- 推測で不変条件を作成しない（根拠がない場合はconfidence: low）
- 既存の `system-map/invariants.yaml` がある場合は差分更新
- 1セッションで全カテゴリを網羅しようとしない（重要度の高いカテゴリから）

---

## Phase 3: コンポーネントカード作成 → component-dossiers/*.yaml

system-map/components.yaml から各コンポーネントの詳細な「ドシエ（調査書）」を作成する。

**重要ルール**: 推測で埋めない。不明点は `unknowns` に、仮定は `assumptions` に明示する。

### 前提条件

- `system-map/components.yaml` が存在すること

### 手順

1. `system-map/components.yaml` を読み、未作成のコンポーネントを1つ選択
2. Exploreエージェントまたはkiri MCPで深掘り調査
3. `component-dossiers/{component-id}.yaml` に出力
4. `component-dossiers/progress.yaml` を更新

```bash
mkdir -p component-dossiers
ls component-dossiers/*.yaml 2>/dev/null || echo "未作成"
```

### 優先順位

1. 依存される側が多いコンポーネント（影響範囲が大きい）
2. 境界に位置するコンポーネント（API Gateway、認証など）
3. 障害モードが定義されているコンポーネント

### 調査内容

```
Task(subagent_type="Explore", prompt="
{component_name}について以下を調査して:
1. 責務（何をするか、何をしないか）
2. 公開API/イベント/DBスキーマ
3. 依存先と依存される側
4. エラーハンドリングとリトライ戦略
5. 状態管理（ステートフル/ステートレス、キャッシュ）
6. テストの有無と種類
")
```

### 出力形式

テンプレートの詳細は [references/card-template.md](references/card-template.md) を参照。最小限のカード:

```yaml
id: order-service
name: 注文サービス
collected_at: "2024-01-21T10:00:00+09:00"
confidence: high  # high=コード確認済 / medium=一部推測 / low=ドキュメントのみ
source_files:
  - src/services/order/

purpose:
  does:
    - 注文の作成・更新・キャンセル
  does_not:
    - 決済処理（payment-serviceに委譲）

contracts:
  apis: [...]
  events_published: [...]
  events_subscribed: [...]
  db_tables: [...]

dependencies:
  depends_on: [...]
  depended_by: [...]

failure_modes:
  - trigger: payment-service timeout
    behavior: pending状態に保持
    recovery: 3回リトライ後に失敗

unknowns:
  - フォールバック戦略が未定義
assumptions:
  - payment-serviceは冪等性を保証していると仮定
```

### 注意事項

- 1セッションで1コンポーネントのみ調査（品質確保のため）
- 既存の `component-dossiers/*.yaml` を確認して重複を避ける
- 大きなコンポーネントは分割を検討
