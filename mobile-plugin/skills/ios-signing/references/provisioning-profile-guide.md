# Provisioning Profile 管理ガイド

## 概要

Provisioning Profile は、アプリ・証明書・デバイス・Entitlements を結びつける設定ファイル。iOS アプリの実行・配布に必須。

## Profile の種類

### 開発用

| 種類 | 用途 | デバイス制限 |
|------|------|-------------|
| iOS App Development | 開発・デバッグ | 登録デバイスのみ |
| tvOS App Development | tvOS 開発 | 登録デバイスのみ |
| watchOS App Development | watchOS 開発 | 登録デバイスのみ |
| macOS App Development | macOS 開発 | なし |

### 配布用

| 種類 | 用途 | デバイス制限 |
|------|------|-------------|
| App Store | App Store 配布 | なし（Apple が管理） |
| Ad Hoc | 限定テスト配布 | 登録デバイス（最大100台） |
| Enterprise | 社内配布 | なし（Enterprise Program 限定） |

### 特殊用途

| 種類 | 用途 |
|------|------|
| Mac Installer Distribution | Mac アプリのインストーラ署名 |
| Developer ID | Mac アプリの App Store 外配布 |

## Profile の構成要素

Profile には以下の情報が含まれる:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist>
<dict>
    <key>AppIDName</key>
    <string>MyApp</string>

    <key>ApplicationIdentifierPrefix</key>
    <array>
        <string>XXXXXXXXXX</string>
    </array>

    <key>CreationDate</key>
    <date>2024-01-01T00:00:00Z</date>

    <key>DeveloperCertificates</key>
    <array>
        <!-- 証明書データ（Base64） -->
    </array>

    <key>Entitlements</key>
    <dict>
        <key>application-identifier</key>
        <string>XXXXXXXXXX.com.company.myapp</string>
        <!-- その他の Entitlements -->
    </dict>

    <key>ExpirationDate</key>
    <date>2025-01-01T00:00:00Z</date>

    <key>Name</key>
    <string>MyApp Development</string>

    <key>ProvisionedDevices</key>
    <array>
        <string>00000000-0000000000000000</string>
    </array>

    <key>TeamIdentifier</key>
    <array>
        <string>XXXXXXXXXX</string>
    </array>

    <key>UUID</key>
    <string>xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</string>
</dict>
</plist>
```

## Profile の作成

### Apple Developer Portal から

1. **[Apple Developer Portal](https://developer.apple.com/) にログイン**
2. **Certificates, Identifiers & Profiles に移動**
3. **Profiles > 「+」ボタン**
4. **Profile タイプを選択**

#### Development Profile の作成

1. **「iOS App Development」を選択**
2. **App ID を選択**
   - 既存の App ID を選択
   - または「Wildcard App ID」（*.com.company.*）を使用
3. **証明書を選択**
   - 使用する開発証明書にチェック
4. **デバイスを選択**
   - テストに使用するデバイスにチェック
5. **Profile 名を入力**
   - 例: `MyApp_Development`
6. **「Generate」をクリック**
7. **Profile をダウンロード**

#### App Store Profile の作成

1. **「App Store」を選択**
2. **App ID を選択**
3. **配布証明書を選択**
   - Apple Distribution 証明書
4. **Profile 名を入力**
   - 例: `MyApp_AppStore`
5. **「Generate」をクリック**

#### Ad Hoc Profile の作成

1. **「Ad Hoc」を選択**
2. **App ID を選択**
3. **配布証明書を選択**
4. **デバイスを選択**
   - テスト配布先のデバイスにチェック
5. **Profile 名を入力**
   - 例: `MyApp_AdHoc`
6. **「Generate」をクリック**

### Xcode から（Automatic Signing）

1. **Xcode > Preferences > Accounts**
2. **Apple ID を追加/選択**
3. **「Download Manual Profiles」をクリック**

Xcode が自動的に必要な Profile を生成・管理。

## Profile のインストール

### ダウンロードした Profile のインストール

```bash
# ダブルクリックでインストール
# または
open /path/to/profile.mobileprovision

# コマンドラインでコピー
cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/
```

### インストール先

```
~/Library/MobileDevice/Provisioning Profiles/
```

## Profile の確認

### インストール済み Profile の一覧

```bash
ls -la ~/Library/MobileDevice/Provisioning\ Profiles/
```

### Profile の内容確認

```bash
# Profile の内容をデコード
security cms -D -i ~/Library/MobileDevice/Provisioning\ Profiles/XXXX.mobileprovision

# 特定の情報を抽出
security cms -D -i profile.mobileprovision | plutil -extract Name raw -

# 有効期限を確認
security cms -D -i profile.mobileprovision | plutil -extract ExpirationDate raw -

# UUID を確認
security cms -D -i profile.mobileprovision | plutil -extract UUID raw -

# 含まれる証明書のSHA-1を確認
security cms -D -i profile.mobileprovision | plutil -extract DeveloperCertificates raw - | \
  openssl x509 -inform DER -noout -fingerprint
```

### Xcode で確認

1. **Xcode > Preferences > Accounts**
2. **チームを選択**
3. **「Manage Certificates」または「Download Manual Profiles」**

## Profile の更新

### 更新が必要なケース

- 証明書を更新した
- 新しいデバイスを追加した
- Capabilities（Entitlements）を変更した
- Profile の有効期限が近い

### 更新手順

1. **Apple Developer Portal にログイン**
2. **対象の Profile を選択**
3. **「Edit」をクリック**
4. **必要な変更を行う**
5. **「Generate」をクリック**
6. **新しい Profile をダウンロード・インストール**

### 自動更新（Xcode）

Automatic Signing を使用している場合、Xcode が必要に応じて自動更新。

## デバイスの登録

### UDID の取得

```bash
# 接続されたデバイスの UDID を取得
system_profiler SPUSBDataType | grep -A 11 "iPhone\|iPad" | grep "Serial Number"

# Xcode から
# Window > Devices and Simulators > 対象デバイスを選択 > Identifier
```

### Apple Developer Portal での登録

1. **Devices > 「+」ボタン**
2. **Platform を選択**
3. **Device Name と UDID を入力**
4. **「Register」をクリック**

### 年間デバイス制限

| プラットフォーム | 制限数 |
|-----------------|--------|
| iPhone / iPad | 100 台 / 年 |
| Apple Watch | 100 台 / 年 |
| Apple TV | 100 台 / 年 |
| Mac | 100 台 / 年 |

**注意**: 登録したデバイスを削除しても、年間枠は回復しない（次の更新サイクルまで）。

## Entitlements との関係

Profile には使用可能な Entitlements が定義されている。アプリの Entitlements は Profile の範囲内でなければならない。

### よく使う Entitlements

| Entitlement | 用途 |
|-------------|------|
| aps-environment | Push Notification |
| com.apple.developer.applesignin | Sign in with Apple |
| com.apple.developer.associated-domains | Universal Links / App Clips |
| com.apple.developer.healthkit | HealthKit |
| com.apple.developer.icloud-container-identifiers | iCloud |
| keychain-access-groups | Keychain 共有 |

### Capabilities の追加

1. **Apple Developer Portal > Identifiers > App ID を選択**
2. **「Capabilities」タブで必要な機能を有効化**
3. **Profile を再生成**
4. **Xcode プロジェクトで Capability を追加**

## トラブルシューティング

### 「Provisioning profile doesn't include signing certificate」

**原因**: Profile に含まれる証明書が Keychain に存在しない

**解決方法**:
1. Profile を再生成して正しい証明書を含める
2. または対応する証明書をインストール

### 「App ID doesn't match bundle identifier」

**原因**: Profile の App ID とプロジェクトの Bundle ID が一致しない

**解決方法**:
1. プロジェクトの Bundle ID を確認・修正
2. または正しい App ID で Profile を再生成

### 「Provisioning profile has expired」

**原因**: Profile の有効期限が切れている

**解決方法**:
1. Apple Developer Portal で Profile を再生成
2. 新しい Profile をダウンロード・インストール

### 「Device is not included in the provisioning profile」

**原因**: テスト対象デバイスが Profile に含まれていない

**解決方法**:
1. Apple Developer Portal でデバイスを登録
2. Profile を編集してデバイスを追加
3. Profile を再生成

### 「Missing entitlement」

**原因**: アプリが要求する Entitlement が Profile に含まれていない

**解決方法**:
1. App ID で対応する Capability を有効化
2. Profile を再生成

## ベストプラクティス

1. **命名規則**
   - `{AppName}_{Environment}_{Type}`
   - 例: `MyApp_Production_AppStore`

2. **Profile の整理**
   - 不要な Profile は定期的に削除
   - 古い Profile が使われていないか確認

3. **Wildcard vs Explicit App ID**
   - 開発初期: Wildcard が便利
   - 本番: Explicit App ID を使用（特定の Capabilities に必要）

4. **有効期限の管理**
   - Development Profile: 1年
   - Distribution Profile: 1年
   - カレンダーにリマインダーを設定

5. **Automatic Signing の活用**
   - 開発時は Automatic Signing を推奨
   - リリースビルドは Manual Signing を検討

## 参考リンク

- [Apple Developer: Provisioning Profiles](https://developer.apple.com/help/account/manage-profiles/create-a-development-provisioning-profile)
- [Maintaining Your Signing Identities and Certificates](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/resolving_common_notarization_issues)
