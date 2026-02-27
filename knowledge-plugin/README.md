# Knowledge Plugin (Architecture, Docs, Research)

アーキテクチャレビュー、ドキュメント生成、情報収集を提供するプラグインです。

## スキル一覧（10スキル）

### Architecture Review
| スキル | 説明 |
|--------|------|
| `system-understanding` | システムマップ収集・不変条件抽出・コンポーネントカード作成 |
| `architecture-reviewer` | 3種類の分析（ノード/エッジ/縦串）＋矛盾検出＋優先順位付け |
| `review-report-generator` | 意思決定用レポート生成 |
| `synthesis-analyzer` | 統合分析 |

### Documentation & Specification
| スキル | 説明 |
|--------|------|
| `doc-gen` | 根拠に基づく開発者向けドキュメント生成 |
| `spec-gen` | コードからAs-Is spec（現状仕様）を抽出 |
| `technical-book-writer` | Markdown形式の技術書執筆支援 |

### Research & Investigation
| スキル | 説明 |
|--------|------|
| `info-gathering` | 技術・一般情報の体系的収集（統合版） |
| `general-info-gathering` | 一般分野の情報収集に特化 |
| `tech-info-gathering` | 技術分野の情報収集に特化 |

## エージェント（2エージェント）

| エージェント | 責務 |
|-------------|------|
| `architecture-knowledge-builder` | Phase 1-3の知識構築（システムマップ→不変条件→コンポーネントカード） |
| `architecture-analysis-reporter` | Phase 4-6の分析・報告（3種類分析→矛盾検出→レポート生成） |

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/knowledge-plugin"
  ]
}
```
