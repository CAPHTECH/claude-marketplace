# CodeRabbit 主要設定オプションリファレンス

公式ドキュメント（網羅的な最新情報）: https://docs.coderabbit.ai/reference/configuration

## TOC

- [トップレベル](#トップレベル)
- [reviews](#reviews)
- [reviews.auto_review](#reviewsauto_review)
- [reviews.finishing_touches](#reviewsfinishing_touches)
- [reviews.pre_merge_checks](#reviewspre_merge_checks)
- [reviews.tools](#reviewstools)
- [chat](#chat)
- [knowledge_base](#knowledge_base)
- [code_generation](#code_generation)
- [issue_enrichment](#issue_enrichment)

## トップレベル

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `language` | string | `"en-US"` | レビュー言語（ISO code: ja, en-US, de, fr等） |
| `tone_instructions` | string | `""` | レビューのトーン指示（最大250文字） |
| `early_access` | bool | `false` | 実験的機能の有効化 |
| `enable_free_tier` | bool | `true` | 無料枠の機能を許可 |

## reviews

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `profile` | string | `"chill"` | `chill`（穏やか）/ `assertive`（厳格） |
| `request_changes_workflow` | bool | `false` | 問題解決後の自動承認 |
| `high_level_summary` | bool | `true` | PR概要を自動生成 |
| `high_level_summary_instructions` | string | `""` | サマリーのカスタム指示 |
| `high_level_summary_placeholder` | string | `"@coderabbitai summary"` | サマリー埋め込み位置 |
| `high_level_summary_in_walkthrough` | bool | `false` | サマリーをウォークスルー内に配置 |
| `auto_title_placeholder` | string | `"@coderabbitai"` | タイトル自動生成のプレースホルダ |
| `auto_title_instructions` | string | `""` | タイトル生成のカスタム指示 |
| `review_status` | bool | `true` | レビューステータスの投稿 |
| `review_details` | bool | `false` | 無視ファイル・コンテキスト詳細 |
| `collapse_walkthrough` | bool | `true` | ウォークスルーを折りたたみ |
| `commit_status` | bool | `true` | コミットステータスの設定 |
| `fail_commit_status` | bool | `false` | 失敗レビューをステータスに反映 |
| `changed_files_summary` | bool | `true` | 変更ファイル一覧 |
| `sequence_diagrams` | bool | `true` | シーケンス図生成 |
| `estimate_code_review_effort` | bool | `true` | レビュー工数見積 |
| `assess_linked_issues` | bool | `true` | リンクIssueの整合性チェック |
| `related_issues` | bool | `true` | 関連Issue提案 |
| `related_prs` | bool | `true` | 関連PR提案 |
| `suggested_labels` | bool | `true` | ラベル提案 |
| `suggested_reviewers` | bool | `true` | レビュアー提案 |
| `auto_apply_labels` | bool | `false` | ラベル自動適用 |
| `auto_assign_reviewers` | bool | `false` | レビュアー自動割当 |
| `in_progress_fortune` | bool | `true` | レビュー中のメッセージ |
| `poem` | bool | `true` | ポエム生成 |
| `enable_prompt_for_ai_agents` | bool | `true` | AIエージェント用プロンプト |
| `abort_on_close` | bool | `true` | PR閉鎖時にレビュー中断 |
| `disable_cache` | bool | `false` | キャッシュ無効化 |
| `path_filters` | string[] | `[]` | globパターン（`!`で除外） |
| `path_instructions` | array | `[]` | パス別レビュー指示 |
| `labeling_instructions` | array | `[]` | ラベル付けルール |

### path_instructions エントリ

```yaml
path_instructions:
  - path: "**/*.ts"        # glob パターン
    instructions: |        # レビュー指示（具体的に）
      型安全性を確認。any型は代替を提案。
```

### labeling_instructions エントリ

```yaml
labeling_instructions:
  - label: "frontend"
    instructions: "Reactコンポーネント変更時に適用"
```

## reviews.auto_review

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `enabled` | bool | `true` | 自動レビュー有効化 |
| `description_keyword` | string | `""` | トリガーキーワード |
| `auto_incremental_review` | bool | `true` | push毎のインクリメンタルレビュー |
| `auto_pause_after_reviewed_commits` | int | `5` | N コミット後に一旦停止 |
| `ignore_title_keywords` | string[] | `[]` | タイトルに含む場合スキップ |
| `labels` | string[] | `[]` | レビュー制御ラベル（`!`で除外） |
| `drafts` | bool | `false` | ドラフトPRを含む |
| `base_branches` | string[] | `[]` | 対象ブランチ（正規表現対応） |
| `ignore_usernames` | string[] | `[]` | スキップするユーザー |

## reviews.finishing_touches

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `docstrings.enabled` | bool | `true` | docstring生成 |
| `unit_tests.enabled` | bool | `true` | ユニットテスト生成 |
| `custom` | array | `[]` | カスタムレシピ（最大5） |

### custom エントリ

```yaml
reviews:
  finishing_touches:
    custom:
      - enabled: true
        name: "import整理"
        instructions: "未使用importを削除し、アルファベット順にソート"
```

## reviews.pre_merge_checks

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `docstrings.mode` | string | `"warning"` | `off` / `warning` / `error` |
| `docstrings.threshold` | number | `80` | 必要カバレッジ% |
| `title.mode` | string | `"warning"` | タイトル検証 |
| `title.requirements` | string | `""` | タイトルルール |
| `description.mode` | string | `"warning"` | 説明文検証 |
| `issue_assessment.mode` | string | `"warning"` | Issue整合性検証 |
| `custom_checks` | array | `[]` | カスタムチェック（最大5） |

### custom_checks エントリ

```yaml
reviews:
  pre_merge_checks:
    custom_checks:
      - mode: "error"
        name: "セキュリティ確認"
        instructions: "機密情報の露出がないこと"
```

## reviews.tools

多数の静的解析ツールが設定可能（最新の対応数は公式ドキュメント参照）。主要なもの:

| ツール | 対象言語 | デフォルト |
|--------|---------|-----------|
| `shellcheck` | Shell | `true` |
| `ruff` | Python | `true` |
| `markdownlint` | Markdown | `true` |
| `biome` | JS/TS | `true` |
| `eslint` | JS/TS | `true` |
| `pylint` | Python | `true` |
| `flake8` | Python | `true` |
| `golangci-lint` | Go | `true` |
| `hadolint` | Dockerfile | `true` |
| `languagetool` | 自然言語 | `true` |
| `github-checks` | CI連携 | `true` |
| `ast-grep` | 多言語 | カスタム |

各ツールの設定例:

```yaml
reviews:
  tools:
    eslint:
      enabled: true
    golangci-lint:
      enabled: true
      config_file: ".golangci.yml"
    languagetool:
      enabled: true
      disabled_categories:
        - TYPOS
        - CASING
    ast-grep:
      rule_dirs: []
      packages: []
      essential_rules: true
```

## chat

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `art` | bool | `true` | ASCII/絵文字アート |
| `auto_reply` | bool | `true` | メンション不要で返信 |
| `integrations.jira.usage` | string | `"auto"` | `auto`/`enabled`/`disabled` |
| `integrations.linear.usage` | string | `"auto"` | `auto`/`enabled`/`disabled` |

## knowledge_base

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `opt_out` | bool | `false` | データ保持機能の無効化 |
| `web_search.enabled` | bool | `true` | Web検索でコンテキスト補強 |
| `code_guidelines.enabled` | bool | `true` | コーディング規約の適用 |
| `code_guidelines.filePatterns` | string[] | `[]` | 規約ファイルのglobパターン |
| `learnings.scope` | string | `"auto"` | `local`/`global`/`auto` |
| `issues.scope` | string | `"auto"` | Issue参照スコープ |
| `pull_requests.scope` | string | `"auto"` | PR参照スコープ |
| `jira.usage` | string | `"auto"` | Jira連携 |
| `jira.project_keys` | string[] | `[]` | 対象プロジェクト |
| `linear.usage` | string | `"auto"` | Linear連携 |
| `linear.team_keys` | string[] | `[]` | 対象チーム |
| `mcp.usage` | string | `"auto"` | MCP連携 |
| `mcp.disabled_servers` | string[] | `[]` | 無効化するMCPサーバー |
| `linked_repositories` | array | `[]` | 関連リポジトリ |

### linked_repositories エントリ

```yaml
knowledge_base:
  linked_repositories:
    - repository: "org/backend-api"
      instructions: "REST APIエンドポイントの定義を含む"
```

## code_generation

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `docstrings.language` | string | `"en-US"` | docstring言語 |
| `docstrings.path_instructions` | array | `[]` | パス別docstring指示 |
| `unit_tests.path_instructions` | array | `[]` | パス別テスト生成指示 |

## issue_enrichment

| キー | 型 | デフォルト | 説明 |
|------|-----|-----------|------|
| `auto_enrich.enabled` | bool | `false` | Issue自動エンリッチ |
| `planning.enabled` | bool | `true` | 実装計画の生成 |
| `planning.auto_planning.enabled` | bool | `true` | 自動計画 |
| `planning.auto_planning.labels` | string[] | `[]` | トリガーラベル |
| `labeling.labeling_instructions` | array | `[]` | Issue用ラベル付けルール |
| `labeling.auto_apply_labels` | bool | `false` | ラベル自動適用 |
