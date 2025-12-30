# ExportOptions.plist リファレンス

## 概要

ExportOptions.plist は `xcodebuild -exportArchive` で使用する設定ファイル。エクスポート方法、署名設定、配布オプションを定義する。

## 基本構造

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- 設定項目 -->
</dict>
</plist>
```

## 配布方法別テンプレート

### App Store

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
    <key>signingStyle</key>
    <string>manual</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>com.company.myapp</key>
        <string>MyApp_AppStore</string>
    </dict>
</dict>
</plist>
```

### App Store（自動アップロードなし）

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
    <string>export</string>
</dict>
</plist>
```

### Ad Hoc

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>ad-hoc</string>
    <key>teamID</key>
    <string>XXXXXXXXXX</string>
    <key>compileBitcode</key>
    <false/>
    <key>thinning</key>
    <string>&lt;none&gt;</string>
    <key>signingStyle</key>
    <string>manual</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>com.company.myapp</key>
        <string>MyApp_AdHoc</string>
    </dict>
</dict>
</plist>
```

### Enterprise

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>enterprise</string>
    <key>teamID</key>
    <string>XXXXXXXXXX</string>
    <key>compileBitcode</key>
    <false/>
    <key>thinning</key>
    <string>&lt;none&gt;</string>
    <key>manifest</key>
    <dict>
        <key>appURL</key>
        <string>https://example.com/apps/myapp.ipa</string>
        <key>displayImageURL</key>
        <string>https://example.com/apps/icon-57.png</string>
        <key>fullSizeImageURL</key>
        <string>https://example.com/apps/icon-512.png</string>
    </dict>
</dict>
</plist>
```

### Development

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>development</string>
    <key>teamID</key>
    <string>XXXXXXXXXX</string>
    <key>compileBitcode</key>
    <false/>
    <key>thinning</key>
    <string>&lt;none&gt;</string>
    <key>signingStyle</key>
    <string>automatic</string>
</dict>
</plist>
```

## 設定項目詳細

### method（必須）

エクスポート方法を指定。

| 値 | 説明 |
|---|---|
| `app-store` | App Store 配布用 |
| `ad-hoc` | Ad Hoc 配布用（登録デバイス限定） |
| `enterprise` | Enterprise（社内）配布用 |
| `development` | 開発用 |
| `validation` | App Store 検証のみ |
| `package` | 開発者署名パッケージ（macOS） |
| `developer-id` | Developer ID 署名（macOS） |
| `mac-application` | Mac App Store 配布用 |

### teamID

開発チームIDを指定（10文字の英数字）。

```xml
<key>teamID</key>
<string>XXXXXXXXXX</string>
```

### signingStyle

署名スタイルを指定。

| 値 | 説明 |
|---|---|
| `automatic` | Xcode が自動で管理 |
| `manual` | 手動で指定 |

### signingCertificate

使用する証明書を指定。

```xml
<key>signingCertificate</key>
<string>Apple Distribution</string>
```

| 値 | 説明 |
|---|---|
| `Apple Development` | 開発用証明書 |
| `Apple Distribution` | 配布用証明書 |
| `iOS Development` | iOS開発用（レガシー） |
| `iOS Distribution` | iOS配布用（レガシー） |
| 証明書の SHA-1 | 特定の証明書を指定 |

### provisioningProfiles

Bundle ID と Profile 名のマッピング。

```xml
<key>provisioningProfiles</key>
<dict>
    <key>com.company.myapp</key>
    <string>MyApp_AppStore</string>
    <key>com.company.myapp.widget</key>
    <string>MyAppWidget_AppStore</string>
</dict>
```

### destination

App Store 配布時の動作を指定。

| 値 | 説明 |
|---|---|
| `upload` | App Store Connect に直接アップロード |
| `export` | IPA ファイルとしてエクスポートのみ |

### uploadSymbols

シンボル（dSYM）を App Store Connect にアップロードするか。

```xml
<key>uploadSymbols</key>
<true/>
```

### compileBitcode

Bitcode を再コンパイルするか（iOS 16以降は不要）。

```xml
<key>compileBitcode</key>
<false/>
```

### thinning

App Thinning の設定。

| 値 | 説明 |
|---|---|
| `<none>` | すべてのデバイス用リソースを含む |
| `<thin-for-all-variants>` | すべてのバリアント用に個別IPA作成 |
| デバイス名 | 特定デバイス用（例: `iPhone14,2`） |

### stripSwiftSymbols

Swift シンボルをストリップするか。

```xml
<key>stripSwiftSymbols</key>
<true/>
```

### iCloudContainerEnvironment

iCloud コンテナの環境を指定。

| 値 | 説明 |
|---|---|
| `Development` | 開発環境 |
| `Production` | 本番環境 |

```xml
<key>iCloudContainerEnvironment</key>
<string>Production</string>
```

### manifest（Enterprise 専用）

Over-the-Air インストール用の manifest 設定。

```xml
<key>manifest</key>
<dict>
    <key>appURL</key>
    <string>https://example.com/app.ipa</string>
    <key>displayImageURL</key>
    <string>https://example.com/icon-57.png</string>
    <key>fullSizeImageURL</key>
    <string>https://example.com/icon-512.png</string>
    <key>assetPackManifestURL</key>
    <string>https://example.com/manifest.plist</string>
</dict>
```

### onDemandResourcesAssetPacksBaseURL

On-Demand Resources のベースURL。

```xml
<key>onDemandResourcesAssetPacksBaseURL</key>
<string>https://cdn.example.com/odr/</string>
```

## 複数ターゲット対応

App Extension や Widget を含む場合:

```xml
<key>provisioningProfiles</key>
<dict>
    <key>com.company.myapp</key>
    <string>MyApp_AppStore</string>
    <key>com.company.myapp.notificationservice</key>
    <string>MyAppNotification_AppStore</string>
    <key>com.company.myapp.widget</key>
    <string>MyAppWidget_AppStore</string>
    <key>com.company.myapp.watchkitapp</key>
    <string>MyAppWatch_AppStore</string>
    <key>com.company.myapp.watchkitapp.watchkitextension</key>
    <string>MyAppWatchExtension_AppStore</string>
</dict>
```

## アーカイブから ExportOptions.plist を生成

既存のアーカイブから設定を抽出:

```bash
# アーカイブの ExportOptions.plist を確認
xcodebuild -exportArchive \
  -archivePath App.xcarchive \
  -exportPath export \
  -exportOptionsPlist - <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
</dict>
</plist>
EOF
```

## トラブルシューティング

### 「Provisioning profile doesn't include signing certificate」

Profile に含まれる証明書と `signingCertificate` が一致しない。

**解決方法**:
- `signingCertificate` を削除して自動選択させる
- または正しい証明書名を指定

### 「No signing certificate found」

指定した証明書が Keychain に存在しない。

**解決方法**:
- 証明書をインストール
- `signingStyle` を `automatic` に変更

### 「App has been rejected because it uses a provisioning profile」

間違った Profile タイプを使用している。

**解決方法**:
- App Store 配布には App Store 用 Profile を使用
- `method` と Profile タイプを一致させる

## ベストプラクティス

1. **環境別に ExportOptions.plist を分ける**
   ```
   ExportOptions/
   ├── AppStore.plist
   ├── AdHoc.plist
   └── Development.plist
   ```

2. **バージョン管理に含める**
   - 設定の変更履歴を追跡可能に

3. **CI/CD での使用**
   - 環境変数で teamID などを動的に設定

4. **セキュリティ**
   - teamID 以外の機密情報は含めない
   - Profile 名はセキュアではないので問題なし
