---
name: tmux-context-snapshot
description: tmux全paneの状態をスナップショットとしてJSON保存・復元・表示する。「状態を保存して」「コンテキストを復元して」「スナップショットを見せて」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[save|restore|show]"
---

# tmux-context-snapshot

tmuxセッションの全pane状態をスナップショットとして保存・復元する。

## 概要

```
save    → 全paneのcwd, git状態, ログ末尾を収集 → JSON保存
restore → JSONからcwd復元 → Claudeが前回状態を要約
show    → 最新スナップショットの表示
```

## 前提チェック

```bash
if [ -z "$TMUX" ]; then
  echo "Error: tmuxセッション内で実行してください"
  exit 1
fi

SESSION_NAME=$(tmux display-message -p '#{session_name}')
SNAPSHOT_DIR="${HOME}/.claude/tmux-snapshots"
mkdir -p "$SNAPSHOT_DIR"
```

## コマンド

### save

全paneの状態を収集してJSONに保存する。

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
# 同一秒の衝突を回避（ランダムサフィックス）
RAND_SUFFIX=$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' ')
SNAPSHOT_FILE="${SNAPSHOT_DIR}/${SESSION_NAME}-${TIMESTAMP}-${RAND_SUFFIX}.json"

# 全paneの情報を収集
PANES_JSON=$(tmux list-panes -s -F '#{window_index}:#{pane_index}' | while read TARGET; do
  WINDOW_IDX=$(echo "$TARGET" | cut -d: -f1)
  PANE_IDX=$(echo "$TARGET" | cut -d: -f2)
  WINDOW_NAME=$(tmux display-message -t "${TARGET}" -p '#{window_name}')
  PANE_CWD=$(tmux display-message -t "${TARGET}" -p '#{pane_current_path}')
  PANE_CMD=$(tmux display-message -t "${TARGET}" -p '#{pane_current_command}')

  # git情報（paneのcwdがgitリポジトリの場合）
  GIT_BRANCH=$(git -C "$PANE_CWD" branch --show-current 2>/dev/null || echo "")
  GIT_STATUS=$(git -C "$PANE_CWD" status --porcelain 2>/dev/null | head -10 || echo "")

  # ログ末尾（最新20行）
  LOG=$(tmux capture-pane -t "${TARGET}" -p -S -20 | python3 -c "
import sys, json
print(json.dumps(sys.stdin.read()))
" 2>/dev/null || echo '""')

  # 安全なJSON生成（sys.argv経由で値を渡す）
  python3 -c "
import sys, json
print(json.dumps({
    'window': int(sys.argv[1]),
    'pane': int(sys.argv[2]),
    'window_name': sys.argv[3],
    'cwd': sys.argv[4],
    'command': sys.argv[5],
    'git_branch': sys.argv[6],
    'git_status': sys.argv[7],
    'log_tail': sys.argv[8]
}))
" "$WINDOW_IDX" "$PANE_IDX" "$WINDOW_NAME" "$PANE_CWD" "$PANE_CMD" "$GIT_BRANCH" "$GIT_STATUS" "$LOG"
done | python3 -c "
import sys, json
entries = [json.loads(line) for line in sys.stdin if line.strip()]
print(json.dumps(entries, indent=2))
")

# スナップショットJSON生成（stdin経由で安全に受け渡し）
echo "$PANES_JSON" | python3 -c "
import json, sys
panes = json.load(sys.stdin)
snapshot = {
    'session': sys.argv[1],
    'timestamp': sys.argv[2],
    'panes': panes
}
with open(sys.argv[3], 'w') as f:
    json.dump(snapshot, f, indent=2, ensure_ascii=False)
" "${SESSION_NAME}" "${TIMESTAMP}" "${SNAPSHOT_FILE}"

echo "スナップショットを保存しました: ${SNAPSHOT_FILE}"
```

### restore

最新（または指定）のスナップショットからcwdを復元する。

```bash
# 最新スナップショットを探す
if [ -n "$1" ]; then
  # 引数指定時はSNAPSHOT_DIR配下かつ.jsonのみ許可
  SNAPSHOT_FILE="$1"
  REAL_SNAP=$(realpath "$SNAPSHOT_FILE" 2>/dev/null || echo "$SNAPSHOT_FILE")
  REAL_DIR=$(realpath "$SNAPSHOT_DIR" 2>/dev/null || echo "$SNAPSHOT_DIR")
  case "$REAL_SNAP" in
    "${REAL_DIR}/"*.json) ;;
    *) echo "Error: スナップショットは ${SNAPSHOT_DIR}/ 配下の.jsonのみ指定可能です"; exit 1 ;;
  esac
else
  SNAPSHOT_FILE=$(ls -t "${SNAPSHOT_DIR}/${SESSION_NAME}"-*.json 2>/dev/null | head -1)
fi

if [ -z "$SNAPSHOT_FILE" ] || [ ! -f "$SNAPSHOT_FILE" ]; then
  echo "Error: スナップショットが見つかりません"
  ls -la "$SNAPSHOT_DIR/" 2>/dev/null
  exit 1
fi

echo "復元中: ${SNAPSHOT_FILE}"

# 各paneのcwdを復元（tmux send-keysで実際にcdを実行）
python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    snapshot = json.load(f)
for pane in snapshot['panes']:
    target = f\"{pane['window']}:{pane['pane']}\"
    cwd = pane['cwd']
    print(f\"{target}\t{cwd}\")
" "$SNAPSHOT_FILE" | while IFS=$'\t' read TARGET CWD; do
  if tmux display-message -t "${TARGET}" -p '#{pane_id}' >/dev/null 2>&1; then
    tmux send-keys -t "${TARGET}" "cd $(printf '%q' "$CWD")" Enter
    echo "Pane ${TARGET}: cd ${CWD}"
  else
    echo "Pane ${TARGET}: スキップ（存在しません）"
  fi
done

# Claudeに前回状態の要約を依頼するために情報を表示
echo ""
echo "=== スナップショット内容 ==="
cat "$SNAPSHOT_FILE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Session: {data['session']}\")
print(f\"Timestamp: {data['timestamp']}\")
print(f\"Panes: {len(data['panes'])}\")
for p in data['panes']:
    branch = p.get('git_branch', '')
    status = '(dirty)' if p.get('git_status', '') else '(clean)'
    print(f\"  [{p['window']}:{p['pane']}] {p['window_name']} - {p['cwd']} [{branch} {status}]\")
"
```

### show

最新スナップショットの内容を表示する。

```bash
SNAPSHOT_FILE=$(ls -t "${SNAPSHOT_DIR}/${SESSION_NAME}"-*.json 2>/dev/null | head -1)

if [ -z "$SNAPSHOT_FILE" ] || [ ! -f "$SNAPSHOT_FILE" ]; then
  echo "スナップショットがありません"
  exit 0
fi

echo "=== 最新スナップショット ==="
echo "File: ${SNAPSHOT_FILE}"
echo ""
cat "$SNAPSHOT_FILE" | python3 -m json.tool
```

## 保存先

```
~/.claude/tmux-snapshots/<session-name>-<YYYYMMDD-HHMMSS>.json
```

## エラーハンドリング

- tmux非実行時: エラーメッセージを出力して終了
- git情報取得失敗: git関連フィールドを空文字で保存
- スナップショット不在: 利用可能なファイル一覧を表示
