---
name: tmux-worktree
description: git worktreeを作成してtmux windowで開く。worktree削除とクリーンアップも行う。「worktreeを作って」「ブランチをworktreeで開いて」「worktreeを削除して」「worktreeを一覧して」と言われた時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[create|delete|list] [branch-name]"
---

# tmux-worktree

git worktreeをtmux windowとして管理する。

## 概要

```
create <branch> → git worktree add → tmux new-window
delete <branch> → git worktree remove → tmux kill-window
list            → git worktree list + tmux list-windows
```

## 前提チェック

スキル実行前に以下を確認:
1. gitリポジトリ内か
2. `tmux` セッション内か（`$TMUX` 変数の存在）— 非tmux時はworktree操作のみ行いパスを出力
3. 現在の作業ディレクトリがworktreeの場合、メインリポジトリのパスを特定する

```bash
# メインリポジトリの特定
COMMON_DIR=$(cd "$(git rev-parse --git-common-dir)" && pwd)
ABS_GIT_DIR=$(cd "$(git rev-parse --absolute-git-dir)" && pwd)
if [ "$COMMON_DIR" != "$ABS_GIT_DIR" ]; then
  REPO_ROOT=$(dirname "$COMMON_DIR")
else
  REPO_ROOT=$(git rev-parse --show-toplevel)
fi
REPO_NAME=$(basename "$REPO_ROOT")
```

復元失敗時のフォールバック: `git worktree list --porcelain` の最初のworktreeエントリがメインrepo。

## パス規則

```
WORKTREE_BASE="${CLAUDE_WORKTREE_DIR:-$(dirname "$REPO_ROOT")/${REPO_NAME}.worktrees}"
```

- デフォルト配置: `../<repo-name>.worktrees/<branch-slug>/`
- 環境変数 `CLAUDE_WORKTREE_DIR` で上書き可能

### slug生成（create時のみ使用）

```bash
# ブランチ名のハッシュ（決定論的、create/delete間で安定）
BRANCH_HASH=$(printf '%s' "$BRANCH" | shasum | cut -c1-6)
# 読みやすいslug + 常にハッシュを付加して一意性を保証
BRANCH_SLUG=$(printf '%s' "$BRANCH" | sed 's/[^A-Za-z0-9._-]/-/g; s/--*/-/g; s/^-//; s/-$//' | cut -c1-60)
# パストラバーサル防止 + 空slug対策
case "$BRANCH_SLUG" in
  ""|"."|"..") BRANCH_SLUG="branch" ;;
esac
BRANCH_SLUG="${BRANCH_SLUG}-${BRANCH_HASH}"
WORKTREE_PATH="${WORKTREE_BASE}/${BRANCH_SLUG}"
```

- `<readable-slug>-<branch-hash>` 形式で常に一意
- ブランチ名のsha1先頭6文字をsuffixとして付加（`feature/a` と `feature-a` の衝突を回避）
- deleteはslugを再計算しない（後述）

## worktreeパスの逆引き

deleteやcreateの既存チェックでは、slugの再計算ではなく `git worktree list --porcelain` からブランチ名でパスを逆引きする。これによりslug計算の不一致によるバグを防ぐ。

```bash
# ブランチ名からworktreeパスを逆引き
find_worktree_by_branch() {
  git worktree list --porcelain | awk -v branch="$1" '
    /^worktree / { path = substr($0, 10) }
    /^branch refs\/heads\// {
      b = substr($0, 19)
      if (b == branch) { print path; exit }
    }
  '
}
```

## コマンド

### create

引数: ブランチ名（必須）。未指定なら質問する。

```bash
# 1. 既存チェック（ブランチ名で逆引き）
EXISTING_PATH=$(find_worktree_by_branch "$BRANCH")
if [ -n "$EXISTING_PATH" ]; then
  echo "Worktree already exists: ${EXISTING_PATH}"
  if [ -n "$TMUX" ]; then
    # 既存windowを探して選択
    WINDOW_NAME=$(basename "$EXISTING_PATH")
    tmux select-window -t "${WINDOW_NAME}" 2>/dev/null || true
  fi
  exit 0
fi

# 2. slug化とパス決定（上記slug生成を使用）

# 3. 書き込み権限チェック + フォールバック
if ! mkdir -p "${WORKTREE_BASE}" 2>/dev/null; then
  WORKTREE_BASE="${TMPDIR:-/tmp}/${REPO_NAME}.worktrees"
  BRANCH_SLUG="${BRANCH_SLUG}"  # slug自体は変わらない
  WORKTREE_PATH="${WORKTREE_BASE}/${BRANCH_SLUG}"
  mkdir -p "${WORKTREE_BASE}"
fi

# 4. worktree作成
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  git worktree add "${WORKTREE_PATH}" "${BRANCH}"
elif REMOTE_REF=$(git branch -r --list "*/${BRANCH}" | head -1 | xargs); [ -n "$REMOTE_REF" ]; then
  git worktree add --track -b "${BRANCH}" "${WORKTREE_PATH}" "$REMOTE_REF"
else
  git worktree add -b "${BRANCH}" "${WORKTREE_PATH}"
fi

# 5. tmux windowを作成（tmux環境の場合のみ）
if [ -n "$TMUX" ]; then
  tmux new-window -n "${BRANCH_SLUG}" -c "${WORKTREE_PATH}"
else
  echo "Worktree created: ${WORKTREE_PATH}"
  echo "cd ${WORKTREE_PATH}"
fi
```

### delete

引数: ブランチ名（必須）。未指定なら `list` の結果から選択を促す。

slugを再計算せず、**ブランチ名からworktreeパスを逆引き**して削除する。

```bash
# 1. ブランチ名からworktreeパスを逆引き
WORKTREE_PATH=$(find_worktree_by_branch "$BRANCH")
if [ -z "$WORKTREE_PATH" ]; then
  echo "Error: No worktree found for branch '${BRANCH}'"
  git worktree list
  exit 1
fi
# メイン作業ツリーの削除を防止
MAIN_TOPLEVEL=$(cd "$REPO_ROOT" && pwd)
WORKTREE_RESOLVED=$(cd "$WORKTREE_PATH" && pwd)
if [ "$WORKTREE_RESOLVED" = "$MAIN_TOPLEVEL" ]; then
  echo "Error: Cannot delete main working tree"
  exit 1
fi
WINDOW_NAME=$(basename "$WORKTREE_PATH")

# 2. Guard: 削除前の安全チェック
WARNINGS=""

# 未commitの変更チェック
DIRTY=$(git -C "$WORKTREE_PATH" status --porcelain 2>/dev/null)
if [ -n "$DIRTY" ]; then
  WARNINGS="${WARNINGS}\n⚠ 未commitの変更があります:\n${DIRTY}\n"
fi

# 未pushのコミットチェック
UNPUSHED=$(git -C "$WORKTREE_PATH" log @{u}.. --oneline 2>/dev/null)
if [ -n "$UNPUSHED" ]; then
  WARNINGS="${WARNINGS}\n⚠ 未pushのコミットがあります:\n${UNPUSHED}\n"
fi

# 実行中プロセスチェック（tmux pane内）
if [ -n "$TMUX" ]; then
  PANE_PIDS=$(tmux list-panes -t "${WINDOW_NAME}" -F '#{pane_pid}' 2>/dev/null)
  for PID in $PANE_PIDS; do
    # macOS互換: pgrep -Pで子プロセスを検出
    CHILDREN=$(pgrep -P "$PID" 2>/dev/null | xargs -I{} ps -p {} -o pid=,comm= 2>/dev/null)
    if [ -n "$CHILDREN" ]; then
      WARNINGS="${WARNINGS}\n⚠ 実行中のプロセスがあります (PID ${PID}):\n${CHILDREN}\n"
    fi
  done
fi

# 警告がある場合はユーザーに確認を求める
if [ -n "$WARNINGS" ]; then
  printf '%s\n' "$WARNINGS"
  echo "---"
  echo "このworktreeを削除しますか？ユーザーに確認してください。"
  echo "確認が取れるまで以降の削除処理を実行しないこと。"
  exit 0
fi

# 3. worktreeを削除（先に実行 — tmux windowが落ちても安全）
git worktree remove "${WORKTREE_PATH}"

# 4. tmux windowを閉じる（失敗しても続行）
if [ -n "$TMUX" ]; then
  tmux kill-window -t "${WINDOW_NAME}" 2>/dev/null || true
fi

# 5. 空ディレクトリの掃除
WORKTREE_BASE=$(dirname "$WORKTREE_PATH")
rmdir "${WORKTREE_BASE}" 2>/dev/null || true
```

### list

引数なし。現在のworktreeとtmux windowの対応を表示。

```bash
echo "=== Git Worktrees ==="
git worktree list

if [ -n "$TMUX" ]; then
  echo ""
  echo "=== tmux Windows ==="
  tmux list-windows -F '#{window_index}: #{window_name} → #{pane_current_path}'
fi
```

## エラーハンドリング

- worktree作成失敗時: `git worktree prune --expire now` を実行してリトライ
- tmux非実行時: worktree操作のみ行い、パスを出力（`$TMUX` で判定）
- 削除時のtmux window不在: 警告を出すがworktree削除は完了済み
- `--git-common-dir` 復元失敗時: `git worktree list --porcelain` の最初のエントリからメインrepoパスを取得
