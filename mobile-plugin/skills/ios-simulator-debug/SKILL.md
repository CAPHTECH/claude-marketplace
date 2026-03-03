---
name: ios-simulator-debug
context: fork
description: iOS SimulatorをAIで操作してデバッグ・検証。ビルド→起動→UI操作→スクショ→分析のループ。UIの動作確認、バグの再現・調査、UI実装の検証、アクセシビリティの確認時に使用。前提条件 mobile-mcp MCPサーバー（mobile-plugin導入で自動設定）
---

# iOS Simulator Debug スキル

iOS SimulatorをAIで操作し、ビルド→起動→操作→スクショ→分析のデバッグループを実行する。

## 前提条件

### 必須
- macOS
- Xcode（Simulator含む）
- Node.js（npx実行用）

### MCP設定（自動）
mobile-pluginを導入すると、`.mcp.json`により`mobile-mcp` MCPサーバーが自動で有効化される。

## ワークフロー

### Step 1: 要件確認

以下をユーザーに確認：
1. **対象アプリ**
   - Xcodeプロジェクト/ワークスペースのパス
   - スキーム名
   - Bundle ID

2. **検証内容**
   - 確認したい画面・機能
   - 再現したいバグの手順
   - 期待する動作

3. **Simulator設定**
   - デバイス（iPhone 15, iPad等）
   - OSバージョン

### Step 2: ビルド＆起動

```bash
# 1. 利用可能なデバイスを確認
# → mobile_list_available_devices ツールを使用

# 2. アプリをビルド
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -sdk iphonesimulator \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -derivedDataPath ./build \
  build

# 3. アプリをインストール
# → mobile_install_app ツールで ./build/Build/Products/Debug-iphonesimulator/App.app をインストール

# 4. アプリを起動
# → mobile_launch_app ツールで Bundle ID を指定して起動
```

### Step 3: UI操作＆検証ループ

```
現状把握 → 操作 → 結果確認 → 分析 → 次のアクション
    ↑                                      ↓
    └──────────── 繰り返し ←───────────────┘
```

## MCPツール一覧

### デバイス管理

| ツール | 説明 | 使用例 |
|--------|------|--------|
| `mobile_list_available_devices` | 利用可能なデバイス一覧を取得 | 最初に実行してデバイスIDを確認 |
| `mobile_install_app` | .app/.ipaをインストール | ビルド後 |
| `mobile_launch_app` | Bundle IDでアプリ起動 | インストール後 |
| `mobile_terminate_app` | アプリを終了 | テスト間のリセット |
| `mobile_list_apps` | インストール済みアプリ一覧 | Bundle ID確認 |

### UI検査

| ツール | 説明 | 使用例 |
|--------|------|--------|
| `mobile_list_elements_on_screen` | 画面上の要素一覧と座標を取得 | 現状把握・要素特定 |
| `mobile_take_screenshot` | スクリーンショット取得（画像データ） | クイック確認 |
| `mobile_save_screenshot` | スクリーンショットをファイルに保存 | 証跡保存 |
| `mobile_get_screen_size` | 画面サイズを取得 | 座標計算 |

### UI操作

| ツール | 説明 | パラメータ |
|--------|------|-----------|
| `mobile_click_on_screen_at_coordinates` | タップ | x, y座標 |
| `mobile_double_tap_on_screen` | ダブルタップ | x, y座標 |
| `mobile_long_press_on_screen_at_coordinates` | 長押し | x, y座標, duration |
| `mobile_type_keys` | テキスト入力 | 入力文字列 |
| `mobile_swipe_on_screen` | スワイプ | 方向（up/down/left/right） |
| `mobile_press_button` | ボタン押下 | ボタン名 |
| `mobile_open_url` | URLを開く | URL |

### 画面設定

| ツール | 説明 |
|--------|------|
| `mobile_set_orientation` | 画面の向きを変更（portrait/landscape） |
| `mobile_get_orientation` | 現在の画面の向きを取得 |

## デバッグパターン

### パターン1: 画面遷移の確認

```
1. mobile_list_elements_on_screen で現在画面を把握
2. mobile_save_screenshot で初期状態を保存
3. mobile_click_on_screen_at_coordinates でボタンをタップ
4. mobile_list_elements_on_screen で遷移後の画面を確認
5. mobile_save_screenshot で結果を保存
6. 期待と比較して分析
```

### パターン2: 入力フォームのテスト

```
1. mobile_list_elements_on_screen でフォーム要素を特定
2. mobile_click_on_screen_at_coordinates でテキストフィールドをタップ
3. mobile_type_keys でテキスト入力
4. mobile_click_on_screen_at_coordinates で送信ボタンをタップ
5. mobile_list_elements_on_screen で結果を確認
```

### パターン3: スクロールコンテンツの確認

```
1. mobile_save_screenshot で現在の表示を保存
2. mobile_swipe_on_screen で下にスクロール
3. mobile_save_screenshot でスクロール後を保存
4. 必要に応じて繰り返し
```

## アクセシビリティ検証

`mobile_list_elements_on_screen` の結果から以下をチェック：

- [ ] すべてのインタラクティブ要素にラベルがある
- [ ] 論理的なフォーカス順序
- [ ] ボタンとリンクの区別が明確
- [ ] 動的コンテンツの通知

## トラブルシューティング

### Simulatorが起動しない
```bash
# Simulatorをリセット
xcrun simctl shutdown all
xcrun simctl erase all
```

### アプリがインストールできない
```bash
# 署名を確認
codesign -dv --verbose=4 App.app

# Simulatorに直接インストール
xcrun simctl install booted App.app
```

## ベストプラクティス

1. **操作前に必ず現状把握**: `mobile_list_elements_on_screen`で画面状態を確認
2. **スクショは証跡として保存**: 問題発見時は`mobile_save_screenshot`で記録
3. **座標はmobile_list_elements_on_screenから取得**: ハードコードせず動的に取得
4. **エラー時は画面を確認**: 期待と異なる場合はスクショで状態確認
5. **デバイスIDは最初に確認**: `mobile_list_available_devices`で取得したIDを使用
