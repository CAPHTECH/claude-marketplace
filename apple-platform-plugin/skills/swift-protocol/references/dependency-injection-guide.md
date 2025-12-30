# Swift 依存性注入ガイド

## 依存性注入の目的

1. **テスタビリティ**: モックやスタブへの差し替えが容易
2. **疎結合**: コンポーネント間の依存関係を明示化
3. **柔軟性**: 実装の交換が容易
4. **コードの再利用**: 異なるコンテキストでの再利用

## 注入パターン

### 1. コンストラクタ注入（Constructor Injection）

最も推奨されるパターン。依存関係が明確。

```swift
protocol UserRepositoryProtocol {
    func fetchUser(id: UUID) async throws -> User
}

protocol AnalyticsProtocol {
    func track(event: String)
}

final class UserService {
    private let repository: UserRepositoryProtocol
    private let analytics: AnalyticsProtocol

    // 依存関係をコンストラクタで受け取る
    init(
        repository: UserRepositoryProtocol,
        analytics: AnalyticsProtocol
    ) {
        self.repository = repository
        self.analytics = analytics
    }

    func getUser(id: UUID) async throws -> User {
        analytics.track(event: "user_fetch_started")
        let user = try await repository.fetchUser(id: id)
        analytics.track(event: "user_fetch_completed")
        return user
    }
}

// 使用
let service = UserService(
    repository: UserRepository(),
    analytics: FirebaseAnalytics()
)
```

### 2. プロパティ注入（Property Injection）

オプショナルな依存関係やSwiftUIで使用。

```swift
final class ImageLoader {
    // オプショナルな依存関係
    var cache: ImageCacheProtocol?
    var logger: LoggerProtocol?

    func load(url: URL) async throws -> UIImage {
        if let cached = cache?.get(url: url) {
            logger?.log("Cache hit: \(url)")
            return cached
        }

        let data = try await URLSession.shared.data(from: url).0
        let image = UIImage(data: data)!
        cache?.set(image, for: url)
        return image
    }
}
```

### 3. メソッド注入（Method Injection）

特定の操作でのみ必要な依存関係。

```swift
struct ReportGenerator {
    func generate(
        data: ReportData,
        formatter: ReportFormatterProtocol  // メソッドで注入
    ) -> FormattedReport {
        formatter.format(data)
    }
}

// 使用時に異なるフォーマッタを渡せる
let generator = ReportGenerator()
let pdfReport = generator.generate(data: data, formatter: PDFFormatter())
let htmlReport = generator.generate(data: data, formatter: HTMLFormatter())
```

## SwiftUI での依存性注入

### Environment による注入

```swift
// 1. プロトコル定義
protocol APIClientProtocol: Sendable {
    func fetch<T: Decodable>(endpoint: String) async throws -> T
}

// 2. 環境キー定義
struct APIClientKey: EnvironmentKey {
    static let defaultValue: APIClientProtocol = URLSessionAPIClient()
}

extension EnvironmentValues {
    var apiClient: APIClientProtocol {
        get { self[APIClientKey.self] }
        set { self[APIClientKey.self] = newValue }
    }
}

// 3. View での使用
struct UserListView: View {
    @Environment(\.apiClient) private var apiClient
    @State private var users: [User] = []

    var body: some View {
        List(users) { user in
            Text(user.name)
        }
        .task {
            users = try? await apiClient.fetch(endpoint: "/users")
        }
    }
}

// 4. 注入
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.apiClient, URLSessionAPIClient())
        }
    }
}

// 5. テスト
struct UserListView_Previews: PreviewProvider {
    static var previews: some View {
        UserListView()
            .environment(\.apiClient, MockAPIClient())
    }
}
```

### @Observable による注入 (iOS 17+)

```swift
// 1. Observable クラス定義
@Observable
final class AppDependencies {
    let userRepository: UserRepositoryProtocol
    let analytics: AnalyticsProtocol

    init(
        userRepository: UserRepositoryProtocol = UserRepository(),
        analytics: AnalyticsProtocol = FirebaseAnalytics()
    ) {
        self.userRepository = userRepository
        self.analytics = analytics
    }
}

// 2. アプリのルートで注入
@main
struct MyApp: App {
    @State private var dependencies = AppDependencies()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(dependencies)
        }
    }
}

// 3. View での使用
struct ProfileView: View {
    @Environment(AppDependencies.self) private var dependencies

    var body: some View {
        // dependencies.userRepository を使用
    }
}
```

## DIコンテナパターン

### シンプルなコンテナ

```swift
protocol Container {
    var userRepository: UserRepositoryProtocol { get }
    var postRepository: PostRepositoryProtocol { get }
    var analyticsService: AnalyticsProtocol { get }
    var networkClient: NetworkClientProtocol { get }
}

// プロダクション用
final class AppContainer: Container {
    // lazy で初回アクセス時に生成
    lazy var networkClient: NetworkClientProtocol = URLSessionClient()

    lazy var userRepository: UserRepositoryProtocol = {
        UserRepository(networkClient: networkClient)
    }()

    lazy var postRepository: PostRepositoryProtocol = {
        PostRepository(networkClient: networkClient)
    }()

    lazy var analyticsService: AnalyticsProtocol = FirebaseAnalytics()
}

// テスト用
final class TestContainer: Container {
    var networkClient: NetworkClientProtocol = MockNetworkClient()
    var userRepository: UserRepositoryProtocol = MockUserRepository()
    var postRepository: PostRepositoryProtocol = MockPostRepository()
    var analyticsService: AnalyticsProtocol = MockAnalytics()
}
```

### Scope を持つコンテナ

```swift
final class ScopedContainer {
    // Singleton スコープ
    private var singletonInstances: [ObjectIdentifier: Any] = [:]

    // Factory スコープ（毎回新しいインスタンス）
    private var factories: [ObjectIdentifier: () -> Any] = [:]

    func registerSingleton<T>(_ type: T.Type, factory: @escaping () -> T) {
        let key = ObjectIdentifier(type)
        factories[key] = factory
    }

    func resolve<T>(_ type: T.Type) -> T {
        let key = ObjectIdentifier(type)

        if let existing = singletonInstances[key] as? T {
            return existing
        }

        guard let factory = factories[key] else {
            fatalError("No factory registered for \(type)")
        }

        let instance = factory() as! T
        singletonInstances[key] = instance
        return instance
    }
}
```

## テストでのモック

### 基本的なモック

```swift
// プロダクションプロトコル
protocol WeatherServiceProtocol {
    func fetchForecast(city: String) async throws -> Forecast
}

// モック実装
final class MockWeatherService: WeatherServiceProtocol {
    var result: Result<Forecast, Error> = .success(.sunny)
    var fetchCallCount = 0
    var lastRequestedCity: String?

    func fetchForecast(city: String) async throws -> Forecast {
        fetchCallCount += 1
        lastRequestedCity = city
        return try result.get()
    }
}

// テスト
@Test
func testWeatherView() async throws {
    let mock = MockWeatherService()
    mock.result = .success(Forecast(temperature: 25, condition: .sunny))

    let viewModel = WeatherViewModel(service: mock)
    await viewModel.loadForecast(for: "Tokyo")

    #expect(mock.fetchCallCount == 1)
    #expect(mock.lastRequestedCity == "Tokyo")
    #expect(viewModel.forecast?.temperature == 25)
}
```

### Spy パターン

```swift
// 呼び出し履歴を記録
final class SpyAnalytics: AnalyticsProtocol {
    private(set) var trackedEvents: [(name: String, params: [String: Any])] = []

    func track(event: String, params: [String: Any]) {
        trackedEvents.append((event, params))
    }

    func wasTracked(_ eventName: String) -> Bool {
        trackedEvents.contains { $0.name == eventName }
    }

    func timesTracked(_ eventName: String) -> Int {
        trackedEvents.filter { $0.name == eventName }.count
    }
}
```

## ベストプラクティス

### 1. 具体型よりプロトコル

```swift
// Bad
final class UserService {
    private let repository: UserRepository  // 具体型

    init(repository: UserRepository) {
        self.repository = repository
    }
}

// Good
final class UserService {
    private let repository: UserRepositoryProtocol  // プロトコル

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }
}
```

### 2. 必須の依存関係はコンストラクタで

```swift
// Bad: 後からセットされないリスク
final class PaymentService {
    var paymentGateway: PaymentGatewayProtocol!  // 危険

    func processPayment(_ payment: Payment) async throws {
        try await paymentGateway.process(payment)  // クラッシュの可能性
    }
}

// Good
final class PaymentService {
    private let paymentGateway: PaymentGatewayProtocol

    init(paymentGateway: PaymentGatewayProtocol) {
        self.paymentGateway = paymentGateway
    }
}
```

### 3. デフォルト実装の提供

```swift
// 便利なファクトリメソッド
final class UserService {
    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    // プロダクション用のファクトリ
    static func production() -> UserService {
        UserService(repository: UserRepository())
    }

    // テスト用のファクトリ
    static func test(repository: UserRepositoryProtocol = MockUserRepository()) -> UserService {
        UserService(repository: repository)
    }
}
```
