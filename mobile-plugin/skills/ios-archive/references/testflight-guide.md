# TestFlight 配布ガイド

## 概要

TestFlight は Apple 公式のベータテスト配布プラットフォーム。App Store 配布前のテストに使用する。

## テスターの種類

### 内部テスター

| 項目 | 内容 |
|------|------|
| 対象 | App Store Connect のチームメンバー |
| 人数制限 | 最大100名 |
| App Review | 不要 |
| 有効期間 | 90日 |
| テスト開始 | ビルド処理完了後すぐ |

### 外部テスター

| 項目 | 内容 |
|------|------|
| 対象 | メールで招待した外部ユーザー |
| 人数制限 | 最大10,000名 |
| App Review | 初回ビルドは必要（通常24-48時間） |
| 有効期間 | 90日 |
| 配布方法 | 個別招待 / Public Link |

## ビルドのアップロード

### 前提条件

- App Store 用 Provisioning Profile で署名
- App Store Connect にアプリが登録済み
- ビルド番号がユニーク

### アップロード方法

#### Xcode から

1. **Product > Archive**
2. **Organizer で Distribute App**
3. **App Store Connect を選択**
4. **Upload を選択**
5. **完了を待つ**

#### コマンドライン

```bash
# altool でアップロード
xcrun altool --upload-app \
  -f MyApp.ipa \
  -t ios \
  --apiKey API_KEY_ID \
  --apiIssuer ISSUER_ID
```

### アップロード後の処理

1. **Processing**: ビルドの検証と処理（5-30分）
2. **Ready to Submit**: TestFlight で利用可能

## 内部テスターへの配布

### グループの作成

1. **App Store Connect > TestFlight > Internal Testing**
2. **「+」ボタンでグループ作成**
3. **グループ名を入力**

### テスターの追加

1. **グループを選択**
2. **Testers セクションで「+」**
3. **App Store Connect ユーザーを選択**

### ビルドの有効化

1. **グループを選択**
2. **Builds セクションで「+」**
3. **配布するビルドを選択**
4. **「Add」をクリック**

### テスト情報の入力

```
What to Test:
- 新機能: ダークモード対応
- 改善: ログイン画面のパフォーマンス向上

Known Issues:
- 設定画面で一部テキストが切れる場合があります
- プッシュ通知が遅延することがあります
```

## 外部テスターへの配布

### グループの作成

1. **App Store Connect > TestFlight > External Testing**
2. **「+」ボタンでグループ作成**
3. **グループ名を入力**

### テスターの招待

#### 個別招待

1. **グループを選択**
2. **Testers セクションで「+」**
3. **Add New Testers を選択**
4. **メールアドレスを入力**（カンマ区切りで複数可）
5. **Add をクリック**

#### Public Link

1. **グループを選択**
2. **「Enable Public Link」をオン**
3. **表示されるリンクを共有**

**注意**: Public Link では誰でも登録可能（上限設定可）

### ビルドの追加と審査

1. **グループの Builds セクションで「+」**
2. **ビルドを選択**
3. **「Add」をクリック**
4. **Beta App Review に提出される**（初回のみ）

### Beta App Review

**審査される内容**:
- クラッシュしないこと
- 基本的な機能が動作すること
- 明らかなガイドライン違反がないこと

**審査期間**: 通常24-48時間

**注意点**:
- 同一ビルドは1回の審査でOK（複数グループに配布可）
- メジャーバージョンアップ時は再審査が必要な場合あり

## テスト情報の管理

### Test Information

各ビルドに設定できる情報:

```
What to Test（必須）:
テスターにテストしてほしい内容を記載

Beta App Description:
アプリの説明（App Store の説明とは別）

Beta App Feedback Email:
フィードバック受信用メールアドレス

Demo Account（オプション）:
テスト用アカウントの情報
- Username: test@example.com
- Password: TestPassword123

Notes:
審査員向けの補足情報
```

### ローカライズ

Test Information は各言語で設定可能:

1. **対象ビルドの Test Information を開く**
2. **言語を追加**
3. **各言語で情報を入力**

## テスターの管理

### テスターの状態

| 状態 | 説明 |
|------|------|
| Invited | 招待メール送信済み、未承諾 |
| Accepted | 招待承諾済み、未インストール |
| Installed | アプリをインストール済み |
| No Builds Available | 利用可能なビルドなし |

### テスターの削除

1. **グループを選択**
2. **テスターを選択**
3. **「Remove」をクリック**

### テスターの再招待

1. **テスターを選択**
2. **「Resend Invitation」をクリック**

## フィードバックの収集

### スクリーンショットフィードバック

テスターは TestFlight アプリから:
1. アプリ使用中にデバイスをシェイク
2. スクリーンショットにマーキング
3. コメントを追加して送信

### フィードバックの確認

1. **App Store Connect > TestFlight > Feedback**
2. **スクリーンショットとコメントを確認**
3. **必要に応じて返信**

### クラッシュレポート

1. **App Store Connect > TestFlight > Crashes**
2. **クラッシュログを確認**
3. **dSYM をアップロードしてシンボル化**

## ビルドの管理

### ビルドの有効期限

- **90日間有効**
- 期限切れ前に新しいビルドを配布

### ビルドの無効化

1. **対象ビルドを選択**
2. **「Expire Build」をクリック**

**使用ケース**:
- 重大なバグが見つかった場合
- 古いビルドのテストを停止したい場合

### 複数バージョンの管理

同時に複数のバージョン/ビルドをテスト可能:

```
バージョン 1.2.0
├─ ビルド 100（安定版）→ 外部テスター
└─ ビルド 101（新機能）→ 内部テスター

バージョン 2.0.0
└─ ビルド 200（開発中）→ 内部テスター
```

## 自動化

### App Store Connect API

```bash
# ビルド一覧取得
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/builds"

# 外部テスターグループにビルド追加
curl -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"data": {"type": "builds", "id": "BUILD_ID"}}' \
  "https://api.appstoreconnect.apple.com/v1/betaGroups/GROUP_ID/relationships/builds"
```

### fastlane

```ruby
# Fastfile
lane :beta do
  build_app(scheme: "MyApp")

  upload_to_testflight(
    skip_waiting_for_build_processing: false,
    distribute_external: true,
    groups: ["External Testers"],
    changelog: "Bug fixes and improvements"
  )
end
```

### GitHub Actions

```yaml
- name: Upload to TestFlight
  run: |
    xcrun altool --upload-app \
      -f App.ipa \
      -t ios \
      --apiKey ${{ secrets.API_KEY_ID }} \
      --apiIssuer ${{ secrets.ISSUER_ID }}
```

## ベストプラクティス

### テスト戦略

1. **内部テスターで初期テスト**
   - 開発チーム、QAチーム
   - 迅速なフィードバック

2. **限定的な外部テスト**
   - アクティブユーザーを招待
   - 詳細なフィードバックを収集

3. **Public Link で広範なテスト**
   - オープンベータ
   - スケーラビリティテスト

### フィードバック収集

1. **明確なテスト指示を提供**
   - 具体的なテスト項目
   - 期待される動作

2. **フィードバック手段を複数用意**
   - TestFlight内フィードバック
   - 専用フォーム/Slack

3. **迅速な対応**
   - クラッシュレポートは優先対応
   - フィードバックへの返信

### ビルド管理

1. **意味のあるリリースノート**
   - 変更内容を明確に記載
   - 既知の問題を開示

2. **適切なビルド頻度**
   - 内部: 日次〜週次
   - 外部: 週次〜隔週

3. **バージョン番号の管理**
   - セマンティックバージョニング
   - ビルド番号は常にインクリメント

## トラブルシューティング

### 「Build is not available」

**原因**: ビルドがまだ処理中、または期限切れ

**解決方法**:
- 処理完了を待つ
- 新しいビルドをアップロード

### テスターが招待メールを受信しない

**原因**: メールフィルタ、Apple ID 不一致

**解決方法**:
- 迷惑メールフォルダを確認
- Apple ID と同じメールアドレスで招待
- 招待を再送信

### 「This beta is full」

**原因**: Public Link の上限に達した

**解決方法**:
- 上限を増やす
- 非アクティブなテスターを削除

### Beta App Review でリジェクト

**原因**: ガイドライン違反、クラッシュ

**解決方法**:
- リジェクト理由を確認
- 問題を修正して再提出

## 参考リンク

- [TestFlight Overview](https://developer.apple.com/testflight/)
- [App Store Connect Help: TestFlight](https://help.apple.com/app-store-connect/#/devdc42b26b8)
- [Beta App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
