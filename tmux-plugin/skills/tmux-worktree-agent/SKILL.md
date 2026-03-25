---
name: tmux-worktree-agent
description: worktreeとtmux windowを作成し、セットアップ後にclaude codeまたはcodexを起動して指示を送る。「worktreeでclaudeに作業させて」「worktreeでcodexに頼んで」「ブランチを切ってagentに任せて」「worktreeでagent起動して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<branch> [claude|codex] <instruction>"
---

# tmux-worktree-agent

worktreeとtmux windowを作成し、エージェント（claude/codex）を起動して指示を送る。

## 概要

```
<branch> [agent-type] <instruction>
  → worktree作成 → tmux window → セットアップ検出・実行 → エージェント起動 → 指示送信 → 送信確認
```

## 前提チェック

```bash
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: gitリポジトリ内で実行してください"; exit 1
fi
if [ -z "$TMUX" ]; then
  echo "Error: tmuxセッション内で実行してください"; exit 1
fi
```

エージェントCLIの存在確認:
```bash
# claude codeの場合
command -v claude >/dev/null 2>&1 || { echo "Error: claude CLIが見つかりません"; exit 1; }
# codexの場合
command -v codex >/dev/null 2>&1 || { echo "Error: codex CLIが見つかりません"; exit 1; }
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

### 1. 引数解析

```bash
BRANCH="$1"        # 必須: ブランチ名
AGENT_TYPE="$2"     # 任意: claude（デフォルト）| codex
INSTRUCTION="$3"    # 必須: エージェントへの指示

# AGENT_TYPEが省略され、$2が指示テキストの場合
if [ "$AGENT_TYPE" != "claude" ] && [ "$AGENT_TYPE" != "codex" ]; then
  INSTRUCTION="${AGENT_TYPE} ${INSTRUCTION}"
  AGENT_TYPE="claude"
fi
```

ブランチ名・指示が未指定なら質問する。

### 2. worktree作成

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

  if ! mkdir -p "${WORKTREE_BASE}" 2>/dev/null; then
    WORKTREE_BASE="${TMPDIR:-/tmp}/${REPO_NAME}.worktrees"
    WORKTREE_PATH="${WORKTREE_BASE}/${BRANCH_SLUG}"
    mkdir -p "${WORKTREE_BASE}"
  fi

  if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    git worktree add "${WORKTREE_PATH}" "${BRANCH}"
  elif REMOTE_REF=$(git branch -r --list "*/${BRANCH}" | head -1 | xargs); [ -n "$REMOTE_REF" ]; then
    git worktree add --track -b "${BRANCH}" "${WORKTREE_PATH}" "$REMOTE_REF"
  else
    git worktree add -b "${BRANCH}" "${WORKTREE_PATH}"
  fi
fi
```

### 3. tmux window作成

```bash
WINDOW_NAME="agent-$(basename "$WORKTREE_PATH")"
tmux new-window -n "${WINDOW_NAME}" -c "${WORKTREE_PATH}"
PANE="${WINDOW_NAME}.0"
```

### 4. セットアップコマンドの検出と実行

worktreeディレクトリ内のファイルを確認し、必要なセットアップコマンドを特定する。

```bash
SETUP_CMDS=""

# mise / asdf
if [ -f "${WORKTREE_PATH}/.mise.toml" ] || [ -f "${WORKTREE_PATH}/.mise/config.toml" ] || [ -f "${WORKTREE_PATH}/.tool-versions" ]; then
  if command -v mise >/dev/null 2>&1; then
    SETUP_CMDS="${SETUP_CMDS}mise trust -a && mise install && "
  fi
fi

# Node.js パッケージマネージャ
if [ -f "${WORKTREE_PATH}/package.json" ]; then
  if [ -f "${WORKTREE_PATH}/pnpm-lock.yaml" ]; then
    SETUP_CMDS="${SETUP_CMDS}pnpm install && "
  elif [ -f "${WORKTREE_PATH}/yarn.lock" ]; then
    SETUP_CMDS="${SETUP_CMDS}yarn install && "
  elif [ -f "${WORKTREE_PATH}/bun.lockb" ]; then
    SETUP_CMDS="${SETUP_CMDS}bun install && "
  elif [ -f "${WORKTREE_PATH}/package-lock.json" ]; then
    SETUP_CMDS="${SETUP_CMDS}npm install && "
  fi
fi

# Python
if [ -f "${WORKTREE_PATH}/pyproject.toml" ] || [ -f "${WORKTREE_PATH}/requirements.txt" ]; then
  if command -v uv >/dev/null 2>&1; then
    SETUP_CMDS="${SETUP_CMDS}uv sync && "
  elif [ -f "${WORKTREE_PATH}/poetry.lock" ]; then
    SETUP_CMDS="${SETUP_CMDS}poetry install && "
  elif [ -f "${WORKTREE_PATH}/requirements.txt" ]; then
    SETUP_CMDS="${SETUP_CMDS}pip install -r requirements.txt && "
  fi
fi

# Go
if [ -f "${WORKTREE_PATH}/go.mod" ]; then
  SETUP_CMDS="${SETUP_CMDS}go mod download && "
fi

# Rust
if [ -f "${WORKTREE_PATH}/Cargo.toml" ]; then
  SETUP_CMDS="${SETUP_CMDS}cargo fetch && "
fi

# Ruby
if [ -f "${WORKTREE_PATH}/Gemfile" ]; then
  SETUP_CMDS="${SETUP_CMDS}bundle install && "
fi
```

セットアップコマンドがある場合、pane内で実行し完了を待つ:

```bash
if [ -n "$SETUP_CMDS" ]; then
  # 末尾の " && " を除去
  SETUP_CMDS="${SETUP_CMDS% && }"
  MARKER="__SETUP_DONE_$$__"
  tmux send-keys -t "$PANE" "${SETUP_CMDS}; echo ${MARKER}" Enter

  # 完了待ち（最大5分）
  ELAPSED=0
  while [ $ELAPSED -lt 300 ]; do
    sleep 3
    if tmux capture-pane -t "$PANE" -p -S -50 | grep -qF "$MARKER"; then
      break
    fi
    ELAPSED=$((ELAPSED + 3))
  done

  if [ $ELAPSED -ge 300 ]; then
    echo "Warning: セットアップが5分以内に完了しませんでした。paneを確認してください。"
  fi
fi
```

### 5. エージェント起動と指示送信

**初回指示はCLI引数として渡す。** `tmux send-keys` でテキスト入力後にEnterを送ると、改行として解釈され送信されない場合があるため、CLI引数渡しが最も確実。

```bash
# 指示をtmpファイルに書き出し（長い指示・特殊文字のエスケープ問題を回避）
PROMPT_FILE=$(mktemp)
printf '%s' "$INSTRUCTION" > "$PROMPT_FILE"

case "$AGENT_TYPE" in
  claude)
    # cat経由で指示を渡し、シェルエスケープの問題を回避
    ESCAPED_FILE=$(printf '%q' "$PROMPT_FILE")
    tmux send-keys -t "$PANE" "claude \"\$(cat ${ESCAPED_FILE})\"" Enter
    ;;
  codex)
    ESCAPED_FILE=$(printf '%q' "$PROMPT_FILE")
    tmux send-keys -t "$PANE" "codex \"\$(cat ${ESCAPED_FILE})\"" Enter
    ;;
esac

# tmpファイルはエージェント起動後に削除（起動完了待ち後）
# verify_agent_running 後に rm -f "$PROMPT_FILE" を実行する
```

### 6. 送信確認

エージェント起動後、実際に指示が受理されたか確認する。

```bash
verify_agent_running() {
  local PANE="$1"
  local MAX_WAIT="${2:-30}"  # デフォルト30秒
  local ELAPSED=0

  while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep 3
    CONTENT=$(tmux capture-pane -t "$PANE" -p -S -20)

    # スピナー文字、ツール実行表示、処理中表示
    if echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏)'; then
      echo "確認: エージェントが指示を処理中（スピナー検出）"
      return 0
    fi

    # claude codeの特徴的な出力（ツール使用表示、ボックス描画）
    if echo "$CONTENT" | grep -qE '(╭─|╰─|│.*Tool|› )'; then
      echo "確認: エージェントが動作中"
      return 0
    fi

    # codexの特徴的な出力
    if echo "$CONTENT" | grep -qE '(Thinking|Working|Running|Executing)'; then
      echo "確認: エージェントが処理中"
      return 0
    fi

    ELAPSED=$((ELAPSED + 3))
  done

  echo "Warning: ${MAX_WAIT}秒以内にエージェントの動作を確認できませんでした"
  return 1
}

verify_agent_running "$PANE" 30

# tmpファイルを削除（エージェントが読み取り済み）
rm -f "$PROMPT_FILE"
```

確認できない場合、pane内容を `tmux capture-pane` で取得してユーザーに状況を報告する。

## 追加メッセージの送信

初回以降にエージェントへ追加指示を送る場合:

```bash
send_message_to_agent() {
  local PANE="$1"
  local MESSAGE="$2"

  # 1. テキストを送信（-l でリテラル送信、特殊文字を安全に処理）
  tmux send-keys -t "$PANE" -l "$MESSAGE"

  # 2. 間を空けてEnterで送信
  sleep 0.5
  tmux send-keys -t "$PANE" Enter

  # 3. 送信確認: pane内容をチェック
  sleep 3
  CONTENT=$(tmux capture-pane -t "$PANE" -p -S -10)

  # テキストがまだ入力欄に残っている場合 = 送信されていない
  # エージェントが処理中でなければ再送信を試みる
  if ! echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏|Thinking|thinking|Working)'; then
    echo "送信未確認。Enterを再送信..."
    tmux send-keys -t "$PANE" Enter
    sleep 3

    # 再確認
    CONTENT=$(tmux capture-pane -t "$PANE" -p -S -10)
    if echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏|Thinking|thinking|Working)'; then
      echo "再送信で送信確認"
    else
      echo "Warning: 送信を確認できません。paneを手動確認してください。"
      echo "--- pane内容 ---"
      tmux capture-pane -t "$PANE" -p -S -15
    fi
  else
    echo "送信確認: OK"
  fi
}
```

## 選択UIの操作

claude code / codex のTUIで選択肢が表示された場合、番号指定はできない。矢印キーで移動しEnterで確定する。

```bash
# 選択肢を下に移動
tmux send-keys -t "$PANE" Down

# 選択肢を上に移動
tmux send-keys -t "$PANE" Up

# 選択を確定
tmux send-keys -t "$PANE" Enter
```

権限確認ダイアログ（Allow / Deny 等）が表示された場合:
1. `tmux capture-pane -t "$PANE" -p -S -10` で現在のpane内容を確認
2. 現在選択されている項目を特定（ハイライト表示やカーソル位置で判断）
3. 目的の選択肢まで Down / Up で移動
4. Enter で確定
5. 確定後に `tmux capture-pane` で状態遷移を確認

**注意**: 選択肢がいくつあるか、現在どれが選択されているかをpane内容から読み取って判断する。盲目的に Down + Enter を送らない。

## 完了情報の表示

```
Branch: <branch>
Worktree: <path>
Window: <window-name>
Agent: <claude|codex>
Setup: <実行したコマンド or なし>
Status: <処理中 or 確認失敗>
```

## クリーンアップ

作業完了後は `tmux-worktree delete <branch>` と同等の操作で環境を削除する。

## エラーハンドリング

- tmux非実行時: エラーメッセージを出力して終了
- エージェントCLI不在: インストール方法を案内
- worktree作成失敗: `git worktree prune --expire now` を実行してリトライ
- セットアップタイムアウト: 警告を出してエージェント起動に進む（ユーザー判断）
- 送信確認失敗: pane内容を表示してユーザーに手動確認を促す
