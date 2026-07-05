# Meta Plugin (CLAUDE.md & Skill Development)

CLAUDE.md管理とスキル開発を支援するメタツールプラグインです。

## スキル一覧（3スキル）

### Skill Development
| スキル | 説明 |
|--------|------|
| `skill-creator` | Claude Code用Skillの設計・実装・検証ガイド |

### CLAUDE.md & Settings Management
| スキル | 説明 |
|--------|------|
| `permission-promoter` | settings.local.jsonのpermissions.allowから安全なコマンドをsettings.jsonへ昇格 |
| `secret-boundary` | AI実行環境のシークレット境界設定（permissions.denyルールの生成） |

## インストール

```json
{
  "plugins": [
    "/path/to/claude-marketplace/meta-plugin"
  ]
}
```
