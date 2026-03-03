# Xcode Cloud ガイド

## 概要

Xcode Cloud は Apple が提供するCI/CDサービス。Xcode と完全に統合されており、ビルド、テスト、配布を自動化できる。

## 特徴

| 項目 | 内容 |
|------|------|
| 統合 | Xcode / App Store Connect と完全統合 |
| 実行環境 | Apple シリコン Mac（仮想マシン） |
| 対応 | iOS, macOS, tvOS, watchOS, visionOS |
| 無料枠 | 月25時間（2024年時点） |
| 署名 | 自動（cloud-managed certificates） |

## セットアップ

### 前提条件

- Xcode 13以降
- App Store Connect へのアクセス権限
- ソースコードがクラウドリポジトリにホスト（GitHub, GitLab, Bitbucket）

### 初期設定

1. **Xcode でプロジェクトを開く**
2. **Product > Xcode Cloud > Create Workflow**
3. **Apple ID でログイン**
4. **リポジトリを接続**
   - GitHub / GitLab / Bitbucket から選択
   - リポジトリへのアクセスを許可
5. **ワークフローを作成**

### リポジトリ接続

#### GitHub

1. **Xcode Cloud が GitHub 接続を要求**
2. **GitHub で「Authorize Xcode Cloud」**
3. **対象リポジトリを選択**

#### GitLab

1. **GitLab アクセストークンを生成**
   - Scopes: `api`, `read_repository`
2. **Xcode Cloud にトークンを入力**

#### Bitbucket

1. **Bitbucket App パスワードを生成**
2. **Xcode Cloud に認証情報を入力**

## ワークフロー設定

### 基本構成

```
Workflow
├─ General
│   ├─ Name（ワークフロー名）
│   └─ Description
├─ Environment
│   ├─ Xcode Version
│   └─ macOS Version
├─ Start Conditions
│   ├─ Branch Changes
│   ├─ Tag Changes
│   └─ Pull Request Changes
├─ Actions
│   ├─ Build
│   ├─ Test
│   ├─ Analyze
│   └─ Archive
└─ Post-Actions
    ├─ TestFlight (Internal)
    ├─ TestFlight (External)
    └─ App Store
```

### Start Conditions

#### Branch Changes

```yaml
# 特定のブランチへのプッシュでトリガー
Branches:
  - main
  - develop
  - release/*
```

#### Tag Changes

```yaml
# 特定パターンのタグ作成でトリガー
Tags:
  - v*
  - release-*
```

#### Pull Request Changes

```yaml
# PRイベントでトリガー
Source Branches:
  - feature/*
  - bugfix/*
Target Branch: main
```

### Environment

| 設定 | 説明 |
|------|------|
| Xcode Version | 使用するXcodeバージョン（Latest / 特定バージョン） |
| macOS Version | 使用するmacOSバージョン |
| Clean Build | クリーンビルドの有無 |

### Actions

#### Build

```yaml
Action: Build
Platform: iOS
Scheme: MyApp
Configuration: Debug / Release
```

#### Test

```yaml
Action: Test
Platform: iOS
Scheme: MyApp
Destination:
  - iPhone 15
  - iPhone 15 Pro
  - iPad Pro (12.9-inch)
```

#### Analyze

```yaml
Action: Analyze
Platform: iOS
Scheme: MyApp
# 静的解析を実行
```

#### Archive

```yaml
Action: Archive
Platform: iOS
Scheme: MyApp
# アーカイブを作成
```

### Post-Actions

#### TestFlight（内部テスター）

```yaml
Artifact: Archive
Distribution: TestFlight (Internal Testing)
Groups:
  - Internal Testers
```

#### TestFlight（外部テスター）

```yaml
Artifact: Archive
Distribution: TestFlight (External Testing)
Groups:
  - Beta Testers
# Beta App Review が必要
```

#### App Store

```yaml
Artifact: Archive
Distribution: App Store
# 審査提出は手動
```

## カスタムスクリプト

### スクリプトの種類

| スクリプト | タイミング | 用途 |
|-----------|-----------|------|
| ci_post_clone.sh | クローン後 | 依存関係インストール |
| ci_pre_xcodebuild.sh | ビルド前 | 設定ファイル生成 |
| ci_post_xcodebuild.sh | ビルド後 | 成果物処理 |

### ディレクトリ構成

```
project_root/
├─ ci_scripts/
│   ├─ ci_post_clone.sh
│   ├─ ci_pre_xcodebuild.sh
│   └─ ci_post_xcodebuild.sh
└─ ...
```

### ci_post_clone.sh 例

```bash
#!/bin/bash
set -e

echo "=== Post Clone Script ==="

# Homebrew のインストール（必要な場合）
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# SwiftLint のインストール
brew install swiftlint

# Mint のインストールとパッケージ取得
brew install mint
mint bootstrap

# CocoaPods の依存関係インストール
if [ -f "Podfile" ]; then
    pod install
fi

# 環境変数からの設定ファイル生成
cat > Config/Secrets.swift << EOF
enum Secrets {
    static let apiKey = "$API_KEY"
    static let analyticsKey = "$ANALYTICS_KEY"
}
EOF

echo "=== Post Clone Complete ==="
```

### ci_pre_xcodebuild.sh 例

```bash
#!/bin/bash
set -e

echo "=== Pre Xcodebuild Script ==="

# ビルド番号の自動インクリメント
if [ "$CI_XCODEBUILD_ACTION" == "archive" ]; then
    BUILD_NUMBER=$CI_BUILD_NUMBER
    agvtool new-version -all $BUILD_NUMBER
fi

# 環境別設定の適用
if [ "$CI_WORKFLOW" == "Production" ]; then
    cp Config/Production.xcconfig Config/Active.xcconfig
else
    cp Config/Development.xcconfig Config/Active.xcconfig
fi

echo "=== Pre Xcodebuild Complete ==="
```

### ci_post_xcodebuild.sh 例

```bash
#!/bin/bash
set -e

echo "=== Post Xcodebuild Script ==="

# テスト結果の処理
if [ "$CI_XCODEBUILD_ACTION" == "test-without-building" ]; then
    # カバレッジレポート生成
    xcrun xccov view --report "$CI_RESULT_BUNDLE_PATH" > coverage_report.txt
fi

# アーカイブ後の処理
if [ "$CI_XCODEBUILD_ACTION" == "archive" ]; then
    # dSYM をシンボル管理サービスにアップロード
    if [ -d "$CI_ARCHIVE_PATH/dSYMs" ]; then
        # Firebase Crashlytics
        # upload-symbols -gsp GoogleService-Info.plist -p ios "$CI_ARCHIVE_PATH/dSYMs"

        # Sentry
        # sentry-cli upload-dif --org ORG --project PROJECT "$CI_ARCHIVE_PATH/dSYMs"
        echo "dSYMs found at $CI_ARCHIVE_PATH/dSYMs"
    fi
fi

echo "=== Post Xcodebuild Complete ==="
```

## 環境変数

### ビルトイン環境変数

| 変数 | 説明 |
|------|------|
| CI | "TRUE" |
| CI_WORKSPACE | ワークスペースパス |
| CI_PRODUCT | プロダクト名 |
| CI_XCODE_PROJECT | プロジェクト名 |
| CI_XCODE_SCHEME | スキーム名 |
| CI_XCODEBUILD_ACTION | アクション（build, test, archive） |
| CI_BUILD_NUMBER | ビルド番号 |
| CI_COMMIT | コミットSHA |
| CI_BRANCH | ブランチ名 |
| CI_TAG | タグ名 |
| CI_PULL_REQUEST_NUMBER | PR番号 |
| CI_ARCHIVE_PATH | アーカイブパス |
| CI_RESULT_BUNDLE_PATH | テスト結果パス |
| CI_WORKFLOW | ワークフロー名 |
| CI_DERIVED_DATA_PATH | DerivedDataパス |

### カスタム環境変数

App Store Connect で設定:

1. **App Store Connect > Xcode Cloud > Settings**
2. **Environment Variables**
3. **「+」で追加**

```
Name: API_KEY
Value: xxxxxxxx
Secret: Yes（機密情報の場合）
```

スクリプトでの使用:

```bash
echo "API Key: $API_KEY"
```

## 署名

### Cloud-Managed Certificates

Xcode Cloud はビルド時に自動で署名を管理:

1. **Cloud signing certificate が自動生成**
2. **App Store Connect で確認可能**
3. **ローカルの証明書は不要**

### Manual Signing

特定の証明書/Profile を使用する場合:

1. **App Store Connect で証明書/Profile を設定**
2. **プロジェクトで Manual Signing を指定**

## ワークフロー例

### 開発ワークフロー

```yaml
Name: Development
Description: PR とプッシュでビルド・テスト

Start Conditions:
  - Branch Changes: develop, feature/*
  - Pull Request: target main

Environment:
  Xcode: Latest Release
  macOS: Latest

Actions:
  - Build (iOS, Debug)
  - Test (iOS, iPhone 15, iPhone 15 Pro)

Post-Actions: なし
```

### リリースワークフロー

```yaml
Name: Release
Description: タグ作成で App Store 配布

Start Conditions:
  - Tag: v*

Environment:
  Xcode: Latest Release
  macOS: Latest

Actions:
  - Archive (iOS, Release)

Post-Actions:
  - TestFlight (Internal)
  - App Store
```

### 日次ビルド

```yaml
Name: Nightly
Description: 毎日自動ビルド・テスト

Start Conditions:
  - Schedule: Daily at 03:00 UTC

Environment:
  Xcode: Latest Release
  macOS: Latest

Actions:
  - Build (iOS, Release)
  - Test (iOS, All Devices)
  - Analyze

Post-Actions:
  - TestFlight (Internal)
```

## モニタリング

### ビルド履歴

1. **App Store Connect > Xcode Cloud**
2. **ビルド一覧を確認**
3. **詳細でログ、テスト結果、成果物を確認**

### 通知設定

1. **App Store Connect > Xcode Cloud > Settings > Notifications**
2. **Slack / Email 通知を設定**

### 使用量

1. **App Store Connect > Xcode Cloud > Usage**
2. **月間使用時間を確認**

## トラブルシューティング

### ビルドが失敗する

1. **ログを確認**
   - Build Logs タブで詳細を確認

2. **ローカルでの再現**
   ```bash
   # クリーンビルドで確認
   xcodebuild clean build -scheme MyApp
   ```

3. **よくある原因**
   - 依存関係の不足
   - 署名設定の問題
   - 環境変数の未設定

### テストが失敗する

1. **Test Reports を確認**
2. **失敗したテストケースを特定**
3. **ローカルで同じデバイス/OSで確認**

### スクリプトが動作しない

1. **実行権限の確認**
   ```bash
   chmod +x ci_scripts/*.sh
   ```

2. **シェバングの確認**
   ```bash
   #!/bin/bash
   ```

3. **パスの確認**
   - 相対パスは `$CI_WORKSPACE` からの相対

## ベストプラクティス

1. **ワークフローの分離**
   - 開発用、リリース用で分ける
   - 目的ごとに最適化

2. **テストの最適化**
   - 並列実行を活用
   - 不要なテストはスキップ

3. **キャッシュの活用**
   - DerivedData は自動キャッシュ
   - 依存関係は毎回インストール

4. **通知の設定**
   - 失敗時は即座に通知
   - 成功は日次サマリー

5. **セキュリティ**
   - シークレットは環境変数で管理
   - ログに機密情報を出力しない

## 料金

| プラン | 月間時間 | 料金 |
|-------|---------|------|
| 無料 | 25時間 | $0 |
| 追加 | 25時間ごと | $49.99 |

**注意**: 無料枠を超えると自動的に課金（設定で制限可能）

## 参考リンク

- [Xcode Cloud Documentation](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Xcode Cloud Custom Build Scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Xcode Cloud Environment Variables](https://developer.apple.com/documentation/xcode/environment-variable-reference)
