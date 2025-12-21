# CAPHTECH Plugin for Claude Code

Claude Codeの機能を拡張するスキル・エージェント・フックのコレクションです。

## PCE (Process-Context Engine) Skills

PCEは、**プロセスがコンテキストを生成し、そのコンテキストが次のプロセスを駆動する**という循環モデルに基づく開発手法です。

### 循環モデル

```
潜在プール → [Compile] → アクティブコンテキスト → [実行] → 成果物 → [Capture] → 潜在プール
     ↑                                                              ↓
     └──────────────────────── [Merge] ←───────────────────────────┘
```

### スキル一覧

| スキル | 責務 | トリガー例 |
|--------|------|-----------|
| `pce-collection` | Capture - Context Delta収集 | 「この判断を記録して」 |
| `pce-structuring` | Store/Merge - 知識の構造化 | 「CLAUDE.mdを更新して」 |
| `pce-activation` | Compile - アクティブコンテキスト構築 | 「この機能を実装して」 |
| `pce-scope` | Scope - 入れ子プロセス間継承設計 | 「タスクを分割して」 |
| `pce-compact` | Compact - コンテキスト圧縮 | 「ここまでをまとめて」 |
| `pce-evaluate` | Evaluate - 出力評価 | 「品質チェックして」 |
| `pce-orchestrate` | 統合オーケストレーション | 「PCEで進めて」 |
| `pce-pr-review` | PRレビュー | 「PRをレビューして」 |
| `pce-task-decomposition` | タスク分解 | 「実装計画を立てて」 |
| `pce-knowledge-transfer` | 知識移転 | 「引き継ぎ資料を作って」 |

### 使い方

```bash
# 統合オーケストレーション（推奨）
/pce-orchestrate

# 個別スキル
/pce-activation      # タスク開始時
/pce-collection      # 知見収集時
/pce-evaluate        # 成果物評価時
/pce-compact         # セッション終了時
```

### PCEの価値

1. **手戻りの低減**: 目的・制約・参照を明確化した投入物でAI出力が安定
2. **知識の蓄積**: 意思決定の痕跡をContext Deltaとして記録
3. **入れ子プロセス対応**: 親→子→孫のコンテキスト継承を設計
4. **セッション継続**: 長期タスクの履歴を圧縮して継続可能に

## LDE (Law-Driven Engineering) Skills

LDEは、**名辞抽象（Vocabulary）と関係抽象（Law）の相互拘束**によって実装の一貫性と保守性を高める開発手法です。

### スキル一覧

| スキル | 責務 | トリガー例 |
|--------|------|-----------|
| `lde` | LDE概要とガイドライン | 「LDEで開発して」 |
| `lde-law-card` | Law Card作成 | 「Lawをカード化して」 |
| `lde-term-card` | Term Card作成 | 「Termをカード化して」 |
| `lde-link-map` | Law↔Term連結表管理 | 「孤立チェックして」 |
| `lde-law-discovery` | Vocabulary/Law発見 | 「Lawを発見して」 |
| `lde-grounding-check` | 接地検証 | 「Groundingチェックして」 |
| `lde-pce-workflow` | PCE-LDE統合ワークフロー | 「PCE-LDEで進めて」 |

## エージェント

PCE×LDE統合開発のための専用エージェント群です。

### PCE×LDE統合エージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `pce-lde-orchestrator` | 開発フロー全体の調整 | Issue受付時、統合開発時 |
| `vocabulary-term-analyst` | 名辞抽象（Term発見・Card化） | Phase A-D、語彙整理時 |
| `law-constraint-analyst` | 関係抽象（Law発見・Card化） | Phase B-C、制約発見時 |
| `mutual-constraint-validator` | 相互拘束検証 | PR作成前、変更影響分析時 |
| `grounding-verifier` | 接地検証 | 実装完了後、Phase E |

### PCEメモリ管理エージェント

| エージェント | 責務 | 使用タイミング |
|-------------|------|---------------|
| `pce-memory-analyzer` | PCEメモリの分析・インサイト抽出 | 過去パターン調査、ADR参照時 |
| `pce-knowledge-architect` | 知識の収集・構造化・文書化 | 実装後の知見整理、CLAUDE.md作成時 |
| `pce-memory-orchestrator` | セッション間の知識永続化 | 長時間調査、コンテキスト復元時 |

### エージェントの使い方

#### 自動選択（推奨）

Claude Codeがタスクの性質に応じて適切なエージェントを自動選択します。

```
ユーザー: 「Issue #123を実装して」
→ pce-lde-orchestrator が自動起動
  → vocabulary-term-analyst, law-constraint-analyst が並列実行
```

#### 明示的な指示

エージェント名またはトリガーフレーズで直接指定できます。

```bash
# エージェント名で指定
「vocabulary-term-analystを使って語彙を整理して」

# トリガーフレーズで指定
「Lawを抽出して」           # → law-constraint-analyst
「孤立を検出して」           # → mutual-constraint-validator
「接地チェックして」         # → grounding-verifier
「過去のエラーパターン調べて」 # → pce-memory-analyzer
```

#### 典型的なワークフロー

```
Issue実装フロー:
  1. pce-lde-orchestrator   ← 「Issueを実装して」
     ├→ vocabulary-term-analyst（並列）
     └→ law-constraint-analyst（並列）
  2. mutual-constraint-validator ← 設計完了後
  3. grounding-verifier         ← 実装完了後
  4. pce-knowledge-architect    ← PR作成前

調査・デバッグフロー:
  1. pce-memory-orchestrator ← 「このバグを調査して」
     └→ pce-memory-analyzer（過去パターン検索）
  2. pce-memory-orchestrator ← 調査中（仮説・発見を随時保存）
  3. pce-knowledge-architect ← 解決後（文書化）
```

## その他のスキル

| スキル | 説明 |
|--------|------|
| `claude-md-customizer` | 対話形式でCLAUDE.mdをカスタマイズ |
| `critical-code-review` | 批判的コードレビュー |
| `pce-memory-collector` | pce-memory情報収集 |
| `resolving-uncertainty` | 不確実性の解消 |

## ディレクトリ構造

```
caphtech-plugin/
├── *.skill           # パッケージ化されたスキル
├── skills/           # スキルのソースディレクトリ
├── agents/           # エージェント定義
├── commands/         # コマンド定義
└── hooks/            # フック定義
```

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
