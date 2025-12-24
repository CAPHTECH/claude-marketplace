# Repository Guidelines

## Project Structure & Module Organization
このリポジトリはClaude Code向けプラグイン/スキルの配布リポジトリです。
- `caphtech-plugin/`: 主力プラグイン。`skills/<skill>/SKILL.md`がソース、`*.skill`が配布アーカイブ。`agents/`にエージェント定義、`commands/`と`hooks/`は予約枠。
- `webapp-dev-plugin/`: Webアプリ開発支援。`skills/webapp-debugger/`と`webapp-debugger.skill`を同梱。
- `.claude-plugin/marketplace.json`: マーケットプレイス登録情報。新規プラグイン追加時に更新。

## Build, Test, and Development Commands
現状、公式のビルド/テスト/実行コマンドは定義されていません。変更後は以下の軽量チェックを推奨します。
- `rg -n "^name:|^description:" caphtech-plugin/skills webapp-dev-plugin/skills`（SKILL.mdのフロントマター確認）
- `rg -n "references/.*\\.md" -g "SKILL.md"`（参照リンクの棚卸し）

## Coding Style & Naming Conventions
- `SKILL.md`はYAMLフロントマター（`name`, `description`）を先頭に置く。インデントは2スペース。
- `skills/<skill>/`のディレクトリ名と`name`はkebab-caseで一致させる。
- `.skill`は配布アーカイブのため直接編集しない。

## Testing Guidelines
自動テストは未整備。変更時は対象SKILLの手順・サンプル・リンクが成立しているかを目視で確認する。

## Commit & Pull Request Guidelines
- コミットは命令形の短い要約が主流（例: “Add …”, “Fix …”, “Update …”）。
- PRには変更目的、影響するスキル/エージェント、`.skill`再生成の有無、`marketplace.json`更新有無を明記する。

## Security & Configuration Tips
- `marketplace.json`に新規プラグインを追加する際は`name/source/version`を揃える。
- スキル本文に機密情報や実運用の秘密鍵を含めない。
