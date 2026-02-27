# Repository Guidelines

## Project Structure & Module Organization
このリポジトリはClaude Code向けプラグイン/スキルの配布リポジトリです。
- `eld-plugin/`: ELD（Evidence-Loop Development）プラグイン。Law/Termモデリング、影響予測、接地検証、知識管理。20スキル、8エージェント。
- `delivery-plugin/`: 開発ワークフロープラグイン。Issue管理、PRワークフロー、観測、テスト設計、コードレビュー。22スキル、4エージェント。
- `knowledge-plugin/`: アーキテクチャ・ドキュメント・リサーチプラグイン。10スキル、2エージェント。
- `creator-plugin/`: デザイン・メタツールプラグイン。アプリデザイン、CLAUDE.md管理、スキル作成。7スキル。
- `webapp-dev-plugin/`: Webアプリ開発支援。`skills/webapp-debugger/`と`webapp-debugger.skill`を同梱。
- `codex-plugin/`: OpenAI Codex連携。セカンドオピニオン・ペアプログラミング・構造化議論。
- `apple-platform-plugin/`: Apple Platform開発支援。
- `.claude-plugin/marketplace.json`: マーケットプレイス登録情報。新規プラグイン追加時に更新。

各プラグインの構造: `skills/<skill>/SKILL.md`がソース、`*.skill`が配布アーカイブ。`agents/`にエージェント定義、`commands/`と`hooks/`は予約枠。

## Build, Test, and Development Commands
現状、公式のビルド/テスト/実行コマンドは定義されていません。変更後は以下の軽量チェックを推奨します。
- `rg -n "^name:|^description:" eld-plugin/skills delivery-plugin/skills knowledge-plugin/skills creator-plugin/skills`（SKILL.mdのフロントマター確認）
- `rg -n "references/.*\.md" -g "SKILL.md"`（参照リンクの棚卸し）

## Coding Style & Naming Conventions
- `SKILL.md`はYAMLフロントマター（`name`, `description`）を先頭に置く。インデントは2スペース。
- `skills/<skill>/`のディレクトリ名と`name`はkebab-caseで一致させる。
- `.skill`は配布アーカイブのため直接編集しない。

## Testing Guidelines
自動テストは未整備。変更時は対象SKILLの手順・サンプル・リンクが成立しているかを目視で確認する。

## Commit & Pull Request Guidelines
- コミットは命令形の短い要約が主流（例: "Add …", "Fix …", "Update …"）。
- PRには変更目的、影響するスキル/エージェント、`.skill`再生成の有無、`marketplace.json`更新有無を明記する。

## Security & Configuration Tips
- `marketplace.json`に新規プラグインを追加する際は`name/source/version`を揃える。
- スキル本文に機密情報や実運用の秘密鍵を含めない。
