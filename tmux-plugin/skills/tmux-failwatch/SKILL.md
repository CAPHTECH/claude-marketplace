---
name: tmux-failwatch
description: tmux pane/windowのプロセスを監視し、失敗時にログを取得して原因分析する。「このコマンドを監視して」「failwatchで見守って」「失敗したら教えて」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[watch|check] [window:pane]"
---

# tmux-failwatch

tmux paneのプロセス完了を監視し、失敗時にログ取得と原因分析を行う。

## 概要

```
watch <target>  → プロセス完了を待機 → 終了コードチェック → 失敗時ログ取得
check <target>  → 指定paneの最新状態を即座にチェック
```

## 前提チェック

```bash
if [ -z "$TMUX" ]; then
  echo "Error: tmuxセッション内で実行してください"
  exit 1
fi
```

## ターゲット指定

```bash
# ターゲットの解決（未指定時は現在のwindow）
TARGET="${1:-$(tmux display-message -p '#{window_index}')}"

# window:pane 形式の解析（:区切りを優先、.含むwindow名に対応）
case "$TARGET" in
  *:*) WINDOW="${TARGET%%:*}"; PANE="${TARGET##*:}" ;;
  *)   WINDOW="$TARGET"; PANE="0" ;;
esac
TARGET_SPEC="${WINDOW}.${PANE}"
```

## コマンド

### watch

指定paneのプロセス完了を監視する。

```bash
# paneのPIDを取得
PANE_PID=$(tmux display-message -t "${TARGET_SPEC}" -p '#{pane_pid}')
if [ -z "$PANE_PID" ]; then
  echo "Error: ターゲットpaneが見つかりません: ${TARGET_SPEC}"
  exit 1
fi

# 子プロセスの完了を待機
echo "Watching pane ${TARGET_SPEC} (PID: ${PANE_PID})..."

# paneのコマンドが完了するまでポーリング（タイムアウト付き）
TIMEOUT="${TMUX_FAILWATCH_TIMEOUT:-600}"  # デフォルト10分
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  # paneが存在するか確認
  if ! PANE_CMD=$(tmux display-message -t "${TARGET_SPEC}" -p '#{pane_current_command}' 2>/dev/null); then
    echo "Error: pane ${TARGET_SPEC} が閉じられました"
    exit 1
  fi
  # シェルに戻った = コマンド完了
  case "$PANE_CMD" in
    bash|zsh|fish|sh|dash|ksh|csh|tcsh|pwsh)
      break
      ;;
  esac
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done

if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
  echo "Error: タイムアウト (${TIMEOUT}秒) に達しました"
  echo "現在のコマンド: ${PANE_CMD}"
  exit 1
fi

# paneのログを取得
LOG=$(tmux capture-pane -t "${TARGET_SPEC}" -p -S -50)

# コマンド完了を通知
echo "=== プロセス完了 ==="
echo "Pane: ${TARGET_SPEC}"
echo ""
echo "=== ログ末尾 ==="
echo "$LOG" | tail -30
```

### check

指定paneの現在の状態を即座にチェックする。

```bash
# paneの現在のコマンド
PANE_CMD=$(tmux display-message -t "${TARGET_SPEC}" -p '#{pane_current_command}')
PANE_PID=$(tmux display-message -t "${TARGET_SPEC}" -p '#{pane_pid}')
PANE_CWD=$(tmux display-message -t "${TARGET_SPEC}" -p '#{pane_current_path}')

echo "=== Pane ${TARGET_SPEC} 状態 ==="
echo "Command: ${PANE_CMD}"
echo "PID: ${PANE_PID}"
echo "CWD: ${PANE_CWD}"
echo ""

# ログ末尾を取得
LOG=$(tmux capture-pane -t "${TARGET_SPEC}" -p -S -30)
echo "=== ログ末尾 ==="
echo "$LOG"
```

## 原因分析

ログ取得後、Claudeが以下を分析して提示する:

- エラーメッセージの特定と原因推定
- スタックトレースがある場合はその解析
- リカバリー提案（修正コマンド or コード変更）
- 再実行コマンドの提示

## エラーハンドリング

- ターゲットpaneが存在しない: エラーメッセージと利用可能なpane一覧を表示
- tmux非実行時: エラーメッセージを出力して終了
- 監視中にpaneが閉じられた: 監視を終了しその旨を通知
