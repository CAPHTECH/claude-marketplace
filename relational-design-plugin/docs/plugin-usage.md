# Installation and Usage

## Local development install

Claude Code の plugin 読み込み方法はいくつかある。ローカル検証では、plugin directory として読み込む方法か、skills directory plugin として置く方法が扱いやすい。

例:

```bash
claude --plugin-dir /path/to/relational-design-plugin
```

または、個人の skills directory 配下に配置する。

```text
~/.claude/skills/relational-design-plugin/
  .claude-plugin/plugin.json
  skills/
  agents/
  hooks/
```

## Plugin reload

`SKILL.md` の変更は比較的反映されやすいが、agents / hooks / plugin manifest の変更は reload が必要になることがある。

```text
/reload-plugins
```

## First run

```text
/relational-design-plugin:design-trace
```

依頼例:

```text
Relational Design で、AI 駆動開発支援サービスの LP を設計して。
対象は技術責任者と事業責任者。速さだけでなく、制御可能性とガバナンスを伝えたい。
```

## Review run

```text
/relational-design-plugin:design-review
```

依頼例:

```text
この pricing page を Relational Design でレビューして。
見た目の好みではなく、ユーザー状態・信頼・行動リスク・情報密度から見て。
```

## Retraction run

```text
/relational-design-plugin:design-retract
```

依頼例:

```text
前提を変更する。主要ユーザーは CTO ではなく、非エンジニアの事業部長だった。
この変更で撤回すべき design decision と copy を分析して。
```

## Backflow run

```text
/relational-design-plugin:design-system-backflow
```

依頼例:

```text
この画面で作った UI パターンを design system に戻して。
tokens, components, interaction rules, copy rules に分けて。
```

## Advisory mode

hooks は advisory-only。

- trace がなくても編集は止まらない
- design-related edit を検出すると Claude へ trace reminder を注入する
- hook event metadata は `.relational-design/events/` に記録される

v0.1 に enforce モード（trace session がない場合に Write/Edit を拒否する）はない。

## Known limitations

- v0.1 は YAML / Markdown trace であり、依存関係の厳密なグラフ DB ではない。`trace-check.py` は ID の重複と `depends_on` 等の参照解決を検証するが、あくまで手動実行のテキストチェックであり、書き込み時に自動で強制されるものではない。
- hook の design-file 判定は heuristic である。
- Python 3 がない環境では hook scripts を調整する必要がある。
- Agent が作る trace は人間レビューを前提にしている。完全な自動統治ではない。
