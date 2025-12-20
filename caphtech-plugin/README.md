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

## その他のスキル

| スキル | 説明 |
|--------|------|
| `claude-md-customizer` | 対話形式でCLAUDE.mdをカスタマイズ |
| `critical-code-review` | 批判的コードレビュー |
| `lde` | Law-Driven Engineering |
| `lde-law-card` | LDE法則カード作成 |
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
