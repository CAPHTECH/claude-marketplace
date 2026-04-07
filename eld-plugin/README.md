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
- Ground 2軸化（Evidence Level × Evaluator Quality）
- Epistemic Status強化（出典必須化）
- Review Hybrid導入

## スキル一覧（16 primary + 8 alias = 24）

### メイン
| スキル | 説明 |
|--------|------|
| `eld` | ELD統合ワークフロー |
| `eld-debug` | Law視点でバグを分析・修正 |

### Sense（感知）
| スキル | 説明 |
|--------|------|
| `eld-sense-activation` | アクティブコンテキスト構築 |
| `eld-sense-planning` | タスク分解・並列実行最適化 |
| `eld-sense-requirements-brainstorming` | 要件の曖昧さを対話的に明確化 |

### Spec（仕様化）← 旧Model
| スキル | 説明 |
|--------|------|
| `eld-spec` | Spec発見+Card化+LinkMap（旧eld-model） |
| `eld-spec-discover` | Law/Term候補の発見（旧eld-model-law-discovery） |
| `eld-spec-card` | Law/Term Cardの作成（旧law-card+term-card統合） |
| `eld-spec-link` | Law↔Term連結表管理（旧eld-model-link-map） |

### Consistency（整合性検査）
| スキル | 説明 |
|--------|------|
| `eld-counterexample-consistency` | 反例駆動で要件、形式仕様、テスト、コード、実行時観測の多層整合性を検査 |

### Predict-Light（予測ゲート）← 旧Predict
| スキル | 説明 |
|--------|------|
| `eld-predict-light` | P0/P1/P2段階化ゲート（旧eld-predict-impact） |

### Change（変更）
| スキル | 説明 |
|--------|------|
| `eld-change-worktree` | 高リスク変更時にgit worktreeで隔離環境を作成 |

### Ground（接地）
| スキル | 説明 |
|--------|------|
| `eld-ground` | 接地検証+PRレビュー統合。2軸（Evidence Level × Evaluator Quality） |
| `eld-ground-tdd-enforcer` | TDDサイクル強制とL1達成 |
| `eld-ground-law-monitor` | 本番でのLaw違反監視 |

### Record（記録）
| スキル | 説明 |
|--------|------|
| `eld-record` | Context Delta収集・検証・構造化・知識移転 |

### 後方互換エイリアス（8エイリアス）
| エイリアス | 転送先 |
|------------|--------|
| `eld-model` | → `/eld-spec` |
| `eld-model-law-card` | → `/eld-spec-card law` |
| `eld-model-term-card` | → `/eld-spec-card term` |
| `eld-model-law-discovery` | → `/eld-spec-discover` |
| `eld-model-link-map` | → `/eld-spec-link` |
| `eld-ground-pr-review` | → `/eld-ground review` |
| `eld-ground-verify` | → `/eld-ground verify` |
| `eld-predict-impact` | → `/eld-predict-light` |

## エージェント（6エージェント）

| エージェント | 責務 |
|-------------|------|
| `pce-lde-orchestrator` | ELDワークフロー統合オーケストレータ（Issue→PR→Record） |
| `law-constraint-analyst` | Law候補の発見・分類・Card化 |
| `vocabulary-term-analyst` | Term発見・Card化 |
| `mutual-constraint-validator` | Law↔Termの相互拘束検証 |
| `grounding-verifier` | 2軸接地検証（Evidence Level × Evaluator Quality） |
| `pce-knowledge-architect` | 知識の収集・構造化・文書化 |

## クロスプラグイン依存

- **delivery-plugin** が本プラグインの `/eld`, `/eld-sense-*`, `/eld-ground-pr-review`（→`/eld-ground review`エイリアス）, `/eld-model`（→`/eld-spec`エイリアス）を参照します。delivery-pluginとの併用を推奨します。
- **codex-plugin** の `pce-lde-orchestrator` エージェントが `/codex-consultant`, `/codex-negotiation` を使用します。codex-pluginとの併用を推奨します。

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/eld-plugin"
  ]
}
```
