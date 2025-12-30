---
name: swift-concurrency
description: |
  Swift Concurrency支援。async/await、Actor、Sendable、データ競合防止。
  使用タイミング: (1) 並行処理コードの実装時、(2) Swift 6 Strict Concurrency対応時、
  (3) データ競合の診断・修正時、(4) MainActorとバックグラウンド処理の設計時
---

# Swift Concurrency 支援スキル

Swift Concurrencyの正しい使用法とデータ競合防止をガイドする。

## 対象

- async/await パターン
- Actor と隔離
- Sendable 準拠
- Task と構造化並行性
- @MainActor とUI更新

## Swift 6 Strict Concurrency

### Sendable要件

```swift
// ✅ 値型は自動的にSendable
struct UserData: Sendable {
    let id: UUID
    let name: String
}

// ✅ Actorは暗黙的にSendable
actor DataManager {
    private var cache: [String: Data] = [:]
    
    func getData(for key: String) -> Data? {
        cache[key]
    }
}

// ⚠️ クラスは明示的な対応が必要
// 方法1: @unchecked Sendable（内部で同期を保証）
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]
    
    func get(_ key: String) -> Any? {
        lock.withLock { storage[key] }
    }
}

// 方法2: 不変クラス
final class ImmutableConfig: Sendable {
    let apiURL: URL
    let timeout: TimeInterval
    
    init(apiURL: URL, timeout: TimeInterval) {
        self.apiURL = apiURL
        self.timeout = timeout
    }
}
```

### Actor隔離

```swift
// グローバルActor定義
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

// Actor隔離されたクラス
@DatabaseActor
class DatabaseService {
    private var connection: DatabaseConnection?
    
    func query(_ sql: String) async throws -> [Row] {
        // DatabaseActor上で実行される
        guard let conn = connection else {
            throw DatabaseError.notConnected
        }
        return try await conn.execute(sql)
    }
}

// MainActorへの切り替え
@DatabaseActor
class ViewModel {
    private var data: [Item] = []
    
    func loadData() async {
        let items = try? await fetchItems()
        
        // UI更新はMainActorで
        await MainActor.run {
            self.updateUI(with: items ?? [])
        }
    }
    
    @MainActor
    private func updateUI(with items: [Item]) {
        // UI更新処理
    }
}
```

## async/await パターン

### 基本パターン

```swift
// 非同期関数
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw APIError.invalidResponse
    }
    
    return try JSONDecoder().decode(User.self, from: data)
}

// 呼び出し
func loadUserProfile() async {
    do {
        let user = try await fetchUser(id: "123")
        await MainActor.run {
            self.user = user
        }
    } catch {
        await MainActor.run {
            self.error = error
        }
    }
}
```

### 並列実行

```swift
// async let で並列実行
func loadDashboard() async throws -> Dashboard {
    async let user = fetchUser()
    async let posts = fetchPosts()
    async let notifications = fetchNotifications()
    
    // すべて並列で実行され、結果を待つ
    return try await Dashboard(
        user: user,
        posts: posts,
        notifications: notifications
    )
}

// TaskGroupで動的な並列処理
func fetchAllUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await self.fetchUser(id: id)
            }
        }
        
        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}
```

## Task管理

### 構造化並行性

```swift
class SearchViewModel: ObservableObject {
    @Published var results: [SearchResult] = []
    @Published var isSearching = false
    
    private var searchTask: Task<Void, Never>?
    
    func search(query: String) {
        // 前の検索をキャンセル
        searchTask?.cancel()
        
        searchTask = Task {
            await MainActor.run {
                isSearching = true
            }
            
            // デバウンス
            try? await Task.sleep(for: .milliseconds(300))
            
            // キャンセルチェック
            guard !Task.isCancelled else { return }
            
            do {
                let results = try await performSearch(query)
                
                guard !Task.isCancelled else { return }
                
                await MainActor.run {
                    self.results = results
                    self.isSearching = false
                }
            } catch {
                guard !Task.isCancelled else { return }
                
                await MainActor.run {
                    self.isSearching = false
                }
            }
        }
    }
    
    deinit {
        searchTask?.cancel()
    }
}
```

### 優先度とdetached Task

```swift
// 優先度指定
Task(priority: .userInitiated) {
    await loadCriticalData()
}

Task(priority: .background) {
    await performBackgroundSync()
}

// detached Task（親のコンテキストを継承しない）
Task.detached(priority: .utility) {
    await self.cleanupCache()
}
```

## よくあるエラーと解決策

### 1. Sendable違反

```swift
// ❌ エラー: Capture of 'self' with non-sendable type
class DataLoader {
    var data: [String] = []
    
    func load() {
        Task {
            self.data = await fetchData()  // エラー
        }
    }
}

// ✅ 解決策1: Actorにする
actor DataLoader {
    var data: [String] = []
    
    func load() {
        Task {
            self.data = await fetchData()  // OK
        }
    }
}

// ✅ 解決策2: @MainActorを使う
@MainActor
class DataLoader {
    var data: [String] = []
    
    func load() {
        Task {
            self.data = await fetchData()  // OK
        }
    }
}
```

### 2. Actor再入問題

```swift
actor BankAccount {
    var balance: Int = 0
    
    // ⚠️ awaitの前後でbalanceが変わる可能性
    func transferTo(_ other: BankAccount, amount: Int) async {
        guard balance >= amount else { return }
        
        balance -= amount  // ここで中断
        await other.deposit(amount)  // 他のタスクがbalanceを変更可能
        // 戻ってきた時、想定外の状態かも
    }
    
    // ✅ トランザクション的に処理
    func withdraw(_ amount: Int) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
    
    func deposit(_ amount: Int) {
        balance += amount
    }
}

// 呼び出し側で制御
func transfer(from: BankAccount, to: BankAccount, amount: Int) async {
    let withdrawn = await from.withdraw(amount)
    if withdrawn {
        await to.deposit(amount)
    }
}
```

### 3. MainActor隔離

```swift
// ❌ バックグラウンドからUI更新
func loadData() async {
    let data = try? await fetchData()
    self.items = data  // MainActorでない場合エラー
}

// ✅ 明示的にMainActorで実行
func loadData() async {
    let data = try? await fetchData()
    await MainActor.run {
        self.items = data
    }
}

// ✅ またはプロパティをMainActorに
@MainActor
var items: [Item] = []
```

## チェックリスト

### 設計時
- [ ] 共有状態を持つクラスはActorにすべきか検討
- [ ] Sendable要件を満たす型設計か
- [ ] MainActorの範囲は適切か

### 実装時
- [ ] async letで並列化できる箇所はあるか
- [ ] Taskのキャンセル処理を実装したか
- [ ] await前後での状態変化を考慮したか

### レビュー時
- [ ] @unchecked Sendableの使用は正当化されているか
- [ ] nonisolated(unsafe)の使用は避けられているか
- [ ] 循環参照やメモリリークはないか
