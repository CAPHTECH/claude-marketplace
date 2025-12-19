# UIデバッグガイド

## 目次
1. [基本的なUI操作](#基本的なui操作)
2. [フォーム操作](#フォーム操作)
3. [動的コンテンツの操作](#動的コンテンツの操作)
4. [ダイアログ処理](#ダイアログ処理)
5. [ファイルアップロード](#ファイルアップロード)

## 基本的なUI操作

### スナップショット取得とuid特定

```
# 基本スナップショット
take_snapshot()

# 詳細情報付きスナップショット（要素が見つからない場合に使用）
take_snapshot(verbose: true)
```

スナップショット結果の読み方:
- 各要素に`uid`が付与される
- a11yツリー構造でページ構成を把握
- 操作対象の要素のuidを特定

### クリック操作

```
# 通常クリック
click(uid: "button-1")

# ダブルクリック
click(uid: "item-1", dblClick: true)
```

### ホバー操作

```
# ツールチップやドロップダウンメニュー表示
hover(uid: "menu-trigger")

# ホバー後に子要素を操作
hover(uid: "dropdown-menu")
take_snapshot()  # メニュー展開後の状態を取得
click(uid: "menu-item-1")
```

### ドラッグ&ドロップ

```
drag(from_uid: "draggable-item", to_uid: "drop-zone")
```

## フォーム操作

### 単一フィールド入力

```
# テキスト入力
fill(uid: "input-name", value: "山田太郎")

# セレクトボックス
fill(uid: "select-country", value: "Japan")
```

### 複数フィールド一括入力

```
fill_form(elements: [
  {uid: "input-email", value: "user@example.com"},
  {uid: "input-password", value: "SecurePass123"},
  {uid: "select-role", value: "admin"}
])
```

### キー入力

```
# 単一キー
press_key(key: "Enter")
press_key(key: "Tab")
press_key(key: "Escape")

# 修飾キー組み合わせ
press_key(key: "Control+A")      # 全選択
press_key(key: "Control+C")      # コピー
press_key(key: "Control+V")      # ペースト
press_key(key: "Control+Shift+R") # ハードリロード
```

## 動的コンテンツの操作

### 要素の出現待機

```
# 特定テキストの出現を待機
wait_for(text: "読み込み完了")

# タイムアウト指定（ミリ秒）
wait_for(text: "処理完了", timeout: 10000)
```

### 非同期操作のパターン

```
# 1. ボタンクリック
click(uid: "btn-submit")

# 2. ローディング完了を待機
wait_for(text: "保存しました")

# 3. 結果確認
take_snapshot()
list_console_messages(types: ["error"])
```

## ダイアログ処理

### alert/confirm/promptの処理

```
# ダイアログを承認
handle_dialog(action: "accept")

# ダイアログをキャンセル
handle_dialog(action: "dismiss")

# promptに入力して承認
handle_dialog(action: "accept", promptText: "入力テキスト")
```

### ダイアログが出る操作のパターン

```
# 削除ボタンをクリック（confirmダイアログが出る想定）
click(uid: "btn-delete")

# ダイアログを承認
handle_dialog(action: "accept")

# 結果確認
wait_for(text: "削除しました")
```

## ファイルアップロード

```
# ファイル入力要素にファイルをアップロード
upload_file(uid: "input-file", filePath: "/path/to/file.pdf")
```

## スクリーンショット

```
# 表示領域のみ
take_screenshot()

# フルページ
take_screenshot(fullPage: true)

# 特定要素のみ
take_screenshot(uid: "target-element")

# ファイル保存
take_screenshot(filePath: "/path/to/screenshot.png")

# 形式・品質指定
take_screenshot(format: "jpeg", quality: 80)
```

## デバッグのベストプラクティス

1. **操作前にスナップショット**: 必ずtake_snapshot()でuid取得
2. **待機を活用**: 非同期操作後はwait_for()で待機
3. **エラーチェック**: 操作後にlist_console_messages(types: ["error"])
4. **段階的操作**: 複雑な操作は小さなステップに分割
5. **verbose活用**: 要素が見つからない場合はverbose: trueで詳細確認
