---
name: op-env
description: .envファイルのシークレットを1Password CLIで管理する。migrate（.env→1Password移行）、run（op run実行）、sync（差分同期）をサポート。「.envを1Passwordに移行して」「op runで実行して」「シークレットを同期して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[migrate|run|sync|add] [options]"
---

# op-env

.envファイルのシークレットを1Password CLI (`op`) で安全に管理する。

## 概要

```
migrate <envfile>        → .envの値を1Passwordに保存し、op://参照に置換
run <envfile> -- <cmd>   → op run --env-file でコマンド実行
sync <envfile>           → .envと1Passwordの差分検出・同期
add <key> <value>        → 新規シークレットを1Passwordに追加し.envに参照を追記
```

## 前提チェック

スキル実行前に以下を確認:

```bash
# 1. op CLIの存在確認
if ! command -v op >/dev/null 2>&1; then
  echo "Error: 1Password CLI (op) がインストールされていません"
  echo "Install: https://developer.1password.com/docs/cli/get-started/"
  exit 1
fi

# 2. op認証状態の確認
if ! op account list >/dev/null 2>&1; then
  echo "Error: 1Passwordにサインインしてください"
  echo "Run: op signin (1Password 8+) or eval \$(op signin) (旧バージョン)"
  exit 1
fi

# 3. .envファイルの存在確認は各コマンドで行う（引数の意味がコマンドごとに異なるため）
```

## 共通設定

```bash
# vault名の決定（環境変数 or デフォルト）
VAULT="${OP_ENV_VAULT:-Development}"

# アイテム名の決定（プロジェクト名ベース）
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_NAME=$(basename "$(git rev-parse --show-toplevel)")
else
  PROJECT_NAME=$(basename "$PWD")
fi
ITEM_NAME="${OP_ENV_ITEM:-${PROJECT_NAME}}"
```

## コマンド

### migrate

既存の.envファイルを1Passwordに移行し、op://参照に置換する。

引数: .envファイルパス（デフォルト: `.env`）

```bash
ENV_FILE="${1:-.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: ${ENV_FILE} が見つかりません"
  exit 1
fi
BACKUP_FILE="${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"

# 1. バックアップ作成
cp "$ENV_FILE" "$BACKUP_FILE" \
  || { echo "Error: バックアップの作成に失敗しました"; exit 1; }
echo "バックアップ: ${BACKUP_FILE}"

# 2. 既存アイテムの確認
EXISTING_ITEM=$(op item get "$ITEM_NAME" --vault="$VAULT" --format=json 2>/dev/null)

# 3. .envファイルを解析してフィールド生成
FIELDS=()
while IFS= read -r line; do
  # 空行・コメント行をスキップ
  [[ -z "$line" || "$line" == \#* ]] && continue
  # すでにop://参照の行はスキップ
  [[ "$line" == *"op://"* ]] && continue

  # KEY=VALUE の厳密パース
  [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
  KEY="${line%%=*}"
  VALUE="${line#*=}"
  # クォートを除去、前後空白をトリム
  VALUE=$(echo "$VALUE" | sed "s/^['\"]//; s/['\"]$//; s/^[[:space:]]*//; s/[[:space:]]*$//")
  # インラインコメントを除去（クォート外の # 以降）
  VALUE=$(echo "$VALUE" | sed 's/[[:space:]]#.*$//')

  [ -z "$KEY" ] && continue
  FIELDS+=("${KEY}[password]=${VALUE}")
done < "$ENV_FILE"

if [ ${#FIELDS[@]} -eq 0 ]; then
  echo "移行対象のシークレットがありません"
  exit 0
fi

# 4. dry-run表示（値は非表示）
echo "=== 移行対象 ==="
echo "Vault: ${VAULT}"
echo "Item: ${ITEM_NAME}"
echo "Fields:"
for F in "${FIELDS[@]}"; do
  echo "  - ${F%%=*}"
done
echo ""
echo "この内容で1Passwordに保存します。ユーザーに確認してください。"
echo "確認が取れるまで以降の処理を実行しないこと。"
exit 0
```

確認後、以下を実行:

```bash
# 5. 1Passwordアイテムの作成 or 更新
if [ -n "$EXISTING_ITEM" ]; then
  op item edit "$ITEM_NAME" --vault="$VAULT" "${FIELDS[@]}" \
    || { echo "Error: 1Passwordアイテムの更新に失敗しました。バックアップ: ${BACKUP_FILE}"; exit 1; }
else
  op item create --category=login --title="$ITEM_NAME" --vault="$VAULT" "${FIELDS[@]}" \
    || { echo "Error: 1Passwordアイテムの作成に失敗しました。バックアップ: ${BACKUP_FILE}"; exit 1; }
fi

# 6. .envファイルをop://参照に置換（1Password保存成功後のみ実行）
TEMP_FILE=$(mktemp)
while IFS= read -r line; do
  if [[ -z "$line" || "$line" == \#* || "$line" == *"op://"* ]]; then
    echo "$line"
    continue
  fi
  KEY="${line%%=*}"
  [ -z "$KEY" ] && { echo "$line"; continue; }
  echo "${KEY}=op://${VAULT}/${ITEM_NAME}/${KEY}"
done < "$ENV_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$ENV_FILE"

echo "=== 移行完了 ==="
echo "元ファイル: ${BACKUP_FILE}"
echo "更新後: ${ENV_FILE}"
echo ""
echo "動作確認: op run --env-file=${ENV_FILE} -- env | head"

# 7. .gitignoreに.env.bakを追加
if [ -f .gitignore ]; then
  if ! grep -qE '^\*\.env\.bak' .gitignore; then
    echo '*.env.bak.*' >> .gitignore
    echo ".gitignoreに *.env.bak.* を追加しました"
  fi
fi
```

### run

op run --env-fileでコマンドを実行する。

引数: .envファイルパス + `--` + 実行コマンド

```bash
# 引数解析: op-env run [envfile] -- command
if [ $# -eq 0 ]; then
  echo "Error: 実行コマンドを指定してください"
  echo "Usage: op-env run [.env] -- <command>"
  exit 1
fi

if [ "$1" = "--" ]; then
  ENV_FILE=".env"
  shift
else
  ENV_FILE="${1:-.env}"
  [ $# -gt 0 ] && shift
  if [ "${1:-}" = "--" ]; then
    shift
  fi
fi

if [ $# -eq 0 ]; then
  echo "Error: 実行コマンドを指定してください"
  echo "Usage: op-env run [.env] -- <command>"
  exit 1
fi

# .envファイルの存在確認
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: ${ENV_FILE} が見つかりません"
  exit 1
fi

# .envファイルにop://参照が含まれるか確認
if ! grep -q 'op://' "$ENV_FILE"; then
  echo "Warning: ${ENV_FILE} にop://参照が含まれていません"
  echo "先に 'op-env migrate' で移行してください"
  exit 1
fi

# op runで実行（シークレットはデフォルトでマスクされる）
op run --env-file="$ENV_FILE" -- "$@"
```

### sync

.envファイルと1Passwordの差分を検出・同期する。

引数: .envファイルパス、`--push`（.env→1Password）/ `--pull`（1Password→.env）

```bash
# 引数解析: sync [envfile] [--diff|--push|--pull]
# 第1引数がモード指定の場合はENV_FILEをデフォルトに
case "${1:-}" in
  --diff|--push|--pull) ENV_FILE=".env"; MODE="$1" ;;
  "") ENV_FILE=".env"; MODE="--diff" ;;
  *) ENV_FILE="$1"; MODE="${2:---diff}" ;;
esac

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: ${ENV_FILE} が見つかりません"
  exit 1
fi

# .envからキー一覧を取得（キー形式を検証）
ENV_KEYS=()
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
  KEY="${line%%=*}"
  [ -z "$KEY" ] && continue
  ENV_KEYS+=("$KEY")
done < "$ENV_FILE"

# 1Passwordからフィールド一覧を取得
OP_JSON=$(op item get "$ITEM_NAME" --vault="$VAULT" --format=json 2>/dev/null)
if [ -z "$OP_JSON" ]; then
  echo "Error: 1Passwordアイテム '${ITEM_NAME}' (vault: ${VAULT}) が見つかりません"
  echo "先に 'op-env migrate' でアイテムを作成してください"
  exit 1
fi
OP_FIELDS=$(echo "$OP_JSON" | op item get "$ITEM_NAME" --vault="$VAULT" --fields label --format=json 2>/dev/null | \
  python3 -c "
import sys, json
try:
    fields = json.load(sys.stdin)
    if isinstance(fields, list):
        for f in fields:
            label = f.get('label', '')
            if label:
                print(label)
    elif isinstance(fields, dict):
        label = fields.get('label', '')
        if label:
            print(label)
except:
    sys.exit(1)
" 2>/dev/null) || {
  echo "Error: フィールド一覧の取得に失敗しました"
  exit 1
}

case "$MODE" in
  --diff)
    echo "=== 差分レポート ==="
    echo "Vault: ${VAULT} / Item: ${ITEM_NAME}"
    echo ""

    # .envにあって1Passwordにないキー
    echo "--- .envのみ（1Passwordに未登録）---"
    for KEY in "${ENV_KEYS[@]}"; do
      if ! echo "$OP_FIELDS" | grep -qxF "$KEY"; then
        echo "  + $KEY"
      fi
    done

    # 1Passwordにあって.envにないキー
    echo "--- 1Passwordのみ（.envに未記載）---"
    while IFS= read -r FIELD; do
      [ -z "$FIELD" ] && continue
      FOUND=false
      for KEY in "${ENV_KEYS[@]}"; do
        if [ "$KEY" = "$FIELD" ]; then
          FOUND=true
          break
        fi
      done
      if [ "$FOUND" = false ]; then
        echo "  - $FIELD"
      fi
    done <<< "$OP_FIELDS"

    echo ""
    echo "同期するには --push または --pull を指定してください"
    ;;

  --push)
    echo "=== Push: .env → 1Password ==="
    # .envにあって1Passwordにないキーを検出
    PUSH_KEYS=()
    for KEY in "${ENV_KEYS[@]}"; do
      if ! echo "$OP_FIELDS" | grep -qxF "$KEY"; then
        PUSH_KEYS+=("$KEY")
      fi
    done
    if [ ${#PUSH_KEYS[@]} -eq 0 ]; then
      echo "同期対象のキーがありません"
      exit 0
    fi
    echo "追加対象: ${PUSH_KEYS[*]}"
    echo "ユーザーに確認してください。確認が取れるまで以降の処理を実行しないこと。"
    exit 0
    ```

    確認後、以下を実行:

    ```bash
    # push実行: .envの平文値を1Passwordに追加
    for KEY in "${PUSH_KEYS[@]}"; do
      # .envから値を取得
      # awkで安全にキーを固定文字列マッチして値を取得
      VALUE=$(awk -F= -v k="$KEY" '$1==k { sub(/^[^=]*=/, ""); print; exit }' "$ENV_FILE")
      VALUE=$(echo "$VALUE" | sed "s/^['\"]//; s/['\"]$//")
      op item edit "$ITEM_NAME" --vault="$VAULT" "${KEY}[password]=${VALUE}" \
        || { echo "Error: ${KEY} の追加に失敗"; continue; }
      # .envをop://参照に置換（awkで安全に置換）
      awk -F= -v k="$KEY" -v ref="op://${VAULT}/${ITEM_NAME}/${KEY}" \
        '$1==k { print k "=" ref; next } { print }' "$ENV_FILE" > "${ENV_FILE}.tmp" \
        && mv "${ENV_FILE}.tmp" "$ENV_FILE"
      echo "追加: ${KEY}"
    done
    ;;

  --pull)
    echo "=== Pull: 1Password → .env ==="
    # 1Passwordのフィールドで.envにないものをop://参照として追記
    while IFS= read -r FIELD; do
      [ -z "$FIELD" ] && continue
      FOUND=false
      for KEY in "${ENV_KEYS[@]}"; do
        if [ "$KEY" = "$FIELD" ]; then
          FOUND=true
          break
        fi
      done
      if [ "$FOUND" = false ]; then
        echo "${FIELD}=op://${VAULT}/${ITEM_NAME}/${FIELD}" >> "$ENV_FILE"
        echo "追加: ${FIELD}"
      fi
    done <<< "$OP_FIELDS"
    echo "完了: ${ENV_FILE}"
    ;;

  *)
    echo "Error: 無効なモードです: ${MODE}"
    echo "Usage: op-env sync <envfile> [--diff|--push|--pull]"
    exit 1
    ;;
esac
```

### add

新規シークレットを1Passwordに追加し、.envにop://参照を追記する。

引数: キー名、値

```bash
KEY="$1"
VALUE="$2"
ENV_FILE="${3:-.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: ${ENV_FILE} が見つかりません"
  exit 1
fi

if [ -z "$KEY" ] || [ -z "$VALUE" ]; then
  echo "Error: キー名と値を指定してください"
  echo "Usage: op-env add API_KEY sk-xxx [.env]"
  exit 1
fi

# キー名のバリデーション（英数字とアンダースコアのみ）
if ! echo "$KEY" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*$'; then
  echo "Error: 無効なキー名です: ${KEY}"
  exit 1
fi

# 1Passwordアイテムの存在確認 → 追加 or 作成
if op item get "$ITEM_NAME" --vault="$VAULT" >/dev/null 2>&1; then
  op item edit "$ITEM_NAME" --vault="$VAULT" "${KEY}[password]=${VALUE}" \
    || { echo "Error: 1Passwordへの追加に失敗しました"; exit 1; }
else
  op item create --category=login --title="$ITEM_NAME" --vault="$VAULT" "${KEY}[password]=${VALUE}" \
    || { echo "Error: 1Passwordアイテムの作成に失敗しました"; exit 1; }
fi

# .envにop://参照を追記（重複チェック）
if grep -qE "^${KEY}=" "$ENV_FILE" 2>/dev/null; then
  echo "Warning: ${KEY} は既に ${ENV_FILE} に存在します。手動で更新してください。"
else
  echo "${KEY}=op://${VAULT}/${ITEM_NAME}/${KEY}" >> "$ENV_FILE"
fi

echo "追加完了: ${KEY} → op://${VAULT}/${ITEM_NAME}/${KEY}"
```

## 環境変数によるカスタマイズ

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `OP_ENV_VAULT` | `Development` | 1Password vault名 |
| `OP_ENV_ITEM` | プロジェクト名 | 1Passwordアイテム名 |

## エラーハンドリング

- op CLI未インストール: インストールURLを表示
- 未認証: `eval $(op signin)` を案内
- アイテム未存在: 自動作成 or 作成を案内
- .envファイル不在: エラーメッセージを表示
- 値の表示制御: シークレット値は出力に含めない
