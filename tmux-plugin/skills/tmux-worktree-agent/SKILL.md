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

### 5. 指示の構成

ユーザーの指示をそのまま渡さず、意図を解釈して伝わりやすいプロンプトに書き換える。大々的な調査は不要。

- 曖昧な表現を具体化する（「いい感じに」→ 何がゴールか明示）
- 省略された前提を補足する（対象ファイル、ブランチの目的など）
- スキルプレフィックスを付加する

```
FULL_INSTRUCTION の構成例:

/task-plan-builder, /agent-coding-preflight, /uncertainty-resolution を活用して取り組むこと。

[ユーザーの意図を明確にした指示文。ゴールと、必要なら対象・制約を簡潔に補足]
```

例: ユーザー「ログイン周りリファクタして」→
「/task-plan-builder, /agent-coding-preflight, /uncertainty-resolution を活用して取り組むこと。ログイン機能のリファクタリング。認証フロー（src/auth/）の可読性と保守性を改善する。既存テストが通る状態を維持すること。」

### 6. エージェント起動と指示送信

**初回指示はCLI引数として渡す。** `tmux send-keys` でテキスト入力後にEnterを送ると、改行として解釈され送信されない場合があるため、CLI引数渡しが最も確実。

```bash
# 指示をtmpファイルに書き出し（長い指示・特殊文字のエスケープ問題を回避）
PROMPT_FILE=$(mktemp)
printf '%s' "$FULL_INSTRUCTION" > "$PROMPT_FILE"

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

### 7. 送信確認と能動的監視

エージェント起動後、pane内容を定期的に取得し、状態を判定して適切に対応する。
**選択ダイアログや権限確認の取りこぼしを防ぐため、毎回pane全体の内容を確認する。**

```bash
# pane内容を取得して状態を分類する
classify_pane_state() {
  local PANE="$1"
  # pane全体を広めに取得（選択UIは画面下部に出るとは限らない）
  local CONTENT
  CONTENT=$(tmux capture-pane -t "$PANE" -p -S -30)

  # 状態を出力して呼び出し元が判定
  echo "$CONTENT"
}

check_pane_state() {
  local CONTENT="$1"

  # 1. 選択ダイアログ検出（最優先で確認）
  #    - "❯" や ">" のある行 + 他の選択肢行 = 選択UI
  #    - "Allow" / "Deny" / "Yes" / "No" / "Trust" = 権限ダイアログ
  if echo "$CONTENT" | grep -qE '(❯|›.*\[|Allow|Deny|Trust|Yes.*No|Approve|Reject)'; then
    echo "SELECTION_DIALOG"
    return
  fi

  # 2. エージェントが処理中
  if echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏)'; then
    echo "PROCESSING_SPINNER"
    return
  fi
  if echo "$CONTENT" | grep -qE '(╭─|╰─|│.*Tool)'; then
    echo "PROCESSING_TOOL"
    return
  fi
  if echo "$CONTENT" | grep -qE '(Thinking|Working|Running|Executing)'; then
    echo "PROCESSING_TEXT"
    return
  fi

  # 3. 入力待ち（エージェントが起動済みでプロンプト表示中）
  if echo "$CONTENT" | grep -qE '(>\s*$|❯\s*$|\$\s*$)'; then
    echo "INPUT_READY"
    return
  fi

  echo "UNKNOWN"
}
```

**指示送信後、エージェントが作業を完了するかユーザーが停止を指示するまで監視を継続する。**

```bash
monitor_agent() {
  local PANE="$1"
  local PROMPT_FILE="$2"
  local PROMPT_CLEANED=false
  local PREV_STATE=""

  while true; do
    sleep 5
    CONTENT=$(classify_pane_state "$PANE")
    STATE=$(check_pane_state "$CONTENT")

    # tmpファイルは最初に動作確認できた時点で削除
    if [ "$PROMPT_CLEANED" = false ] && [ "$STATE" != "UNKNOWN" ] && [ "$STATE" != "INPUT_READY" ]; then
      rm -f "$PROMPT_FILE"
      PROMPT_CLEANED=true
    fi

    # 状態が変わった時だけ報告（同じ状態の連続報告を抑制）
    if [ "$STATE" = "$PREV_STATE" ] && [ "$STATE" != "SELECTION_DIALOG" ]; then
      continue
    fi
    PREV_STATE="$STATE"

    case "$STATE" in
      SELECTION_DIALOG)
        # 選択ダイアログ検出 — pane内容を表示して選択UIの操作セクションに従い対応
        echo "=== 選択ダイアログ検出 ==="
        echo "$CONTENT" | tail -15
        echo "==========================="
        # ここで選択UIの操作セクションの手順に従い対応する
        # 対応後、監視を継続
        ;;
      PROCESSING_SPINNER|PROCESSING_TOOL|PROCESSING_TEXT)
        echo "監視: エージェント動作中 (${STATE})"
        ;;
      INPUT_READY)
        # エージェントが入力待ち = 作業完了または応答待ち
        echo "=== エージェントが入力待ち ==="
        echo "$CONTENT" | tail -10
        echo "=============================="
        echo "エージェントが応答待ちか作業完了の可能性。pane内容を確認。"
        break
        ;;
      UNKNOWN)
        # pane内容を確認して判断
        echo "=== pane状態不明 — 内容確認 ==="
        echo "$CONTENT" | tail -15
        echo "================================"
        ;;
    esac
  done
}

# tmpファイル名を渡して監視開始
monitor_agent "$PANE" "$PROMPT_FILE"
```

**重要**: 監視は無期限ループ。各イテレーションで `classify_pane_state` → `check_pane_state` を実行し、選択ダイアログが出たら即座にpane内容を表示して対応する。状態変化時のみ報告し、同じ状態の繰り返しは抑制する。

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
