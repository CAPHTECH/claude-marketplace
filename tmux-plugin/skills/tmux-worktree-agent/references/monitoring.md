# 監視・選択UI操作リファレンス

## pane状態の分類

```bash
classify_pane_state() {
  local PANE="$1"
  tmux capture-pane -t "$PANE" -p -S -30
}

check_pane_state() {
  local CONTENT="$1"

  # 1. 選択ダイアログ検出（最優先）
  if echo "$CONTENT" | grep -qE '(❯|›.*\[|Allow|Deny|Trust|Yes.*No|Approve|Reject)'; then
    echo "SELECTION_DIALOG"; return
  fi

  # 2. エージェント処理中
  if echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏)'; then
    echo "PROCESSING_SPINNER"; return
  fi
  if echo "$CONTENT" | grep -qE '(╭─|╰─|│.*Tool)'; then
    echo "PROCESSING_TOOL"; return
  fi
  if echo "$CONTENT" | grep -qE '(Thinking|Working|Running|Executing)'; then
    echo "PROCESSING_TEXT"; return
  fi

  # 3. 入力待ち
  if echo "$CONTENT" | grep -qE '(>\s*$|❯\s*$|\$\s*$)'; then
    echo "INPUT_READY"; return
  fi

  echo "UNKNOWN"
}
```

## 選択UIの操作

claude code / codex のTUIで選択肢が表示された場合、番号指定はできない。矢印キーで移動しEnterで確定する。

```bash
tmux send-keys -t "$PANE" Down   # 下に移動
tmux send-keys -t "$PANE" Up     # 上に移動
tmux send-keys -t "$PANE" Enter  # 確定
```

権限確認ダイアログ（Allow / Deny 等）が表示された場合:
1. `tmux capture-pane -t "$PANE" -p -S -10` で現在のpane内容を確認
2. 現在選択されている項目を特定（ハイライト表示やカーソル位置で判断）
3. 目的の選択肢まで Down / Up で移動
4. Enter で確定
5. 確定後に `tmux capture-pane` で状態遷移を確認

**注意**: 選択肢がいくつあるか、現在どれが選択されているかをpane内容から読み取って判断する。盲目的に Down + Enter を送らない。

## 追加メッセージの送信

初回以降にエージェントへ追加指示を送る場合:

```bash
send_message_to_agent() {
  local PANE="$1"
  local MESSAGE="$2"

  tmux send-keys -t "$PANE" -l "$MESSAGE"
  sleep 0.5
  tmux send-keys -t "$PANE" Enter

  sleep 3
  CONTENT=$(tmux capture-pane -t "$PANE" -p -S -10)

  if ! echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏|Thinking|thinking|Working)'; then
    echo "送信未確認。Enterを再送信..."
    tmux send-keys -t "$PANE" Enter
    sleep 3
    CONTENT=$(tmux capture-pane -t "$PANE" -p -S -10)
    if ! echo "$CONTENT" | grep -qE '(⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏|Thinking|thinking|Working)'; then
      echo "Warning: 送信を確認できません。paneを手動確認してください。"
      tmux capture-pane -t "$PANE" -p -S -15
    fi
  else
    echo "送信確認: OK"
  fi
}
```
