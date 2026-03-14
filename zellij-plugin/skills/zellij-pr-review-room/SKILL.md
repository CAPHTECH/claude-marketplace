---
name: zellij-pr-review-room
description: PR番号を指定してレビュー用worktreeとzellijレイアウトを構築する。「PRをレビューして」「PR #123のレビュー環境を作って」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<pr-number>"
---

# zellij-pr-review-room

PR専用のレビュー環境をzellij上に構築する。

## 概要

```
<pr-number> → gh pr view → worktree作成 → zellijレイアウト構築 → レビュー情報表示
```

## 前提チェック

スキル実行前に以下を確認:
1. gitリポジトリ内か
2. `gh` CLIが利用可能か
3. `zellij` セッション内か（`$ZELLIJ` 変数の存在）— 非zellij時はPR情報の表示のみ

```bash
# 前提チェック
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: gitリポジトリ内で実行してください"
  exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLIがインストールされていません"
  exit 1
fi
```

## メインリポジトリの特定

```bash
COMMON_DIR=$(cd "$(git rev-parse --git-common-dir)" && pwd)
ABS_GIT_DIR=$(cd "$(git rev-parse --absolute-git-dir)" && pwd)
if [ "$COMMON_DIR" != "$ABS_GIT_DIR" ]; then
  REPO_ROOT=$(dirname "$COMMON_DIR")
else
  REPO_ROOT=$(git rev-parse --show-toplevel)
fi
REPO_NAME=$(basename "$REPO_ROOT")
```

## 手順

### 1. PR情報の取得

```bash
PR_NUMBER="$1"  # 引数から取得。未指定なら質問する
if [ -z "$PR_NUMBER" ] || ! echo "$PR_NUMBER" | grep -qE '^[0-9]+$'; then
  echo "Error: 有効なPR番号を指定してください（例: 123）"
  exit 1
fi

# PR情報をJSON形式で取得
PR_JSON=$(gh pr view "$PR_NUMBER" --json title,headRefName,baseRefName,files,body,author,url)
PR_TITLE=$(echo "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")
PR_BRANCH=$(echo "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['headRefName'])")
PR_BASE=$(echo "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['baseRefName'])")
PR_URL=$(echo "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])")

# 変更ファイル一覧
CHANGED_FILES=$(echo "$PR_JSON" | python3 -c "
import sys, json
files = json.load(sys.stdin)['files']
for f in files:
    print(f'{f[\"additions\"]:+d}/{f[\"deletions\"]:+d}\t{f[\"path\"]}')
")
```

### 2. worktreeの作成

zellij-worktreeスキルと同等のロジックでworktreeを作成する。

```bash
WORKTREE_BASE="${CLAUDE_WORKTREE_DIR:-$(dirname "$REPO_ROOT")/${REPO_NAME}.worktrees}"

# ブランチ名からworktreeパスを逆引き
find_worktree_by_branch() {
  git worktree list --porcelain | awk -v branch="$1" '
    /^worktree / { path = substr($0, 10) }
    /^branch refs\/heads\// {
      b = substr($0, 19)
      if (b == branch) { print path; exit }
    }
  '
}

EXISTING_PATH=$(find_worktree_by_branch "$PR_BRANCH")
if [ -n "$EXISTING_PATH" ]; then
  WORKTREE_PATH="$EXISTING_PATH"
else
  # slug生成
  BRANCH_HASH=$(printf '%s' "$PR_BRANCH" | shasum | cut -c1-6)
  BRANCH_SLUG=$(printf '%s' "$PR_BRANCH" | sed 's/[^A-Za-z0-9._-]/-/g; s/--*/-/g; s/^-//; s/-$//' | cut -c1-60)
  case "$BRANCH_SLUG" in
    ""|"."|"..") BRANCH_SLUG="branch" ;;
  esac
  BRANCH_SLUG="${BRANCH_SLUG}-${BRANCH_HASH}"
  WORKTREE_PATH="${WORKTREE_BASE}/${BRANCH_SLUG}"

  # 書き込み権限チェック + フォールバック
  if ! mkdir -p "${WORKTREE_BASE}" 2>/dev/null; then
    WORKTREE_BASE="${TMPDIR:-/tmp}/${REPO_NAME}.worktrees"
    WORKTREE_PATH="${WORKTREE_BASE}/${BRANCH_SLUG}"
    mkdir -p "${WORKTREE_BASE}"
  fi

  # リモートブランチをfetch
  git fetch origin "$PR_BRANCH" 2>/dev/null || true

  if git show-ref --verify --quiet "refs/heads/${PR_BRANCH}"; then
    git worktree add "${WORKTREE_PATH}" "${PR_BRANCH}"
  elif REMOTE_REF=$(git branch -r --list "*/${PR_BRANCH}" | head -1 | xargs); [ -n "$REMOTE_REF" ]; then
    git worktree add --track -b "${PR_BRANCH}" "${WORKTREE_PATH}" "$REMOTE_REF"
  else
    echo "Error: ブランチ '${PR_BRANCH}' が見つかりません"
    exit 1
  fi
fi
```

### 3. zellijレイアウト構築

```bash
if [ -n "$ZELLIJ" ]; then
  # worktree deleteとの整合性のため、タブ名はworktreeディレクトリのbasenameを使用
  TAB_NAME=$(basename "${WORKTREE_PATH}")

  # 既存タブがあればそこに移動、なければ新規作成
  if ! zellij action go-to-tab-name "${TAB_NAME}" 2>/dev/null; then
    zellij action new-tab --name "${TAB_NAME}" --cwd "${WORKTREE_PATH}"
  fi

  # diff表示pane（下部）— --cwdでworktreeを指定し、shell injection を回避
  SAFE_BASE=$(printf '%q' "$PR_BASE")
  SAFE_HEAD=$(printf '%q' "$PR_BRANCH")
  zellij run --direction down --cwd "${WORKTREE_PATH}" -- \
    bash -c "git diff ${SAFE_BASE}...${SAFE_HEAD} --stat; echo '---'; echo 'Press Enter to exit'; read"

  # メインpaneにフォーカス
  zellij action focus-previous-pane
else
  echo "Worktree created: ${WORKTREE_PATH}"
  echo "cd ${WORKTREE_PATH}"
fi
```

### 4. レビュー情報の表示

zellijレイアウト構築後、以下の情報をClaudeが表示する:

```
PR #<number>: <title>
URL: <url>
Branch: <head> → <base>

変更ファイル:
<additions/deletions  filepath>

レビュー推奨順序とリスク分析をClaudeが提案する。
```

変更ファイルのリスク分析基準:
- 変更行数が多いファイル → 高リスク
- 設定ファイル・マイグレーション → 高リスク
- テストファイル → 低リスク
- ファイルの依存関係（import先が多いファイルは影響範囲が広い）

## クリーンアップ

レビュー完了後は `zellij-worktree delete <branch>` と同等の操作で環境を削除する。

## エラーハンドリング

- PR番号が無効: `gh pr view` のエラーメッセージを表示
- ブランチ取得失敗: fetchリトライ後にエラー表示
- zellij非実行時: worktree作成とPR情報表示のみ行う
