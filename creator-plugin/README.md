# Creator Plugin (Design & Meta Tools)

アプリデザイン、CLAUDE.md管理、スキル作成を提供するデザイン・メタツールプラグインです。

## スキル一覧（7スキル）

### App Design
| スキル | 説明 |
|--------|------|
| `web-app-designer` | Webアプリのデザインを体系的に行う |
| `mobile-app-designer` | iOS/Androidアプリのデザイン（HIG/Material Design 3準拠） |
| `app-idea-workshop` | アプリアイデアを共創型インタビューで具体化 |

### CLAUDE.md Management
| スキル | 説明 |
|--------|------|
| `claude-md-customizer` | 対話形式でCLAUDE.mdをカスタマイズ |
| `claude-md-optimizer` | 既存CLAUDE.mdをベストプラクティスに基づいて分析・適正化 |

### Skill Development
| スキル | 説明 |
|--------|------|
| `skill-creator` | Claude Code用Skillの設計・実装・検証ガイド |
| `skill-extraction-finder` | プロジェクトからSkill化すべきドメイン知識を発見 |

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/creator-plugin"
  ]
}
```
