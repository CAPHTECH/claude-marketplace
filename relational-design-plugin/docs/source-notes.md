# Source Notes

この plugin は Claude Code Plugin の現行ドキュメントに合わせて、以下の実装上の前提を置いている。

- plugin manifest は `.claude-plugin/plugin.json` に置く。
- component directories は plugin root 直下に置く。
- skills は `skills/<skill-name>/SKILL.md` として配置する。
- agents は `agents/*.md` として配置する。
- hooks は `hooks/hooks.json` として配置する。
- plugin-shipped agents では `permissionMode` を使わない。
- hooks は command hook として stdin の JSON を読み、stdout に JSON を返す。
- PreToolUse の許可・拒否は `hookSpecificOutput.permissionDecision` を使う。

詳細は Claude Code Docs の Plugins reference / Hooks reference / Skills reference を参照。
