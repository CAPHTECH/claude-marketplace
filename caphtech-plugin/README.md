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
| **Predict** | 影響を因果タイプ分類、段階化 | - |
| **Change** | 最小単位で変更 | - |
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
| `eld-sense-activation` | アクティブコンテキスト構築 |
| `eld-sense-scope` | タスクスコープの定義 |
| `eld-sense-task-decomposition` | タスク分解 |

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
| `eld-ground-check` | 接地状況の検証 |
| `eld-ground-evaluate` | 成果物評価 |
| `eld-ground-law-monitor` | Law違反監視 |
| `eld-ground-pr-review` | PRレビュー |

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
| `test-design-audit` | モデル駆動型テスト設計。モデル化と監査で抜け漏れを見える化 |
| `llm-eval-designer` | LLM生成システムの検証設計。幻覚・過学習などLLM特有の失敗モードを考慮 |
| `critical-code-review` | 批判的コードレビュー |

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

## エージェント

ELD統合開発のための専用エージェント群です。

### ELD統合エージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `pce-lde-orchestrator` | 開発フロー全体の調整 | Issue受付時、統合開発時 |
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

## スキル一覧（全40スキル）

| カテゴリ | スキル数 |
|---------|---------|
| ELD (Evidence-Loop Development) | 18 |
| Observation | 7 |
| Onboarding & Knowledge | 5 |
| Documentation & Specification | 3 |
| Testing & Quality | 3 |
| Refactoring | 2 |
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
