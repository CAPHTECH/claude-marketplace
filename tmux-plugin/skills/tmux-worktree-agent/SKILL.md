---
name: tmux-worktree-agent
description: worktreeとtmux windowを作成し、セットアップ後にclaude codeまたはcodexを起動して指示を送る。タスクに応じて複数windowで複数エージェントを並列起動できる。「worktreeでclaudeに作業させて」「worktreeでcodexに頼んで」「ブランチを切ってagentに任せて」「worktreeでagent起動して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<branch> [claude|codex] <instruction>"
---

# tmux-worktree-agent

worktreeとtmux windowを作成し、エージェント（claude/codex）を起動して指示を送る。
タスクに応じて複数のwindowで複数エージェントを並列起動できる。

## 概要

```
<branch> [agent-type] <instruction>
  → worktree作成 → タスク分析・エージェント構成決定
  → window作成 × N → セットアップ → エージェント起動 × N → 全pane監視
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

エージェントCLIの存在確認（使用するものだけ）:
```bash
command -v claude >/dev/null 2>&1 || { echo "Error: claude CLIが見つかりません"; exit 1; }
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

### 3. タスク分析とエージェント構成の決定

ユーザーの指示を解釈し、**単一エージェントで十分か、複数エージェントが有効か**を判断する。

**複数エージェントが有効なケース:**
- 実装とレビューを並行したい → claude(実装) + codex(レビュー)
- フロントエンドとバックエンドの同時開発 → claude × 2
- 実装 + テスト作成の並行 → claude(実装) + claude(テスト)
- ユーザーが明示的に複数エージェントを要求

**単一エージェントで十分なケース:**
- シンプルなバグ修正、単一ファイルの変更、小さな機能追加

判断結果として、エージェント構成リストを作成する:

```
AGENTS = [
  { type: "claude", role: "impl",   instruction: "..." },
  { type: "codex", role: "review",  instruction: "..." },
]
```

各エージェントの指示は、ユーザーの意図を解釈して伝わりやすいプロンプトに書き換える:
- 曖昧な表現を具体化する
- 省略された前提を補足する
- スキルプレフィックスを付加する
- 複数エージェント時は各自の役割と担当範囲を明確化する

```
各エージェントの INSTRUCTION 構成例:

/task-plan-builder, /agent-coding-preflight, /uncertainty-resolution を活用して取り組むこと。

[役割と担当範囲を明確にした指示文]
```

**エージェント種別ごとの追加指示:**
- **claude の場合**: 「TeamCreateでチームを作成し、複数のsubagentで並列に作業を進めること。」を指示に含める
- **codex の場合**: 「Agentツールでsubagentを積極的に活用し、調査・実装・検証を並列化すること。」を指示に含める

例（単一 claude）: ユーザー「ログイン周りリファクタして」→
「/task-plan-builder, /agent-coding-preflight, /uncertainty-resolution を活用して取り組むこと。TeamCreateでチームを作成し、複数のsubagentで並列に作業を進めること。ログイン機能のリファクタリング。認証フロー（src/auth/）の可読性と保守性を改善する。既存テストが通る状態を維持すること。」

例（複数）: ユーザー「API追加してテストも書いて」→
- Agent 1 (claude/impl): 「...TeamCreateでチームを作成し並列に作業を進めること。APIエンドポイントの実装。」
- Agent 2 (codex/test): 「...Agentツールでsubagentを活用すること。追加されたAPIエンドポイントのテストを作成。」

### 4. セットアップコマンドの検出

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

# Go / Rust / Ruby
[ -f "${WORKTREE_PATH}/go.mod" ] && SETUP_CMDS="${SETUP_CMDS}go mod download && "
[ -f "${WORKTREE_PATH}/Cargo.toml" ] && SETUP_CMDS="${SETUP_CMDS}cargo fetch && "
[ -f "${WORKTREE_PATH}/Gemfile" ] && SETUP_CMDS="${SETUP_CMDS}bundle install && "
```

### 5. window作成・セットアップ・エージェント起動（エージェントごとに繰り返し）

各エージェントに対して以下を実行する。**セットアップは最初のwindowでのみ実行し、完了を待ってから残りのwindowを起動する。**

```bash
PANES=()  # 監視対象pane一覧
PROMPT_FILES=()  # tmpファイル一覧

for i in $(seq 0 $((AGENT_COUNT - 1))); do
  AGENT_TYPE="${AGENTS[$i].type}"
  AGENT_ROLE="${AGENTS[$i].role}"
  AGENT_INSTRUCTION="${AGENTS[$i].instruction}"

  # window作成
  WINDOW_NAME="agent-${AGENT_ROLE}-$(basename "$WORKTREE_PATH")"
  tmux new-window -n "${WINDOW_NAME}" -c "${WORKTREE_PATH}"
  PANE="${WINDOW_NAME}.0"
  PANES+=("$PANE")

  # セットアップ（最初のwindowのみ）
  if [ $i -eq 0 ] && [ -n "$SETUP_CMDS" ]; then
    SETUP_CMDS_TRIMMED="${SETUP_CMDS% && }"
    MARKER="__SETUP_DONE_$$__"
    tmux send-keys -t "$PANE" "${SETUP_CMDS_TRIMMED}; echo ${MARKER}" Enter

    ELAPSED=0
    while [ $ELAPSED -lt 300 ]; do
      sleep 3
      if tmux capture-pane -t "$PANE" -p -S -50 | grep -qF "$MARKER"; then
        break
      fi
      ELAPSED=$((ELAPSED + 3))
    done
  fi

  # エージェント起動（CLI引数で指示を渡す）
  PROMPT_FILE=$(mktemp)
  printf '%s' "$AGENT_INSTRUCTION" > "$PROMPT_FILE"
  PROMPT_FILES+=("$PROMPT_FILE")
  ESCAPED_FILE=$(printf '%q' "$PROMPT_FILE")

  case "$AGENT_TYPE" in
    claude)
      tmux send-keys -t "$PANE" "claude \"\$(cat ${ESCAPED_FILE})\"" Enter ;;
    codex)
      tmux send-keys -t "$PANE" "codex \"\$(cat ${ESCAPED_FILE})\"" Enter ;;
  esac
done
```

### 6. 全エージェントの監視

全paneをラウンドロビンで監視する。選択ダイアログの検出・対応手順は references/monitoring.md を参照。

```bash
PROMPT_CLEANED=false
declare -A PREV_STATES

while true; do
  sleep 5
  ALL_INPUT_READY=true

  for PANE in "${PANES[@]}"; do
    CONTENT=$(tmux capture-pane -t "$PANE" -p -S -30)
    STATE=$(check_pane_state "$CONTENT")  # references/monitoring.md の関数

    # tmpファイルは最初に動作確認できた時点で削除
    if [ "$PROMPT_CLEANED" = false ] && [ "$STATE" != "UNKNOWN" ] && [ "$STATE" != "INPUT_READY" ]; then
      for F in "${PROMPT_FILES[@]}"; do rm -f "$F"; done
      PROMPT_CLEANED=true
    fi

    # 状態が変わった時だけ報告
    PREV="${PREV_STATES[$PANE]:-}"
    if [ "$STATE" = "$PREV" ] && [ "$STATE" != "SELECTION_DIALOG" ]; then
      [ "$STATE" != "INPUT_READY" ] && ALL_INPUT_READY=false
      continue
    fi
    PREV_STATES[$PANE]="$STATE"

    case "$STATE" in
      SELECTION_DIALOG)
        echo "=== [$PANE] 選択ダイアログ検出 ==="
        echo "$CONTENT" | tail -15
        echo "==========================="
        # references/monitoring.md の選択UI操作手順に従い対応
        ALL_INPUT_READY=false
        ;;
      PROCESSING_SPINNER|PROCESSING_TOOL|PROCESSING_TEXT)
        echo "監視: [$PANE] 動作中 (${STATE})"
        ALL_INPUT_READY=false
        ;;
      INPUT_READY)
        echo "=== [$PANE] 入力待ち ==="
        echo "$CONTENT" | tail -10
        ;;
      UNKNOWN)
        echo "=== [$PANE] 状態不明 ==="
        echo "$CONTENT" | tail -15
        ALL_INPUT_READY=false
        ;;
    esac
  done

  # 全エージェントが入力待ち = 全作業完了
  if [ "$ALL_INPUT_READY" = true ]; then
    echo "全エージェントが作業を完了しました。"
    break
  fi
done
```

## 完了情報の表示

```
Branch: <branch>
Worktree: <path>
Agents:
  Window: <window-name> | Type: <claude|codex> | Role: <role> | Status: <状態>
  Window: <window-name> | Type: <claude|codex> | Role: <role> | Status: <状態>
Setup: <実行したコマンド or なし>
```

## 監視・選択UI・追加メッセージ

詳細な操作手順（pane状態分類、選択UI操作、追加メッセージ送信）→ references/monitoring.md

## クリーンアップ

作業完了後は `tmux-worktree delete <branch>` と同等の操作で環境を削除する。

## エラーハンドリング

- tmux非実行時: エラーメッセージを出力して終了
- エージェントCLI不在: インストール方法を案内
- worktree作成失敗: `git worktree prune --expire now` を実行してリトライ
- セットアップタイムアウト: 警告を出してエージェント起動に進む（ユーザー判断）
- 送信確認失敗: pane内容を表示してユーザーに手動確認を促す
