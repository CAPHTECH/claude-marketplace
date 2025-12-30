# CI/CD 環境でのコード署名ガイド

## 概要

CI/CD 環境（GitHub Actions、Bitrise、CircleCI など）でiOSアプリをビルド・署名するための設定方法を解説する。

## 事前準備

### 必要なファイル

1. **証明書 (.p12)**
   - 秘密鍵を含む証明書ファイル
   - 強力なパスワードで保護

2. **Provisioning Profile (.mobileprovision)**
   - App Store / Ad Hoc / Development 用 Profile

3. **App Store Connect API キー（推奨）**
   - 自動アップロード用

### 証明書のエクスポート

```bash
# Keychain Access から .p12 をエクスポート
# 1. Keychain Access を開く
# 2. 証明書を右クリック > Export
# 3. .p12 形式で保存
# 4. 強力なパスワードを設定
```

### Base64 エンコード

シークレットとして保存するため Base64 エンコード:

```bash
# 証明書
base64 -i certificate.p12 | pbcopy
# クリップボードにコピーされる

# Provisioning Profile
base64 -i profile.mobileprovision | pbcopy
```

## GitHub Actions での設定

### シークレットの登録

Settings > Secrets and variables > Actions で以下を登録:

| シークレット名 | 内容 |
|---------------|------|
| `CERTIFICATE_BASE64` | .p12 の Base64 |
| `CERTIFICATE_PASSWORD` | .p12 のパスワード |
| `PROVISIONING_PROFILE_BASE64` | Profile の Base64 |
| `KEYCHAIN_PASSWORD` | 一時 Keychain 用パスワード |

### ワークフロー例

```yaml
name: iOS Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: macos-14

    steps:
    - uses: actions/checkout@v4

    - name: Select Xcode
      run: sudo xcode-select -s /Applications/Xcode_15.2.app

    - name: Install Certificate and Profile
      env:
        CERTIFICATE_BASE64: ${{ secrets.CERTIFICATE_BASE64 }}
        CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
        PROVISIONING_PROFILE_BASE64: ${{ secrets.PROVISIONING_PROFILE_BASE64 }}
        KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
      run: |
        # 一時ファイル用ディレクトリ
        CERTIFICATE_PATH=$RUNNER_TEMP/certificate.p12
        PROFILE_PATH=$RUNNER_TEMP/profile.mobileprovision
        KEYCHAIN_PATH=$RUNNER_TEMP/build.keychain-db

        # Base64 デコード
        echo -n "$CERTIFICATE_BASE64" | base64 --decode -o $CERTIFICATE_PATH
        echo -n "$PROVISIONING_PROFILE_BASE64" | base64 --decode -o $PROFILE_PATH

        # 一時 Keychain 作成
        security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
        security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
        security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

        # 証明書インポート
        security import $CERTIFICATE_PATH -P "$CERTIFICATE_PASSWORD" -A -t cert -f pkcs12 -k $KEYCHAIN_PATH
        security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
        security list-keychain -d user -s $KEYCHAIN_PATH

        # Profile インストール
        mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
        cp $PROFILE_PATH ~/Library/MobileDevice/Provisioning\ Profiles/

    - name: Build
      run: |
        xcodebuild clean build \
          -project MyApp.xcodeproj \
          -scheme MyApp \
          -destination 'generic/platform=iOS' \
          -configuration Release \
          CODE_SIGN_STYLE=Manual \
          PROVISIONING_PROFILE_SPECIFIER="MyApp_AppStore"

    - name: Archive
      run: |
        xcodebuild archive \
          -project MyApp.xcodeproj \
          -scheme MyApp \
          -archivePath $RUNNER_TEMP/MyApp.xcarchive \
          -destination 'generic/platform=iOS' \
          CODE_SIGN_STYLE=Manual \
          PROVISIONING_PROFILE_SPECIFIER="MyApp_AppStore"

    - name: Export IPA
      run: |
        xcodebuild -exportArchive \
          -archivePath $RUNNER_TEMP/MyApp.xcarchive \
          -exportPath $RUNNER_TEMP/export \
          -exportOptionsPlist ExportOptions.plist

    - name: Upload Artifact
      uses: actions/upload-artifact@v4
      with:
        name: app
        path: ${{ runner.temp }}/export/*.ipa

    - name: Cleanup
      if: always()
      run: |
        security delete-keychain $RUNNER_TEMP/build.keychain-db
        rm -f $RUNNER_TEMP/certificate.p12
        rm -f $RUNNER_TEMP/profile.mobileprovision
```

### ExportOptions.plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>XXXXXXXXXX</string>
    <key>uploadSymbols</key>
    <true/>
    <key>destination</key>
    <string>upload</string>
</dict>
</plist>
```

### 配布方法別の ExportOptions

#### App Store

```xml
<key>method</key>
<string>app-store</string>
```

#### Ad Hoc

```xml
<key>method</key>
<string>ad-hoc</string>
<key>thinning</key>
<string>&lt;none&gt;</string>
```

#### Enterprise

```xml
<key>method</key>
<string>enterprise</string>
```

#### Development

```xml
<key>method</key>
<string>development</string>
```

## App Store Connect API キーの活用

### API キーの作成

1. **App Store Connect > Users and Access > Keys**
2. **「+」ボタンで新しいキーを作成**
3. **ロール: App Manager 以上**
4. **キーをダウンロード（1回のみ）**

### GitHub Actions での使用

```yaml
- name: Install App Store Connect API Key
  env:
    API_KEY_BASE64: ${{ secrets.APP_STORE_CONNECT_API_KEY_BASE64 }}
    API_KEY_ID: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
    API_KEY_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_API_ISSUER_ID }}
  run: |
    mkdir -p ~/.appstoreconnect/private_keys
    echo -n "$API_KEY_BASE64" | base64 --decode > ~/.appstoreconnect/private_keys/AuthKey_${API_KEY_ID}.p8

- name: Upload to App Store Connect
  run: |
    xcrun altool --upload-app \
      -f $RUNNER_TEMP/export/MyApp.ipa \
      -t ios \
      --apiKey ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }} \
      --apiIssuer ${{ secrets.APP_STORE_CONNECT_API_ISSUER_ID }}
```

## fastlane との連携

### fastlane match の活用

```ruby
# Matchfile
git_url("git@github.com:company/certificates.git")
storage_mode("git")
type("appstore")
app_identifier(["com.company.myapp"])
```

### GitHub Actions での fastlane 使用

```yaml
- name: Install Ruby
  uses: ruby/setup-ruby@v1
  with:
    ruby-version: '3.2'
    bundler-cache: true

- name: Install fastlane
  run: bundle install

- name: Run fastlane
  env:
    MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
    MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
  run: bundle exec fastlane release
```

## Bitrise での設定

### Code Signing & Files

1. **Workflow Editor > Code Signing & Files**
2. **PROVISIONING PROFILE(S)**: Profile をアップロード
3. **CODE SIGNING IDENTITY(S)**: .p12 をアップロード

### Certificate and Profile Installer ステップ

```yaml
- certificate-and-profile-installer@1:
    inputs:
    - install_defaults: "no"
```

### Xcode Archive ステップ

```yaml
- xcode-archive@4:
    inputs:
    - project_path: MyApp.xcodeproj
    - scheme: MyApp
    - configuration: Release
    - export_method: app-store
    - team_id: XXXXXXXXXX
```

## CircleCI での設定

### 環境変数

Project Settings > Environment Variables:

| 変数名 | 内容 |
|-------|------|
| `CERTIFICATE_BASE64` | .p12 の Base64 |
| `CERTIFICATE_PASSWORD` | .p12 のパスワード |
| `PROVISIONING_PROFILE_BASE64` | Profile の Base64 |

### config.yml

```yaml
version: 2.1

orbs:
  macos: circleci/macos@2

jobs:
  build:
    macos:
      xcode: 15.2.0
    steps:
      - checkout
      - run:
          name: Install Certificates
          command: |
            echo $CERTIFICATE_BASE64 | base64 --decode > certificate.p12
            echo $PROVISIONING_PROFILE_BASE64 | base64 --decode > profile.mobileprovision

            security create-keychain -p "" build.keychain
            security default-keychain -s build.keychain
            security unlock-keychain -p "" build.keychain
            security import certificate.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign
            security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "" build.keychain

            mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
            cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/

            rm certificate.p12 profile.mobileprovision
      - run:
          name: Build
          command: |
            xcodebuild archive \
              -project MyApp.xcodeproj \
              -scheme MyApp \
              -archivePath MyApp.xcarchive
```

## セキュリティベストプラクティス

### シークレット管理

1. **環境変数の暗号化**
   - 各CIサービスの暗号化機能を使用
   - 平文での保存は絶対に避ける

2. **アクセス制限**
   - シークレットへのアクセス権限を最小化
   - フォークからのPRではシークレットを使用しない

3. **定期的なローテーション**
   - 証明書・APIキーは定期的に更新
   - 退職者がいる場合は即座に更新

### 一時ファイルの扱い

```bash
# ビルド後のクリーンアップ
security delete-keychain $KEYCHAIN_PATH
rm -f $CERTIFICATE_PATH
rm -f $PROFILE_PATH
```

### ログの注意

```yaml
# パスワードを含むコマンドは set +x で無効化
- name: Install Certificate
  run: |
    set +x
    security import certificate.p12 -P "$CERTIFICATE_PASSWORD" ...
    set -x
```

## トラブルシューティング

### 「The specified item could not be found in the keychain」

**原因**: Keychain が正しくセットアップされていない

**解決方法**:
```bash
# Keychain をデフォルトに設定
security list-keychain -d user -s $KEYCHAIN_PATH
```

### 「User interaction is not allowed」

**原因**: Keychain がロックされている、またはユーザー確認が必要

**解決方法**:
```bash
# Keychain をアンロック
security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

# コード署名の許可
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
```

### 「Provisioning profile doesn't include signing certificate」

**原因**: Profile と証明書の不一致

**解決方法**:
1. Profile に含まれる証明書を確認
2. 正しい証明書をCIにアップロード
3. または Profile を再生成

### ビルドは成功するが署名されない

**原因**: ビルド設定が Manual になっていない

**解決方法**:
```bash
xcodebuild ... \
  CODE_SIGN_STYLE=Manual \
  CODE_SIGN_IDENTITY="Apple Distribution" \
  PROVISIONING_PROFILE_SPECIFIER="ProfileName"
```

## 参考リンク

- [GitHub Actions: iOS builds](https://docs.github.com/en/actions/deployment/deploying-xcode-applications)
- [Bitrise: iOS code signing](https://devcenter.bitrise.io/en/code-signing/ios-code-signing.html)
- [CircleCI: iOS builds](https://circleci.com/docs/ios-codesigning/)
- [fastlane match](https://docs.fastlane.tools/actions/match/)
