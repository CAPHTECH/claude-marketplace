---
name: github-project
context: fork
description: |
  GitHub Projectの管理スキル。ghコマンドを使用してプロジェクトの確認、アイテム追加・状態変更、フィールド更新を行う。

  トリガー条件:
  - 「Projectを確認して」「プロジェクトのアイテム一覧」「Project #N を見せて」
  - 「IssueをProjectに追加」「PRをProjectに紐付け」
  - 「ステータスをDoneに変更」「フィールドを更新」
  - 「カンバンを操作」「タスクの進捗を更新」
---

# GitHub Project Manager

ghコマンドでGitHub Projectを操作する。

## 前提条件

```bash
# projectスコープが必要
gh auth refresh -s project
```

## デフォルト設定

ユーザーがデフォルトプロジェクトを指定している場合、以下を使用:

```yaml
default_project:
  owner: "@me"  # または org/user名
  number: 1     # プロジェクト番号
```

指定がない場合は `gh project list` で選択を促す。

## 基本操作

### プロジェクト一覧・詳細

```bash
# 一覧
gh project list --owner "@me"

# 詳細（アイテム数、フィールド情報）
gh project view NUMBER --owner OWNER --format json
```

### アイテム一覧

```bash
gh project item-list NUMBER --owner OWNER --format json --limit 50
```

### アイテム追加

```bash
# Issue/PRを追加
gh project item-add NUMBER --owner OWNER --url ISSUE_OR_PR_URL

# ドラフトIssue作成
gh project item-create NUMBER --owner OWNER --title "タイトル" --body "本文"
```

### フィールド更新（重要）

フィールド更新には複数のIDが必要。詳細は [references/operations.md](references/operations.md) 参照。

```bash
# 1. フィールドID取得
gh project field-list NUMBER --owner OWNER --format json

# 2. アイテムID取得
gh project item-list NUMBER --owner OWNER --format json

# 3. プロジェクトID取得
gh project view NUMBER --owner OWNER --format json --jq '.id'

# 4. フィールド更新
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --single-select-option-id OPTION_ID  # Status等の場合
```

### アイテム削除・アーカイブ

```bash
# アーカイブ（非表示）
gh project item-archive NUMBER --owner OWNER --id ITEM_ID

# 削除
gh project item-delete NUMBER --owner OWNER --id ITEM_ID
```

## 典型的なワークフロー

### 1. ステータス変更（カンバン操作）

```bash
# フィールド情報を取得してStatusのoption_idを特定
gh project field-list NUMBER --owner OWNER --format json | jq '.fields[] | select(.name=="Status")'

# ステータス更新
gh project item-edit --id ITEM_ID --project-id PROJECT_ID --field-id FIELD_ID --single-select-option-id OPTION_ID
```

### 2. Issue作成と同時にProject追加

```bash
# Issue作成
gh issue create --title "タイトル" --body "本文" --repo OWNER/REPO

# Project追加
gh project item-add NUMBER --owner OWNER --url ISSUE_URL
```

## リファレンス

- [references/operations.md](references/operations.md) - 詳細な操作手順とID取得方法
