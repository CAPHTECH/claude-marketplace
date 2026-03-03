# Instruments 活用ガイド

## Instruments の起動方法

### Xcode から起動

1. `Product` → `Profile` (Cmd + I)
2. テンプレート選択画面で目的の Instrument を選択
3. Record ボタンでプロファイリング開始

### 単独起動

1. `/Applications/Xcode.app/Contents/Applications/Instruments.app`
2. またはSpotlightで「Instruments」を検索

## 主要 Instruments

### Time Profiler

CPU使用率とスタックトレースを分析。

**用途**:
- 重い処理の特定
- ホットスポットの発見
- スレッド使用状況の確認

**使い方**:
```
1. Time Profiler テンプレートを選択
2. Record 開始
3. アプリで対象操作を実行
4. Record 停止
5. Call Tree で分析

重要な設定:
- Invert Call Tree: チェック（最も重い関数が上に）
- Hide System Libraries: 必要に応じて
- Flatten Recursion: 再帰呼び出しをまとめる
```

**読み方**:
```
Weight: その関数で費やされた時間の割合
Self Weight: その関数自体（子を除く）の時間
Symbol Name: 関数名
```

### Allocations

メモリ割り当てを追跡。

**用途**:
- メモリ使用量の推移確認
- 大量のオブジェクト生成の検出
- メモリフットプリントの分析

**使い方**:
```
1. Allocations テンプレートを選択
2. Record 開始
3. 操作を実行
4. 操作前後でスナップショット（Mark Generation）
5. 世代間の差分を分析

重要な操作:
- Mark Generation: 現時点のスナップショット
- Growth: 前の世代からの増加量
- Persistent: 現在も生存しているオブジェクト
```

**チェックポイント**:
```
1. All Heap Allocations で全体傾向を確認
2. Statistics で大きなオブジェクトを特定
3. Call Tree でどこで割り当てられたか追跡
```

### Leaks

メモリリークを検出。

**用途**:
- リークしているオブジェクトの特定
- 循環参照の発見
- リテインサイクルの可視化

**使い方**:
```
1. Leaks テンプレートを選択
2. Record 開始
3. リークが疑われる操作を繰り返す
   （例：画面を開いて閉じるを繰り返す）
4. 赤いバーが表示されたらリーク検出
5. Leaks インストゥルメントをクリックして詳細確認

Cycles & Roots:
- リテインサイクルを視覚的に表示
- どのオブジェクト間で循環しているか確認
```

### App Launch

起動時間を分析。

**用途**:
- 起動フェーズごとの時間計測
- ボトルネックの特定
- 起動最適化の効果測定

**使い方**:
```
1. App Launch テンプレートを選択
2. アプリを終了させた状態で Record 開始
3. 自動的にアプリが起動
4. 最初の描画完了まで計測
5. 各フェーズの時間を確認

フェーズ:
- Process Initialization: dyld、ランタイム初期化
- UIKit Initialization: UIApplication初期化
- Initial Frame Rendering: 最初のフレーム描画
```

### Core Animation

UIのレンダリングパフォーマンスを分析。

**用途**:
- フレームレートの監視
- レンダリングボトルネックの特定
- オフスクリーンレンダリングの検出

**使い方**:
```
1. Core Animation テンプレートを選択
2. Record 開始
3. スクロール等のUI操作を実行
4. FPSグラフを確認

Debug Options（シミュレータ/デバイスで有効化）:
- Color Blended Layers: ブレンディング発生箇所を表示
- Color Offscreen-Rendered: オフスクリーンレンダリング箇所
- Color Hits Green and Misses Red: キャッシュ効率
```

### Animation Hitches (iOS 14+)

UIのヒッチ（カクつき）を検出。

**用途**:
- スクロール時のカクつき検出
- アニメーションの問題特定
- Commit/Render のどちらが原因か特定

**ヒッチの種類**:
```
Commit Hitch:
- メインスレッドでの処理が重い
- レイアウト計算、Auto Layout

Render Hitch:
- GPU側の処理が重い
- 複雑な描画、エフェクト

Hitch Ratio = Hitch Time / Duration
目標: < 5ms/s
```

### Energy Log

バッテリー消費を分析。

**用途**:
- 電力消費の傾向把握
- 高消費の原因特定
- バックグラウンド処理の影響確認

**使い方**:
```
1. Energy Log テンプレートを選択
2. Record 開始
3. アプリを使用
4. 各コンポーネントの消費を確認

コンポーネント:
- CPU: 処理による消費
- Network: 通信による消費
- Location: 位置情報による消費
- GPU: 描画による消費
- Background: バックグラウンド処理
```

### Network

ネットワーク通信を分析。

**用途**:
- API呼び出しの監視
- データ転送量の確認
- 接続の効率確認

**確認項目**:
```
- リクエスト/レスポンスのサイズ
- レイテンシ
- 接続の再利用状況
- HTTP/2, HTTP/3 の使用状況
```

## カスタム Instruments

### os_signpost の活用

```swift
import os.signpost

let log = OSLog(subsystem: "com.myapp", category: "Performance")
let signpostID = OSSignpostID(log: log)

// 処理開始
os_signpost(.begin, log: log, name: "Heavy Operation", signpostID: signpostID)

// 処理実行
performHeavyOperation()

// 処理終了
os_signpost(.end, log: log, name: "Heavy Operation", signpostID: signpostID)
```

### Points of Interest

```swift
import os.signpost

let poi = OSLog(subsystem: "com.myapp", category: .pointsOfInterest)

// イベントをマーク
os_signpost(.event, log: poi, name: "User Tapped Button")
```

## プロファイリングのベストプラクティス

### 1. 実機でプロファイリング

```
シミュレータの問題:
- CPUアーキテクチャが異なる（x86 vs ARM）
- メモリ制限が緩い
- GPUが異なる

推奨:
- 最低スペックのサポートデバイスでテスト
- Releaseビルドでプロファイリング
```

### 2. Releaseビルドの使用

```
Scheme設定:
1. Edit Scheme → Profile
2. Build Configuration を Release に設定
3. または Release with Debug Info

Debugビルドの問題:
- 最適化が無効
- 追加の検証コード
- デバッグシンボルのオーバーヘッド
```

### 3. 複数回計測

```
変動要因:
- システムの状態
- バックグラウンドプロセス
- サーマルスロットリング

推奨:
- 最低3回計測
- 中央値を採用
- ウォームアップ後に計測
```

### 4. ベースラインの確立

```
手順:
1. 現状のパフォーマンスを計測
2. 最適化を実施
3. 再計測して比較
4. 改善率を記録

記録項目:
- 計測日時
- デバイス/OS
- アプリバージョン
- 計測値
```

## トラブルシューティング

### Instruments が接続できない

```
対処法:
1. デバイスを再起動
2. Xcodeを再起動
3. DerivedData を削除
4. デバイスの信頼設定をリセット
```

### シンボルが表示されない

```
対処法:
1. dSYMファイルの確認
2. Archive から dSYM をエクスポート
3. Instruments の Symbols 設定を確認
```

### 計測値が不安定

```
対処法:
1. 低電力モードをオフ
2. 機内モードでネットワーク影響を排除
3. 他のアプリを終了
4. デバイスを冷却（サーマルスロットリング対策）
```

## クイックリファレンス

### キーボードショートカット

| ショートカット | 操作 |
|--------------|------|
| Cmd + R | Record/Stop |
| Cmd + E | トラック追加 |
| Space | 再生/停止 |
| +/- | ズームイン/アウト |
| Cmd + F | 検索 |

### よく使う設定

```
Call Tree:
- Invert Call Tree: ON
- Separate by Thread: ON
- Hide System Libraries: 状況により
- Flatten Recursion: ON

Allocations:
- Record reference counts: メモリ調査時ON
- Discard events for freed memory: 通常OFF
```
