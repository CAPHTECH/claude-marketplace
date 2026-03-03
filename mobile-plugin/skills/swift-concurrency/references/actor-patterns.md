# Swift Actor パターン集

## Actor の基本

### Actor とは

Actorは参照型で、内部の可変状態へのアクセスを直列化することでデータ競合を防ぐ。

```swift
actor Counter {
    private var count = 0

    func increment() {
        count += 1  // 安全：同時に1つのタスクのみ実行
    }

    func getCount() -> Int {
        count
    }
}
```

### Actor のアクセスルール

```swift
let counter = Counter()

// 外部からのアクセスは await が必要
let count = await counter.getCount()

// Actor 内部からは await 不要
actor Counter {
    func incrementAndGet() -> Int {
        increment()  // await 不要
        return getCount()  // await 不要
    }
}
```

## パターン集

### 1. キャッシュパターン

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]
    private var inProgress: [URL: Task<UIImage, Error>] = [:]

    func image(for url: URL) async throws -> UIImage {
        // キャッシュヒット
        if let cached = cache[url] {
            return cached
        }

        // 重複リクエストの防止
        if let existingTask = inProgress[url] {
            return try await existingTask.value
        }

        // 新しいリクエスト
        let task = Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            guard let image = UIImage(data: data) else {
                throw ImageError.invalidData
            }
            return image
        }

        inProgress[url] = task

        do {
            let image = try await task.value
            cache[url] = image
            inProgress.removeValue(forKey: url)
            return image
        } catch {
            inProgress.removeValue(forKey: url)
            throw error
        }
    }

    func clearCache() {
        cache.removeAll()
    }
}
```

### 2. シングルトンパターン

```swift
actor SharedDatabase {
    static let shared = SharedDatabase()

    private var connection: DatabaseConnection?

    private init() {}

    func connect() async throws {
        if connection == nil {
            connection = try await DatabaseConnection.open()
        }
    }

    func query(_ sql: String) async throws -> [Row] {
        guard let connection else {
            throw DatabaseError.notConnected
        }
        return try await connection.execute(sql)
    }
}

// 使用
await SharedDatabase.shared.connect()
let rows = try await SharedDatabase.shared.query("SELECT * FROM users")
```

### 3. 状態マシンパターン

```swift
actor DownloadManager {
    enum State {
        case idle
        case downloading(progress: Double)
        case completed(URL)
        case failed(Error)
    }

    private(set) var state: State = .idle

    func startDownload(from url: URL) async {
        state = .downloading(progress: 0)

        do {
            let localURL = try await performDownload(from: url) { progress in
                Task { await self.updateProgress(progress) }
            }
            state = .completed(localURL)
        } catch {
            state = .failed(error)
        }
    }

    private func updateProgress(_ progress: Double) {
        if case .downloading = state {
            state = .downloading(progress: progress)
        }
    }

    func reset() {
        state = .idle
    }
}
```

### 4. リソースプールパターン

```swift
actor ConnectionPool {
    private var available: [DatabaseConnection] = []
    private var inUse: Set<ObjectIdentifier> = []
    private let maxConnections: Int
    private var waitingContinuations: [CheckedContinuation<DatabaseConnection, Never>] = []

    init(maxConnections: Int = 10) {
        self.maxConnections = maxConnections
    }

    func acquire() async -> DatabaseConnection {
        // 利用可能な接続がある
        if let connection = available.popLast() {
            inUse.insert(ObjectIdentifier(connection))
            return connection
        }

        // 新しい接続を作成可能
        if inUse.count < maxConnections {
            let connection = await DatabaseConnection.create()
            inUse.insert(ObjectIdentifier(connection))
            return connection
        }

        // 待機
        return await withCheckedContinuation { continuation in
            waitingContinuations.append(continuation)
        }
    }

    func release(_ connection: DatabaseConnection) {
        inUse.remove(ObjectIdentifier(connection))

        if let continuation = waitingContinuations.first {
            waitingContinuations.removeFirst()
            inUse.insert(ObjectIdentifier(connection))
            continuation.resume(returning: connection)
        } else {
            available.append(connection)
        }
    }
}

// 使用
let pool = ConnectionPool()
let connection = await pool.acquire()
defer { Task { await pool.release(connection) } }
// connection を使用
```

### 5. イベントストリームパターン

```swift
actor EventBroadcaster<Event: Sendable> {
    private var continuations: [UUID: AsyncStream<Event>.Continuation] = [:]

    func subscribe() -> AsyncStream<Event> {
        let id = UUID()
        return AsyncStream { continuation in
            Task { await self.addSubscriber(id: id, continuation: continuation) }
            continuation.onTermination = { _ in
                Task { await self.removeSubscriber(id: id) }
            }
        }
    }

    private func addSubscriber(id: UUID, continuation: AsyncStream<Event>.Continuation) {
        continuations[id] = continuation
    }

    private func removeSubscriber(id: UUID) {
        continuations.removeValue(forKey: id)
    }

    func broadcast(_ event: Event) {
        for continuation in continuations.values {
            continuation.yield(event)
        }
    }
}

// 使用
let broadcaster = EventBroadcaster<UserEvent>()

Task {
    for await event in await broadcaster.subscribe() {
        print("Received: \(event)")
    }
}

await broadcaster.broadcast(.userLoggedIn(userId: "123"))
```

## GlobalActor

### カスタム GlobalActor

```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

// すべてのメソッドが DatabaseActor で実行される
@DatabaseActor
class DatabaseService {
    private var connection: Connection?

    func connect() async throws {
        connection = try await Connection.open()
    }

    func query(_ sql: String) async throws -> [Row] {
        guard let connection else {
            throw DatabaseError.notConnected
        }
        return try connection.execute(sql)
    }
}

// 個別のメソッドに適用
class MixedService {
    @DatabaseActor
    func saveToDatabase(_ data: Data) async throws {
        // DatabaseActor で実行
    }

    @MainActor
    func updateUI() {
        // MainActor で実行
    }
}
```

### MainActor の使い分け

```swift
// クラス全体に適用（ViewModel向け）
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func load() async {
        items = await repository.fetchAll()
    }
}

// 特定のプロパティに適用
class Service {
    @MainActor var uiState: UIState = .initial

    func process() async {
        // バックグラウンドで処理
        let result = await heavyComputation()

        // UI更新はMainActorで
        await MainActor.run {
            uiState = .completed(result)
        }
    }
}
```

## Actor の注意点

### 1. Actor Reentrancy

```swift
actor Counter {
    var count = 0

    func incrementTwice() async {
        count += 1
        await someAsyncWork()  // 他のタスクが実行される可能性
        count += 1  // count が予期しない値の可能性
    }
}

// 対策：状態を先に取得して処理
actor Counter {
    var count = 0

    func incrementTwice() async {
        let currentCount = count
        await someAsyncWork()
        count = currentCount + 2  // 明示的に期待値を設定
    }
}
```

### 2. Actor Isolation の境界

```swift
actor DataStore {
    var data: [String: Any] = [:]

    // 問題：辞書の参照を返すと外部で変更される可能性
    func getData() -> [String: Any] {
        data  // コピーが返される（値型なので安全）
    }

    // 問題：クラスの参照を返す
    func getItem() -> Item {  // Itemがclassの場合は危険
        items.first!
    }
}
```

### 3. デッドロック回避

```swift
// 問題：相互に await する
actor A {
    let b: B

    func doWork() async {
        await b.doWork()  // B の完了を待つ
    }
}

actor B {
    let a: A

    func doWork() async {
        await a.doWork()  // A の完了を待つ（デッドロック）
    }
}

// 対策：依存関係を単方向にする、または Task.detached を使う
```
