# Delivery Plugin (Development Workflow)

Issue管理、PRワークフロー、観測、テスト設計、コードレビューを提供する開発ワークフロープラグインです。

## スキル一覧（22スキル）

### Issue Workflow
| スキル | 説明 |
|--------|------|
| `issue-intake` | Issue初期トリアージ（分類・深刻度・不確実性フラグ） |
| `issue-workflow-orchestrator` | Issue→PR完了のワークフロー制御 |
| `impact-analysis` | コード変更の影響範囲分析（8影響面） |

### Onboarding & Context
| スキル | 説明 |
|--------|------|
| `ai-led-onboarding` | AI主導の作業開始オンボーディング |
| `uncertainty-resolution` | 不確実性の解消・検証済み仮説のLaw昇格 |

### PR Workflow
| スキル | 説明 |
|--------|------|
| `pr-comment-resolver` | PRコメントの収集・分類・対応実行 |
| `pr-ci-responder` | PRのCI失敗を自動診断・修正 |
| `pr-onboarding` | PR作成時のオンボーディング記述 |

### Observation（観測）
| スキル | 説明 |
|--------|------|
| `observation-minimum-set` | 最小観測セット（6失敗モードを網羅） |
| `spec-observation` | 仕様誤解の早期発見 |
| `boundary-observation` | 境界条件・エッジケースの観測 |
| `dependency-observation` | 依存関係の観測 |
| `security-observation` | セキュリティ観測 |
| `concurrency-observation` | 並行性の観測 |
| `operability-observation` | 運用観測性の確保 |

### Testing & Quality
| スキル | 説明 |
|--------|------|
| `test-design-audit` | テスト設計監査（Law/Term駆動） |
| `systematic-test-design` | ユニットテスト＋PBTの体系的テスト設計 |
| `llm-eval-designer` | LLM生成システムの検証設計 |

### Code Review & Refactoring
| スキル | 説明 |
|--------|------|
| `critical-code-review` | 批判的コードレビュー |
| `refactoring` | リファクタリング機会の検出・安全な段階的実行 |
| `ai-readability-analysis` | AI可読性分析 |

### Project Management
| スキル | 説明 |
|--------|------|
| `github-project` | GitHub Projectの管理 |

## エージェント（4エージェント）

| エージェント | 責務 |
|-------------|------|
| `issue-workflow-orchestrator-agent` | Issue起点のワークフロー全体制御 |
| `observation-orchestrator` | 観測スキルの選択・実行 |
| `pr-comment-resolver-agent` | PRコメントの収集・分類・対応 |
| `pr-ci-responder` | CI失敗の自動診断・修正 |

## クロスプラグイン依存

- **eld-plugin** との併用を推奨。`issue-workflow-orchestrator` が `/eld`, `/eld-sense-*`, `/eld-ground-pr-review` を参照します。`test-design-audit` が Law/Term概念を参照します。

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/delivery-plugin"
  ]
}
```
