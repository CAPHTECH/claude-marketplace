# テストデータ管理ガイド

## テストデータ戦略

### データカテゴリ

| カテゴリ | 用途 | 管理方法 |
|---------|------|---------|
| Factory | オブジェクト生成 | Swiftコード |
| Fixture | 静的データ | JSON/plistファイル |
| Seed | 初期状態 | スクリプト/コード |
| Builder | 複雑なオブジェクト | Builderパターン |

## Factory パターン

### 基本構造

```swift
// MARK: - User Factory

enum UserFactory {
    /// デフォルト値でUserを生成
    static func make(
        id: String = UUID().uuidString,
        name: String = "Test User",
        email: String = "test@example.com",
        age: Int = 25,
        isActive: Bool = true,
        createdAt: Date = Date()
    ) -> User {
        User(
            id: id,
            name: name,
            email: email,
            age: age,
            isActive: isActive,
            createdAt: createdAt
        )
    }
    
    // MARK: - Presets
    
    /// アクティブユーザー
    static var active: User {
        make(isActive: true)
    }
    
    /// 非アクティブユーザー
    static var inactive: User {
        make(isActive: false)
    }
    
    /// 管理者ユーザー
    static var admin: User {
        make(name: "Admin User", email: "admin@example.com")
    }
    
    /// 未成年ユーザー
    static var minor: User {
        make(age: 17)
    }
    
    /// 複数ユーザーのリスト
    static func makeList(count: Int) -> [User] {
        (0..<count).map { i in
            make(
                id: "user-\(i)",
                name: "User \(i)",
                email: "user\(i)@example.com"
            )
        }
    }
}
```

### 関連オブジェクトを含むFactory

```swift
// MARK: - Order Factory

enum OrderFactory {
    static func make(
        id: String = UUID().uuidString,
        user: User = UserFactory.make(),
        items: [OrderItem] = [OrderItemFactory.make()],
        status: OrderStatus = .pending,
        createdAt: Date = Date()
    ) -> Order {
        Order(
            id: id,
            user: user,
            items: items,
            status: status,
            createdAt: createdAt
        )
    }
    
    /// 完了済み注文
    static var completed: Order {
        make(status: .completed)
    }
    
    /// キャンセル済み注文
    static var cancelled: Order {
        make(status: .cancelled)
    }
    
    /// 複数商品を含む注文
    static func withMultipleItems(count: Int) -> Order {
        make(items: OrderItemFactory.makeList(count: count))
    }
}

enum OrderItemFactory {
    static func make(
        id: String = UUID().uuidString,
        product: Product = ProductFactory.make(),
        quantity: Int = 1,
        price: Decimal = 1000
    ) -> OrderItem {
        OrderItem(
            id: id,
            product: product,
            quantity: quantity,
            price: price
        )
    }
    
    static func makeList(count: Int) -> [OrderItem] {
        (0..<count).map { i in
            make(
                id: "item-\(i)",
                quantity: i + 1,
                price: Decimal(1000 * (i + 1))
            )
        }
    }
}
```

## Builder パターン

### 複雑なオブジェクト用Builder

```swift
// MARK: - User Builder

final class UserBuilder {
    private var id: String = UUID().uuidString
    private var name: String = "Test User"
    private var email: String = "test@example.com"
    private var age: Int = 25
    private var isActive: Bool = true
    private var preferences: UserPreferences = .default
    private var addresses: [Address] = []
    private var paymentMethods: [PaymentMethod] = []
    
    @discardableResult
    func with(id: String) -> Self {
        self.id = id
        return self
    }
    
    @discardableResult
    func with(name: String) -> Self {
        self.name = name
        return self
    }
    
    @discardableResult
    func with(email: String) -> Self {
        self.email = email
        return self
    }
    
    @discardableResult
    func with(age: Int) -> Self {
        self.age = age
        return self
    }
    
    @discardableResult
    func active(_ isActive: Bool = true) -> Self {
        self.isActive = isActive
        return self
    }
    
    @discardableResult
    func with(preferences: UserPreferences) -> Self {
        self.preferences = preferences
        return self
    }
    
    @discardableResult
    func with(addresses: [Address]) -> Self {
        self.addresses = addresses
        return self
    }
    
    @discardableResult
    func addAddress(_ address: Address) -> Self {
        self.addresses.append(address)
        return self
    }
    
    @discardableResult
    func with(paymentMethods: [PaymentMethod]) -> Self {
        self.paymentMethods = paymentMethods
        return self
    }
    
    func build() -> User {
        User(
            id: id,
            name: name,
            email: email,
            age: age,
            isActive: isActive,
            preferences: preferences,
            addresses: addresses,
            paymentMethods: paymentMethods
        )
    }
}

// 使用例
func test_complexUser() {
    let user = UserBuilder()
        .with(name: "Premium User")
        .with(email: "premium@example.com")
        .active()
        .addAddress(AddressFactory.make(type: .home))
        .addAddress(AddressFactory.make(type: .work))
        .with(paymentMethods: [PaymentMethodFactory.creditCard])
        .build()
    
    XCTAssertEqual(user.addresses.count, 2)
    XCTAssertEqual(user.paymentMethods.count, 1)
}
```

## Fixture ファイル管理

### ディレクトリ構造

```
Tests/
├── Fixtures/
│   ├── JSON/
│   │   ├── Users/
│   │   │   ├── single_user.json
│   │   │   ├── user_list.json
│   │   │   └── user_with_orders.json
│   │   ├── Products/
│   │   │   ├── product.json
│   │   │   └── product_list.json
│   │   └── Errors/
│   │       ├── validation_error.json
│   │       └── network_error.json
│   └── Stubs/
│       ├── User+Stub.swift
│       └── Product+Stub.swift
```

### Fixture ローダー

```swift
// MARK: - Fixture Loader

enum FixtureLoader {
    enum FixtureError: Error {
        case fileNotFound(String)
        case decodingFailed(Error)
    }
    
    /// JSONファイルからオブジェクトを読み込む
    static func load<T: Decodable>(
        _ filename: String,
        as type: T.Type,
        in subdirectory: String? = nil
    ) throws -> T {
        let bundle = Bundle(for: BundleToken.self)
        
        var path: String?
        if let subdirectory = subdirectory {
            path = bundle.path(forResource: filename, ofType: "json", inDirectory: "Fixtures/JSON/\(subdirectory)")
        } else {
            path = bundle.path(forResource: filename, ofType: "json", inDirectory: "Fixtures/JSON")
        }
        
        guard let filePath = path else {
            throw FixtureError.fileNotFound(filename)
        }
        
        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: filePath))
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(T.self, from: data)
        } catch {
            throw FixtureError.decodingFailed(error)
        }
    }
    
    /// 生データを読み込む
    static func loadData(_ filename: String, extension ext: String = "json") throws -> Data {
        let bundle = Bundle(for: BundleToken.self)
        guard let url = bundle.url(forResource: filename, withExtension: ext, subdirectory: "Fixtures") else {
            throw FixtureError.fileNotFound(filename)
        }
        return try Data(contentsOf: url)
    }
}

private class BundleToken {}

// 使用例
func test_decodeUserFromFixture() throws {
    let user: User = try FixtureLoader.load("single_user", as: User.self, in: "Users")
    XCTAssertEqual(user.id, "fixture-user-1")
}
```

### Fixture ファイルの例

```json
// single_user.json
{
    "id": "fixture-user-1",
    "name": "Fixture User",
    "email": "fixture@example.com",
    "age": 30,
    "isActive": true,
    "createdAt": "2024-01-01T00:00:00Z"
}

// user_list.json
[
    {
        "id": "user-1",
        "name": "User One",
        "email": "user1@example.com",
        "age": 25,
        "isActive": true,
        "createdAt": "2024-01-01T00:00:00Z"
    },
    {
        "id": "user-2",
        "name": "User Two",
        "email": "user2@example.com",
        "age": 30,
        "isActive": false,
        "createdAt": "2024-01-02T00:00:00Z"
    }
]
```

## Stub 拡張

### Model + Stub

```swift
// User+Stub.swift

extension User {
    /// 基本的なスタブ
    static var stub: User {
        UserFactory.make()
    }
    
    /// 特定条件のスタブ
    static var stubActive: User {
        UserFactory.active
    }
    
    static var stubInactive: User {
        UserFactory.inactive
    }
    
    static var stubAdmin: User {
        UserFactory.admin
    }
}

// 使用例
func test_displayUser() {
    let viewModel = UserViewModel(user: .stub)
    XCTAssertNotNil(viewModel.displayName)
}
```

## テストデータの境界値

### 境界値ファクトリ

```swift
enum BoundaryTestData {
    // MARK: - String Boundaries
    
    static var emptyString: String { "" }
    static var singleChar: String { "a" }
    static var maxLengthString: String { String(repeating: "a", count: 255) }
    static var overMaxLengthString: String { String(repeating: "a", count: 256) }
    static var unicodeString: String { "日本語テスト🎉" }
    static var specialCharsString: String { "<script>alert('xss')</script>" }
    
    // MARK: - Numeric Boundaries
    
    static var zeroInt: Int { 0 }
    static var negativeInt: Int { -1 }
    static var maxInt: Int { Int.max }
    static var minInt: Int { Int.min }
    
    static var zeroDecimal: Decimal { 0 }
    static var smallDecimal: Decimal { 0.01 }
    static var largeDecimal: Decimal { 999999999.99 }
    
    // MARK: - Date Boundaries
    
    static var distantPast: Date { Date.distantPast }
    static var distantFuture: Date { Date.distantFuture }
    static var epoch: Date { Date(timeIntervalSince1970: 0) }
    static var now: Date { Date() }
    static var yesterday: Date { Calendar.current.date(byAdding: .day, value: -1, to: Date())! }
    static var tomorrow: Date { Calendar.current.date(byAdding: .day, value: 1, to: Date())! }
    
    // MARK: - Collection Boundaries
    
    static var emptyArray: [Any] { [] }
    static var singleElementArray: [Int] { [1] }
    static func largeArray(count: Int = 10000) -> [Int] {
        Array(0..<count)
    }
}
```

### 無効データファクトリ

```swift
enum InvalidTestData {
    // MARK: - Invalid Email
    
    static var invalidEmails: [String] {
        [
            "",
            "invalid",
            "@nodomain.com",
            "no@domain",
            "spaces in@email.com",
            "double@@at.com",
            ".startswithdot@email.com"
        ]
    }
    
    // MARK: - Invalid Password
    
    static var weakPasswords: [String] {
        [
            "",           // 空
            "short",      // 短すぎ
            "12345678",   // 数字のみ
            "abcdefgh",   // 小文字のみ
            "ABCDEFGH"    // 大文字のみ
        ]
    }
    
    // MARK: - Invalid Phone
    
    static var invalidPhones: [String] {
        [
            "",
            "abc",
            "123",        // 短すぎ
            "123456789012345"  // 長すぎ
        ]
    }
}
```

## テストコンテキスト

### コンテキスト管理

```swift
// MARK: - Test Context

final class TestContext {
    // 日付
    var currentDate: Date = Date()
    var dateProvider: MockDateProvider
    
    // ユーザー
    var currentUser: User?
    var userRepository: MockUserRepository
    
    // 設定
    var featureFlags: [String: Bool] = [:]
    var appConfig: AppConfig
    
    init() {
        dateProvider = MockDateProvider(now: currentDate)
        userRepository = MockUserRepository()
        appConfig = AppConfig.default
    }
    
    // MARK: - Convenience Setters
    
    @discardableResult
    func withLoggedInUser(_ user: User = .stub) -> Self {
        currentUser = user
        userRepository.currentUser = user
        return self
    }
    
    @discardableResult
    func withFeatureFlag(_ flag: String, enabled: Bool) -> Self {
        featureFlags[flag] = enabled
        return self
    }
    
    @discardableResult
    func withDate(_ date: Date) -> Self {
        currentDate = date
        dateProvider.now = date
        return self
    }
    
    // MARK: - Factory Methods
    
    func makeViewModel() -> HomeViewModel {
        HomeViewModel(
            userRepository: userRepository,
            dateProvider: dateProvider,
            featureFlags: featureFlags
        )
    }
}

// 使用例
final class HomeViewModelTests: XCTestCase {
    private var context: TestContext!
    
    override func setUp() {
        super.setUp()
        context = TestContext()
    }
    
    func test_greeting_whenLoggedIn_showsUserName() {
        // Given
        context.withLoggedInUser(UserFactory.make(name: "Alice"))
        let viewModel = context.makeViewModel()
        
        // When/Then
        XCTAssertEqual(viewModel.greeting, "Hello, Alice!")
    }
    
    func test_feature_whenFlagEnabled_showsNewUI() {
        // Given
        context
            .withLoggedInUser()
            .withFeatureFlag("new_home_ui", enabled: true)
        let viewModel = context.makeViewModel()
        
        // When/Then
        XCTAssertTrue(viewModel.showNewUI)
    }
}
```

## データベーステストデータ

### Seed データ

```swift
// MARK: - Database Seeder

final class DatabaseSeeder {
    private let database: DatabaseProtocol
    
    init(database: DatabaseProtocol) {
        self.database = database
    }
    
    func seedMinimal() async throws {
        // 最小限のデータ
        try await database.insert(UserFactory.make(id: "user-1"))
    }
    
    func seedStandard() async throws {
        // 標準的なテストデータ
        for i in 0..<10 {
            try await database.insert(UserFactory.make(id: "user-\(i)"))
        }
        
        for i in 0..<5 {
            try await database.insert(ProductFactory.make(id: "product-\(i)"))
        }
    }
    
    func seedLarge() async throws {
        // 大量データ（パフォーマンステスト用）
        for i in 0..<1000 {
            try await database.insert(UserFactory.make(id: "user-\(i)"))
        }
    }
    
    func clear() async throws {
        try await database.deleteAll(User.self)
        try await database.deleteAll(Product.self)
        try await database.deleteAll(Order.self)
    }
}

// 使用例
final class DatabaseTests: XCTestCase {
    private var database: InMemoryDatabase!
    private var seeder: DatabaseSeeder!
    
    override func setUp() async throws {
        try await super.setUp()
        database = InMemoryDatabase()
        seeder = DatabaseSeeder(database: database)
    }
    
    override func tearDown() async throws {
        try await seeder.clear()
        try await super.tearDown()
    }
    
    func test_fetchUsers_returnsAllSeededUsers() async throws {
        // Given
        try await seeder.seedStandard()
        let repository = UserRepository(database: database)
        
        // When
        let users = try await repository.fetchAll()
        
        // Then
        XCTAssertEqual(users.count, 10)
    }
}
```

## ベストプラクティス

### 1. デフォルト値の活用

```swift
// Good: デフォルト値で簡潔に
let user = UserFactory.make()
let userWithName = UserFactory.make(name: "Custom Name")

// Bad: 毎回全引数指定
let user = User(id: "1", name: "Test", email: "test@example.com", age: 25, isActive: true)
```

### 2. 意図が明確なプリセット

```swift
// Good: 意図が明確
let admin = UserFactory.admin
let expiredSession = SessionFactory.expired

// Bad: マジックナンバー
let user = UserFactory.make(age: 17)  // 何のための17歳？
```

### 3. テストデータの独立性

```swift
// Good: 各テストで独立したデータ
func test_A() {
    let user = UserFactory.make(id: "test-a-user")
    // ...
}

func test_B() {
    let user = UserFactory.make(id: "test-b-user")
    // ...
}

// Bad: 共有データへの依存
static let sharedUser = UserFactory.make()  // 状態が共有される危険
```

### 4. ファイル管理

```swift
// ファイル配置
Tests/
├── Factories/
│   ├── UserFactory.swift
│   ├── ProductFactory.swift
│   └── OrderFactory.swift
├── Builders/
│   ├── UserBuilder.swift
│   └── OrderBuilder.swift
├── Fixtures/
│   └── JSON/
│       └── ...
└── Helpers/
    ├── FixtureLoader.swift
    └── TestContext.swift
```
