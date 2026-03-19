# zellij-plugin 設計書

## 概要

tmux-pluginのzellij版。zellijのpane introspection制限（出力キャプチャ、CWD取得、特定paneへのキー送信が不可）を踏まえ、1:1移植ではなく**source of truthをpane状態からファイルベースに移す**設計で再構築。

## 設計方針

1. **zellijビルトインCLIのみで動作**（zjctl等の外部ツール不要）
2. **`$ZELLIJ` env varで環境判定**、非zellij時はworktree操作+パス出力のみ
3. **`zellij run`でコマンド直接起動**（`send-keys`パターン不要）
4. **結果収集はファイルベース**（`.exit`, `.log` — pane captureに依存しない）
5. **delete時はタブ閉じ→worktree削除の順**（cwdが消える前にタブを閉じる）

## 推奨キーバインド設定

zellijのデフォルトキーバインドはEmacs系ショートカット（Ctrl-p, Ctrl-n, Ctrl-a等）と衝突する。

### 推奨: `Ctrl-t` prefix + locked デフォルト

`Ctrl-t`をunlock/prefixキーとして使用し、通常時はlocked（zellijキーバインド無効）にする。

- `Ctrl-t` はEmacs上では`transpose-chars`（使用頻度が低い）
- tmuxの`Ctrl-b`/`Ctrl-a` prefix方式と同じ操作感
- `Ctrl-p`, `Ctrl-n`, `Ctrl-a` 等のEmacs必須キーが完全に使える

### config.kdl

`~/.config/zellij/config.kdl` に以下を設定:

```kdl
default_mode "locked"

keybinds {
    // デフォルトのCtrl系バインドを全解除
    unbind "Ctrl g" "Ctrl q" "Ctrl p" "Ctrl n" "Ctrl s" "Ctrl o" "Ctrl t" "Ctrl h" "Ctrl b"

    // Locked: Ctrl-t でNormalモードに入る
    locked {
        bind "Ctrl t" { SwitchToMode "Normal"; }
    }

    // Normal/他モード: Ctrl-t でLockedに戻る
    shared_except "locked" {
        bind "Ctrl t" { SwitchToMode "Locked"; }
        bind "Ctrl q" { Quit; }
    }

    // 各モードへの遷移（Normalモードから1キーで）
    shared_except "pane" "locked"    { bind "p" { SwitchToMode "Pane"; } }
    shared_except "tab" "locked"     { bind "t" { SwitchToMode "Tab"; } }
    shared_except "resize" "locked"  { bind "r" { SwitchToMode "Resize"; } }
    shared_except "scroll" "locked"  { bind "s" { SwitchToMode "Scroll"; } }
    shared_except "session" "locked" { bind "o" { SwitchToMode "Session"; } }
    shared_except "move" "locked"    { bind "m" { SwitchToMode "Move"; } }
}
```

### 操作例

| 操作 | キーシーケンス |
|------|---------------|
| 新しいpane（右） | `Ctrl-t` → `p` → `n` |
| タブ切り替え | `Ctrl-t` → `t` → `h`/`l` |
| paneリサイズ | `Ctrl-t` → `r` → `h`/`j`/`k`/`l` |
| セッション管理 | `Ctrl-t` → `o` |
| ロックに戻る | `Ctrl-t` |

## tmux → zellij コマンドマッピング

| tmux | zellij |
|------|--------|
| `$TMUX` | `$ZELLIJ` |
| `tmux new-window -n <name> -c <path>` | `zellij action new-tab --name <name> --cwd <path>` |
| `tmux split-window -h -c <path>` | `zellij action new-pane --direction right --cwd <path>` |
| `tmux split-window -v -c <path>` | `zellij action new-pane --direction down --cwd <path>` |
| `tmux send-keys -t <target> <cmd> Enter` | `zellij run --direction <dir> -- <cmd>` (起動時のみ) |
| `tmux kill-window -t <name>` | `zellij action go-to-tab-name <name> && zellij action close-tab` |
| `tmux select-window -t <name>` | `zellij action go-to-tab-name <name>` |
| `tmux select-layout tiled` | N/A（zellijは自動レイアウト） |
| `tmux capture-pane` | N/A（ファイルベースで代替） |
| `tmux list-panes` / `list-windows` | N/A |

## zellijの制限事項

### pane introspection不可
- pane内の出力キャプチャ（`tmux capture-pane`相当）がない
- pane内のCWD取得ができない
- 特定paneへのキー送信（`tmux send-keys`相当）ができない

### タブ操作の制約
- `close-tab`は現在フォーカス中のタブのみ閉じられる（名前指定で直接閉じられない）
- タブ一覧をCLIで取得するAPIが限定的

### 影響と対策
| 影響を受ける機能 | tmux版の方式 | zellij版の対策 |
|-----------------|-------------|---------------|
| 結果収集 | `capture-pane` | `.exit`/`.log`ファイルに書き出し |
| コマンド送信 | `send-keys` | `zellij run`でpane作成時にコマンド指定 |
| タブ削除 | `kill-window -t <name>` | `go-to-tab-name` → `close-tab` |
| プロセス検出 | `list-panes` + `pgrep` | zellij自体のタブ閉じ確認に委ねる |

## v1スコープ

### 含まれるスキル
1. **zellij-worktree** — worktree管理 + zellijタブ連携
2. **zellij-issue-room** — Issue開発環境構築
3. **zellij-pr-review-room** — PRレビュー環境構築
4. **zellij-agent-lanes** — 並列エージェントレーン（start-only）
5. **zellij-devloop-matrix** — マトリクステスト（file-backed）

### v2候補（ドロップ）
- **context-snapshot** — pane CWD・scrollback取得が不可のため
- **failwatch** — pane current command取得が不可のため
