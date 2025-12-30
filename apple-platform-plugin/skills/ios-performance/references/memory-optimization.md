# メモリ最適化詳細

## メモリの種類

### iOS メモリモデル

```
Clean Memory:
- ディスクからマップされたメモリ
- 必要に応じて破棄・再読み込み可能
- 例: フレームワーク、実行コード

Dirty Memory:
- アプリが書き込んだメモリ
- スワップ不可（iOSにはスワップがない）
- 例: ヒープオブジェクト、画像データ

Compressed Memory:
- iOS 7+ で導入
- 使用頻度の低いページを圧縮
```

### メモリ警告レベル

```swift
// メモリ警告の通知
NotificationCenter.default.addObserver(
    forName: UIApplication.didReceiveMemoryWarningNotification,
    object: nil,
    queue: .main
) { _ in
    // キャッシュクリア等
    ImageCache.shared.clear()
}
```

## メモリリークの検出と修正

### 循環参照パターン

#### パターン1: クロージャでの循環参照

```swift
// Bad
class ViewController: UIViewController {
    var timer: Timer?
    
    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.updateUI()  // strong reference
        }
    }
}

// Good
class ViewController: UIViewController {
    var timer: Timer?
    
    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.updateUI()
        }
    }
    
    deinit {
        timer?.invalidate()
    }
}
```

#### パターン2: デリゲートでの循環参照

```swift
// Bad
protocol DataManagerDelegate: AnyObject {
    func didUpdateData()
}

class DataManager {
    var delegate: DataManagerDelegate?  // strong reference
}

class ViewController: UIViewController, DataManagerDelegate {
    let dataManager = DataManager()
    
    override func viewDidLoad() {
        dataManager.delegate = self  // 循環参照
    }
}

// Good
class DataManager {
    weak var delegate: DataManagerDelegate?  // weak reference
}
```

#### パターン3: NotificationCenterでの参照保持

```swift
// Bad (iOS 9以降は自動的に解除されるが明示的に)
class ViewController: UIViewController {
    override func viewDidLoad() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleNotification),
            name: .someNotification,
            object: nil
        )
    }
    
    // removeObserver を忘れると問題になる可能性
}

// Good
class ViewController: UIViewController {
    private var notificationToken: Any?
    
    override func viewDidLoad() {
        notificationToken = NotificationCenter.default.addObserver(
            forName: .someNotification,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            self?.handleNotification(notification)
        }
    }
    
    deinit {
        if let token = notificationToken {
            NotificationCenter.default.removeObserver(token)
        }
    }
}
```

#### パターン4: Combine での循環参照

```swift
// Bad
class ViewModel: ObservableObject {
    var cancellables = Set<AnyCancellable>()
    
    func fetch() {
        apiClient.fetch()
            .sink { result in
                self.handleResult(result)  // strong reference
            }
            .store(in: &cancellables)
    }
}

// Good
class ViewModel: ObservableObject {
    var cancellables = Set<AnyCancellable>()
    
    func fetch() {
        apiClient.fetch()
            .sink { [weak self] result in
                self?.handleResult(result)
            }
            .store(in: &cancellables)
    }
}
```

### リーク検出のデバッグ

```swift
// deinit での確認
class ViewController: UIViewController {
    deinit {
        print("ViewController deinit")  // これが呼ばれないとリーク
    }
}

// Memory Graph Debugger の使用
// 1. Xcode: Debug → View Debugging → Memory Graph Hierarchy
// 2. リークしているオブジェクトを選択
// 3. 右側のパネルで参照関係を確認
```

## メモリフットプリント削減

### 画像最適化

#### ダウンサンプリング

```swift
/// 表示サイズに合わせて画像をダウンサンプリング
func downsample(imageAt url: URL, to pointSize: CGSize, scale: CGFloat = UIScreen.main.scale) -> UIImage? {
    let imageSourceOptions = [kCGImageSourceShouldCache: false] as CFDictionary
    
    guard let imageSource = CGImageSourceCreateWithURL(url as CFURL, imageSourceOptions) else {
        return nil
    }
    
    let maxDimensionInPixels = max(pointSize.width, pointSize.height) * scale
    
    let downsampleOptions = [
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceShouldCacheImmediately: true,
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceThumbnailMaxPixelSize: maxDimensionInPixels
    ] as CFDictionary
    
    guard let downsampledImage = CGImageSourceCreateThumbnailAtIndex(imageSource, 0, downsampleOptions) else {
        return nil
    }
    
    return UIImage(cgImage: downsampledImage)
}
```

#### 遅延デコード

```swift
// 画像をすぐにデコードしない
let image = UIImage(contentsOfFile: path)  // 遅延デコード

// 明示的にデコード（バックグラウンドで）
func preloadImage(at url: URL) async -> UIImage? {
    return await Task.detached(priority: .utility) {
        guard let image = UIImage(contentsOfFile: url.path) else { return nil }
        
        // 強制デコード
        let format = UIGraphicsImageRendererFormat()
        format.scale = image.scale
        
        let renderer = UIGraphicsImageRenderer(size: image.size, format: format)
        return renderer.image { _ in
            image.draw(at: .zero)
        }
    }.value
}
```

#### メモリ使用量の計算

```swift
/// 画像のメモリ使用量を計算
func memorySize(of image: UIImage) -> Int {
    guard let cgImage = image.cgImage else { return 0 }
    
    let bytesPerPixel = cgImage.bitsPerPixel / 8
    let width = cgImage.width
    let height = cgImage.height
    
    return width * height * bytesPerPixel
}

// 例: 4000 x 3000 ピクセル、32bit カラー
// 4000 * 3000 * 4 = 48,000,000 bytes = 約 48MB
```

### データ構造の最適化

#### 値型 vs 参照型

```swift
// 参照型: ヒープ割り当て
class UserClass {
    var name: String
    var age: Int
    
    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

// 値型: スタック割り当て（小さい場合）
struct UserStruct {
    var name: String
    var age: Int
}

// 大量のオブジェクトを扱う場合、structの方がメモリ効率が良い
let users: [UserStruct] = loadUsers()  // 連続したメモリ配置
```

#### ContiguousArray

```swift
// 通常の Array（クラスの場合、間接参照が発生）
let items: [ItemClass] = ...

// ContiguousArray（常に連続したメモリ配置を保証）
let items: ContiguousArray<ItemClass> = ...

// プロトコル型の場合は特に効果的
protocol Item {}
let items: ContiguousArray<Item> = ...  // Existential Container のオーバーヘッド軽減
```

### キャッシュ戦略

#### NSCache の活用

```swift
class ImageCache {
    static let shared = ImageCache()
    
    private let cache = NSCache<NSString, UIImage>()
    
    init() {
        // メモリ警告時に自動クリア
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1024 * 1024  // 50MB
    }
    
    func image(for key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }
    
    func setImage(_ image: UIImage, for key: String) {
        let cost = image.cgImage.map { $0.bytesPerRow * $0.height } ?? 0
        cache.setObject(image, forKey: key as NSString, cost: cost)
    }
    
    func clear() {
        cache.removeAllObjects()
    }
}
```

#### 自前のLRUキャッシュ

```swift
class LRUCache<Key: Hashable, Value> {
    private let capacity: Int
    private var cache: [Key: Value] = [:]
    private var order: [Key] = []
    
    init(capacity: Int) {
        self.capacity = capacity
    }
    
    func get(_ key: Key) -> Value? {
        guard let value = cache[key] else { return nil }
        
        // アクセス順序を更新
        if let index = order.firstIndex(of: key) {
            order.remove(at: index)
            order.append(key)
        }
        
        return value
    }
    
    func set(_ key: Key, value: Value) {
        if cache[key] != nil {
            // 既存キーの更新
            if let index = order.firstIndex(of: key) {
                order.remove(at: index)
            }
        } else if cache.count >= capacity {
            // 最も古いエントリを削除
            if let oldest = order.first {
                cache.removeValue(forKey: oldest)
                order.removeFirst()
            }
        }
        
        cache[key] = value
        order.append(key)
    }
}
```

## Autorelease Pool の最適化

### ループ内での大量オブジェクト生成

```swift
// Bad: Autorelease Pool が溜まる
for i in 0..<10000 {
    let image = processImage(at: urls[i])
    results.append(image)
}

// Good: 定期的に Autorelease Pool を解放
for i in 0..<10000 {
    autoreleasepool {
        let image = processImage(at: urls[i])
        results.append(image)
    }
}

// Better: バッチ処理
for batch in urls.chunked(into: 100) {
    autoreleasepool {
        for url in batch {
            let image = processImage(at: url)
            results.append(image)
        }
    }
}
```

## メモリ使用量の監視

### プログラムによる監視

```swift
/// 現在のメモリ使用量を取得
func reportMemory() -> UInt64 {
    var info = mach_task_basic_info()
    var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4
    
    let kerr = withUnsafeMutablePointer(to: &info) {
        $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
            task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
        }
    }
    
    guard kerr == KERN_SUCCESS else {
        return 0
    }
    
    return info.resident_size
}

// 使用例
let memoryBefore = reportMemory()
performOperation()
let memoryAfter = reportMemory()
print("Memory delta: \(memoryAfter - memoryBefore) bytes")
```

### メモリ警告のハンドリング

```swift
class MemoryManager {
    static let shared = MemoryManager()
    
    private var warningObserver: Any?
    
    func startMonitoring() {
        warningObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.didReceiveMemoryWarningNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.handleMemoryWarning()
        }
    }
    
    private func handleMemoryWarning() {
        // 1. キャッシュクリア
        ImageCache.shared.clear()
        URLCache.shared.removeAllCachedResponses()
        
        // 2. 一時データ削除
        clearTemporaryData()
        
        // 3. 再作成可能なリソースを解放
        releaseRecreateableResources()
        
        // 4. ログ
        print("Memory warning handled")
    }
}
```

## チェックリスト

### メモリリーク防止

- [ ] クロージャで `[weak self]` または `[unowned self]` を使用
- [ ] デリゲートは `weak` で宣言
- [ ] Timer は deinit で invalidate
- [ ] NotificationCenter の observer を適切に解除
- [ ] Combine の cancellables を適切に管理

### メモリ効率

- [ ] 大きな画像はダウンサンプリング
- [ ] 表示に必要なサイズでのみ画像を保持
- [ ] NSCache を使用してメモリ警告時に自動解放
- [ ] 大量データ処理では autoreleasepool を使用
- [ ] 適切なデータ構造を選択（struct vs class）

### モニタリング

- [ ] deinit でオブジェクト解放を確認
- [ ] Memory Graph Debugger で定期的に確認
- [ ] Instruments (Leaks, Allocations) でプロファイリング
- [ ] メモリ警告ハンドラを実装
