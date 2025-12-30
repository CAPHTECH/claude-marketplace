# CPU最適化詳細

## CPU 使用率の理解

### スレッドと優先度

```swift
// Quality of Service (QoS) レベル
// 高優先度 → 低優先度
.userInteractive  // UI更新、アニメーション
.userInitiated    // ユーザーアクションの即時結果
.default          // 一般的な処理
.utility          // 長時間処理、プログレス表示あり
.background       // バックグラウンド処理、ユーザーには見えない

// 使用例
DispatchQueue.global(qos: .userInitiated).async {
    // 重い処理
}

Task(priority: .userInitiated) {
    // async/await での重い処理
}
```

### メインスレッドの保護

```swift
// Bad: メインスレッドをブロック
func loadData() {
    let data = try! Data(contentsOf: url)  // 同期読み込み
    process(data)
    updateUI()
}

// Good: バックグラウンドで処理
func loadData() async {
    let data = await Task.detached(priority: .userInitiated) {
        try? Data(contentsOf: url)
    }.value
    
    guard let data = data else { return }
    
    let processed = await Task.detached {
        process(data)
    }.value
    
    await MainActor.run {
        updateUI(with: processed)
    }
}
```

## 処理の最適化

### アルゴリズムの改善

#### 検索の最適化

```swift
// Bad: O(n) の線形検索
func findUser(id: String, in users: [User]) -> User? {
    users.first { $0.id == id }
}

// Good: O(1) のハッシュ検索
class UserRepository {
    private var usersById: [String: User] = [:]
    
    func addUser(_ user: User) {
        usersById[user.id] = user
    }
    
    func findUser(id: String) -> User? {
        usersById[id]
    }
}
```

#### ソートの最適化

```swift
// Bad: 毎回ソート
func getSortedItems() -> [Item] {
    items.sorted { $0.date > $1.date }
}

// Good: ソート済み状態を維持
class ItemManager {
    private var sortedItems: [Item] = []
    
    func addItem(_ item: Item) {
        // 二分探索で挿入位置を決定
        let index = sortedItems.insertionIndex(of: item) { $0.date > $1.date }
        sortedItems.insert(item, at: index)
    }
}

extension Array {
    func insertionIndex(of element: Element, isOrderedBefore: (Element, Element) -> Bool) -> Int {
        var low = 0
        var high = count
        while low < high {
            let mid = (low + high) / 2
            if isOrderedBefore(self[mid], element) {
                low = mid + 1
            } else {
                high = mid
            }
        }
        return low
    }
}
```

### 遅延評価

#### lazy の活用

```swift
// Bad: 即時評価
let processedItems = items.map { process($0) }.filter { $0.isValid }

// Good: 遅延評価
let processedItems = items.lazy.map { process($0) }.filter { $0.isValid }

// 必要な分だけ処理される
for item in processedItems.prefix(10) {
    display(item)
}
```

#### Computed Property の最適化

```swift
// Bad: 毎回計算
var formattedDate: String {
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    return formatter.string(from: date)
}

// Good: キャッシュ
private var _formattedDate: String?
var formattedDate: String {
    if let cached = _formattedDate {
        return cached
    }
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    let result = formatter.string(from: date)
    _formattedDate = result
    return result
}

// Better: lazy var（不変の場合）
lazy var formattedDate: String = {
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    return formatter.string(from: date)
}()
```

### バッチ処理

```swift
// Bad: 個別処理
for item in items {
    saveToDatabase(item)
}

// Good: バッチ処理
func saveToDatabase(items: [Item]) {
    database.performBatchUpdates {
        for item in items {
            database.insert(item)
        }
    }
}
```

## 並行処理の最適化

### Task Group

```swift
// 並列処理で複数の画像をダウンロード
func downloadImages(urls: [URL]) async -> [UIImage] {
    await withTaskGroup(of: (Int, UIImage?).self) { group in
        for (index, url) in urls.enumerated() {
            group.addTask {
                let image = try? await downloadImage(from: url)
                return (index, image)
            }
        }
        
        var images = Array<UIImage?>(repeating: nil, count: urls.count)
        for await (index, image) in group {
            images[index] = image
        }
        
        return images.compactMap { $0 }
    }
}
```

### Actor

```swift
// データ競合を防ぐ
actor DataStore {
    private var cache: [String: Data] = [:]
    
    func getData(for key: String) -> Data? {
        cache[key]
    }
    
    func setData(_ data: Data, for key: String) {
        cache[key] = data
    }
}

// 使用
let store = DataStore()
Task {
    await store.setData(data, for: "key")
    let cached = await store.getData(for: "key")
}
```

### 適切な並列度

```swift
// システムの推奨並列度を使用
let processorCount = ProcessInfo.processInfo.activeProcessorCount

// OperationQueue での制御
let queue = OperationQueue()
queue.maxConcurrentOperationCount = processorCount

// カスタム制御
actor ConcurrencyLimiter {
    private let limit: Int
    private var running = 0
    private var waiting: [CheckedContinuation<Void, Never>] = []
    
    init(limit: Int) {
        self.limit = limit
    }
    
    func acquire() async {
        if running < limit {
            running += 1
        } else {
            await withCheckedContinuation { continuation in
                waiting.append(continuation)
            }
        }
    }
    
    func release() {
        if let next = waiting.first {
            waiting.removeFirst()
            next.resume()
        } else {
            running -= 1
        }
    }
}
```

## 特定処理の最適化

### 文字列処理

```swift
// Bad: 文字列連結
var result = ""
for item in items {
    result += item.description + ", "
}

// Good: joined
let result = items.map { $0.description }.joined(separator: ", ")

// Better: 大量の場合は reserveCapacity
var result = ""
result.reserveCapacity(items.count * 20)  // 推定サイズ
for item in items {
    result += item.description + ", "
}
```

### JSON パース

```swift
// 大きな JSON のストリーミングパース
func parseJSONStream(data: Data) throws -> [Item] {
    var items: [Item] = []
    
    try JSONSerialization.jsonObject(with: data, options: .fragmentsAllowed)
    
    // または、Codable でのパース最適化
    let decoder = JSONDecoder()
    decoder.dateDecodingStrategy = .iso8601
    
    // バッチでデコード
    return try decoder.decode([Item].self, from: data)
}
```

### 正規表現

```swift
// Bad: 毎回コンパイル
func matches(_ string: String) -> Bool {
    let regex = try! NSRegularExpression(pattern: pattern)
    return regex.firstMatch(in: string, range: NSRange(string.startIndex..., in: string)) != nil
}

// Good: 事前コンパイル
class Matcher {
    private let regex: NSRegularExpression
    
    init(pattern: String) throws {
        regex = try NSRegularExpression(pattern: pattern)
    }
    
    func matches(_ string: String) -> Bool {
        regex.firstMatch(in: string, range: NSRange(string.startIndex..., in: string)) != nil
    }
}

// Swift 5.7+ Regex
let regex = /\d{3}-\d{4}/
if string.contains(regex) { ... }
```

### DateFormatter

```swift
// Bad: 毎回生成
func formatDate(_ date: Date) -> String {
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    return formatter.string(from: date)
}

// Good: 再利用
class DateFormatterCache {
    static let shared = DateFormatterCache()
    
    private var formatters: [String: DateFormatter] = [:]
    private let queue = DispatchQueue(label: "DateFormatterCache")
    
    func formatter(for format: String) -> DateFormatter {
        queue.sync {
            if let existing = formatters[format] {
                return existing
            }
            let formatter = DateFormatter()
            formatter.dateFormat = format
            formatters[format] = formatter
            return formatter
        }
    }
}
```

## Time Profiler の活用

### 分析手順

1. **全体像の把握**
   ```
   - Weight でソート
   - 最も時間を消費している関数を特定
   ```

2. **ホットパスの特定**
   ```
   - Call Tree を展開
   - 深い呼び出しで時間がかかっている箇所を特定
   ```

3. **ボトルネックの分類**
   ```
   - CPU bound: 計算処理
   - I/O bound: ファイル/ネットワーク
   - Wait: ロック待ち
   ```

### よくあるパターン

#### メインスレッドのブロック

```
症状: UI がフリーズする
確認: Main Thread のトレースを確認
対策: 重い処理をバックグラウンドへ
```

#### 過剰なオブジェクト生成

```
症状: Allocations で大量のオブジェクト
確認: Time Profiler で alloc/init が多い
対策: オブジェクトの再利用、プール
```

#### 非効率なループ

```
症状: 同じ関数が大量に呼ばれている
確認: Call Tree で呼び出し回数を確認
対策: アルゴリズム改善、キャッシュ
```

## パフォーマンステスト

### XCTest での計測

```swift
func testPerformance() throws {
    let items = (0..<10000).map { Item(id: $0) }
    
    measure {
        _ = items.sorted { $0.id < $1.id }
    }
}

func testPerformanceWithMetrics() throws {
    let metrics: [XCTMetric] = [
        XCTClockMetric(),
        XCTCPUMetric(),
        XCTMemoryMetric()
    ]
    
    let options = XCTMeasureOptions()
    options.iterationCount = 10
    
    measure(metrics: metrics, options: options) {
        performOperation()
    }
}
```

### Baseline の設定

```swift
// Baseline を設定して性能劣化を検出
func testCriticalPathPerformance() throws {
    // Edit Scheme → Test → Options → Performance
    // Baseline を設定すると、劣化時にテスト失敗
    
    measure {
        criticalOperation()
    }
}
```

## チェックリスト

### 設計時

- [ ] 適切なデータ構造を選択
- [ ] アルゴリズムの計算量を考慮
- [ ] 並行処理の必要性を検討
- [ ] キャッシュ戦略を計画

### 実装時

- [ ] メインスレッドをブロックしない
- [ ] 適切な QoS を設定
- [ ] 遅延評価を活用
- [ ] 不要な計算を避ける

### テスト時

- [ ] Time Profiler でホットスポットを確認
- [ ] パフォーマンステストを作成
- [ ] Baseline を設定
- [ ] 複数デバイスで検証
