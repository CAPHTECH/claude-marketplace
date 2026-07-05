# テストデータ管理ガイド

Swift/XCTestに固有のフィクスチャ管理パターン。

## ディレクトリ構造

```
Tests/
├── Factories/
│   └── UserFactory.swift
├── Fixtures/
│   ├── JSON/
│   │   ├── Users/
│   │   │   └── single_user.json
│   │   └── Errors/
│   │       └── validation_error.json
│   └── Stubs/
│       └── User+Stub.swift
└── Helpers/
    └── FixtureLoader.swift
```

## Fixture ローダー

`Bundle(for:)` でテストバンドル内のJSONを解決し、`JSONDecoder` でデコードする。

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
        
        let path = bundle.path(
            forResource: filename,
            ofType: "json",
            inDirectory: subdirectory.map { "Fixtures/JSON/\($0)" } ?? "Fixtures/JSON"
        )
        
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
}

private class BundleToken {}

// 使用例
func test_decodeUserFromFixture() throws {
    let user: User = try FixtureLoader.load("single_user", as: User.self, in: "Users")
    XCTAssertEqual(user.id, "fixture-user-1")
}
```

## 境界値テストデータ

Swift標準ライブラリの境界定数（`Int.max/min`、`Date.distantPast/Future`、`Decimal`）を使った境界値ファクトリ。

```swift
enum BoundaryTestData {
    // MARK: - String Boundaries
    
    static var emptyString: String { "" }
    static var maxLengthString: String { String(repeating: "a", count: 255) }
    static var overMaxLengthString: String { String(repeating: "a", count: 256) }
    static var unicodeString: String { "日本語テスト🎉" }
    
    // MARK: - Numeric Boundaries
    
    static var zeroInt: Int { 0 }
    static var maxInt: Int { Int.max }
    static var minInt: Int { Int.min }
    
    static var zeroDecimal: Decimal { 0 }
    static var largeDecimal: Decimal { 999999999.99 }
    
    // MARK: - Date Boundaries
    
    static var distantPast: Date { Date.distantPast }
    static var distantFuture: Date { Date.distantFuture }
    static var epoch: Date { Date(timeIntervalSince1970: 0) }
}
```

## Stub 拡張

モデルの `static var stub` をプロトコル適合ではなくextensionで持たせ、Factory経由でプリセットを組み立てる。

```swift
// User+Stub.swift

extension User {
    static var stub: User {
        UserFactory.make()
    }
    
    static var stubAdmin: User {
        UserFactory.admin
    }
}
```
