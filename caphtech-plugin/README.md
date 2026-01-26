# CAPHTECH Plugin for Claude Code

Claude Codeの機能を拡張するスキル・エージェント・フックのコレクションです。

## ELD (Evidence-Loop Development)

ELDは、**証拠で回す**統合開発手法です。DCCA（コード観測）、PCE（知識管理）、LDE（Law/Term規範）、Proprioceptive（安全な変更）を統一ループで実行します。

### 統一ループ

```
Sense → Model → Predict → Change → Ground → Record
  ↑                                            ↓
  └──────────────── 循環 ←─────────────────────┘
```

| Phase | 内容 | 主要スキル |
|-------|------|-----------|
| **Sense** | コードの事実/意図/関係を観測 | `eld-sense-*` |
| **Model** | 語彙（Term）と関係（Law）を同定 | `eld-model-*` |
| **Predict** | 影響を因果タイプ分類、段階化 | `eld-predict-impact` |
| **Change** | 最小単位で変更、高リスク時は隔離 | `eld-change-worktree` |
| **Ground** | テスト/Telemetryで接地 | `eld-ground-*` |
| **Record** | Context Deltaを記録 | `eld-record-*` |

### スキル一覧

#### メイン
| スキル | 説明 |
|--------|------|
| `eld` | ELD統合ワークフロー |

#### Sense（感知）
| スキル | 説明 |
|--------|------|
| `eld-sense-requirements-brainstorming` | 要件の曖昧さを対話的に明確化 |
| `eld-sense-activation` | アクティブコンテキスト構築 |
| `eld-sense-scope` | タスクスコープの定義 |
| `eld-sense-task-decomposition` | タスク分解 |
| `eld-sense-parallel-orchestrator` | 並列実行最適化 |

#### Model（モデル化）
| スキル | 説明 |
|--------|------|
| `eld-model-law-discovery` | Law候補の発見 |
| `eld-model-law-card` | Law Card作成 |
| `eld-model-term-card` | Term Card作成 |
| `eld-model-link-map` | Law↔Term連結表管理 |

#### Ground（接地）
| スキル | 説明 |
|--------|------|
| `eld-ground-tdd-enforcer` | TDDサイクル強制とL1達成 |
| `eld-ground-check` | 接地状況の検証 |
| `eld-ground-evaluate` | 成果物評価 |
| `eld-ground-law-monitor` | Law違反監視 |
| `eld-ground-pr-review` | PRレビュー |
| `eld-ground-pre-completion` | PR作成前の完成前検証 |

#### Record（記録）
| スキル | 説明 |
|--------|------|
| `eld-record-collection` | Context Delta収集 |
| `eld-record-structuring` | 知識の構造化 |
| `eld-record-compact` | 履歴圧縮 |
| `eld-record-maintenance` | 知識メンテナンス |
| `eld-record-memory-collector` | メモリ収集 |
| `eld-record-knowledge-transfer` | 知識転送 |

### 使い方

```bash
# 統合ワークフロー（推奨）
/eld

# フェーズ別
/eld-sense-activation    # Senseフェーズ
/eld-model-law-discovery # Modelフェーズ
/eld-ground-check        # Groundフェーズ
/eld-record-collection   # Recordフェーズ
```

### ELDの核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
4. **Minimal Change**: 最小単位で変更し、即時検証する
5. **Source of Truth**: 真実は常に「現在のコード」

## 開発フロー

このプラグインは2つの主要ワークフローを提供します。

### ワークフロー選択

| ケース | 推奨ワークフロー | トリガー |
|--------|-----------------|----------|
| Issue起点で作業開始 | Issue Workflow | `Issue #N を対応して` |
| 新機能/バグ修正/リファクタリング | ELD統合ループ | `/eld` |
| 総合的な開発（Issue→PR完了） | 両方を組み合わせ | `issue-workflow-orchestrator-agent` |

### Issue Workflow（Issue起点開発）

Issue受領からPR完了までを一貫管理するワークフロー。

```
Phase 1: Intake（トリアージ）
  └→ /issue-intake
     - 分類: Critical/Major/Minor/Enhancement/NeedsInfo
     - severity_score + confidence
     - uncertainty_flags → 次フェーズ判断

Phase 2: Context（文脈構築）
  └→ /ai-led-onboarding
  └→ /impact-analysis（Major以上）

Phase 3: Uncertainty Resolution（不確実性解消）
  └→ /resolving-uncertainty（不確実性がある場合）

Phase 4: Task Decomposition（タスク分解）
  └→ /eld-sense-task-decomposition

Phase 5: Implementation（実装）
  └→ /eld + /observation-minimum-set

Phase 6: Review（レビュー）
  └→ /eld-ground-pr-review → PR作成
```

#### ワークフローテンプレート

| 分類 | severity | テンプレート | 特徴 |
|------|----------|-------------|------|
| trivial | 1-2 | `trivial_fix_v1` | 最小フロー（intake→実装→review） |
| minor | 3-5 | `minor_bugfix_v1` | 標準フロー |
| major | 6-8 | `major_bugfix_v2` | 標準＋オンボーディング＋強化観測 |
| critical | 9-10 | `critical_hotfix_v1` | 緊急フロー（並列化、事後対応） |
| security | - | `security_fix_v1` | セキュリティ強化フロー |
| feature | - | `feature_v1` | 設計フェーズ追加 |

### ELD統合ループ（証拠駆動開発）

```
Phase 1: Issue（受付）
  - pce.memory.activate で関連知識を活性化
  - Issue Contractを作成（目的/不変条件/物差し/停止条件）
  - Term/Law候補を列挙
  → スキル: /eld-sense-activation, /eld-model-law-discovery

Phase 2: Design（設計）
  - Law/Term Cards作成（相互参照あり、孤立なし）
  - Grounding Plan（必要テスト/Telemetry）
  - Change Plan（微小変更列＋各ステップのチェック）
  → スキル: /eld-model-law-card, /eld-model-term-card

Phase 3: Implementation（実装ループ）
  1. Sense   → 触るシンボル/境界/設定の身体図更新
  2. Predict → 期待される因果と失敗モード
  3. Change  → 最小単位で変更、Pure/IO分離を維持
  4. Ground  → テスト/Telemetryで観測写像を満たす
  5. Record  → Context Delta記録
  → スキル: /eld

Phase 4: Review（レビュー）
  - 因果と証拠の整合
  - Law/Term孤立チェック
  - Evidence Ladder達成レベル確認
  → スキル: /eld-ground-check, /eld-ground-pr-review

Phase 5: Ops（運用）
  - Telemetryで Law違反を監視
  - pce-memoryへのフィードバック
```

### エージェントの使い分け

| 状況 | 使用エージェント |
|------|-----------------|
| Issue起点で作業開始 | `issue-workflow-orchestrator-agent` |
| PCE-LDE統合開発 | `pce-lde-orchestrator` |
| 観測スキルの選択・実行 | `observation-orchestrator` |
| Term発見・Card化 | `vocabulary-term-analyst` |
| Law発見・Card化 | `law-constraint-analyst` |
| 相互拘束検証（PR前） | `mutual-constraint-validator` |
| 接地検証 | `grounding-verifier` |
| 知識の収集・文書化 | `pce-knowledge-architect` |
| 過去パターン調査 | `pce-memory-analyzer` |
| 長時間調査（知識永続化） | `pce-memory-orchestrator` |

### クイックスタート

```bash
# Issue起点の開発（推奨）
「Issue #123 を対応して」  # issue-workflow-orchestrator-agent が起動

# 機能開発・バグ修正
/eld

# 個別フェーズの実行
/issue-intake          # Issue初期トリアージ
/eld-sense-activation  # コンテキスト活性化
/eld-model-law-card    # Law Card作成
/eld-ground-check      # 接地状況の検証
/eld-record-collection # 知識記録

# 観測（品質チェック）
/observation-minimum-set  # 最小観測セット
/security-observation     # セキュリティ観測
/boundary-observation     # 境界条件観測
```

### 完了条件と停止条件

#### 完了条件
- Issue Contractの物差しが満たされている
- Law/Termが接地している（Evidence Ladder L1以上）
- Evidence Packが揃っている
- すべての必須テストがパス

#### 停止条件（発生時は追加計測/スコープ縮小）
- 予測と現実の継続的乖離（想定外のテスト失敗3回以上）
- 観測不能な変更の増加
- セキュリティ脆弱性検出
- スコープ変更検出（affected_modules > 3）

## Observation Skills

コード品質と安全性を観測するためのスキル群です。

| スキル | 説明 |
|--------|------|
| `boundary-observation` | 境界条件・エッジケースの観測 |
| `concurrency-observation` | 並行性の観測 |
| `dependency-observation` | 依存関係の観測 |
| `operability-observation` | 運用性の観測 |
| `security-observation` | セキュリティの観測 |
| `spec-observation` | 仕様整合性の観測 |
| `observation-minimum-set` | 最小観測セット |

## Issue Workflow

Issue起点の開発ワークフローを支援するスキル群です。

| スキル | 説明 |
|--------|------|
| `issue-intake` | Issue初期トリアージ。severity_score + confidence分離、NeedsInfo分類、uncertainty_flags→next_actions接続 |
| `issue-workflow-orchestrator` | Issue→PR完了のワークフロー制御。状態機械、artifact契約、stop_conditions、6テンプレート |
| `impact-analysis` | コード変更の影響範囲分析。8影響面（code/interface/data/external/config/runtime/security/observability）、根拠ベースimpact |

## Onboarding & Knowledge Management

オンボーディングと知識管理のためのスキル群です。

| スキル | 説明 |
|--------|------|
| `ai-led-onboarding` | AI主導の作業開始オンボーディング。最小スキーマ（因果・境界・不変条件・壊れ方・観測）を短時間で再構築 |
| `pr-onboarding` | PR作成時のオンボーディング記述。変更の契約（What/Why/不変条件/影響範囲/壊れ方/検証/ロールバック）をPR本文に |
| `knowledge-validator` | pce-memory活用の5種類の知識検証ワークフロー |
| `uncertainty-to-law` | 検証済み仮説をLDEのLawに昇格 |
| `resolving-uncertainty` | 不確実性の解消 |

## Documentation & Specification

ドキュメント生成と仕様管理のためのスキル群です。

| スキル | 説明 |
|--------|------|
| `doc-gen` | 根拠に基づく開発者向けドキュメント生成（マップ・フロー・プレイブック・台帳） |
| `spec-gen` | コードからAs-Is spec（現状仕様）を根拠付きで抽出 |
| `technical-book-writer` | Markdown形式の技術書執筆支援 |

## Testing & Quality

テスト設計と品質管理のためのスキル群です。

| スキル | 説明 |
|--------|------|
| `test-design-audit` | テスト設計プロセス全体のフレームワーク。要求→モデル化→テスト条件→監査の流れで「何をテストすべきか」を導出 |
| `systematic-test-design` | ユニットテスト＋PBT（Property-Based Testing）の実装スキル。「どうテストを実装するか」を設計 |
| `llm-eval-designer` | LLM生成システムの検証設計。幻覚・過学習などLLM特有の失敗モードを考慮 |
| `critical-code-review` | 批判的コードレビュー |

### test-design-audit vs systematic-test-design

| 観点 | test-design-audit | systematic-test-design |
|------|-------------------|------------------------|
| **目的** | テスト設計プロセス全体（抜け漏れ防止） | テスト実装の具体的手法 |
| **フォーカス** | 「何をテストすべきか」を導出 | 「どうテストを実装するか」を設計 |
| **成果物** | 要求一覧、テスト条件ツリー、トレーサビリティ表 | ユニットテスト、プロパティカタログ、ジェネレータ群、反例コーパス |
| **手法** | 5モデル化＋監査＋Evidence Ladder | ユニットテスト3種類（典型例/境界例/回帰例）＋PBT7分類＋意地悪レベルL0-L8 |

**使い分け**: `test-design-audit`で「テスト条件」を導出し、`systematic-test-design`で「テストコード」を実装する。

## Refactoring

リファクタリング支援のためのスキル群です。

| スキル | 説明 |
|--------|------|
| `refactoring-discovery` | リファクタリング機会の検出（責務過多・密結合・SOLID違反など） |
| `refactoring-executor` | テストファースト検証で安全な段階的リファクタリング実行 |

## Other Skills

その他の開発支援スキル群です。

| スキル | 説明 |
|--------|------|
| `app-idea-workshop` | アプリアイデアワークショップ |
| `claude-md-customizer` | 対話形式でCLAUDE.mdをカスタマイズ |

## Architecture Review

アーキテクチャの体系的なレビューを行うためのスキル群です。「推測で埋めない」を原則とし、unknownはunknown、assumptionは明示的に記録します。

### ワークフロー

```
Phase 1-3: Knowledge Building（知識構築）
  system-map-collector → invariant-extractor → component-dossier-builder

Phase 4-6: Analysis & Reporting（分析・報告）
  architecture-reviewer → synthesis-analyzer → review-report-generator
```

### Phase 1-3: Knowledge Building

| スキル | Phase | 説明 |
|--------|-------|------|
| `system-map-collector` | 1 | システムマップ収集。コンポーネント、依存関係、データフロー、境界、ランタイム、認証フロー、API契約を構造化 |
| `invariant-extractor` | 2 | 不変条件抽出。システムマップから8カテゴリのInvariants/Global Rulesを抽出（Security/Data/Audit/Idempotency/Architecture/API/Failure/Environment） |
| `component-dossier-builder` | 3 | コンポーネントカード作成。RAG検索単位となる詳細なコンポーネントカードを生成（purpose/contracts/owned_data/dependencies/failure_modes/state/non_functional/test_strategy/unknowns/assumptions） |

### Phase 4-6: Analysis & Reporting

| スキル | Phase | 説明 |
|--------|-------|------|
| `architecture-reviewer` | 4 | 3種類の分析を並行実行。コンポーネント内（ノード）、インタラクション（エッジ）、クロスカッティング（縦串）の3視点で問題検出 |
| `synthesis-analyzer` | 5 | 矛盾検出と優先順位付け。4類型の矛盾（改善案間/前提破壊/不変条件/ADR）を検出し、プロジェクト特性に基づきP0-P4で優先順位付け |
| `review-report-generator` | 6 | 意思決定用レポート生成。scope/failure_mode/trigger_conditions/evidence/options/priority/implementation/acceptance_criteriaを含む標準形式 |

### 使い方

```bash
# Phase 1-3: 知識構築
/system-map-collector      # システムマップ収集
/invariant-extractor       # 不変条件抽出
/component-dossier-builder # コンポーネントカード作成

# Phase 4-6: 分析・報告
/architecture-reviewer     # 3種類の分析
/synthesis-analyzer        # 矛盾検出・優先順位付け
/review-report-generator   # レポート生成
```

### 出力ファイル

```
system-map/
├── components.yaml      # Phase 1
├── dependencies.yaml    # Phase 1
├── data-flow.yaml       # Phase 1
├── boundaries.yaml      # Phase 1
├── runtime.yaml         # Phase 1
├── auth-flow.yaml       # Phase 1
├── api-contracts.yaml   # Phase 1
└── invariants.yaml      # Phase 2

component-dossiers/
└── {component-id}.yaml  # Phase 3

architecture-review/{timestamp}/
├── findings.yaml        # Phase 4
├── synthesis.yaml       # Phase 5
└── report/              # Phase 6
    ├── summary.md
    ├── p0-blockers.md
    ├── p1-critical.md
    ├── p2-high.md
    ├── backlog.md
    └── adrs-needed.md
```

## エージェント

ELD統合開発のための専用エージェント群です。

### Issue Workflowエージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `issue-workflow-orchestrator-agent` | Issue起点のワークフロー全体制御 | 「Issue #N を対応して」、Issue起点で作業開始時 |

### ELD統合エージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `pce-lde-orchestrator` | 開発フロー全体の調整（issue-intake/impact-analysis連携含む） | Issue受付時、統合開発時 |
| `vocabulary-term-analyst` | Term発見・Card化 | Model Phase |
| `law-constraint-analyst` | Law発見・Card化 | Model Phase |
| `mutual-constraint-validator` | 相互拘束検証 | PR作成前 |
| `grounding-verifier` | 接地検証 | Ground Phase |

### メモリ管理エージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `pce-memory-analyzer` | メモリの分析・インサイト抽出 | 過去パターン調査時 |
| `pce-knowledge-architect` | 知識の収集・構造化・文書化 | Record Phase |
| `pce-memory-orchestrator` | セッション間の知識永続化 | 長時間調査時 |

### Architecture Reviewエージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `architecture-knowledge-builder` | Phase 1-3の知識構築（システムマップ→不変条件→コンポーネントカード） | 「アーキテクチャの知識を構築して」、レビュー準備段階 |
| `architecture-analysis-reporter` | Phase 4-6の分析・報告（3種類分析→矛盾検出→レポート生成） | 「アーキテクチャを分析して」、「レビューレポートを作成して」 |

## ディレクトリ構造

```
caphtech-plugin/
├── *.skill           # パッケージ化されたスキル
├── skills/           # スキルのソースディレクトリ
│   ├── eld/          # ELDメインスキル
│   ├── eld-sense-*/  # Senseフェーズスキル
│   ├── eld-model-*/  # Modelフェーズスキル
│   ├── eld-ground-*/ # Groundフェーズスキル
│   ├── eld-record-*/ # Recordフェーズスキル
│   ├── *-observation/ # Observationスキル
│   └── ...           # その他のスキル
├── agents/           # エージェント定義
├── commands/         # コマンド定義
└── hooks/            # フック定義
```

## スキル一覧（全52スキル）

| カテゴリ | スキル数 |
|---------|---------|
| ELD (Evidence-Loop Development) | 20 |
| Observation | 7 |
| Issue Workflow | 3 |
| Onboarding & Knowledge | 5 |
| Documentation & Specification | 3 |
| Testing & Quality | 4 |
| Refactoring | 2 |
| Architecture Review | 6 |
| Other | 2 |

## インストール

1. このリポジトリをクローン
2. Claude Codeの設定でpluginパスを追加

```json
{
  "plugins": [
    "/path/to/claude-marketplace/caphtech-plugin"
  ]
}
```

## ライセンス

MIT License
