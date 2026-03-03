# SwiftUIスナップショットガイド

## 基本的な使い方

### View のスナップショット

```swift
import SnapshotTesting
import SwiftUI
import XCTest
@testable import MyApp

final class MyViewSnapshotTests: XCTestCase {
    
    // 最もシンプルな形式
    func test_myView_default() {
        let view = MyView()
        assertSnapshot(of: view, as: .image)
    }
    
    // サイズ指定
    func test_myView_fixedSize() {
        let view = MyView()
        assertSnapshot(
            of: view,
            as: .image(layout: .fixed(width: 300, height: 200))
        )
    }
    
    // コンテンツに合わせたサイズ
    func test_myView_sizeThatFits() {
        let view = MyView()
        assertSnapshot(
            of: view,
            as: .image(layout: .sizeThatFits)
        )
    }
    
    // デバイス指定
    func test_myView_onDevice() {
        let view = MyView()
        assertSnapshot(
            of: view,
            as: .image(layout: .device(config: .iPhone15))
        )
    }
}
```

## レイアウトオプション

### SwiftUISnapshotLayout

```swift
// 固定サイズ
.image(layout: .fixed(width: 375, height: 667))

// コンテンツサイズ
.image(layout: .sizeThatFits)

// デバイスサイズ
.image(layout: .device(config: .iPhone15))
.image(layout: .device(config: .iPhone15Pro))
.image(layout: .device(config: .iPadPro11))
```

### カスタムレイアウト

```swift
extension SwiftUISnapshotLayout {
    // カード用レイアウト
    static var card: SwiftUISnapshotLayout {
        .fixed(width: 343, height: 200)
    }
    
    // リストセル用レイアウト
    static var listCell: SwiftUISnapshotLayout {
        .fixed(width: 375, height: 80)
    }
    
    // フルスクリーン（iPhone 15）
    static var fullScreen: SwiftUISnapshotLayout {
        .device(config: .iPhone15)
    }
}

// 使用
assertSnapshot(of: ProductCard(product: .stub), as: .image(layout: .card))
```

## Environment の設定

### ColorScheme（ダークモード）

```swift
func test_view_lightMode() {
    let view = ContentView()
        .environment(\.colorScheme, .light)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

func test_view_darkMode() {
    let view = ContentView()
        .environment(\.colorScheme, .dark)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### Locale（ローカライゼーション）

```swift
func test_view_japanese() {
    let view = ContentView()
        .environment(\.locale, Locale(identifier: "ja"))
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

func test_view_english() {
    let view = ContentView()
        .environment(\.locale, Locale(identifier: "en"))
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### Dynamic Type（文字サイズ）

```swift
func test_view_accessibilityXXXLarge() {
    let view = ContentView()
        .environment(\.sizeCategory, .accessibilityExtraExtraExtraLarge)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

func test_view_allSizeCategories() {
    let categories: [ContentSizeCategory] = [
        .extraSmall,
        .medium,
        .extraLarge,
        .accessibilityExtraExtraExtraLarge
    ]
    
    for category in categories {
        let view = ContentView()
            .environment(\.sizeCategory, category)
        
        assertSnapshot(
            of: view,
            as: .image(layout: .device(config: .iPhone15)),
            named: String(describing: category)
        )
    }
}
```

### Layout Direction（RTL対応）

```swift
func test_view_rightToLeft() {
    let view = ContentView()
        .environment(\.layoutDirection, .rightToLeft)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### 複合設定

```swift
func test_view_complexEnvironment() {
    let view = ContentView()
        .environment(\.colorScheme, .dark)
        .environment(\.locale, Locale(identifier: "ja"))
        .environment(\.sizeCategory, .large)
        .environment(\.layoutDirection, .leftToRight)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

## 状態管理

### @State を持つ View

```swift
struct CounterView: View {
    @State private var count = 0
    
    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") { count += 1 }
        }
    }
}

// テスト: 初期状態
func test_counterView_initialState() {
    let view = CounterView()
    assertSnapshot(of: view, as: .image(layout: .sizeThatFits))
}

// 特定の状態をテストしたい場合は、状態を外部から注入可能にする
struct TestableCounterView: View {
    let initialCount: Int
    @State private var count: Int
    
    init(initialCount: Int = 0) {
        self.initialCount = initialCount
        _count = State(initialValue: initialCount)
    }
    
    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") { count += 1 }
        }
    }
}

func test_counterView_withValue() {
    let view = TestableCounterView(initialCount: 42)
    assertSnapshot(of: view, as: .image(layout: .sizeThatFits))
}
```

### @ObservedObject / @StateObject

```swift
class UserViewModel: ObservableObject {
    @Published var name: String
    @Published var isLoading: Bool
    @Published var error: Error?
    
    init(name: String = "", isLoading: Bool = false, error: Error? = nil) {
        self.name = name
        self.isLoading = isLoading
        self.error = error
    }
}

struct UserView: View {
    @ObservedObject var viewModel: UserViewModel
    
    var body: some View {
        // ...
    }
}

// テスト
func test_userView_loading() {
    let viewModel = UserViewModel(isLoading: true)
    let view = UserView(viewModel: viewModel)
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

func test_userView_loaded() {
    let viewModel = UserViewModel(name: "John Doe")
    let view = UserView(viewModel: viewModel)
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

func test_userView_error() {
    let viewModel = UserViewModel(error: NSError(domain: "", code: 0))
    let view = UserView(viewModel: viewModel)
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

## NavigationStack / NavigationView

```swift
func test_navigationView() {
    let view = NavigationStack {
        List {
            Text("Item 1")
            Text("Item 2")
            Text("Item 3")
        }
        .navigationTitle("My List")
    }
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

## Sheet / Alert / FullScreenCover

### Sheet

```swift
struct SheetContainerView: View {
    @State private var isPresented = true
    
    var body: some View {
        Color.clear
            .sheet(isPresented: $isPresented) {
                SheetContent()
            }
    }
}

func test_sheet() {
    let view = SheetContainerView()
    
    // シートが表示されるまで待機
    let exp = expectation(description: "Sheet presented")
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
        exp.fulfill()
    }
    wait(for: [exp], timeout: 1)
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### Alert（iOS 15+）

```swift
// Alertはスナップショットが困難なため、Alert内容のViewを個別にテスト
func test_alertContent() {
    let alertContent = VStack {
        Text("Title")
            .font(.headline)
        Text("Message")
            .font(.body)
        HStack {
            Button("Cancel") {}
            Button("OK") {}
        }
    }
    .padding()
    .background(Color(.systemBackground))
    
    assertSnapshot(of: alertContent, as: .image(layout: .sizeThatFits))
}
```

## List と LazyVStack

### List

```swift
func test_list_withItems() {
    let items = (1...5).map { "Item \($0)" }
    
    let view = List(items, id: \.self) { item in
        Text(item)
    }
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### LazyVStack（スクロール）

```swift
func test_lazyVStack() {
    let items = (1...20).map { "Item \($0)" }
    
    let view = ScrollView {
        LazyVStack {
            ForEach(items, id: \.self) { item in
                Text(item)
                    .padding()
            }
        }
    }
    .frame(height: 600)  // 固定高さで表示範囲を制限
    
    assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 600)))
}
```

## カスタムSnapshotting

### トレイト付きスナップショット

```swift
extension Snapshotting where Value: SwiftUI.View, Format == UIImage {
    static func image(
        on config: ViewImageConfig,
        colorScheme: ColorScheme
    ) -> Snapshotting {
        .image(layout: .device(config: config))
    }
}
```

### 複数設定の一括テスト

```swift
struct SnapshotConfig {
    let name: String
    let device: ViewImageConfig
    let colorScheme: ColorScheme
    let sizeCategory: ContentSizeCategory
    
    static let standard: [SnapshotConfig] = [
        SnapshotConfig(name: "iPhone15_light", device: .iPhone15, colorScheme: .light, sizeCategory: .medium),
        SnapshotConfig(name: "iPhone15_dark", device: .iPhone15, colorScheme: .dark, sizeCategory: .medium),
        SnapshotConfig(name: "iPhoneSE_light", device: .iPhoneSe, colorScheme: .light, sizeCategory: .medium),
        SnapshotConfig(name: "iPhone15_a11y", device: .iPhone15, colorScheme: .light, sizeCategory: .accessibilityLarge)
    ]
}

extension XCTestCase {
    func assertSnapshots<V: View>(
        of view: V,
        configs: [SnapshotConfig] = SnapshotConfig.standard,
        file: StaticString = #file,
        testName: String = #function,
        line: UInt = #line
    ) {
        for config in configs {
            let themedView = view
                .environment(\.colorScheme, config.colorScheme)
                .environment(\.sizeCategory, config.sizeCategory)
            
            assertSnapshot(
                of: themedView,
                as: .image(layout: .device(config: config.device)),
                named: config.name,
                file: file,
                testName: testName,
                line: line
            )
        }
    }
}

// 使用
func test_productCard() {
    let view = ProductCard(product: .stub)
    assertSnapshots(of: view)
}
```

## アニメーション対策

### Transaction でアニメーション無効化

```swift
func test_animatedView() {
    let view = AnimatedView()
        .transaction { $0.animation = nil }
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

### withAnimation のスキップ

```swift
// テスト用のフラグで制御
struct AnimatedView: View {
    var disableAnimations = false
    
    var body: some View {
        // ...
    }
}

func test_animatedView() {
    let view = AnimatedView(disableAnimations: true)
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}
```

## 非同期コンテンツ

### AsyncImage

```swift
// 実際のAsyncImageはテストが困難なため、テスト用のラッパーを用意
struct TestableAsyncImage: View {
    let phase: AsyncImagePhase
    
    var body: some View {
        switch phase {
        case .empty:
            ProgressView()
        case .success(let image):
            image.resizable()
        case .failure:
            Image(systemName: "exclamationmark.triangle")
        @unknown default:
            EmptyView()
        }
    }
}

func test_asyncImage_loading() {
    let view = TestableAsyncImage(phase: .empty)
    assertSnapshot(of: view, as: .image(layout: .fixed(width: 200, height: 200)))
}

func test_asyncImage_loaded() {
    let testImage = Image(systemName: "photo")
    let view = TestableAsyncImage(phase: .success(testImage))
    assertSnapshot(of: view, as: .image(layout: .fixed(width: 200, height: 200)))
}

func test_asyncImage_failed() {
    let view = TestableAsyncImage(phase: .failure(URLError(.badURL)))
    assertSnapshot(of: view, as: .image(layout: .fixed(width: 200, height: 200)))
}
```

## SafeArea 対応

```swift
// SafeAreaを含むデバイス表示
func test_view_withSafeArea() {
    let view = ContentView()
        .ignoresSafeArea()  // または .safeAreaInset
    
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
}

// SafeAreaを無視したコンテンツのみ
func test_view_contentOnly() {
    let view = ContentView()
    
    assertSnapshot(of: view, as: .image(layout: .sizeThatFits))
}
```
