# ELD × state_gate 統合

Evidence-Loop Development (ELD) の状態遷移を state_gate で管理し、各フェーズで適切なスキルを自動参照させる仕組み。

## 概要

2つのプロセスを提供:

1. **eld-process.yaml** - 新機能開発用（11状態）
2. **eld-debug-process.yaml** - デバッグ用（9状態）

### 開発プロセス (eld-process)

```
┌────────┐  start_task   ┌─────────┐  briefing_ready  ┌────────┐
│  Idle  │──────────────▶│ Onboard │─────────────────▶│ Sense  │
└────────┘               └─────────┘                  └───┬────┘
                          /ai-led-onboarding              │
                                                          │ /eld-sense-*
                                                          ▼
┌────────┐  record_done  ┌────────┐  grounding_passed ┌────────┐
│Complete│◀──────────────│ Record │◀──────────────────│ Ground │
└────────┘               └────────┘                   └───┬────┘
                          /eld-record-*                   │
                                                          │ /eld-ground-*, /test-design-audit
                                                          ▲
                                                     ┌────────┐
                                                     │ Change │
                                                     └───┬────┘
                                                         │ /eld-change-*, /systematic-test-design
                                                         ▲
┌────────┐  model_ready  ┌─────────┐  plan_approved  ┌────────────┐
│ Model  │──────────────▶│ Predict │────────────────▶│Test Design │
└────────┘               └─────────┘                 └────────────┘
 /eld-model-*             /eld-predict-impact         /test-design-audit
                                                      /systematic-test-design
```

### デバッグプロセス (eld-debug-process)

```
┌────────┐  start_debug  ┌────────┐  observation_complete  ┌────────┐
│  Idle  │──────────────▶│ Sense  │───────────────────────▶│ Model  │
└────────┘               └────────┘                        └───┬────┘
                          症状観測                              │
                                                               │ hypothesis_formed
                                                               ▼
┌────────┐  knowledge    ┌────────┐  verification_passed  ┌─────────┐
│Complete│◀─────────────│ Record │◀───────────────────────│ Ground  │
└────────┘  _recorded    └────────┘                       └────┬────┘
            バグパターン記録                                    │
                                                               │ fix_applied
                                                               ▲
                         ┌──────────────────┐            ┌────────┐
                         │hypothesis_rejected│◀───FAIL───│ Change │
                         └────────┬─────────┘            └───┬────┘
                                  │                          │
                                  │ restart_observation      │ impact_predicted
                                  ▼                          ▲
                              ┌────────┐              ┌─────────┐
                              │ Sense  │              │ Predict │
                              └────────┘              └─────────┘
                                                       影響予測
```

## フェーズとスキル対応

### 開発プロセス

| フェーズ | 主要スキル | 目的 |
|---------|-----------|------|
| **Onboard** | `/ai-led-onboarding` | 最小スキーマ（6点）構築 |
| **Sense** | `/eld-sense-*`, `/resolving-uncertainty` | コンテキスト構築・要件明確化 |
| **Model** | `/eld-model-*` | Law/Term定義 |
| **Predict** | `/eld-predict-impact` | 影響予測・段階化計画 |
| **Test Design** | `/test-design-audit`, `/systematic-test-design` | テスト設計（TDDのRED準備） |
| **Change** | `/eld-change-*`, `/eld-ground-tdd-enforcer`, `/systematic-test-design` | 実装（TDD） |
| **Ground** | `/eld-ground-*`, `/test-design-audit` | 接地検証 |
| **Record** | `/eld-record-*` | 知識記録 |
| **Blocked** | `/resolving-uncertainty` | 不確実性解消 |

### デバッグプロセス

| フェーズ | 主要スキル | 目的 |
|---------|-----------|------|
| **Sense** | `/eld-debug`, `/test-design-audit` | 症状観測・テストギャップ特定 |
| **Model** | `/eld-debug`, `/eld-model-law-discovery`, `/systematic-test-design` | 法則違反の仮説形成・PBTでエッジケース炙り出し |
| **Predict** | `/eld-debug`, `/eld-predict-impact` | 影響予測・修正計画 |
| **Change** | `/eld-debug`, `/eld-ground-tdd-enforcer`, `/systematic-test-design` | 法則復元・PBTリグレッション防止 |
| **Ground** | `/eld-debug`, `/eld-ground-check`, `/test-design-audit`, `/systematic-test-design` | 証拠による検証・カバレッジ監査 |
| **Record** | `/eld-debug`, `/eld-record-collection` | バグパターン記録 |
| **Hypothesis Rejected** | `/resolving-uncertainty` | 仮説再形成 |

## ディレクトリ構成

```
.state_gate/
├── processes/
│   ├── eld-process.yaml       # 開発プロセス（11状態）
│   └── eld-debug-process.yaml # デバッグプロセス（9状態）
├── schemas/
│   ├── briefing.schema.yaml
│   ├── active-context.schema.yaml
│   ├── uncertainty-register.schema.yaml
│   ├── impact-prediction.schema.yaml
│   ├── grounding-report.schema.yaml
│   ├── test-design.schema.yaml
│   ├── debug-symptom.schema.yaml       # デバッグ用
│   ├── debug-hypothesis.schema.yaml    # デバッグ用
│   ├── debug-fix-prediction.schema.yaml # デバッグ用
│   ├── debug-fix-log.schema.yaml       # デバッグ用
│   ├── debug-verification.schema.yaml  # デバッグ用
│   └── debug-bug-pattern.schema.yaml   # デバッグ用
├── templates/
│   ├── briefing.template.yaml
│   └── active-context.template.yaml
├── artifacts/
│   ├── briefing.yaml
│   ├── active-context.yaml
│   ├── law-term-snapshot.yaml
│   ├── impact-prediction.yaml
│   ├── test-design.yaml
│   ├── change-log.yaml
│   ├── grounding-report.yaml
│   ├── record-summary.yaml
│   ├── uncertainty-register.yaml
│   └── debug/                 # デバッグ用成果物
│       ├── symptom-observation.yaml
│       ├── hypothesis.yaml
│       ├── fix-prediction.yaml
│       ├── fix-log.yaml
│       ├── verification-report.yaml
│       └── bug-pattern.yaml
└── README.md
```

## セットアップ

### 1. state_gate のインストール

```bash
npm install -g @caphtech/state-gate
# または
npx @caphtech/state-gate
```

### 2. MCP Server の設定

`.mcp.json` に追加:

```json
{
  "mcpServers": {
    "state-gate-dev": {
      "command": "state-gate",
      "args": ["serve", "--process=.state_gate/processes/eld-process.yaml"],
      "env": {
        "STATE_GATE_PROJECT_ROOT": "."
      }
    },
    "state-gate-debug": {
      "command": "state-gate",
      "args": ["serve", "--process=.state_gate/processes/eld-debug-process.yaml"],
      "env": {
        "STATE_GATE_PROJECT_ROOT": "."
      }
    }
  }
}
```

### 3. Run の作成

```bash
# 開発用
state-gate create-run --process-id eld-development

# デバッグ用
state-gate create-run --process-id eld-debug
```

## 使い方

### 基本フロー

```bash
# 1. 現在の状態を確認
state-gate get-state

# 2. イベントを発行して遷移
state-gate emit-event --event start_task  # 開発用
state-gate emit-event --event start_debug # デバッグ用

# 3. 成果物を提出
state-gate submit-artifact --path .state_gate/artifacts/briefing.yaml
```

### Claude Code での使用

state_gate が MCP Server として動作し、各フェーズの `prompt` が自動的にコンテキストに注入されます。

#### 開発の場合

```
User: 新しい機能を実装して

Claude:
[state: idle -> onboard]

Onboardフェーズを開始します。
/ai-led-onboarding を実行して作戦ブリーフを作成します。

## オンボーディング契約
...
```

#### デバッグの場合

```
User: このバグを調査して

Claude:
[state: idle -> sense]

Senseフェーズを開始します。
/eld-debug を使用して症状を観測します。

## 症状観測
現象: ...
再現条件: ...
法則候補: ...
```

## 対話スキルの使い分け

| 状況 | スキル | 特徴 |
|------|--------|------|
| タスク開始直後 | `/ai-led-onboarding` | 最小スキーマ（6点）を構築 |
| 要件が曖昧 | `/eld-sense-requirements-brainstorming` | 多角的質問でIssue Contract作成 |
| 意思決定できない | `/resolving-uncertainty` | 不確実性台帳 → 観測タスク |
| バグ調査 | `/eld-debug` | 法則駆動デバッグ |

## ガード条件

遷移には以下のガード条件が設定されています:

- **artifact_exists**: 成果物が存在するか
- **manual_approval**: 人間の承認が必要（predict → change）
- **custom**: カスタムスクリプト（S0/S1 Law/Term接地確認）
- **role**: 特定ロールのみ実行可能

## デバッグプロセスの特徴

### 仮説却下ループ

デバッグでは仮説が間違っていることがあります。検証で仮説が否定された場合:

```
ground --[verification_failed]--> hypothesis_rejected
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼ restart_observation                   ▼ revise_hypothesis
                  sense                                   model
```

- **restart_observation**: 追加観測から再開
- **revise_hypothesis**: 新しい仮説を形成

### 停止条件

以下が発生したら即座に停止:

- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加
- ロールバック線の崩壊

## トラブルシューティング

### 状態がブロックされた場合

```bash
# 現在の状態と必要な成果物を確認
state-gate get-state --verbose

# 強制的に遷移（緊急時のみ）
state-gate emit-event --event override --role human
```

### 成果物の検証

```bash
# スキーマに対して検証
state-gate validate-artifact --path .state_gate/artifacts/briefing.yaml
```

## ライセンス

MIT
