# ELD Plugin v3 (Evidence-Loop Development)

証拠で回す統合開発手法 ELD のコアプラグイン。Spec駆動モデリング、Predict-Lightゲート、2軸接地検証、知識管理を提供します。

## ELD統合ループ（5+1フェーズ）

```
Sense → Spec → Change → Ground → Record
  ↑                                  ↓
  └──────────── 循環 ←──────────────┘
         ↑
    Predict-Light (ゲート: P0/P1/P2)
```

**v1.0からの主な変更:**
- Model+Predict → Spec（SDD統合）、Predict-Lightゲート新設
- Commit → Change に吸収
- Ground 2軸化（Grounding Level × Evaluator Quality）+ TDD統制を統合
- Epistemic Status強化（出典必須化）
- Review Hybrid導入

## スキル一覧（12）

### メイン
| スキル | 説明 |
|--------|------|
| `eld` | ELD統合ワークフロー（デバッグへの適用を含む） |

### Sense（感知）
| スキル | 説明 |
|--------|------|
| `eld-sense-planning` | アクティブコンテキスト構築・タスク分解・並列実行最適化 |
| `eld-sense-requirements-brainstorming` | 要件の曖昧さを対話的に明確化 |

### Spec（仕様化）
| スキル | 説明 |
|--------|------|
| `eld-spec` | Spec発見+Card化+LinkMapの統合ルーティング |
| `eld-spec-discover` | Law/Term候補の発見 |
| `eld-spec-card` | Law/Term Cardの作成 |
| `eld-spec-link` | Law↔Term連結表管理 |

### Predict-Light（予測ゲート）
| スキル | 説明 |
|--------|------|
| `eld-predict-light` | P0/P1/P2段階化ゲート |

### Change（変更）
| スキル | 説明 |
|--------|------|
| `eld-change-worktree` | 高リスク変更時にgit worktreeで隔離環境を作成 |

### Ground（接地）
| スキル | 説明 |
|--------|------|
| `eld-ground` | 接地検証+PRレビュー+TDD統制を統合。2軸（Grounding Level × Evaluator Quality） |
| `eld-ground-law-monitor` | 本番でのLaw違反監視 |

### Record（記録）
| スキル | 説明 |
|--------|------|
| `eld-record` | Context Delta収集・検証・構造化・知識移転 |

## エージェント（3エージェント）

| エージェント | 責務 |
|-------------|------|
| `pce-lde-orchestrator` | ELDワークフロー統合オーケストレータ（Issue→PR→Record） |
| `spec-discovery-analyst` | Law/Term候補の発見・分類（`/eld-spec-discover`をディスパッチ） |
| `grounding-verifier` | 2軸接地検証（Grounding Level × Evaluator Quality） |

## クロスプラグイン依存

- **delivery-plugin** が本プラグインの `/eld`, `/eld-sense-*`, `/eld-ground`, `/eld-spec` を参照します。delivery-pluginとの併用を推奨します。
- **codex-plugin** の `pce-lde-orchestrator` エージェントが `/codex-consultant`, `/codex-negotiation` を使用します。codex-pluginとの併用を推奨します。

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/eld-plugin"
  ]
}
```
