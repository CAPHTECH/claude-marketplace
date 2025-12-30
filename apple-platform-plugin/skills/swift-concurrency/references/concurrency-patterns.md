# Swift Concurrency パターン集

## async/await パターン

### 1. 基本的な非同期呼び出し

```swift
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}
```

### 2. 複数の非同期処理の並列実行

```swift
// async letパターン
async let user = fetchUser()
async let posts = fetchPosts()
let (u, p) = try await (user, posts)

// TaskGroupパターン
try await withThrowingTaskGroup(of: Item.self) { group in
    for id in ids {
        group.addTask { try await fetchItem(id) }
    }
    return try await group.reduce(into: []) { $0.append($1) }
}
```

### 3. タイムアウト付き処理

```swift
func fetchWithTimeout() async throws -> Data {
    try await withThrowingTaskGroup(of: Data.self) { group in
        group.addTask {
            try await fetchData()
        }
        group.addTask {
            try await Task.sleep(for: .seconds(10))
            throw TimeoutError()
        }
        let result = try await group.next()!
        group.cancelAll()
        return result
    }
}
```

## Actor パターン

### 1. 基本的なActor

```swift
actor Counter {
    private var count = 0
    
    func increment() { count += 1 }
    func getCount() -> Int { count }
}
```

### 2. グローバルActor

```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
func performDatabaseOperation() async { }
```

### 3. Actor間の連携

```swift
actor UserService {
    func getUser(id: String) async -> User? { ... }
}

actor PostService {
    let userService: UserService
    
    func getPosts(for userId: String) async -> [Post] {
        guard let user = await userService.getUser(id: userId) else {
            return []
        }
        return user.posts
    }
}
```

## Sendable パターン

### 1. 値型（自動的にSendable）

```swift
struct UserData: Sendable {
    let id: UUID
    let name: String
}
```

### 2. 不変クラス

```swift
final class Config: Sendable {
    let apiKey: String
    init(apiKey: String) { self.apiKey = apiKey }
}
```

### 3. @unchecked Sendable（内部で同期を保証）

```swift
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]
    
    func get(_ key: String) -> Any? {
        lock.withLock { storage[key] }
    }
}
```

## MainActor パターン

### 1. ビュー全体をMainActorに

```swift
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
    
    func load() async {
        items = try? await fetchItems() ?? []
    }
}
```

### 2. 特定のメソッドのみMainActorに

```swift
class DataManager {
    func processData() async -> [Item] {
        // バックグラウンド処理
        let items = await fetchItems()
        await updateUI(items)
        return items
    }
    
    @MainActor
    private func updateUI(_ items: [Item]) {
        // UI更新
    }
}
```

### 3. MainActor.runの使用

```swift
func loadData() async {
    let data = try? await fetchData()
    await MainActor.run {
        self.data = data
    }
}
```

## Task管理パターン

### 1. キャンセル可能なTask

```swift
class SearchViewModel {
    private var searchTask: Task<Void, Never>?
    
    func search(_ query: String) {
        searchTask?.cancel()
        searchTask = Task {
            try? await Task.sleep(for: .milliseconds(300))
            guard !Task.isCancelled else { return }
            // 検索実行
        }
    }
}
```

### 2. 優先度の指定

```swift
Task(priority: .userInitiated) { await loadCriticalData() }
Task(priority: .background) { await syncData() }
```

### 3. Detached Task

```swift
Task.detached(priority: .utility) {
    await self.cleanupCache()
}
```
