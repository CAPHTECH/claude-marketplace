---
name: tmux-issue-room
description: Issue番号を指定してworktreeとtmux開発環境を構築する。「Issueに取り組んで」「Issue #45の作業環境を作って」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<issue-number>"
---

# tmux-issue-room

Issue専用の開発環境をtmux上に構築する。

## 概要

```
<issue-number> → gh issue view → ブランチ名生成 → worktree作成 → tmuxレイアウト構築
```

## 前提チェック

スキル実行前に以下を確認:
1. gitリポジトリ内か
2. `gh` CLIが利用可能か
3. `tmux` セッション内か（`$TMUX` 変数の存在）— 非tmux時はworktree作成とパス出力のみ

```bash
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

### 1. Issue情報の取得

```bash
ISSUE_NUMBER="$1"  # 引数から取得。未指定なら質問する
if [ -z "$ISSUE_NUMBER" ] || ! echo "$ISSUE_NUMBER" | grep -qE '^[0-9]+$'; then
  echo "Error: 有効なIssue番号を指定してください（例: 45）"
  exit 1
fi

# Issue情報をJSON形式で取得
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" --json title,body,labels,assignees,url)
ISSUE_TITLE=$(echo "$ISSUE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")
ISSUE_URL=$(echo "$ISSUE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])")
ISSUE_LABELS=$(echo "$ISSUE_JSON" | python3 -c "
import sys, json
labels = json.load(sys.stdin).get('labels', [])
print(', '.join(l['name'] for l in labels)) if labels else print('none')
")
```

### 2. ブランチ名の生成

```bash
# タイトルからslugを生成
TITLE_SLUG=$(printf '%s' "$ISSUE_TITLE" | \
  tr '[:upper:]' '[:lower:]' | \
  sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//' | \
  cut -c1-40)
BRANCH="issue-${ISSUE_NUMBER}-${TITLE_SLUG}"
```

### 3. worktreeの作成

tmux-worktreeスキルと同等のロジック。

```bash
WORKTREE_BASE="${CLAUDE_WORKTREE_DIR:-$(dirname "$REPO_ROOT")/${REPO_NAME}.worktrees}"

find_worktree_by_branch() {
  git worktree list --porcelain | awk -v branch="$1" '
    /^worktree / { path = substr($0, 10) }
    /^branch refs\/heads\// {
      b = substr($0, 19)
      if (b == branch) { print path; exit }
    }
  '
}

EXISTING_PATH=$(find_worktree_by_branch "$BRANCH")
if [ -n "$EXISTING_PATH" ]; then
  WORKTREE_PATH="$EXISTING_PATH"
  echo "既存のworktreeを使用: ${WORKTREE_PATH}"
else
  BRANCH_HASH=$(printf '%s' "$BRANCH" | shasum | cut -c1-6)
  BRANCH_SLUG=$(printf '%s' "$BRANCH" | sed 's/[^A-Za-z0-9._-]/-/g; s/--*/-/g; s/^-//; s/-$//' | cut -c1-60)
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

  # デフォルトブランチから分岐
  DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
  if [ -z "$DEFAULT_BRANCH" ]; then
    DEFAULT_BRANCH="main"
  fi

  git worktree add -b "${BRANCH}" "${WORKTREE_PATH}" "${DEFAULT_BRANCH}"
fi
```

### 4. tmuxレイアウト構築

```bash
if [ -n "$TMUX" ]; then
  WINDOW_NAME="issue-${ISSUE_NUMBER}"

  # メインpane: worktreeディレクトリで開く
  tmux new-window -n "${WINDOW_NAME}" -c "${WORKTREE_PATH}"
else
  echo "Worktree created: ${WORKTREE_PATH}"
  echo "cd ${WORKTREE_PATH}"
fi
```

### 5. 開発情報の表示

tmuxレイアウト構築後、以下を表示する:

```
Issue #<number>: <title>
URL: <url>
Labels: <labels>
Branch: <branch>
Worktree: <path>
```

Claudeがプロジェクト構造を分析し、Issue内容に関連するファイルを特定して提示する。

## クリーンアップ

作業完了後は `tmux-worktree delete <branch>` と同等の操作で環境を削除する。

## エラーハンドリング

- Issue番号が無効: `gh issue view` のエラーメッセージを表示
- ブランチ名衝突: 既存worktreeが見つかった場合はそれを使用
- tmux非実行時: worktree作成とIssue情報表示のみ行う
