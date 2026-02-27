# ELD Plugin (Evidence-Loop Development)

証拠で回す統合開発手法 ELD のコアプラグイン。Law/Termモデリング、影響予測、接地検証、知識管理を提供します。

## ELD統合ループ

```
Sense → Model → Predict → Change → Ground → Record
  ↑                                            ↓
  └──────────────── 循環 ←─────────────────────┘
```

## スキル一覧（20スキル）

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

### Model（モデル化）
| スキル | 説明 |
|--------|------|
| `eld-model` | Law/Term候補の発見・Card作成 |
| `eld-model-law-discovery` | Law候補の発見 |
| `eld-model-law-card` | Law Cardの作成 |
| `eld-model-term-card` | Term Cardの作成 |
| `eld-model-link-map` | Law↔Term連結表管理 |

### Predict（予測）
| スキル | 説明 |
|--------|------|
| `eld-predict-impact` | 影響を因果タイプで分類し段階化戦略を確定 |

### Change（変更）
| スキル | 説明 |
|--------|------|
| `eld-change-worktree` | 高リスク変更時にgit worktreeで隔離環境を作成 |

### Ground（接地）
| スキル | 説明 |
|--------|------|
| `eld-ground-verify` | 接地状況の検証・Evidence Pack評価 |
| `eld-ground-tdd-enforcer` | TDDサイクル強制とL1達成 |
| `eld-ground-pr-review` | PRレビュー |
| `eld-ground-law-monitor` | 本番でのLaw違反監視 |

### Record（記録）
| スキル | 説明 |
|--------|------|
| `eld-record` | Context Delta収集・知識の構造化・メモリ収集 |
| `eld-record-compact` | 履歴圧縮 |
| `eld-record-maintenance` | 知識メンテナンス |

### Knowledge
| スキル | 説明 |
|--------|------|
| `knowledge-validator` | pce-memory活用の知識検証・整合性チェック |

## エージェント（8エージェント）

| エージェント | 責務 |
|-------------|------|
| `pce-lde-orchestrator` | PCE/LDE統合開発フロー全体の調整 |
| `law-constraint-analyst` | Law候補の発見・分類・Card化 |
| `vocabulary-term-analyst` | Term発見・Card化 |
| `mutual-constraint-validator` | Law↔Termの相互拘束検証 |
| `grounding-verifier` | Law/Termの検証手段・観測手段の検証 |
| `pce-memory-orchestrator` | セッション間の知識永続化 |
| `pce-memory-analyzer` | メモリの分析・インサイト抽出 |
| `pce-knowledge-architect` | 知識の収集・構造化・文書化 |

## クロスプラグイン依存

- **delivery-plugin** が本プラグインの `/eld`, `/eld-sense-*`, `/eld-ground-pr-review` を参照します。delivery-pluginとの併用を推奨します。

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/eld-plugin"
  ]
}
```
