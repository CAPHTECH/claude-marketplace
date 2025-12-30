# レンダリング最適化詳細

## レンダリングパイプライン

### iOS のレンダリングフロー

```
1. Layout (CPU)
   - Auto Layout 計算
   - フレーム決定

2. Display (CPU)
   - drawRect 呼び出し
   - Core Graphics 描画

3. Prepare (CPU)
   - 画像デコード
   - テクスチャ変換

4. Commit (CPU → GPU)
   - レイヤーツリーの送信
   - GPU へのコミット

5. Render (GPU)
   - 実際の描画処理
```

### フレームレートの目標

```
60fps: 16.67ms per frame
120fps: 8.33ms per frame (ProMotion)

メインスレッドの処理時間を上記以内に収める必要がある
```

## フレームドロップの検出

### CADisplayLink による監視

```swift
class FrameRateMonitor {
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var frameDropCount = 0
    
    func start() {
        displayLink = CADisplayLink(target: self, selector: #selector(tick))
        displayLink?.add(to: .main, forMode: .common)
    }
    
    @objc private func tick(_ link: CADisplayLink) {
        if lastTimestamp > 0 {
            let duration = link.timestamp - lastTimestamp
            let fps = 1.0 / duration
            
            // 目標FPSの90%を下回ったらドロップとカウント
            let targetFPS: Double = 60
            if fps < targetFPS * 0.9 {
                frameDropCount += 1
                print("Frame drop: \(String(format: "%.1f", fps)) fps")
            }
        }
        lastTimestamp = link.timestamp
    }
    
    func stop() {
        displayLink?.invalidate()
        displayLink = nil
        print("Total frame drops: \(frameDropCount)")
    }
}
```

### MetricKit での監視 (iOS 14+)

```swift
import MetricKit

class HitchMetricsCollector: NSObject, MXMetricManagerSubscriber {
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            if let animationMetrics = payload.animationMetrics {
                let scrollHitchRate = animationMetrics.scrollHitchTimeRatio
                print("Scroll hitch rate: \(scrollHitchRate)")
            }
        }
    }
}
```

## オフスクリーンレンダリング

### 発生原因

```swift
// オフスクリーンレンダリングを引き起こす操作
view.layer.cornerRadius = 10
view.layer.masksToBounds = true  // これと cornerRadius の組み合わせ

view.layer.shadowColor = UIColor.black.cgColor
view.layer.shadowOffset = CGSize(width: 0, height: 2)
view.layer.shadowOpacity = 0.3
// shadowPath が設定されていないとオフスクリーン

view.layer.mask = maskLayer  // マスク使用
view.layer.shouldRasterize = true  // ラスタライズ（条件による）
```

### 回避策

#### 角丸 + 影

```swift
// Bad: オフスクリーンレンダリング発生
contentView.layer.cornerRadius = 10
contentView.layer.masksToBounds = true
contentView.layer.shadowColor = UIColor.black.cgColor
contentView.layer.shadowOpacity = 0.3
contentView.layer.shadowOffset = CGSize(width: 0, height: 2)

// Good: 影用の別レイヤー
let shadowView = UIView(frame: contentView.frame)
shadowView.layer.shadowColor = UIColor.black.cgColor
shadowView.layer.shadowOpacity = 0.3
shadowView.layer.shadowOffset = CGSize(width: 0, height: 2)
shadowView.layer.shadowPath = UIBezierPath(
    roundedRect: contentView.bounds,
    cornerRadius: 10
).cgPath

contentView.layer.cornerRadius = 10
contentView.layer.masksToBounds = true
```

#### shadowPath の設定

```swift
// Bad: shadowPath なし
view.layer.shadowColor = UIColor.black.cgColor
view.layer.shadowOpacity = 0.3

// Good: shadowPath を明示的に設定
view.layer.shadowColor = UIColor.black.cgColor
view.layer.shadowOpacity = 0.3
view.layer.shadowPath = UIBezierPath(rect: view.bounds).cgPath

// 角丸の場合
view.layer.shadowPath = UIBezierPath(
    roundedRect: view.bounds,
    cornerRadius: view.layer.cornerRadius
).cgPath
```

#### ラスタライズの適切な使用

```swift
// 静的なコンテンツのみラスタライズ
view.layer.shouldRasterize = true
view.layer.rasterizationScale = UIScreen.main.scale

// 注意: アニメーション中やコンテンツ変更時は無効化
view.layer.shouldRasterize = false
```

## SwiftUI での最適化

### drawingGroup

```swift
// 複雑な描画を GPU でまとめて処理
VStack {
    ForEach(items) { item in
        ComplexView(item: item)
    }
}
.drawingGroup()  // Metal でレンダリング
```

### compositingGroup

```swift
// 透明度やエフェクトをグループ化
VStack {
    Text("Title")
    Text("Subtitle")
}
.compositingGroup()
.shadow(radius: 5)
```

### 条件付きモディファイア

```swift
// Bad: 不要なモディファイアの適用
Text("Hello")
    .shadow(color: showShadow ? .black : .clear, radius: 5)

// Good: 条件分岐
if showShadow {
    Text("Hello")
        .shadow(color: .black, radius: 5)
} else {
    Text("Hello")
}

// または extension
extension View {
    @ViewBuilder
    func conditionalShadow(_ show: Bool) -> some View {
        if show {
            self.shadow(color: .black, radius: 5)
        } else {
            self
        }
    }
}
```

## UITableView / UICollectionView の最適化

### セルの再利用

```swift
// 適切な再利用識別子
tableView.register(ProductCell.self, forCellReuseIdentifier: "ProductCell")

func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "ProductCell", for: indexPath) as! ProductCell
    cell.configure(with: products[indexPath.row])
    return cell
}
```

### 高さの事前計算

```swift
// Bad: 毎回計算
func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
    return calculateHeight(for: products[indexPath.row])
}

// Good: キャッシュ
private var heightCache: [IndexPath: CGFloat] = [:]

func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
    if let cached = heightCache[indexPath] {
        return cached
    }
    let height = calculateHeight(for: products[indexPath.row])
    heightCache[indexPath] = height
    return height
}

// Better: estimatedHeight + Self-Sizing
tableView.estimatedRowHeight = 100
tableView.rowHeight = UITableView.automaticDimension
```

### プリフェッチ

```swift
class ProductListViewController: UIViewController, UITableViewDataSourcePrefetching {
    func tableView(_ tableView: UITableView, prefetchRowsAt indexPaths: [IndexPath]) {
        for indexPath in indexPaths {
            let product = products[indexPath.row]
            imageLoader.prefetch(url: product.imageURL)
        }
    }
    
    func tableView(_ tableView: UITableView, cancelPrefetchingForRowsAt indexPaths: [IndexPath]) {
        for indexPath in indexPaths {
            let product = products[indexPath.row]
            imageLoader.cancelPrefetch(url: product.imageURL)
        }
    }
}
```

## SwiftUI List の最適化

### LazyVStack vs List

```swift
// List: 自動的に遅延読み込み
List(items) { item in
    ItemView(item: item)
}

// LazyVStack: カスタマイズ可能
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemView(item: item)
        }
    }
}
```

### id の適切な設定

```swift
// Bad: インデックスベース
ForEach(0..<items.count, id: \.self) { index in
    ItemView(item: items[index])
}

// Good: Identifiable準拠
struct Item: Identifiable {
    let id: UUID
    // ...
}

ForEach(items) { item in
    ItemView(item: item)
}
```

### equatable 最適化

```swift
struct ItemView: View, Equatable {
    let item: Item
    
    static func == (lhs: ItemView, rhs: ItemView) -> Bool {
        lhs.item.id == rhs.item.id &&
        lhs.item.title == rhs.item.title
    }
    
    var body: some View {
        // ...
    }
}

// 使用
ForEach(items) { item in
    ItemView(item: item)
        .equatable()  // 等価の場合は再描画をスキップ
}
```

## 画像の最適化

### 適切なサイズでの表示

```swift
// Bad: 大きな画像をそのまま表示
imageView.image = UIImage(named: "large_image")

// Good: 表示サイズに合わせてリサイズ
let targetSize = imageView.bounds.size
let scaledImage = resizeImage(originalImage, to: targetSize)
imageView.image = scaledImage
```

### バックグラウンドでのデコード

```swift
func loadImage(from url: URL, into imageView: UIImageView) {
    DispatchQueue.global(qos: .userInitiated).async {
        guard let data = try? Data(contentsOf: url),
              let image = UIImage(data: data) else { return }
        
        // バックグラウンドでデコード
        UIGraphicsBeginImageContextWithOptions(image.size, true, image.scale)
        image.draw(at: .zero)
        let decodedImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        
        DispatchQueue.main.async {
            imageView.image = decodedImage
        }
    }
}
```

## アニメーションの最適化

### Core Animation の活用

```swift
// UIView.animate より CABasicAnimation が効率的な場合
let animation = CABasicAnimation(keyPath: "transform.scale")
animation.fromValue = 1.0
animation.toValue = 1.2
animation.duration = 0.3
animation.autoreverses = true
view.layer.add(animation, forKey: "pulse")
```

### 不要なアニメーションの回避

```swift
// アニメーション中は他の更新を抑制
UIView.performWithoutAnimation {
    collectionView.reloadData()
}

// SwiftUI
withTransaction { transaction in
    transaction.animation = nil
    state.value = newValue
}
```

## デバッグオプション

### Simulator Debug Options

```
Debug → Color Blended Layers
- 赤: ブレンディング発生（半透明レイヤー）
- 緑: 不透明

Debug → Color Offscreen-Rendered
- 黄色: オフスクリーンレンダリング

Debug → Color Hits Green and Misses Red
- 緑: キャッシュヒット
- 赤: キャッシュミス
```

### 実機でのデバッグ

```swift
// CADisplayLink でFPS表示
class FPSLabel: UILabel {
    private var displayLink: CADisplayLink?
    private var count = 0
    private var lastTime: CFTimeInterval = 0
    
    func start() {
        displayLink = CADisplayLink(target: self, selector: #selector(tick))
        displayLink?.add(to: .main, forMode: .common)
    }
    
    @objc private func tick(_ link: CADisplayLink) {
        count += 1
        let delta = link.timestamp - lastTime
        if delta >= 1.0 {
            text = "\(count) FPS"
            count = 0
            lastTime = link.timestamp
        }
    }
}
```

## チェックリスト

### レイアウト

- [ ] 複雑な Auto Layout を簡素化
- [ ] 固定サイズを可能な限り使用
- [ ] intrinsicContentSize のキャッシュ

### 描画

- [ ] オフスクリーンレンダリングを回避
- [ ] shadowPath を明示的に設定
- [ ] 不透明ビューは isOpaque = true
- [ ] ラスタライズは静的コンテンツのみ

### テーブル/コレクション

- [ ] セルの再利用を確認
- [ ] estimatedHeight を設定
- [ ] プリフェッチを実装
- [ ] デキュー時の処理を最小化

### 画像

- [ ] 表示サイズでロード
- [ ] バックグラウンドでデコード
- [ ] キャッシュを活用
- [ ] 不要な画像は解放
