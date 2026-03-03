# Swift Task パターン集

## Task の基本

### Task の種類

| 種類 | 継承 | 用途 |
|------|------|------|
| Task { } | 優先度、Actor | 通常の非同期作業 |
| Task.detached { } | なし | 独立したバックグラウンド処理 |
| TaskGroup | 優先度、Actor | 複数タスクの並列実行 |

### 基本的な使用法

```swift
// 構造化 Task
func loadData() {
    Task {
        let data = try await fetchData()
        await MainActor.run {
            updateUI(with: data)
        }
    }
}

// デタッチド Task（構造化されない）
func startBackgroundSync() {
    Task.detached(priority: .background) {
        await syncAllData()
    }
}
```

## キャンセレーションパターン

### 1. 検索デバウンス

```swift
class SearchController {
    private var searchTask: Task<Void, Never>?

    func search(query: String) {
        // 前回の検索をキャンセル
        searchTask?.cancel()

        guard !query.isEmpty else {
            results = []
            return
        }

        searchTask = Task {
            // デバウンス（300ms待機）
            do {
                try await Task.sleep(for: .milliseconds(300))
            } catch {
                return  // キャンセルされた
            }

            // キャンセルされていなければ検索実行
            guard !Task.isCancelled else { return }

            let results = await performSearch(query)

            guard !Task.isCancelled else { return }

            await MainActor.run {
                self.results = results
            }
        }
    }
}
```

### 2. 協調的キャンセル

```swift
func downloadFiles(urls: [URL]) async throws -> [Data] {
    var results: [Data] = []

    for url in urls {
        // キャンセルチェックポイント
        try Task.checkCancellation()

        let data = try await downloadFile(url: url)
        results.append(data)
    }

    return results
}

// 長時間処理でのキャンセルチェック
func processLargeDataset(_ data: [Item]) async throws -> [ProcessedItem] {
    var processed: [ProcessedItem] = []

    for (index, item) in data.enumerated() {
        // 100件ごとにキャンセルチェック
        if index % 100 == 0 {
            try Task.checkCancellation()
        }

        processed.append(process(item))
    }

    return processed
}
```

### 3. クリーンアップ付きキャンセル

```swift
func downloadWithCleanup(url: URL) async throws -> Data {
    let tempFile = createTempFile()

    return try await withTaskCancellationHandler {
        // 通常の処理
        let data = try await download(to: tempFile, from: url)
        return data
    } onCancel: {
        // キャンセル時のクリーンアップ
        // 注意：同期的に実行される
        try? FileManager.default.removeItem(at: tempFile)
    }
}
```

## TaskGroup パターン

### 1. 並列フェッチ

```swift
func fetchAllUsers(ids: [UUID]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await self.fetchUser(id: id)
            }
        }

        var users: [User] = []
        users.reserveCapacity(ids.count)

        for try await user in group {
            users.append(user)
        }

        return users
    }
}
```

### 2. 順序を保持した並列処理

```swift
func fetchUsersOrdered(ids: [UUID]) async throws -> [User] {
    try await withThrowingTaskGroup(of: (Int, User).self) { group in
        for (index, id) in ids.enumerated() {
            group.addTask {
                let user = try await self.fetchUser(id: id)
                return (index, user)
            }
        }

        var indexedResults: [(Int, User)] = []
        indexedResults.reserveCapacity(ids.count)

        for try await result in group {
            indexedResults.append(result)
        }

        // インデックスでソートして返す
        return indexedResults
            .sorted { $0.0 < $1.0 }
            .map(\.1)
    }
}
```

### 3. 最初の成功を返す

```swift
func fetchFromMultipleSources<T: Sendable>(
    sources: [() async throws -> T]
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        for source in sources {
            group.addTask {
                try await source()
            }
        }

        // 最初に成功したものを返す
        guard let first = try await group.next() else {
            throw FetchError.noResults
        }

        // 残りのタスクをキャンセル
        group.cancelAll()

        return first
    }
}
```

### 4. 並列数の制限

```swift
func processWithLimit(
    items: [Item],
    maxConcurrency: Int = 4
) async throws -> [ProcessedItem] {
    try await withThrowingTaskGroup(of: ProcessedItem.self) { group in
        var iterator = items.makeIterator()
        var results: [ProcessedItem] = []
        results.reserveCapacity(items.count)

        // 最初のバッチを追加
        for _ in 0..<min(maxConcurrency, items.count) {
            if let item = iterator.next() {
                group.addTask {
                    try await self.process(item)
                }
            }
        }

        // 1つ完了するごとに次を追加
        for try await result in group {
            results.append(result)

            if let item = iterator.next() {
                group.addTask {
                    try await self.process(item)
                }
            }
        }

        return results
    }
}
```

### 5. 部分的な失敗を許容

```swift
func fetchWithPartialResults(ids: [UUID]) async -> [Result<User, Error>] {
    await withTaskGroup(of: (Int, Result<User, Error>).self) { group in
        for (index, id) in ids.enumerated() {
            group.addTask {
                do {
                    let user = try await self.fetchUser(id: id)
                    return (index, .success(user))
                } catch {
                    return (index, .failure(error))
                }
            }
        }

        var results: [(Int, Result<User, Error>)] = []
        for await result in group {
            results.append(result)
        }

        return results
            .sorted { $0.0 < $1.0 }
            .map(\.1)
    }
}
```

## タイムアウトパターン

### 1. レース方式

```swift
func fetchWithTimeout<T>(
    timeout: Duration,
    operation: @escaping () async throws -> T
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask {
            try await operation()
        }

        group.addTask {
            try await Task.sleep(for: timeout)
            throw TimeoutError()
        }

        guard let result = try await group.next() else {
            throw TimeoutError()
        }

        group.cancelAll()
        return result
    }
}

// 使用
let data = try await fetchWithTimeout(timeout: .seconds(10)) {
    try await fetchLargeData()
}
```

### 2. withTimeout ユーティリティ

```swift
struct TimeoutError: Error {}

func withTimeout<T: Sendable>(
    _ duration: Duration,
    operation: @Sendable @escaping () async throws -> T
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask(operation: operation)

        group.addTask {
            try await Task.sleep(for: duration)
            throw TimeoutError()
        }

        defer { group.cancelAll() }

        if let result = try await group.next() {
            return result
        }

        throw TimeoutError()
    }
}
```

## リトライパターン

### 1. 指数バックオフ

```swift
func withExponentialBackoff<T>(
    maxAttempts: Int = 3,
    initialDelay: Duration = .seconds(1),
    maxDelay: Duration = .seconds(30),
    operation: () async throws -> T
) async throws -> T {
    var delay = initialDelay
    var lastError: Error?

    for attempt in 1...maxAttempts {
        do {
            return try await operation()
        } catch {
            lastError = error

            if attempt < maxAttempts {
                try await Task.sleep(for: delay)
                delay = min(delay * 2, maxDelay)
            }
        }
    }

    throw lastError!
}

// 使用
let data = try await withExponentialBackoff {
    try await fetchData()
}
```

### 2. 条件付きリトライ

```swift
func withRetry<T>(
    maxAttempts: Int = 3,
    shouldRetry: (Error) -> Bool = { _ in true },
    operation: () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 1...maxAttempts {
        do {
            return try await operation()
        } catch {
            lastError = error

            // 特定のエラーのみリトライ
            guard shouldRetry(error), attempt < maxAttempts else {
                throw error
            }

            try await Task.sleep(for: .seconds(1))
        }
    }

    throw lastError!
}

// 使用
let data = try await withRetry(
    shouldRetry: { error in
        if let apiError = error as? APIError {
            return apiError.isRetryable
        }
        return false
    }
) {
    try await fetchData()
}
```

## AsyncStream パターン

### 1. イベントストリーム

```swift
func notifications(named name: Notification.Name) -> AsyncStream<Notification> {
    AsyncStream { continuation in
        let observer = NotificationCenter.default.addObserver(
            forName: name,
            object: nil,
            queue: nil
        ) { notification in
            continuation.yield(notification)
        }

        continuation.onTermination = { _ in
            NotificationCenter.default.removeObserver(observer)
        }
    }
}

// 使用
for await notification in notifications(named: .userLoggedIn) {
    handleLogin(notification)
}
```

### 2. ポーリング

```swift
func poll<T>(
    interval: Duration,
    fetch: @escaping () async throws -> T
) -> AsyncThrowingStream<T, Error> {
    AsyncThrowingStream { continuation in
        let task = Task {
            while !Task.isCancelled {
                do {
                    let value = try await fetch()
                    continuation.yield(value)
                    try await Task.sleep(for: interval)
                } catch {
                    continuation.finish(throwing: error)
                    return
                }
            }
        }

        continuation.onTermination = { _ in
            task.cancel()
        }
    }
}
```
