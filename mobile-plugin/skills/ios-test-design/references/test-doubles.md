# テストダブル設計ガイド

## テストダブルの種類

### 概要

| 種類 | 目的 | 入力 | 出力 | 検証 |
|-----|------|------|------|------|
| Dummy | 引数を埋める | 未使用 | 未使用 | なし |
| Stub | 事前定義した値を返す | 無視 | 固定値 | なし |
| Spy | 呼び出しを記録 | 記録 | 本物or固定 | 呼び出し履歴 |
| Mock | 期待値を検証 | 検証 | 固定値 | 期待値との一致 |
| Fake | 軽量な実装 | 使用 | 計算結果 | なし |

### 使い分けの指針

```
依存先が副作用を持つ？
  ├─ Yes → 副作用を制御したい？
  │         ├─ Yes → Stub（出力制御）/ Mock（呼び出し検証）
  │         └─ No  → Fake（軽量実装）
  └─ No  → 出力を固定したい？
            ├─ Yes → Stub
            └─ No  → Spy（呼び出し記録のみ）
```

## プロトコルベースの設計

### 1. プロトコルの定義

```swift
// 抽象化されたプロトコル
protocol UserRepositoryProtocol {
    func fetch(id: String) async throws -> User
    func save(_ user: User) async throws
    func delete(id: String) async throws
    func fetchAll() async throws -> [User]
}

// 本番実装
final class UserRepository: UserRepositoryProtocol {
    private let apiClient: APIClient
    private let cache: CacheStorage
    
    func fetch(id: String) async throws -> User {
        if let cached = cache.get(key: id) as User? {
            return cached
        }
        let user = try await apiClient.request(UserEndpoint.fetch(id: id))
        cache.set(key: id, value: user)
        return user
    }
    
    // ... 他のメソッド
}
```

### 2. Stub の実装

```swift
/// 事前定義した値を返すスタブ
final class StubUserRepository: UserRepositoryProtocol {
    // 返却値の設定
    var fetchResult: Result<User, Error> = .success(User.stub)
    var saveResult: Result<Void, Error> = .success(())
    var deleteResult: Result<Void, Error> = .success(())
    var fetchAllResult: Result<[User], Error> = .success([])
    
    func fetch(id: String) async throws -> User {
        try fetchResult.get()
    }
    
    func save(_ user: User) async throws {
        try saveResult.get()
    }
    
    func delete(id: String) async throws {
        try deleteResult.get()
    }
    
    func fetchAll() async throws -> [User] {
        try fetchAllResult.get()
    }
}

// 使用例
func test_viewModel_fetchUser_success() async {
    // Given
    let stub = StubUserRepository()
    stub.fetchResult = .success(User(id: "1", name: "Test"))
    let viewModel = UserViewModel(repository: stub)
    
    // When
    await viewModel.loadUser(id: "1")
    
    // Then
    XCTAssertEqual(viewModel.user?.name, "Test")
}
```

### 3. Mock の実装

```swift
/// 呼び出しを検証するモック
final class MockUserRepository: UserRepositoryProtocol {
    // 呼び出し記録
    private(set) var fetchCallCount = 0
    private(set) var saveCallCount = 0
    private(set) var deleteCallCount = 0
    
    // 引数記録
    private(set) var lastFetchedId: String?
    private(set) var lastSavedUser: User?
    private(set) var lastDeletedId: String?
    
    // 返却値設定
    var fetchResult: Result<User, Error> = .success(User.stub)
    var saveResult: Result<Void, Error> = .success(())
    var deleteResult: Result<Void, Error> = .success(())
    var fetchAllResult: Result<[User], Error> = .success([])
    
    func fetch(id: String) async throws -> User {
        fetchCallCount += 1
        lastFetchedId = id
        return try fetchResult.get()
    }
    
    func save(_ user: User) async throws {
        saveCallCount += 1
        lastSavedUser = user
        try saveResult.get()
    }
    
    func delete(id: String) async throws {
        deleteCallCount += 1
        lastDeletedId = id
        try deleteResult.get()
    }
    
    func fetchAll() async throws -> [User] {
        try fetchAllResult.get()
    }
    
    // 検証ヘルパー
    func verify(fetchCalledWith id: String, file: StaticString = #file, line: UInt = #line) {
        XCTAssertEqual(lastFetchedId, id, file: file, line: line)
    }
    
    func verify(saveCalledWith user: User, file: StaticString = #file, line: UInt = #line) {
        XCTAssertEqual(lastSavedUser, user, file: file, line: line)
    }
}

// 使用例
func test_saveUser_callsRepository() async {
    // Given
    let mock = MockUserRepository()
    let useCase = SaveUserUseCase(repository: mock)
    let user = User(id: "1", name: "Test")
    
    // When
    try await useCase.execute(user)
    
    // Then
    XCTAssertEqual(mock.saveCallCount, 1)
    mock.verify(saveCalledWith: user)
}
```

### 4. Spy の実装

```swift
/// 呼び出し履歴を記録するスパイ
final class SpyUserRepository: UserRepositoryProtocol {
    // 呼び出し履歴
    enum Call: Equatable {
        case fetch(id: String)
        case save(user: User)
        case delete(id: String)
        case fetchAll
    }
    
    private(set) var callHistory: [Call] = []
    
    // 返却値設定（実際の値を返すことも可能）
    var fetchResult: Result<User, Error> = .success(User.stub)
    var saveResult: Result<Void, Error> = .success(())
    var deleteResult: Result<Void, Error> = .success(())
    var fetchAllResult: Result<[User], Error> = .success([])
    
    func fetch(id: String) async throws -> User {
        callHistory.append(.fetch(id: id))
        return try fetchResult.get()
    }
    
    func save(_ user: User) async throws {
        callHistory.append(.save(user: user))
        try saveResult.get()
    }
    
    func delete(id: String) async throws {
        callHistory.append(.delete(id: id))
        try deleteResult.get()
    }
    
    func fetchAll() async throws -> [User] {
        callHistory.append(.fetchAll)
        return try fetchAllResult.get()
    }
    
    // 履歴クリア
    func reset() {
        callHistory.removeAll()
    }
}

// 使用例: 呼び出し順序の検証
func test_syncUser_callsInCorrectOrder() async {
    // Given
    let spy = SpyUserRepository()
    let syncService = UserSyncService(repository: spy)
    
    // When
    await syncService.sync(userId: "1")
    
    // Then
    XCTAssertEqual(spy.callHistory, [
        .fetch(id: "1"),
        .save(user: User.stub),
    ])
}
```

### 5. Fake の実装

```swift
/// インメモリで動作する軽量実装
final class FakeUserRepository: UserRepositoryProtocol {
    private var storage: [String: User] = [:]
    
    func fetch(id: String) async throws -> User {
        guard let user = storage[id] else {
            throw RepositoryError.notFound
        }
        return user
    }
    
    func save(_ user: User) async throws {
        storage[user.id] = user
    }
    
    func delete(id: String) async throws {
        storage.removeValue(forKey: id)
    }
    
    func fetchAll() async throws -> [User] {
        Array(storage.values)
    }
    
    // テスト用ヘルパー
    func seed(_ users: [User]) {
        for user in users {
            storage[user.id] = user
        }
    }
    
    func clear() {
        storage.removeAll()
    }
}

// 使用例: 統合テスト
func test_userFlow_createAndFetch() async throws {
    // Given
    let fake = FakeUserRepository()
    let createUseCase = CreateUserUseCase(repository: fake)
    let fetchUseCase = FetchUserUseCase(repository: fake)
    
    // When: ユーザー作成
    let newUser = User(id: "1", name: "New User")
    try await createUseCase.execute(newUser)
    
    // Then: 作成したユーザーを取得できる
    let fetchedUser = try await fetchUseCase.execute(userId: "1")
    XCTAssertEqual(fetchedUser.name, "New User")
}
```

## 自動生成パターン

### Protocol Witness パターン

```swift
// Protocol Witness 構造体
struct UserRepositoryWitness {
    var fetch: (String) async throws -> User
    var save: (User) async throws -> Void
    var delete: (String) async throws -> Void
    var fetchAll: () async throws -> [User]
}

extension UserRepositoryWitness {
    /// 本番実装
    static func live(apiClient: APIClient) -> Self {
        Self(
            fetch: { id in try await apiClient.request(UserEndpoint.fetch(id: id)) },
            save: { user in try await apiClient.request(UserEndpoint.save(user: user)) },
            delete: { id in try await apiClient.request(UserEndpoint.delete(id: id)) },
            fetchAll: { try await apiClient.request(UserEndpoint.fetchAll) }
        )
    }
    
    /// テスト用スタブ
    static func stub(
        fetch: @escaping (String) async throws -> User = { _ in User.stub },
        save: @escaping (User) async throws -> Void = { _ in },
        delete: @escaping (String) async throws -> Void = { _ in },
        fetchAll: @escaping () async throws -> [User] = { [] }
    ) -> Self {
        Self(fetch: fetch, save: save, delete: delete, fetchAll: fetchAll)
    }
}

// 使用例
func test_with_witness() async {
    let witness = UserRepositoryWitness.stub(
        fetch: { _ in User(id: "1", name: "Stubbed") }
    )
    
    let user = try await witness.fetch("1")
    XCTAssertEqual(user.name, "Stubbed")
}
```

## 外部依存のモック

### ネットワーク

```swift
protocol NetworkClientProtocol {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

final class MockNetworkClient: NetworkClientProtocol {
    var responses: [String: Any] = [:]
    var errors: [String: Error] = [:]
    
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let key = endpoint.path
        
        if let error = errors[key] {
            throw error
        }
        
        guard let response = responses[key] as? T else {
            throw NetworkError.noMockData
        }
        
        return response
    }
    
    func setResponse<T: Encodable>(_ response: T, for path: String) {
        responses[path] = response
    }
    
    func setError(_ error: Error, for path: String) {
        errors[path] = error
    }
}
```

### 永続化

```swift
protocol StorageProtocol {
    func save<T: Encodable>(_ value: T, forKey key: String) throws
    func load<T: Decodable>(forKey key: String) throws -> T?
    func delete(forKey key: String) throws
}

final class InMemoryStorage: StorageProtocol {
    private var storage: [String: Data] = [:]
    
    func save<T: Encodable>(_ value: T, forKey key: String) throws {
        storage[key] = try JSONEncoder().encode(value)
    }
    
    func load<T: Decodable>(forKey key: String) throws -> T? {
        guard let data = storage[key] else { return nil }
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    func delete(forKey key: String) throws {
        storage.removeValue(forKey: key)
    }
}
```

### 時間

```swift
protocol DateProviderProtocol {
    var now: Date { get }
}

struct SystemDateProvider: DateProviderProtocol {
    var now: Date { Date() }
}

final class MockDateProvider: DateProviderProtocol {
    var now: Date
    
    init(now: Date = Date()) {
        self.now = now
    }
    
    func advance(by interval: TimeInterval) {
        now = now.addingTimeInterval(interval)
    }
}

// 使用例
func test_session_expiresAfter30Minutes() {
    // Given
    let dateProvider = MockDateProvider(now: Date())
    let session = Session(createdAt: dateProvider.now, expiresIn: 1800)
    
    // When: 29分経過
    dateProvider.advance(by: 29 * 60)
    
    // Then: まだ有効
    XCTAssertFalse(session.isExpired(at: dateProvider.now))
    
    // When: さらに2分経過（合計31分）
    dateProvider.advance(by: 2 * 60)
    
    // Then: 期限切れ
    XCTAssertTrue(session.isExpired(at: dateProvider.now))
}
```

### 乱数

```swift
protocol RandomGeneratorProtocol {
    func nextInt(in range: Range<Int>) -> Int
    func nextDouble() -> Double
    func nextBool() -> Bool
}

struct SystemRandomGenerator: RandomGeneratorProtocol {
    func nextInt(in range: Range<Int>) -> Int {
        Int.random(in: range)
    }
    
    func nextDouble() -> Double {
        Double.random(in: 0..<1)
    }
    
    func nextBool() -> Bool {
        Bool.random()
    }
}

final class SeededRandomGenerator: RandomGeneratorProtocol {
    private var values: [Any]
    private var index = 0
    
    init(intSequence: [Int] = [], doubleSequence: [Double] = [], boolSequence: [Bool] = []) {
        self.values = intSequence.map { $0 as Any } 
                    + doubleSequence.map { $0 as Any }
                    + boolSequence.map { $0 as Any }
    }
    
    func nextInt(in range: Range<Int>) -> Int {
        defer { index += 1 }
        return values[index % values.count] as! Int
    }
    
    func nextDouble() -> Double {
        defer { index += 1 }
        return values[index % values.count] as! Double
    }
    
    func nextBool() -> Bool {
        defer { index += 1 }
        return values[index % values.count] as! Bool
    }
}
```

## ベストプラクティス

### 1. テストダブルの命名規則

```
Mock<Protocol>   - 呼び出し検証が主目的
Stub<Protocol>   - 固定値返却が主目的
Fake<Protocol>   - 軽量実装
Spy<Protocol>    - 呼び出し記録
```

### 2. 検証メソッドの提供

```swift
final class MockAnalytics: AnalyticsProtocol {
    private(set) var trackedEvents: [(name: String, params: [String: Any])] = []
    
    func track(event: String, params: [String: Any]) {
        trackedEvents.append((event, params))
    }
    
    // 検証ヘルパー
    func assertTracked(
        _ event: String,
        file: StaticString = #file,
        line: UInt = #line
    ) {
        let found = trackedEvents.contains { $0.name == event }
        XCTAssertTrue(found, "Event '\(event)' was not tracked", file: file, line: line)
    }
    
    func assertTracked(
        _ event: String,
        with params: [String: Any],
        file: StaticString = #file,
        line: UInt = #line
    ) {
        let found = trackedEvents.contains { 
            $0.name == event && NSDictionary(dictionary: $0.params).isEqual(to: params)
        }
        XCTAssertTrue(found, "Event '\(event)' with params was not tracked", file: file, line: line)
    }
}
```

### 3. リセット機能の提供

```swift
protocol Resettable {
    func reset()
}

final class MockUserRepository: UserRepositoryProtocol, Resettable {
    private(set) var fetchCallCount = 0
    private(set) var lastFetchedId: String?
    var fetchResult: Result<User, Error> = .success(User.stub)
    
    func reset() {
        fetchCallCount = 0
        lastFetchedId = nil
        fetchResult = .success(User.stub)
    }
    
    // ... 他のメソッド
}
```

### 4. 遅延シミュレーション

```swift
final class DelayedMockRepository: UserRepositoryProtocol {
    var delay: TimeInterval = 0.1
    var fetchResult: Result<User, Error> = .success(User.stub)
    
    func fetch(id: String) async throws -> User {
        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        return try fetchResult.get()
    }
}
```
