# ネットワークデバッグガイド

## 目次
1. [リクエスト一覧の取得](#リクエスト一覧の取得)
2. [リクエスト詳細の確認](#リクエスト詳細の確認)
3. [API呼び出しのデバッグ](#api呼び出しのデバッグ)
4. [ネットワークエミュレーション](#ネットワークエミュレーション)
5. [トラブルシューティング](#トラブルシューティング)

## リクエスト一覧の取得

### 基本的な取得

```
# 全リクエスト取得
list_network_requests()

# ページネーション指定
list_network_requests(pageIdx: 0, pageSize: 50)
```

### リソースタイプでフィルタリング

```
# XHR/Fetchのみ（API呼び出し）
list_network_requests(resourceTypes: ["xhr", "fetch"])

# 画像リソースのみ
list_network_requests(resourceTypes: ["image"])

# スクリプトのみ
list_network_requests(resourceTypes: ["script"])

# スタイルシートのみ
list_network_requests(resourceTypes: ["stylesheet"])

# ドキュメント（HTML）のみ
list_network_requests(resourceTypes: ["document"])
```

利用可能なリソースタイプ:
- `document`, `stylesheet`, `image`, `media`, `font`
- `script`, `texttrack`, `xhr`, `fetch`, `prefetch`
- `eventsource`, `websocket`, `manifest`, `ping`, `other`

### 履歴リクエストの取得

```
# 過去3ナビゲーションのリクエストを含める
list_network_requests(includePreservedRequests: true)
```

## リクエスト詳細の確認

### 特定リクエストの詳細取得

```
# reqidを指定して詳細取得
get_network_request(reqid: 123)

# DevToolsで選択中のリクエストを取得
get_network_request()
```

### 確認できる情報

- リクエストURL
- HTTPメソッド
- ステータスコード
- リクエストヘッダー
- レスポンスヘッダー
- リクエストボディ
- レスポンスボディ
- タイミング情報

## API呼び出しのデバッグ

### APIエラーの調査手順

```
# 1. 操作を実行
click(uid: "btn-save")

# 2. API呼び出しを確認
list_network_requests(resourceTypes: ["xhr", "fetch"])

# 3. 失敗したリクエストの詳細を確認
get_network_request(reqid: <失敗したリクエストのID>)
```

### ステータスコード別の対応

| ステータス | 意味 | 確認ポイント |
|-----------|------|-------------|
| 400 | Bad Request | リクエストボディの形式を確認 |
| 401 | Unauthorized | 認証トークンの有無・有効期限を確認 |
| 403 | Forbidden | 権限設定を確認 |
| 404 | Not Found | URLパスを確認 |
| 422 | Unprocessable | バリデーションエラーの内容を確認 |
| 500 | Server Error | サーバーログを確認 |

### 認証関連のデバッグ

```
# 1. ログインAPI呼び出しを確認
list_network_requests(resourceTypes: ["xhr", "fetch"])

# 2. レスポンスヘッダーでトークン確認
get_network_request(reqid: <ログインAPIのID>)

# 3. 後続APIのリクエストヘッダーで認証情報確認
get_network_request(reqid: <認証が必要なAPIのID>)
```

## ネットワークエミュレーション

### ネットワーク速度の制限

```
# オフラインにする
emulate(networkConditions: "Offline")

# 低速3G
emulate(networkConditions: "Slow 3G")

# 高速3G
emulate(networkConditions: "Fast 3G")

# 低速4G
emulate(networkConditions: "Slow 4G")

# 高速4G
emulate(networkConditions: "Fast 4G")

# エミュレーション解除
emulate(networkConditions: "No emulation")
```

### 低速環境でのテスト手順

```
# 1. 低速ネットワーク設定
emulate(networkConditions: "Slow 3G")

# 2. ページリロード
navigate_page(type: "reload")

# 3. 読み込み状態を確認
take_screenshot()

# 4. エミュレーション解除
emulate(networkConditions: "No emulation")
```

## トラブルシューティング

### よくある問題と解決策

**問題: APIが呼ばれない**
```
# コンソールエラー確認
list_console_messages(types: ["error"])

# JavaScriptエラーがないか確認
```

**問題: CORSエラー**
```
# コンソールでCORSエラーを確認
list_console_messages(types: ["error"])

# ネットワークリクエストでpreflightを確認
list_network_requests(resourceTypes: ["preflight"])
```

**問題: レスポンスが遅い**
```
# パフォーマンストレースで詳細分析
performance_start_trace(reload: true, autoStop: true)
```

**問題: キャッシュの影響**
```
# キャッシュを無視してリロード
navigate_page(type: "reload", ignoreCache: true)
```

### デバッグのベストプラクティス

1. **操作前にネットワーク監視開始**: 操作前に状態を把握
2. **resourceTypesでフィルタリング**: 関連するリクエストのみに絞り込み
3. **詳細確認はget_network_request**: リクエスト/レスポンスボディを確認
4. **エミュレーションで再現**: 環境依存の問題を再現テスト
