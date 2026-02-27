# ELD Plugin v2.3 (Evidence-Loop Development)

証拠で回す統合開発手法 ELD v2.3 のコアプラグイン。Spec駆動モデリング、Predict-Lightゲート、2軸接地検証、Context Engineering統合、知識管理を提供します。

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
- Context Engineering統合（動的メモリポリシー）
- Epistemic Status強化（自動降格、出典必須化）
- Review Hybrid導入

## スキル一覧（16 primary + 3 alias = 19）

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
| `eld-record` | Context Engineering統合。compact/maintenanceサブモード含む |

### Knowledge
| スキル | 説明 |
|--------|------|
| `knowledge-validator` | pce-memory活用の知識検証・整合性チェック |

### 後方互換エイリアス
| エイリアス | 転送先 | 理由 |
|------------|--------|------|
| `eld-model` | → `/eld-spec` | delivery-plugin互換 |
| `eld-ground-pr-review` | → `/eld-ground review` | delivery-plugin互換 |
| `eld-predict-impact` | → `/eld-predict-light` | 既存ユーザー互換 |

## エージェント（8エージェント）

| エージェント | 責務 |
|-------------|------|
| `pce-lde-orchestrator` | PCE/LDE統合開発フロー全体の調整 |
| `law-constraint-analyst` | Law候補の発見・分類・Card化 |
| `vocabulary-term-analyst` | Term発見・Card化 |
| `mutual-constraint-validator` | Law↔Termの相互拘束検証 |
| `grounding-verifier` | 2軸接地検証（Evidence Level × Evaluator Quality） |
| `pce-memory-orchestrator` | 3層メモリモデル+動的ポリシー |
| `pce-memory-analyzer` | メモリの分析・インサイト抽出 |
| `pce-knowledge-architect` | 知識の収集・構造化・文書化 |

## クロスプラグイン依存

- **delivery-plugin** が本プラグインの `/eld`, `/eld-sense-*`, `/eld-ground-pr-review`（→`/eld-ground review`エイリアス）, `/eld-model`（→`/eld-spec`エイリアス）を参照します。delivery-pluginとの併用を推奨します。

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/eld-plugin"
  ]
}
```
