# 活用シナリオ集

## 目次
1. [コード変更の検証](#コード変更の検証)
2. [エラー診断](#エラー診断)
3. [E2Eテスト自動化](#e2eテスト自動化)
4. [レイアウト問題の修正](#レイアウト問題の修正)
5. [パフォーマンス監査](#パフォーマンス監査)
6. [認証フローのテスト](#認証フローのテスト)

## コード変更の検証

### ユースケース
コード変更後、ブラウザで意図通りに動作するか自動確認。

### プロンプト例
```
localhost:3000を開いて、ボタンをクリックしたときの動作を確認して
```

### ワークフロー
```
1. new_page(url: "http://localhost:3000")
2. take_snapshot()
3. click(uid: "target-button")
4. wait_for(text: "期待する結果")
5. list_console_messages(types: ["error"])
6. take_screenshot()
```

## エラー診断

### ユースケース
フォーム送信時のエラー、API呼び出し失敗、コンソールエラーの原因調査。

### プロンプト例
```
ログインフォームを送信したときのエラーを分析して
```

### ワークフロー
```
1. new_page(url: "http://localhost:3000/login")
2. take_snapshot()
3. fill_form(elements: [
     {uid: "input-email", value: "test@example.com"},
     {uid: "input-password", value: "password123"}
   ])
4. click(uid: "btn-login")
5. list_console_messages(types: ["error", "warn"])
6. list_network_requests(resourceTypes: ["xhr", "fetch"])
7. get_network_request(reqid: <失敗したリクエストID>)
```

### 確認ポイント
- コンソールエラーの内容
- ネットワークリクエストのステータスコード
- レスポンスボディのエラーメッセージ
- CORSエラーの有無

## E2Eテスト自動化

### ユースケース
ユーザーフロー全体をシミュレートし、各ステップの動作を確認。

### プロンプト例
```
新規ユーザー登録フローをテストして：
1. サインアップページを開く
2. フォームを入力
3. 送信
4. 確認画面が表示されるか確認
```

### ワークフロー
```
1. new_page(url: "http://localhost:3000/signup")
2. take_snapshot()
3. fill_form(elements: [
     {uid: "input-name", value: "テストユーザー"},
     {uid: "input-email", value: "test@example.com"},
     {uid: "input-password", value: "SecurePass123"}
   ])
4. click(uid: "btn-submit")
5. wait_for(text: "登録完了")
6. take_screenshot()
7. list_console_messages(types: ["error"])
```

### テストケース管理
テストケースドキュメントを渡して、自動的にテストを実行することも可能：
```
このテストケースドキュメントに従ってテストを実行して
```

## レイアウト問題の修正

### ユースケース
CSSレイアウト問題（オーバーフロー、崩れ）の診断と修正提案。

### プロンプト例
```
localhost:8080のヘッダーでオーバーフローしている要素を特定して修正案を提案して
```

### ワークフロー
```
1. new_page(url: "http://localhost:8080")
2. take_snapshot(verbose: true)
3. take_screenshot(fullPage: true)
4. evaluate_script(function: "() => {
     const elements = document.querySelectorAll('*');
     const overflowing = [];
     elements.forEach(el => {
       if (el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight) {
         overflowing.push({tag: el.tagName, class: el.className});
       }
     });
     return overflowing;
   }")
```

### レスポンシブテスト
```
# モバイルサイズでテスト
resize_page(width: 375, height: 812)
take_screenshot()

# タブレットサイズでテスト
resize_page(width: 768, height: 1024)
take_screenshot()
```

## パフォーマンス監査

### ユースケース
Core Web Vitals（LCP、CLS、FID）の計測と最適化提案。

### プロンプト例
```
このページのパフォーマンスを分析して、LCPが遅い原因を特定して
```

### ワークフロー
```
1. new_page(url: "https://example.com")
2. performance_start_trace(reload: true, autoStop: true)
3. performance_analyze_insight(insightSetId: "...", insightName: "LCPBreakdown")
4. performance_analyze_insight(insightSetId: "...", insightName: "RenderBlocking")
5. list_network_requests()
```

### 低速環境シミュレーション
```
# モバイル環境をシミュレート
emulate(networkConditions: "Slow 4G", cpuThrottlingRate: 4)

# パフォーマンストレース
performance_start_trace(reload: true, autoStop: true)

# 元に戻す
emulate(networkConditions: "No emulation", cpuThrottlingRate: 1)
```

### 主要なインサイト
| インサイト | 分析内容 |
|-----------|----------|
| LCPBreakdown | LCPの内訳（ネットワーク、レンダリング） |
| RenderBlocking | レンダリングブロックリソース |
| DocumentLatency | ドキュメント読み込み遅延 |
| LongTasks | 長時間JavaScriptタスク |

## 認証フローのテスト

### ユースケース
ログイン、ログアウト、セッション管理のテスト。

### プロンプト例
```
ログイン後にダッシュボードにアクセスできるか確認して
```

### ワークフロー
```
1. new_page(url: "http://localhost:3000/login")
2. take_snapshot()
3. fill_form(elements: [
     {uid: "input-email", value: "admin@example.com"},
     {uid: "input-password", value: "adminpass"}
   ])
4. click(uid: "btn-login")
5. wait_for(text: "ダッシュボード")
6. list_network_requests(resourceTypes: ["xhr", "fetch"])
7. # 認証トークンの確認
   get_network_request(reqid: <ログインAPIのID>)
```

### 認証状態の維持
Chrome DevTools MCPはユーザーデータディレクトリを共有するため、セッションが維持される。
`--isolated`オプションで新規セッションを使用可能。

## ベストプラクティス

### 1. 段階的なデバッグ
```
# 悪い例：一度に全部
"ログインしてダッシュボードを確認してエラーを修正して"

# 良い例：段階的に
1. "ログインページを開いて"
2. "フォームを入力して送信"
3. "エラーがあれば分析"
4. "修正案を提案"
```

### 2. スナップショットの活用
```
# 操作前に必ずスナップショット
take_snapshot()
# これでuidが取得でき、正確な要素操作が可能
```

### 3. 待機の活用
```
# 非同期操作後は待機
click(uid: "btn-submit")
wait_for(text: "完了")  # 結果が表示されるまで待機
```

### 4. エラーチェックの習慣化
```
# 操作後は常にエラーチェック
list_console_messages(types: ["error"])
list_network_requests(resourceTypes: ["xhr", "fetch"])
```
