# App Store Connect ガイド

## 概要

App Store Connect は、App Store へのアプリ公開、TestFlight でのテスト配布、分析、売上管理などを行うためのポータル。

## アカウントと権限

### ロール

| ロール | 説明 | 主な権限 |
|-------|------|---------|
| Account Holder | アカウント所有者 | すべての権限 |
| Admin | 管理者 | ユーザー管理、すべてのアプリ管理 |
| App Manager | アプリ管理者 | アプリの作成・管理、TestFlight |
| Developer | 開発者 | ビルドアップロード、TestFlight（内部） |
| Marketing | マーケティング | アプリ情報の編集 |
| Finance | 財務 | 売上・支払いレポート |

### ユーザー追加

1. **Users and Access > 「+」ボタン**
2. **メールアドレスを入力**
3. **ロールを選択**
4. **アプリへのアクセス権を設定**

## アプリの登録

### 新規アプリの作成

1. **App Store Connect にログイン**
2. **My Apps > 「+」ボタン > New App**
3. **必須情報を入力**:
   - Platforms: iOS / macOS / tvOS / watchOS
   - Name: App Store での表示名
   - Primary Language: 主要言語
   - Bundle ID: プロジェクトと一致
   - SKU: 内部管理用ID（ユニーク）
   - User Access: 全員 / 特定のユーザー

### Bundle ID の登録

Apple Developer Portal で事前に登録が必要:

1. **Certificates, Identifiers & Profiles > Identifiers**
2. **「+」ボタン > App IDs**
3. **Bundle ID を入力**
4. **Capabilities を設定**

## アプリ情報の設定

### App Information

- **Name**: App Store での表示名（30文字以内）
- **Subtitle**: サブタイトル（30文字以内）
- **Category**: プライマリ/セカンダリカテゴリ
- **Content Rights**: サードパーティコンテンツの有無
- **Age Rating**: App Store の年齢制限

### Pricing and Availability

- **Price**: 価格帯の設定
- **Availability**: 配布する国/地域
- **Pre-Orders**: 予約注文の設定

### App Privacy

**必須項目**（2020年12月以降）:

1. **Privacy Policy URL**: プライバシーポリシーのURL
2. **Data Types**: 収集するデータの種類
3. **Data Use**: データの使用目的

### 収集データの例

| データタイプ | 例 |
|-------------|-----|
| Contact Info | 名前、メール、電話番号 |
| Health & Fitness | ヘルスデータ、フィットネスデータ |
| Financial Info | 支払い情報、クレジットカード |
| Location | 正確な位置情報、おおまかな位置情報 |
| Contacts | 連絡先リスト |
| User Content | 写真、動画、音声 |
| Browsing History | 閲覧履歴 |
| Search History | 検索履歴 |
| Identifiers | デバイスID、ユーザーID |
| Usage Data | 操作履歴、クラッシュログ |
| Diagnostics | パフォーマンスデータ |

## バージョン管理

### 新バージョンの作成

1. **App Store タブ > 「+」ボタン（iOS App の横）**
2. **バージョン番号を入力**（例: 1.2.0）

### バージョン情報の編集

- **What's New**: リリースノート（各言語）
- **Description**: アプリの説明（各言語）
- **Keywords**: 検索キーワード（各言語、100文字以内）
- **Support URL**: サポートページのURL
- **Marketing URL**: プロモーションページのURL

### スクリーンショット

| デバイス | サイズ（ピクセル） | 必須 |
|---------|-------------------|------|
| iPhone 6.7" | 1290 x 2796 | はい |
| iPhone 6.5" | 1284 x 2778 または 1242 x 2688 | はい |
| iPhone 5.5" | 1242 x 2208 | はい |
| iPad Pro 12.9" | 2048 x 2732 | iPadアプリの場合 |
| iPad Pro 11" | 1668 x 2388 | iPadアプリの場合 |

**各サイズ最大10枚まで**

### App Preview（動画）

- 最大30秒
- MP4 または MOV 形式
- H.264 コーデック

## ビルドのアップロード

### Xcode から

1. **Product > Archive**
2. **Organizer > Distribute App**
3. **App Store Connect を選択**
4. **Upload**

### コマンドライン

```bash
# altool を使用
xcrun altool --upload-app \
  -f App.ipa \
  -t ios \
  --apiKey API_KEY_ID \
  --apiIssuer ISSUER_ID

# notarytool を使用（macOS アプリ）
xcrun notarytool submit App.pkg \
  --key AuthKey_XXXX.p8 \
  --key-id API_KEY_ID \
  --issuer ISSUER_ID \
  --wait
```

### Transporter

1. **Transporter アプリをインストール**
2. **Apple ID でログイン**
3. **IPA ファイルをドラッグ&ドロップ**
4. **「配信」をクリック**

## 審査

### 審査提出

1. **すべての必須情報を入力**
2. **ビルドを選択**
3. **Submit for Review**

### 審査ガイドライン

主要なチェックポイント:

| カテゴリ | 内容 |
|---------|------|
| Safety | 不適切なコンテンツ、ユーザーの安全 |
| Performance | バグ、クラッシュ、完成度 |
| Business | 課金、広告、サブスクリプション |
| Design | UIガイドライン、使いやすさ |
| Legal | プライバシー、知的財産権 |

### よくあるリジェクト理由

1. **Guideline 2.1 - Performance: App Completeness**
   - クラッシュ、未完成の機能

2. **Guideline 2.3 - Performance: Accurate Metadata**
   - スクリーンショットと実際のアプリが異なる

3. **Guideline 4.0 - Design**
   - Apple UI ガイドライン違反

4. **Guideline 5.1.1 - Data Collection and Storage**
   - プライバシー情報の不備

### 審査加速（Expedited Review）

緊急の場合にリクエスト可能:

1. **App Store Connect > 対象バージョン**
2. **「Request an expedited review」リンク**
3. **理由を詳細に説明**

## リリース

### 手動リリース

1. **審査通過後、App Store タブで「Release This Version」**

### 自動リリース

- **Automatically release this version**: 審査通過後すぐに公開
- **Manually release this version**: 手動で公開
- **Automatically release on a date**: 指定日時に自動公開

### 段階的ロールアウト

1. **App Store タブ > Phased Release for Automatic Updates**
2. **有効化**

| 日数 | 割合 |
|-----|------|
| 1日目 | 1% |
| 2日目 | 2% |
| 3日目 | 5% |
| 4日目 | 10% |
| 5日目 | 20% |
| 6日目 | 50% |
| 7日目 | 100% |

## App Store Connect API

### API キーの作成

1. **Users and Access > Keys**
2. **「+」ボタン**
3. **名前とロールを設定**
4. **キーをダウンロード（1回のみ）**

### 認証

JWT を使用:

```bash
# JWT 生成（Python例）
import jwt
import time

private_key = open('AuthKey_XXXX.p8').read()
token = jwt.encode({
    'iss': 'ISSUER_ID',
    'iat': int(time.time()),
    'exp': int(time.time()) + 1200,
    'aud': 'appstoreconnect-v1'
}, private_key, algorithm='ES256', headers={'kid': 'KEY_ID'})
```

### API 使用例

```bash
# アプリ一覧を取得
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/apps"

# ビルド一覧を取得
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/builds"
```

## トラブルシューティング

### ビルドが処理中のまま

- 通常5-30分で完了
- 1時間以上かかる場合は Apple サポートに連絡

### 「Missing Compliance」警告

暗号化に関する申告が必要:

1. **TestFlight > ビルドを選択**
2. **「Provide Export Compliance Information」**
3. **質問に回答**

### 「Missing Push Notification Entitlement」

APNs 証明書/キーが設定されていない:

1. **Apple Developer Portal で APNs を設定**
2. **App Store Connect > Keys で確認**

## ベストプラクティス

1. **バージョン番号の管理**
   - セマンティックバージョニングを使用
   - ビルド番号は常にインクリメント

2. **スクリーンショットの準備**
   - 事前に全サイズ用意
   - ローカライズ版も準備

3. **リリースノート**
   - ユーザーにとって意味のある変更を記載
   - 技術的な詳細は避ける

4. **審査対応**
   - 審査ノートに必要な情報を記載
   - テストアカウントを提供

5. **モニタリング**
   - クラッシュレポートを定期確認
   - ユーザーレビューに対応
