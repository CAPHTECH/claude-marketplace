# Swift 6 Strict Concurrency チェックリスト

## 移行準備チェック

### ビルド設定
```swift
// Package.swift
swiftSettings: [
    .enableExperimentalFeature("StrictConcurrency")
    // または
    .swiftLanguageMode(.v6)
]
```

### Xcodeプロジェクト
- Build Settings > Swift Compiler - Upcoming Features
- `SWIFT_STRICT_CONCURRENCY = complete`

## Sendable適合パターン

### 自動Sendable推論
```swift
// 値型は自動的にSendable（すべてのプロパティがSendable）
struct Point: Sendable {  // 明示的に書くのが推奨
    let x: Double
    let y: Double
}

// enumも同様
enum Direction: Sendable {
    case north, south, east, west
}
```

### 手動Sendable適合
```swift
// 参照型はActorか明示的なSendable適合が必要
final class Counter: Sendable {
    // 注意: すべてのプロパティが不変でSendableである必要
    let initialValue: Int

    init(initialValue: Int) {
        self.initialValue = initialValue
    }
}
```

### @unchecked Sendable
```swift
// 内部で同期を保証している場合のみ使用
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]

    func get(_ key: String) -> Any? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}
```

## Actor分離パターン

### 基本的なActor
```swift
actor UserRepository {
    private var users: [UUID: User] = [:]

    func add(_ user: User) {
        users[user.id] = user
    }

    func get(id: UUID) -> User? {
        users[id]
    }
}
```

### GlobalActor
```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
class DatabaseManager {
    // すべてのメソッドがDatabaseActorで実行される
    func query(_ sql: String) -> [Row] { ... }
}
```

### MainActor
```swift
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func loadItems() async {
        // UIスレッドで実行される
        items = await repository.fetchAll()
    }
}
```

### nonisolated
```swift
actor DataStore {
    let id: UUID  // 不変プロパティ

    nonisolated var identifier: String {
        // idは不変なのでactor分離なしでアクセス可能
        id.uuidString
    }

    nonisolated func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}
```

## クロージャとキャプチャ

### @Sendableクロージャ
```swift
func performAsync(completion: @Sendable @escaping () -> Void) {
    Task {
        await someAsyncWork()
        completion()
    }
}

// 使用例
let counter = Counter()
performAsync { [counter] in  // counterがSendableでないとエラー
    print(counter.value)
}
```

### Task内のキャプチャ
```swift
class ViewController {
    var data: [String] = []

    func loadData() {
        Task { [weak self] in
            // selfのキャプチャ注意
            guard let self else { return }

            // MainActorでない場合は明示的に
            await MainActor.run {
                self.data = newData
            }
        }
    }
}
```

## よくある問題と解決策

### 問題1: プロトコルにSendable要件を追加
```swift
// Before
protocol Repository {
    func fetch() async -> [Item]
}

// After
protocol Repository: Sendable {
    func fetch() async -> [Item]
}
```

### 問題2: デリゲートパターン
```swift
// Before
protocol DataDelegate: AnyObject {
    func didUpdate(data: [Item])
}

// After
protocol DataDelegate: AnyObject, Sendable {
    @MainActor func didUpdate(data: [Item])
}
```

### 問題3: Notification
```swift
// 安全なNotification Observer
Task { @MainActor in
    for await _ in NotificationCenter.default.notifications(named: .myNotification) {
        // MainActorで処理
        handleNotification()
    }
}
```

## 段階的移行戦略

### Phase 1: 警告を有効化
```swift
// Package.swift
.enableUpcomingFeature("StrictConcurrency")
```

### Phase 2: 新コードから適用
- 新規作成ファイルはStrict Concurrency準拠
- 既存コードは警告を確認しながら修正

### Phase 3: モジュール単位で移行
- ユーティリティモジュールから開始
- 依存関係の少ないモジュールを優先

### Phase 4: アプリ全体をSwift 6モードへ
```swift
// Package.swift
swiftLanguageMode: .v6
```
