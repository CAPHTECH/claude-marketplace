# XCTestパターン集

## 基本パターン

### AAA（Arrange-Act-Assert）パターン

```swift
func test_calculate_withPositiveNumbers_returnsSum() {
    // Arrange（準備）
    let calculator = Calculator()
    let a = 5
    let b = 3
    
    // Act（実行）
    let result = calculator.add(a, b)
    
    // Assert（検証）
    XCTAssertEqual(result, 8)
}
```

### Given-When-Then パターン

```swift
func test_user_whenDeactivated_becomesInactive() {
    // Given: アクティブなユーザー
    var user = User(name: "Test", isActive: true)
    
    // When: 非アクティブ化
    user.deactivate()
    
    // Then: 非アクティブ状態
    XCTAssertFalse(user.isActive)
}
```

## 非同期テストパターン

### async/await テスト

```swift
func test_fetchUser_returnsUser() async throws {
    // Given
    let repository = MockUserRepository()
    repository.fetchResult = .success(User.stub)
    let useCase = FetchUserUseCase(repository: repository)
    
    // When
    let user = try await useCase.execute(userId: "123")
    
    // Then
    XCTAssertEqual(user.id, "123")
}
```

### Expectation パターン（レガシー非同期）

```swift
func test_fetchData_completesWithSuccess() {
    // Given
    let expectation = expectation(description: "Fetch completes")
    let service = DataService()
    var receivedData: Data?
    
    // When
    service.fetchData { result in
        if case .success(let data) = result {
            receivedData = data
        }
        expectation.fulfill()
    }
    
    // Then
    wait(for: [expectation], timeout: 5.0)
    XCTAssertNotNil(receivedData)
}
```

### Combine テスト

```swift
func test_publisher_emitsValues() {
    // Given
    let viewModel = ViewModel()
    var cancellables = Set<AnyCancellable>()
    var receivedValues: [String] = []
    let expectation = expectation(description: "Values received")
    expectation.expectedFulfillmentCount = 3
    
    // When
    viewModel.$state
        .dropFirst() // 初期値をスキップ
        .sink { value in
            receivedValues.append(value)
            expectation.fulfill()
        }
        .store(in: &cancellables)
    
    viewModel.performActions()
    
    // Then
    wait(for: [expectation], timeout: 1.0)
    XCTAssertEqual(receivedValues, ["loading", "loaded", "idle"])
}
```

## エラーハンドリングテスト

### throws テスト

```swift
func test_parse_withInvalidJSON_throwsDecodingError() {
    // Given
    let invalidJSON = "{ invalid }"
    let parser = JSONParser<User>()
    
    // When/Then
    XCTAssertThrowsError(try parser.parse(invalidJSON)) { error in
        XCTAssertTrue(error is DecodingError)
    }
}
```

### 特定エラーの検証

```swift
func test_validate_withEmptyName_throwsValidationError() {
    // Given
    let validator = UserValidator()
    let user = User(name: "", email: "test@example.com")
    
    // When/Then
    XCTAssertThrowsError(try validator.validate(user)) { error in
        guard case ValidationError.emptyField(let field) = error else {
            XCTFail("Expected ValidationError.emptyField")
            return
        }
        XCTAssertEqual(field, "name")
    }
}
```

## パラメータ化テスト

### 複数入力のテスト

```swift
func test_isValidEmail_withVariousInputs() {
    // テストケース定義
    let testCases: [(input: String, expected: Bool)] = [
        ("test@example.com", true),
        ("user.name@domain.co.jp", true),
        ("invalid", false),
        ("@nodomain.com", false),
        ("no@domain", false),
        ("", false)
    ]
    
    let validator = EmailValidator()
    
    for (input, expected) in testCases {
        // When
        let result = validator.isValid(input)
        
        // Then
        XCTAssertEqual(result, expected, "Failed for input: \(input)")
    }
}
```

### 境界値テスト

```swift
func test_passwordStrength_atBoundaries() {
    let testCases: [(length: Int, expected: PasswordStrength)] = [
        (0, .invalid),
        (1, .weak),
        (7, .weak),
        (8, .medium),    // 境界: 8文字以上でmedium
        (9, .medium),
        (11, .medium),
        (12, .strong),   // 境界: 12文字以上でstrong
        (13, .strong),
        (100, .strong)
    ]
    
    let checker = PasswordChecker()
    
    for (length, expected) in testCases {
        let password = String(repeating: "a", count: length)
        let result = checker.checkStrength(password)
        XCTAssertEqual(result, expected, "Failed for length: \(length)")
    }
}
```

## モック検証パターン

### 呼び出し回数の検証

```swift
func test_save_callsRepositoryOnce() {
    // Given
    let mockRepository = MockUserRepository()
    let useCase = SaveUserUseCase(repository: mockRepository)
    
    // When
    useCase.execute(User.stub)
    
    // Then
    XCTAssertEqual(mockRepository.saveCallCount, 1)
}
```

### 引数の検証

```swift
func test_search_passesCorrectQuery() {
    // Given
    let mockAPI = MockSearchAPI()
    let searchService = SearchService(api: mockAPI)
    
    // When
    searchService.search(query: "test", filters: ["category": "books"])
    
    // Then
    XCTAssertEqual(mockAPI.lastQuery, "test")
    XCTAssertEqual(mockAPI.lastFilters?["category"], "books")
}
```

### 呼び出し順序の検証

```swift
func test_process_callsMethodsInOrder() {
    // Given
    let spy = SpyProcessor()
    let orchestrator = Orchestrator(processor: spy)
    
    // When
    orchestrator.process()
    
    // Then
    XCTAssertEqual(spy.callLog, ["prepare", "execute", "cleanup"])
}
```

## セットアップ/ティアダウンパターン

### クラスレベルセットアップ

```swift
final class DatabaseTests: XCTestCase {
    static var testDatabase: TestDatabase!
    
    override class func setUp() {
        super.setUp()
        // クラス全体で一度だけ実行（重い初期化）
        testDatabase = TestDatabase()
        testDatabase.migrate()
    }
    
    override class func tearDown() {
        testDatabase.destroy()
        testDatabase = nil
        super.tearDown()
    }
    
    override func setUp() {
        super.setUp()
        // 各テスト前にデータをクリア
        Self.testDatabase.truncateAll()
    }
}
```

### コンテキスト別セットアップ

```swift
final class UserViewModelTests: XCTestCase {
    private var sut: UserViewModel!
    private var mockRepository: MockUserRepository!
    
    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        sut = UserViewModel(repository: mockRepository)
    }
    
    override func tearDown() {
        sut = nil
        mockRepository = nil
        super.tearDown()
    }
    
    // MARK: - Logged In Context
    
    private func setUpLoggedInContext() {
        mockRepository.currentUser = User.stub
        sut.checkLoginStatus()
    }
    
    func test_fetchProfile_whenLoggedIn_showsProfile() {
        // Given
        setUpLoggedInContext()
        
        // When/Then
        ...
    }
    
    // MARK: - Logged Out Context
    
    private func setUpLoggedOutContext() {
        mockRepository.currentUser = nil
        sut.checkLoginStatus()
    }
    
    func test_fetchProfile_whenLoggedOut_showsLogin() {
        // Given
        setUpLoggedOutContext()
        
        // When/Then
        ...
    }
}
```

## パフォーマンステスト

### 実行時間の測定

```swift
func test_sort_performance() {
    let largeArray = (0..<10000).map { _ in Int.random(in: 0...10000) }
    let sorter = Sorter()
    
    measure {
        _ = sorter.sort(largeArray)
    }
}
```

### メトリクスの設定

```swift
func test_parse_performance() {
    let options = XCTMeasureOptions()
    options.iterationCount = 10
    
    let largeJSON = loadLargeJSONFixture()
    let parser = JSONParser<[User]>()
    
    measure(options: options) {
        _ = try? parser.parse(largeJSON)
    }
}
```

## ヘルパーメソッドパターン

### アサーションヘルパー

```swift
extension XCTestCase {
    func assertEventuallyEqual<T: Equatable>(
        _ expression: @autoclosure () -> T,
        _ expected: T,
        timeout: TimeInterval = 1.0,
        file: StaticString = #file,
        line: UInt = #line
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        
        while Date() < deadline {
            if expression() == expected {
                return
            }
            RunLoop.current.run(until: Date().addingTimeInterval(0.01))
        }
        
        XCTAssertEqual(expression(), expected, file: file, line: line)
    }
}
```

### Result型のアサーション

```swift
extension XCTestCase {
    func assertSuccess<T, E: Error>(
        _ result: Result<T, E>,
        file: StaticString = #file,
        line: UInt = #line
    ) -> T? {
        switch result {
        case .success(let value):
            return value
        case .failure(let error):
            XCTFail("Expected success but got error: \(error)", file: file, line: line)
            return nil
        }
    }
    
    func assertFailure<T, E: Error>(
        _ result: Result<T, E>,
        file: StaticString = #file,
        line: UInt = #line
    ) -> E? {
        switch result {
        case .success(let value):
            XCTFail("Expected failure but got success: \(value)", file: file, line: line)
            return nil
        case .failure(let error):
            return error
        }
    }
}
```
