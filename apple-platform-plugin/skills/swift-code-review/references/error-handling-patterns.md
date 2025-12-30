# Swift エラーハンドリングパターン

## エラーの分類

### 回復可能なエラー（Recoverable Errors）
ユーザーに通知して再試行可能なエラー。`throws`/`Result`で表現。

```swift
enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError(code: Int)
    case invalidResponse
}

func fetchData() async throws -> Data {
    guard let url = URL(string: endpoint) else {
        throw NetworkError.invalidResponse
    }
    // ...
}
```

### 回復不能なエラー（Unrecoverable Errors）
プログラムのバグや不正な状態。`fatalError`/`precondition`で表現。

```swift
func processItem(at index: Int) {
    precondition(index >= 0, "Index must be non-negative")
    // ...
}

func handleUnexpectedState() -> Never {
    fatalError("Entered unexpected state - this is a bug")
}
```

## エラー型の設計

### 具体的なエラー型
```swift
// 良い例: 具体的で情報を持つ
enum AuthenticationError: LocalizedError {
    case invalidCredentials
    case accountLocked(until: Date)
    case sessionExpired
    case networkUnavailable(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "ユーザー名またはパスワードが正しくありません"
        case .accountLocked(let until):
            return "アカウントは\(until.formatted())までロックされています"
        case .sessionExpired:
            return "セッションの有効期限が切れました"
        case .networkUnavailable:
            return "ネットワーク接続を確認してください"
        }
    }
}
```

### エラーの階層化
```swift
enum AppError: Error {
    case network(NetworkError)
    case storage(StorageError)
    case validation(ValidationError)
    case unknown(Error)
}

// 使用例
do {
    try await networkService.fetch()
} catch let error as NetworkError {
    throw AppError.network(error)
} catch {
    throw AppError.unknown(error)
}
```

## throws と Result の使い分け

### throws を使う場合
- 即座にエラー処理する場合
- async/awaitと組み合わせる場合
- エラーが例外的な場合

```swift
func loadUser(id: UUID) async throws -> User {
    guard let user = try await repository.find(id: id) else {
        throw UserError.notFound(id: id)
    }
    return user
}
```

### Result を使う場合
- エラーを後で処理する場合
- コールバックやクロージャで使う場合
- エラーが通常のフローの一部の場合

```swift
func validate(_ input: String) -> Result<ValidatedInput, ValidationError> {
    guard !input.isEmpty else {
        return .failure(.empty)
    }
    guard input.count >= 8 else {
        return .failure(.tooShort(minimum: 8))
    }
    return .success(ValidatedInput(value: input))
}

// 使用例
let results = inputs.map { validate($0) }
let (successes, failures) = results.partitioned()
```

## Optionalの適切な使用

### Optional vs throws
```swift
// Optional: 値がないことが正常なケース
func findUser(byEmail email: String) -> User? {
    users.first { $0.email == email }
}

// throws: 値がないことがエラーのケース
func getUser(id: UUID) throws -> User {
    guard let user = users[id] else {
        throw UserError.notFound(id: id)
    }
    return user
}
```

### 安全なアンラップパターン
```swift
// guard let: 早期リターン
func process(_ value: String?) {
    guard let value else {
        logger.warning("Value was nil")
        return
    }
    // valueを使用
}

// if let: 条件分岐
func display(_ value: String?) {
    if let value {
        label.text = value
    } else {
        label.text = "N/A"
    }
}

// map/flatMap: 変換
let length = optionalString.map { $0.count }  // Int?
let user = optionalId.flatMap { users[$0] }   // User?

// nil合体演算子: デフォルト値
let name = user?.name ?? "Unknown"
```

## async/await とエラー

### Task でのエラーハンドリング
```swift
Task {
    do {
        let data = try await fetchData()
        try await processData(data)
    } catch is CancellationError {
        // キャンセルは特別扱い
        logger.info("Task was cancelled")
    } catch {
        // その他のエラー
        await handleError(error)
    }
}
```

### TaskGroup でのエラー
```swift
func fetchAll(ids: [UUID]) async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item.self) { group in
        for id in ids {
            group.addTask {
                try await self.fetch(id: id)
            }
        }

        var results: [Item] = []
        for try await item in group {
            results.append(item)
        }
        return results
    }
}
```

## ベストプラクティス

### 1. エラーは具体的に
```swift
// Bad
throw NSError(domain: "App", code: -1, userInfo: nil)

// Good
throw ValidationError.invalidEmail(provided: email)
```

### 2. LocalizedErrorを実装
```swift
enum DataError: LocalizedError {
    case corrupted(file: String)

    var errorDescription: String? {
        switch self {
        case .corrupted(let file):
            return "ファイル '\(file)' が破損しています"
        }
    }

    var recoverySuggestion: String? {
        "ファイルを削除して再度ダウンロードしてください"
    }
}
```

### 3. rethrowsの活用
```swift
func withRetry<T>(
    attempts: Int = 3,
    operation: () async throws -> T
) async rethrows -> T {
    var lastError: Error?
    for _ in 0..<attempts {
        do {
            return try await operation()
        } catch {
            lastError = error
            try await Task.sleep(for: .seconds(1))
        }
    }
    throw lastError!
}
```

### 4. 強制アンラップを避ける
```swift
// Bad
let url = URL(string: urlString)!

// Good (静的な場合)
let url = URL(string: "https://example.com")!  // コンパイル時に検証可能

// Good (動的な場合)
guard let url = URL(string: urlString) else {
    throw URLError(.badURL)
}
```
