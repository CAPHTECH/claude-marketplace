# SwiftUI 状態管理ガイド

## Property Wrapper 選択フローチャート

```
状態の所有者は？
├── このViewのみ → @State
├── 親View → @Binding
├── 環境（アプリ全体） → @Environment / @EnvironmentObject
└── 外部オブジェクト
    ├── iOS 17+ → @Observable + @State
    └── iOS 16以前 → @ObservedObject / @StateObject
```

## @State

### 用途
- Viewローカルの単純な状態
- UI状態（表示/非表示、選択状態など）
- アニメーション状態

### ベストプラクティス
```swift
struct ToggleView: View {
    // 常にprivateで宣言
    @State private var isOn = false

    var body: some View {
        Toggle("Switch", isOn: $isOn)
    }
}
```

### 注意点
- 初期値はinit内ではなく宣言時に設定
- 他のViewから直接変更しない

## @Binding

### 用途
- 親Viewの状態への参照
- 双方向データフロー

### ベストプラクティス
```swift
struct ChildView: View {
    @Binding var value: String

    var body: some View {
        TextField("Enter", text: $value)
    }
}

// 親View
struct ParentView: View {
    @State private var text = ""

    var body: some View {
        ChildView(value: $text)
    }
}
```

### 定数Binding
```swift
#Preview {
    ToggleView(isOn: .constant(true))
}
```

## @Observable (iOS 17+)

### 用途
- 複雑なビジネスロジック
- 複数のViewで共有する状態
- 非同期処理を含む状態

### 基本パターン
```swift
@Observable
class ShoppingCart {
    var items: [CartItem] = []
    var couponCode: String = ""

    var total: Decimal {
        items.reduce(0) { $0 + $1.price * Decimal($1.quantity) }
    }

    var discountedTotal: Decimal {
        if isValidCoupon {
            return total * 0.9
        }
        return total
    }

    private var isValidCoupon: Bool {
        couponCode == "DISCOUNT10"
    }

    func addItem(_ item: CartItem) {
        items.append(item)
    }

    func removeItem(at index: Int) {
        items.remove(at: index)
    }
}
```

### Viewでの使用
```swift
struct CartView: View {
    // 所有する場合
    @State private var cart = ShoppingCart()

    var body: some View {
        List(cart.items) { item in
            ItemRow(item: item)
        }
        Text("Total: \(cart.total.formatted())")
    }
}

struct CartItemView: View {
    // 参照する場合（自動的にBindableになる）
    @Bindable var cart: ShoppingCart

    var body: some View {
        TextField("Coupon", text: $cart.couponCode)
    }
}
```

### 環境に注入
```swift
@main
struct MyApp: App {
    @State private var cart = ShoppingCart()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(cart)
        }
    }
}

struct ContentView: View {
    @Environment(ShoppingCart.self) var cart

    var body: some View {
        Text("Items: \(cart.items.count)")
    }
}
```

## @ObservedObject / @StateObject (iOS 16以前)

### @StateObject（所有する場合）
```swift
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func load() async {
        items = await repository.fetchAll()
    }
}

struct ListView: View {
    // Viewが所有する場合は@StateObject
    @StateObject private var viewModel = ViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .task {
            await viewModel.load()
        }
    }
}
```

### @ObservedObject（参照する場合）
```swift
struct ChildView: View {
    // 親からもらう場合は@ObservedObject
    @ObservedObject var viewModel: ViewModel

    var body: some View {
        Text("Count: \(viewModel.items.count)")
    }
}
```

## @Environment

### 用途
- システム設定（カラースキーム、サイズカテゴリなど）
- カスタム環境値

### システム環境値
```swift
struct AdaptiveView: View {
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.sizeCategory) var sizeCategory
    @Environment(\.horizontalSizeClass) var horizontalSizeClass

    var body: some View {
        if horizontalSizeClass == .compact {
            compactLayout
        } else {
            regularLayout
        }
    }
}
```

### カスタム環境値
```swift
// 環境キーの定義
struct ThemeKey: EnvironmentKey {
    static let defaultValue: Theme = .default
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// 使用
struct ThemedView: View {
    @Environment(\.theme) var theme

    var body: some View {
        Text("Hello")
            .foregroundStyle(theme.primaryColor)
    }
}

// 注入
ContentView()
    .environment(\.theme, .dark)
```

## @FocusState

### 用途
- フォーカス管理
- キーボードの表示/非表示制御

```swift
struct LoginForm: View {
    enum Field: Hashable {
        case username
        case password
    }

    @State private var username = ""
    @State private var password = ""
    @FocusState private var focusedField: Field?

    var body: some View {
        Form {
            TextField("Username", text: $username)
                .focused($focusedField, equals: .username)
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .password
                }

            SecureField("Password", text: $password)
                .focused($focusedField, equals: .password)
                .submitLabel(.go)
                .onSubmit {
                    login()
                }
        }
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") {
                    focusedField = nil
                }
            }
        }
    }
}
```

## 状態管理アンチパターン

### 1. 不必要な@StateObject
```swift
// Bad: 毎回新しいインスタンスが作られる
struct BadView: View {
    @ObservedObject var viewModel = ViewModel()  // 危険！
}

// Good
struct GoodView: View {
    @StateObject var viewModel = ViewModel()
}
```

### 2. 過剰な状態
```swift
// Bad: 派生値を状態として保持
struct BadView: View {
    @State private var items: [Item] = []
    @State private var count: Int = 0  // 冗長

    // itemsが変わるたびにcountを更新する必要がある
}

// Good: 計算プロパティを使用
struct GoodView: View {
    @State private var items: [Item] = []

    var count: Int { items.count }  // 自動的に更新される
}
```

### 3. 深すぎるBinding
```swift
// Bad: Bindingのバケツリレー
struct A: View {
    @State private var value = ""
    var body: some View { B(value: $value) }
}
struct B: View {
    @Binding var value: String
    var body: some View { C(value: $value) }
}
struct C: View {
    @Binding var value: String
    var body: some View { D(value: $value) }
}

// Good: 環境を使用
@Observable class SharedState {
    var value = ""
}

struct A: View {
    @State private var state = SharedState()
    var body: some View {
        B().environment(state)
    }
}
```
