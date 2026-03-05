---
name: tmux-agent-lanes
description: 役割リストを指定してpaneごとにclaude codeを起動し並列作業する。「エージェントレーンを作って」「implement,test,reviewで並列作業して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<role1,role2,...> [--cwd <path>]"
---

# tmux-agent-lanes

役割ごとにtmux paneを作成し、各paneでclaude codeを起動する。

## 概要

```
<roles> → pane作成 → 各paneでclaude起動 → 役割プロンプト設定 → 完了待ち → 成果集約
```

## 前提チェック

```bash
if [ -z "$TMUX" ]; then
  echo "Error: tmuxセッション内で実行してください"
  exit 1
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "Error: claude CLIがインストールされていません"
  exit 1
fi
```

## 手順

### 1. 引数解析

```bash
# 役割リスト（カンマ区切り）
ROLES_INPUT="$1"  # 例: "implement,test,review"
if [ -z "$ROLES_INPUT" ]; then
  echo "Error: 役割リストを指定してください（例: implement,test,review）"
  exit 1
fi

# CWD（オプション）
WORK_DIR="${PWD}"
if [ "$2" = "--cwd" ] && [ -n "$3" ]; then
  WORK_DIR="$3"
fi

# カンマ区切りを配列に変換
IFS=',' read -ra ROLES <<< "$ROLES_INPUT"
ROLE_COUNT=${#ROLES[@]}

if [ "$ROLE_COUNT" -lt 2 ]; then
  echo "Error: 2つ以上の役割を指定してください"
  exit 1
fi
if [ "$ROLE_COUNT" -gt 6 ]; then
  echo "Error: 役割は6つまでです"
  exit 1
fi
```

### 2. 役割プロンプトの生成

各役割に対応するプロンプトを生成する。

```bash
get_role_prompt() {
  local ROLE="$1"
  case "$ROLE" in
    implement|impl)
      echo "あなたは実装担当です。要件に従ってコードを実装してください。テストは別の担当が書きます。"
      ;;
    test)
      echo "あなたはテスト担当です。実装コードに対するテストを書いてください。エッジケースも網羅してください。"
      ;;
    review)
      echo "あなたはレビュー担当です。コードの品質、セキュリティ、パフォーマンスを確認してください。"
      ;;
    docs|doc)
      echo "あなたはドキュメント担当です。コードの変更に合わせてドキュメントを更新してください。"
      ;;
    refactor)
      echo "あなたはリファクタリング担当です。コードの可読性と保守性を改善してください。"
      ;;
    *)
      echo "あなたは${ROLE}担当です。指示された作業を行ってください。"
      ;;
  esac
}
```

### 3. tmux pane構成

```bash
WINDOW_NAME="lanes-$(date +%H%M%S)"
tmux new-window -n "${WINDOW_NAME}" -c "${WORK_DIR}"

# レイアウト: 役割数に応じてpaneを分割
for i in $(seq 1 $((ROLE_COUNT - 1))); do
  if [ $((i % 2)) -eq 1 ]; then
    tmux split-window -h -c "${WORK_DIR}" -t "${WINDOW_NAME}"
  else
    tmux split-window -v -c "${WORK_DIR}" -t "${WINDOW_NAME}"
  fi
done

# 均等レイアウトに調整
tmux select-layout -t "${WINDOW_NAME}" tiled
```

### 4. 各paneでclaude起動

```bash
for i in $(seq 0 $((ROLE_COUNT - 1))); do
  ROLE="${ROLES[$i]}"
  PROMPT=$(get_role_prompt "$ROLE")

  # 安全なエスケープでpaneにコマンドを送信
  ESCAPED_PROMPT=$(printf '%q' "$PROMPT")
  tmux send-keys -t "${WINDOW_NAME}.${i}" \
    "claude --prompt ${ESCAPED_PROMPT}" Enter
done

echo "=== Agent Lanes 起動完了 ==="
echo "Window: ${WINDOW_NAME}"
echo "Roles:"
for i in $(seq 0 $((ROLE_COUNT - 1))); do
  echo "  Pane ${i}: ${ROLES[$i]}"
done
```

### 5. 成果集約

全pane完了後、Claudeが以下を行う:

- 各paneのログを `tmux capture-pane` で取得
- 各役割の成果を要約
- 競合や矛盾がないか確認
- 必要に応じてマージ作業の提案

```bash
# 成果集約用コマンド（手動実行）
echo ""
echo "=== 成果集約 ==="
for i in $(seq 0 $((ROLE_COUNT - 1))); do
  echo "--- ${ROLES[$i]} (Pane ${i}) ---"
  tmux capture-pane -t "${WINDOW_NAME}.${i}" -p -S -50
done
```

## エラーハンドリング

- tmux非実行時: エラーメッセージを出力して終了
- claude CLI不在: インストール方法を案内
- pane作成失敗: 作成済みpaneを閉じてエラー表示
- 役割数が多すぎる: 6つまでに制限（画面の視認性のため）
