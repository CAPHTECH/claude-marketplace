# パフォーマンス分析ガイド

## 目次
1. [パフォーマンストレース](#パフォーマンストレース)
2. [Core Web Vitals分析](#core-web-vitals分析)
3. [インサイト分析](#インサイト分析)
4. [エミュレーション設定](#エミュレーション設定)
5. [ベストプラクティス](#ベストプラクティス)

## パフォーマンストレース

### 基本的なトレース取得

```
# 自動停止付きでリロードしてトレース
performance_start_trace(reload: true, autoStop: true)

# 手動でトレース開始（操作を挟む場合）
performance_start_trace(reload: false, autoStop: false)

# 手動停止
performance_stop_trace()
```

### トレースのパターン

**パターン1: ページ読み込み分析**
```
# リロードして読み込みパフォーマンスを計測
performance_start_trace(reload: true, autoStop: true)
```

**パターン2: ユーザー操作の分析**
```
# 1. トレース開始（手動モード）
performance_start_trace(reload: false, autoStop: false)

# 2. 分析したい操作を実行
click(uid: "btn-load-data")
wait_for(text: "データ読み込み完了")

# 3. トレース停止
performance_stop_trace()
```

**パターン3: 特定画面遷移の分析**
```
# 1. トレース開始
performance_start_trace(reload: false, autoStop: false)

# 2. ナビゲーション
navigate_page(type: "url", url: "https://example.com/heavy-page")

# 3. 読み込み完了待機
wait_for(text: "ページタイトル")

# 4. トレース停止
performance_stop_trace()
```

## Core Web Vitals分析

トレース結果には以下のCore Web Vitalsが含まれる:

| 指標 | 説明 | 良好な値 |
|------|------|----------|
| LCP | Largest Contentful Paint | < 2.5s |
| FID | First Input Delay | < 100ms |
| CLS | Cumulative Layout Shift | < 0.1 |
| FCP | First Contentful Paint | < 1.8s |
| TTFB | Time to First Byte | < 800ms |

## インサイト分析

### インサイトの詳細取得

```
# 特定のインサイトを詳細分析
performance_analyze_insight(
  insightSetId: "<トレース結果のinsightSetId>",
  insightName: "LCPBreakdown"
)
```

### 主要なインサイト名

| インサイト名 | 分析内容 |
|-------------|----------|
| LCPBreakdown | LCPの内訳分析 |
| DocumentLatency | ドキュメント読み込み遅延 |
| RenderBlocking | レンダリングブロック要因 |
| NetworkRequests | ネットワークリクエスト分析 |
| LongTasks | 長時間タスクの検出 |

## エミュレーション設定

### CPU速度の制限

```
# CPUを4倍遅くする（モバイル相当）
emulate(cpuThrottlingRate: 4)

# CPUを6倍遅くする（低スペック端末相当）
emulate(cpuThrottlingRate: 6)

# 制限解除
emulate(cpuThrottlingRate: 1)
```

### 位置情報のエミュレーション

```
# 東京にセット
emulate(geolocation: {latitude: 35.6762, longitude: 139.6503})

# エミュレーション解除
emulate(geolocation: null)
```

### 複合エミュレーション

```
# モバイル環境をシミュレート
emulate(
  networkConditions: "Slow 4G",
  cpuThrottlingRate: 4
)

# デスクトップに戻す
emulate(
  networkConditions: "No emulation",
  cpuThrottlingRate: 1
)
```

## 分析ワークフロー

### 1. 初期パフォーマンス計測

```
# ベースライン計測
performance_start_trace(reload: true, autoStop: true)
```

### 2. 問題箇所の特定

```
# インサイト分析
performance_analyze_insight(insightSetId: "...", insightName: "LCPBreakdown")
performance_analyze_insight(insightSetId: "...", insightName: "RenderBlocking")
```

### 3. ネットワークリクエスト確認

```
# 重いリクエストを特定
list_network_requests()
```

### 4. 低スペック環境での確認

```
# モバイル環境シミュレート
emulate(networkConditions: "Slow 4G", cpuThrottlingRate: 4)
performance_start_trace(reload: true, autoStop: true)
```

## ベストプラクティス

### パフォーマンス計測のポイント

1. **複数回計測**: 1回の計測結果だけで判断しない
2. **キャッシュ考慮**: 初回読み込みと2回目を区別して計測
3. **実環境シミュレート**: エミュレーションで実際のユーザー環境を再現
4. **インサイト活用**: 数値だけでなくインサイトで原因特定

### よくあるパフォーマンス問題

| 問題 | 確認方法 | 対策 |
|------|----------|------|
| LCP遅延 | LCPBreakdownインサイト | 画像最適化、プリロード |
| レンダリングブロック | RenderBlockingインサイト | CSS/JSの遅延読み込み |
| ネットワーク遅延 | list_network_requests | CDN活用、圧縮 |
| JavaScript実行遅延 | LongTasksインサイト | コード分割、遅延実行 |

### 計測環境の標準化

```
# 標準的なモバイル環境
emulate(
  networkConditions: "Fast 4G",
  cpuThrottlingRate: 4
)

# 計測
performance_start_trace(reload: true, autoStop: true)
```
