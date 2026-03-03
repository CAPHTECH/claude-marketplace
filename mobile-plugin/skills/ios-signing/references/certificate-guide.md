# iOS 証明書管理ガイド

## 概要

iOS アプリのコード署名には Apple が発行する証明書が必要。証明書は公開鍵暗号に基づき、アプリの出所と改ざんされていないことを保証する。

## 証明書の種類

### 開発用証明書

| 種類 | 用途 | 有効期限 |
|------|------|----------|
| Apple Development | 開発・デバッグ用 | 1年 |
| iOS Development（旧） | iOS開発用（レガシー） | 1年 |
| Mac Development（旧） | macOS開発用（レガシー） | 1年 |

**Apple Development**: iOS、macOS、tvOS、watchOS すべてで使用可能な統合証明書（推奨）

### 配布用証明書

| 種類 | 用途 | 有効期限 |
|------|------|----------|
| Apple Distribution | App Store / Ad Hoc / Enterprise 配布 | 1年 |
| iOS Distribution（旧） | iOS配布用（レガシー） | 1年 |
| Mac App Distribution（旧） | Mac App Store用（レガシー） | 1年 |

### その他の証明書

| 種類 | 用途 |
|------|------|
| Apple Push Notification service SSL | APNs 通信用 |
| Pass Type ID Certificate | Wallet Pass 署名用 |
| Website Push ID Certificate | Safari Push Notification 用 |

## 証明書の作成

### 手順 1: CSR（Certificate Signing Request）の作成

1. **Keychain Access を起動**
2. **メニュー > Certificate Assistant > Request a Certificate From a Certificate Authority**
3. **以下を入力**:
   - User Email Address: Apple ID のメールアドレス
   - Common Name: 任意の名前（証明書の識別用）
   - CA Email Address: 空欄
4. **「Saved to disk」を選択**
5. **CSR ファイルを保存**

### 手順 2: Apple Developer Portal で証明書発行

1. **[Apple Developer Portal](https://developer.apple.com/) にログイン**
2. **Certificates, Identifiers & Profiles に移動**
3. **Certificates > 「+」ボタン**
4. **証明書タイプを選択**:
   - Apple Development（開発用）
   - Apple Distribution（配布用）
5. **CSR ファイルをアップロード**
6. **証明書をダウンロード**

### 手順 3: 証明書のインストール

```bash
# ダウンロードした .cer ファイルをダブルクリック
# または
security add-certificates /path/to/certificate.cer
```

## 証明書の確認

### Keychain Access で確認

1. **Keychain Access を起動**
2. **「login」キーチェーンを選択**
3. **「My Certificates」カテゴリを選択**
4. **「Apple Development」または「Apple Distribution」を確認**

秘密鍵が紐付いていない場合、証明書の横に警告アイコンが表示される。

### コマンドラインで確認

```bash
# 署名に使用可能な証明書一覧
security find-identity -v -p codesigning

# 詳細情報
security find-certificate -c "Apple Development" -p | openssl x509 -noout -text
```

### 有効期限の確認

```bash
# 証明書の有効期限を確認
security find-certificate -c "Apple Development" -p | \
  openssl x509 -noout -dates
```

出力例:
```
notBefore=Jan  1 00:00:00 2024 GMT
notAfter=Jan  1 00:00:00 2025 GMT
```

## 証明書のエクスポート（.p12）

CI/CD 環境や他のマシンで使用するために、秘密鍵付きでエクスポート。

### Keychain Access から

1. **証明書を右クリック > Export**
2. **ファイル形式: Personal Information Exchange (.p12)**
3. **パスワードを設定**（強力なパスワードを使用）

### コマンドラインから

```bash
# 証明書と秘密鍵をエクスポート
security export -k ~/Library/Keychains/login.keychain-db \
  -t identities \
  -f pkcs12 \
  -P "password" \
  -o certificate.p12
```

## 証明書のインポート（.p12）

```bash
# Keychain にインポート
security import certificate.p12 \
  -k ~/Library/Keychains/login.keychain-db \
  -P "password" \
  -T /usr/bin/codesign

# コード署名を許可
security set-key-partition-list \
  -S apple-tool:,apple:,codesign: \
  -s \
  -k "keychain-password" \
  ~/Library/Keychains/login.keychain-db
```

## 証明書の更新

### 期限切れ前の更新手順

1. **新しい CSR を作成**（既存の秘密鍵を再利用可能）
2. **Apple Developer Portal で新しい証明書を発行**
3. **新しい証明書をインストール**
4. **Provisioning Profile を再生成**
5. **CI/CD シークレットを更新**

### 既存の秘密鍵を再利用する場合

1. **Keychain Access で既存の秘密鍵を選択**
2. **右クリック > Request a Certificate From a Certificate Authority**
3. **生成された CSR を使用**

## 証明書の失効

### 失効が必要なケース

- 秘密鍵が漏洩した
- 証明書が不要になった
- チームメンバーが退職した

### 失効手順

1. **Apple Developer Portal にログイン**
2. **Certificates を選択**
3. **対象の証明書を選択**
4. **「Revoke」ボタンをクリック**

**注意**: 失効した証明書で署名されたアプリは影響を受けない（既にインストール済みのアプリは動作継続）。

## トラブルシューティング

### 「秘密鍵がありません」

**原因**: 証明書に対応する秘密鍵が Keychain にない

**解決方法**:
1. CSR を作成したマシンから .p12 をエクスポート
2. 対象マシンにインポート

### 「証明書が信頼されていません」

**原因**: Apple のルート証明書がインストールされていない

**解決方法**:
```bash
# Apple のルート証明書を取得
curl -O https://www.apple.com/appleca/AppleIncRootCertificate.cer

# インストール
security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain AppleIncRootCertificate.cer
```

### 「証明書が期限切れです」

**原因**: 証明書の有効期限が過ぎている

**解決方法**:
1. 新しい証明書を作成
2. Provisioning Profile を再生成
3. 古い証明書を削除（任意）

### 複数の証明書が存在する

**原因**: 複数のバージョンの証明書がインストールされている

**解決方法**:
```bash
# 重複確認
security find-identity -v -p codesigning | grep "Apple Development"

# 不要な証明書を削除（Keychain Access で実施）
```

## ベストプラクティス

1. **証明書は最小限に**
   - チームで共有する場合は配布用のみ
   - 個人の開発証明書は各自で管理

2. **秘密鍵のバックアップ**
   - p12 ファイルを安全な場所にバックアップ
   - パスワードは別途管理

3. **定期的な確認**
   - 毎月の証明書有効期限チェック
   - カレンダーにリマインダーを設定

4. **CI/CD での運用**
   - 専用の証明書を作成
   - シークレット管理サービスを使用
   - 定期的なローテーション

5. **チーム管理**
   - Apple Developer Portal のロール管理を活用
   - 証明書へのアクセス権限を最小化

## 参考リンク

- [Apple Developer: Certificates](https://developer.apple.com/support/certificates/)
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
