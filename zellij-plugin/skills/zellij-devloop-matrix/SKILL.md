---
name: zellij-devloop-matrix
description: 条件マトリクスを定義してpaneごとに並列実行し、結果をファイルベースで比較する。「マトリクステストして」「複数条件で並列実行して」「devloop-matrixで比較して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "<command> --matrix <key=val1,val2,...> [--matrix <key=val1,val2,...>]"
---

# zellij-devloop-matrix

条件マトリクスをpaneごとに並列実行し、結果をファイルベースで比較・分析する。

## 概要

```
<command> --matrix <conditions> → pane生成（zellij run） → 並列実行 → ファイルベース結果収集 → 比較テーブル
```

## 前提チェック

```bash
if [ -z "$ZELLIJ" ]; then
  echo "Error: zellijセッション内で実行してください"
  exit 1
fi
```

## 手順

### 1. 引数解析

```bash
# 使用例:
#   zellij-devloop-matrix "npm test" --matrix node=18,20,22
#   zellij-devloop-matrix "pytest" --matrix python=3.10,3.11,3.12 --matrix db=sqlite,postgres

COMMAND_ARGS=()
MATRIX_KEYS=()
MATRIX_VALUES=()

while [ $# -gt 0 ]; do
  case "$1" in
    --matrix)
      shift
      if [ -z "$1" ] || [ "${1#--}" != "$1" ]; then
        echo "Error: --matrix には key=val1,val2 形式の値が必要です"
        exit 1
      fi
      KEY=$(echo "$1" | cut -d= -f1)
      VALUES=$(echo "$1" | cut -d= -f2)
      if [ -z "$KEY" ] || [ -z "$VALUES" ]; then
        echo "Error: --matrix の形式が不正です: $1 (期待: key=val1,val2)"
        exit 1
      fi
      MATRIX_KEYS+=("$KEY")
      MATRIX_VALUES+=("$VALUES")
      shift
      ;;
    *)
      COMMAND_ARGS+=("$1")
      shift
      ;;
  esac
done

if [ ${#COMMAND_ARGS[@]} -eq 0 ]; then
  echo "Error: 実行コマンドを指定してください"
  exit 1
fi
if [ ${#MATRIX_KEYS[@]} -eq 0 ]; then
  echo "Error: --matrix で条件を1つ以上指定してください"
  exit 1
fi
```

### 2. マトリクスの展開

```bash
# 条件の組み合わせを生成
# 単一キーの場合: 値の数だけpane
# 複数キーの場合: 直積（最大12組み合わせに制限）
generate_combinations() {
  # キーと値をJSON配列としてstdin経由で安全に渡す
  python3 -c "
import itertools, json, re, sys

data = json.load(sys.stdin)
keys = data['keys']
values = [v.split(',') for v in data['values']]

combos = list(itertools.product(*values))
if len(combos) > 12:
    print('ERROR:TOO_MANY', file=sys.stderr)
    sys.exit(1)

for combo in combos:
    env_pairs = ' '.join(f'{k}={v}' for k, v in zip(keys, combo))
    # ラベルは安全な文字のみ（パストラバーサル防止）
    label = '_'.join(f'{k}-{v}' for k, v in zip(keys, combo))
    label = re.sub(r'[^A-Za-z0-9._-]', '_', label)
    print(f'{label}|{env_pairs}')
" <<< "$(python3 -c "
import json
keys = $(printf '%s\n' "${MATRIX_KEYS[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin]))")
values = $(printf '%s\n' "${MATRIX_VALUES[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin]))")
print(json.dumps({'keys': keys, 'values': values}))
")"
}

COMBINATIONS=$(generate_combinations)
if [ $? -ne 0 ]; then
  echo "Error: 組み合わせが12を超えています。条件を絞ってください。"
  exit 1
fi

COMBO_COUNT=$(echo "$COMBINATIONS" | wc -l | tr -d ' ')
```

### 3. 結果ディレクトリの準備

```bash
RESULTS_DIR=$(mktemp -d)
mkdir -p "${RESULTS_DIR}"
```

### 4. zellij pane構成と実行

zellijでは `zellij run` でpane作成とコマンド実行を同時に行う。各paneの結果は `.exit` と `.log` ファイルに書き出す。

```bash
TAB_NAME="matrix-$(date +%H%M%S)"
zellij action new-tab --name "${TAB_NAME}" --cwd "${PWD}"

# 全組み合わせをzellij runで新しいpaneとして起動
# 最初のpane（タブ作成時のデフォルトpane）は制御・結果確認用として残る
INDEX=0
echo "$COMBINATIONS" | while IFS='|' read LABEL ENV_PAIRS; do
  SAFE_LABEL=$(echo "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
  EXIT_FILE="${RESULTS_DIR}/${SAFE_LABEL}.exit"
  LOG_FILE="${RESULTS_DIR}/${SAFE_LABEL}.log"

  # ENV_PAIRSを構築
  ENV_CMD=""
  IFS=' ' read -ra PAIRS <<< "$ENV_PAIRS"
  for PAIR in "${PAIRS[@]}"; do
    [ -z "$PAIR" ] && continue
    ENV_CMD="${ENV_CMD} $(printf '%q' "$PAIR")"
  done

  ESCAPED_CMD=""
  for ARG in "${COMMAND_ARGS[@]}"; do
    ESCAPED_CMD="${ESCAPED_CMD} $(printf '%q' "$ARG")"
  done

  # 実行コマンド: env設定 → コマンド実行 → exit code保存 → ログ保存
  RUN_CMD="echo '=== ${SAFE_LABEL} ===' && env${ENV_CMD}${ESCAPED_CMD} 2>&1 | tee $(printf '%q' "${LOG_FILE}"); echo \${PIPESTATUS[0]} > $(printf '%q' "${EXIT_FILE}")"

  if [ $((INDEX % 2)) -eq 0 ]; then
    DIRECTION="right"
  else
    DIRECTION="down"
  fi
  zellij run --direction "${DIRECTION}" --cwd "${PWD}" --name "${SAFE_LABEL}" -- \
    bash -c "$RUN_CMD"

  INDEX=$((INDEX + 1))
done

echo "=== Matrix 実行開始 ==="
echo "Tab: ${TAB_NAME}"
echo "Command: ${COMMAND_ARGS[*]}"
echo "Combinations: ${COMBO_COUNT}"
echo "Results dir: ${RESULTS_DIR}"
```

### 5. 結果収集と比較

全pane完了後にClaudeが実行する。結果はファイルベースで収集する（pane captureに依存しない）。

```bash
echo "=== Matrix 結果 ==="
echo ""
printf "%-30s %-10s\n" "CONDITION" "EXIT_CODE"
printf "%-30s %-10s\n" "------------------------------" "----------"

echo "$COMBINATIONS" | while IFS='|' read LABEL ENV_PAIRS; do
  SAFE_LABEL=$(echo "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
  EXIT_FILE="${RESULTS_DIR}/${SAFE_LABEL}.exit"
  if [ -f "$EXIT_FILE" ]; then
    EXIT_CODE=$(cat "$EXIT_FILE")
    if [ "$EXIT_CODE" = "0" ]; then
      STATUS="OK"
    else
      STATUS="FAIL(${EXIT_CODE})"
    fi
  else
    STATUS="PENDING"
  fi
  printf "%-30s %-10s\n" "$LABEL" "$STATUS"
done

# 各条件のログを表示
echo ""
echo "=== 詳細ログ ==="
echo "$COMBINATIONS" | while IFS='|' read LABEL ENV_PAIRS; do
  SAFE_LABEL=$(echo "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
  LOG_FILE="${RESULTS_DIR}/${SAFE_LABEL}.log"
  echo "--- ${LABEL} ---"
  if [ -f "$LOG_FILE" ]; then
    tail -20 "$LOG_FILE"
  else
    echo "(ログファイル未生成)"
  fi
done
```

## Claudeによる分析

結果収集後、Claudeが以下を提供する:

- 成功/失敗の比較テーブル
- 失敗した条件の原因分析
- ボトルネック推定（実行時間の差分があれば）
- 条件間の差分要約

## エラーハンドリング

- zellij非実行時: エラーメッセージを出力して終了
- 組み合わせ過多: 12を超える場合は条件の絞り込みを要求
- 結果ファイル不在: PENDINGとして表示
