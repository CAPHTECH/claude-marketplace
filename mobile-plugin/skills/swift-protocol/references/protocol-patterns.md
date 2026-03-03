# Swift プロトコルパターン集

## 基本パターン

### 1. 型消去パターン（Type Erasure）

Associated Typeを持つプロトコルを存在型として扱う場合に使用。

```swift
// プロトコル定義
protocol AnyPublisher {
    associatedtype Output
    associatedtype Failure: Error

    func subscribe<S: Subscriber>(_ subscriber: S) where S.Input == Output, S.Failure == Failure
}

// 型消去ラッパー
struct AnyPublisherWrapper<Output, Failure: Error>: Publisher {
    private let _subscribe: (AnySubscriber<Output, Failure>) -> Void

    init<P: Publisher>(_ publisher: P) where P.Output == Output, P.Failure == Failure {
        _subscribe = { subscriber in
            publisher.subscribe(subscriber)
        }
    }

    func subscribe<S>(_ subscriber: S) where S: Subscriber, Output == S.Input, Failure == S.Failure {
        _subscribe(AnySubscriber(subscriber))
    }
}
```

### 2. Witness パターン

プロトコルの代わりに構造体でインターフェースを定義（パフォーマンス重視）。

```swift
// プロトコルの代わりに構造体
struct Logger {
    var log: (String) -> Void
    var error: (Error) -> Void

    static let console = Logger(
        log: { print($0) },
        error: { print("Error: \($0)") }
    )

    static let silent = Logger(
        log: { _ in },
        error: { _ in }
    )
}

// 使用
struct App {
    let logger: Logger

    func run() {
        logger.log("App started")
    }
}

let app = App(logger: .console)
```

### 3. Protocol Composition + typealias

複数の小さなプロトコルを組み合わせる。

```swift
protocol Identifiable {
    var id: UUID { get }
}

protocol Timestamped {
    var createdAt: Date { get }
    var updatedAt: Date { get }
}

protocol Versionable {
    var version: Int { get }
}

// 組み合わせ
typealias Auditable = Identifiable & Timestamped & Versionable

// 使用
struct Document: Auditable {
    let id: UUID
    let createdAt: Date
    var updatedAt: Date
    var version: Int
    var content: String
}
```

## 依存性注入パターン

### 4. コンテナパターン

```swift
// 依存性コンテナ
protocol DependencyContainer {
    var networkClient: NetworkClient { get }
    var userRepository: UserRepositoryProtocol { get }
    var analytics: AnalyticsTracking { get }
}

// プロダクション用
final class AppContainer: DependencyContainer {
    lazy var networkClient: NetworkClient = URLSessionClient()
    lazy var userRepository: UserRepositoryProtocol = UserRepository(networkClient: networkClient)
    lazy var analytics: AnalyticsTracking = FirebaseAnalytics()
}

// テスト用
final class TestContainer: DependencyContainer {
    var networkClient: NetworkClient = MockNetworkClient()
    var userRepository: UserRepositoryProtocol = MockUserRepository()
    var analytics: AnalyticsTracking = MockAnalytics()
}
```

### 5. Factory パターン

```swift
protocol UserServiceFactory {
    func makeUserService() -> UserServiceProtocol
}

struct ProductionFactory: UserServiceFactory {
    let container: DependencyContainer

    func makeUserService() -> UserServiceProtocol {
        UserService(
            repository: container.userRepository,
            analytics: container.analytics
        )
    }
}

struct TestFactory: UserServiceFactory {
    func makeUserService() -> UserServiceProtocol {
        MockUserService()
    }
}
```

## Extension パターン

### 6. 条件付きデフォルト実装

```swift
protocol Describable {
    var description: String { get }
}

// Encodableな型に自動実装
extension Describable where Self: Encodable {
    var description: String {
        guard let data = try? JSONEncoder().encode(self),
              let json = String(data: data, encoding: .utf8) else {
            return String(describing: self)
        }
        return json
    }
}

// CustomStringConvertibleと競合しない
struct User: Describable, Encodable {
    let name: String
    let age: Int
}

let user = User(name: "Alice", age: 30)
print(user.description)  // {"name":"Alice","age":30}
```

### 7. Protocol + Class 制約

```swift
protocol Reloadable: AnyObject {
    func reload()
}

extension Reloadable where Self: UIViewController {
    func reload() {
        // UIViewController固有の実装
        view.setNeedsLayout()
        viewDidLoad()
    }
}

// または特定の型に制限
protocol ViewControllerReloadable where Self: UIViewController {
    func reloadContent()
}
```

## 高度なパターン

### 8. Self要件パターン

```swift
protocol Copyable {
    func copy() -> Self
}

final class Document: Copyable {
    var content: String

    init(content: String) {
        self.content = content
    }

    func copy() -> Document {
        Document(content: content)
    }
}
```

### 9. Associated Type + where句

```swift
protocol Container {
    associatedtype Element
    associatedtype Iterator: IteratorProtocol where Iterator.Element == Element

    func makeIterator() -> Iterator
}

// 複雑な制約
protocol Graph {
    associatedtype Node: Hashable
    associatedtype Edge where Edge: Equatable, Edge == (Node, Node)

    var nodes: Set<Node> { get }
    var edges: [Edge] { get }
}
```

### 10. Opaque Type + some Protocol

```swift
protocol Animal {
    var name: String { get }
    func speak() -> String
}

struct Cat: Animal {
    var name: String
    func speak() -> String { "Meow" }
}

struct Dog: Animal {
    var name: String
    func speak() -> String { "Woof" }
}

// Opaque return type
struct AnimalFactory {
    static func makePet(prefersCats: Bool) -> some Animal {
        if prefersCats {
            return Cat(name: "Whiskers")
        } else {
            return Dog(name: "Buddy")
        }
    }
}
```

## アンチパターンと対策

### アンチパターン1: 過度な抽象化

```swift
// Bad: 1つしか実装がないのにプロトコル化
protocol LoggerProtocol {
    func log(_ message: String)
}

final class Logger: LoggerProtocol {
    func log(_ message: String) {
        print(message)
    }
}

// Good: 実装が1つならプロトコルは不要
// テストで差し替える必要が出た時点でプロトコル化
final class Logger {
    func log(_ message: String) {
        print(message)
    }
}
```

### アンチパターン2: Fat Protocol

```swift
// Bad: 責任が多すぎる
protocol UserManager {
    func fetchUser(id: UUID) async throws -> User
    func saveUser(_ user: User) async throws
    func deleteUser(id: UUID) async throws
    func validateUser(_ user: User) -> Bool
    func notifyUser(_ user: User, message: String) async throws
    func trackUserActivity(_ user: User, activity: Activity)
}

// Good: 責任を分割
protocol UserRepository {
    func fetch(id: UUID) async throws -> User
    func save(_ user: User) async throws
    func delete(id: UUID) async throws
}

protocol UserValidator {
    func validate(_ user: User) -> Bool
}

protocol UserNotifier {
    func notify(_ user: User, message: String) async throws
}
```

### アンチパターン3: Existential の過剰使用

```swift
// Bad: パフォーマンスに影響
let items: [any Equatable] = [1, "hello", 3.14]

// Good: Generics を使用
func process<T: Equatable>(_ items: [T]) {
    // 型情報が保持される
}

// または Opaque Type
func getItems() -> some Collection<Int> {
    [1, 2, 3]
}
```
