---
name: zellij-agent-lanes
description: 役割リストを指定してpaneごとにclaude codeを起動し並列作業する。「エージェントレーンを作って」「implement,test,reviewで並列作業して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<role1,role2,...> [--cwd <path>]"
---

# zellij-agent-lanes

役割ごとにzellij paneを作成し、各paneでclaude codeを起動する。

## 概要

```
<roles> → pane作成 → 各paneでclaude起動（zellij runで直接起動） → 完了後ユーザー確認
```

## 前提チェック

```bash
if [ -z "$ZELLIJ" ]; then
  echo "Error: zellijセッション内で実行してください"
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

### 3. zellij pane構成とclaude起動

zellijでは `zellij run` でpane作成とコマンド起動を同時に行える。tmuxの `send-keys` と異なり、pane作成時にコマンドを直接指定する。

```bash
TAB_NAME="lanes-$(date +%H%M%S)"
zellij action new-tab --name "${TAB_NAME}" --cwd "${WORK_DIR}"

# 全役割をzellij runで新しいpaneとして起動
# 最初のpane（タブ作成時のデフォルトpane）は制御用として残る
for i in $(seq 0 $((ROLE_COUNT - 1))); do
  ROLE="${ROLES[$i]}"
  PROMPT=$(get_role_prompt "$ROLE")

  if [ $((i % 2)) -eq 0 ]; then
    DIRECTION="right"
  else
    DIRECTION="down"
  fi

  zellij run --direction "${DIRECTION}" --cwd "${WORK_DIR}" --name "${ROLE}" -- \
    claude --prompt "$PROMPT"
done
```

### 4. 起動情報の表示

```bash
echo "=== Agent Lanes 起動完了 ==="
echo "Tab: ${TAB_NAME}"
echo "Roles:"
for i in $(seq 0 $((ROLE_COUNT - 1))); do
  echo "  Pane ${i}: ${ROLES[$i]}"
done
```

### 5. 成果集約

zellijではpane captureが利用できないため、各paneの結果はユーザーが各paneを確認する。

Claudeが以下を案内する:
- 各paneに移動して結果を確認するよう案内
- 競合や矛盾がないか確認する手順を提示
- 必要に応じてマージ作業の提案

## エラーハンドリング

- zellij非実行時: エラーメッセージを出力して終了
- claude CLI不在: インストール方法を案内
- 役割数が多すぎる: 6つまでに制限（画面の視認性のため）
