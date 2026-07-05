# 活用シナリオ集（非自明なレシピ）

## レイアウト問題の修正

### ユースケース
CSSレイアウト問題（オーバーフロー、崩れ）の診断と修正提案。

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
ログイン、ログアウト、セッション管理のテスト。認証済みAPIリクエストのトークンをネットワークログから確認する場合に使う。

### 認証状態の維持
Chrome DevTools MCPはユーザーデータディレクトリを共有するため、セッションが維持される。`--isolated`オプションで新規セッションを使用可能。
