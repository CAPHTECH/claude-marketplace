# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Claude Code向けプラグイン/スキルのマーケットプレイスリポジトリ。9つのプラグインを配布。

## Architecture

### Plugin Structure
```
<plugin>/
├── .claude-plugin/plugin.json   # プラグインマニフェスト（version等）
├── skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md             # スキル本体（YAMLフロントマター + 手順）
│   │   └── references/          # 詳細リファレンス（オプション）
│   └── <skill-name>.skill       # 配布用zipアーカイブ
├── agents/                      # エージェント定義（YAML）
├── commands/                    # 予約枠
└── hooks/                       # 予約枠
```

### Version Management (重要)
バージョンは**2箇所で管理**され、変更時は必ず両方を同時に更新すること:
- `.claude-plugin/marketplace.json` — マーケットプレイス登録
- `<plugin>/.claude-plugin/plugin.json` — プラグインマニフェスト（`/plugin`コマンドはこちらを参照）

### Skill Archive (.skill)
`.skill`ファイルはzipアーカイブ。直接編集しない。ソースは`skills/<name>/SKILL.md`。
```bash
# 生成
cd <plugin>/skills/<skill-name> && zip -r ../<skill-name>.skill . -x '.*'
```

## Development Commands

### Validation
```bash
# スキル構造の検証
python3 meta-plugin/skills/skill-creator/scripts/validate_skill.py <skill-folder>

# フロントマター確認
rg -n "^name:|^description:" */skills/*/SKILL.md

# 参照リンク棚卸し
rg -n "references/.*\.md" -g "SKILL.md"

# 全プラグインのバージョン整合性チェック
for d in *-plugin; do
  pv=$(python3 -c "import json; print(json.load(open('$d/.claude-plugin/plugin.json'))['version'])")
  mv=$(python3 -c "import json; ps=json.load(open('.claude-plugin/marketplace.json'))['plugins']; print(next((p['version'] for p in ps if p['name']=='$d'), 'N/A'))")
  echo "$d: plugin=$pv marketplace=$mv $([ "$pv" = "$mv" ] && echo OK || echo MISMATCH)"
done
```

## Conventions

### SKILL.md
- YAMLフロントマター必須: `name`, `context`, `description`（1行、YAML multiline `>` や `<`/`>` 禁止）
- ディレクトリ名とフロントマター`name`はkebab-caseで一致
- references/へのリンクはバッククォートで囲まない（validate_skill.pyの正規表現が`references/file.md`を直接検出）
- SKILL.md本体は500行以下推奨。詳細はreferences/に分離

### Commits
- 命令形の短い要約（例: "Add ...", "Fix ...", "Update ..."）
- PRには変更目的、影響するスキル/エージェント、`.skill`再生成の有無、バージョン更新有無を明記

### New Plugin Checklist
1. `<plugin>/.claude-plugin/plugin.json` 作成
2. `.claude-plugin/marketplace.json` にエントリ追加（name/source/version一致）
3. スキルごとにSKILL.md作成 → validate → .skill生成
