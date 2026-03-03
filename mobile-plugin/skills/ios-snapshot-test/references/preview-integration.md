# SwiftUI Preview 連携ガイド

## Preview と Snapshot Test の関係

### 設計思想

PreviewProvider で定義した表示パターンを、そのままスナップショットテストでも活用する。
これにより、開発時のプレビューとテストの一貫性を保つ。

```
Preview定義 → 開発時の視覚確認
     ↓ 同じパターンを共有
Snapshot Test → CI/CDでの自動検証
```

### メリット

1. **重複排除**: 表示パターンを一箇所で管理
2. **一貫性**: 開発者が見るものとテストされるものが同じ
3. **保守性**: パターン追加時にテストも自動的にカバー

## 基本パターン

### パターン1: Preview用プロパティの共有

```swift
// MARK: - View定義

struct ProductCard: View {
    let product: Product
    let onTap: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            AsyncImage(url: product.imageURL) { image in
                image.resizable().aspectRatio(contentMode: .fill)
            } placeholder: {
                Color.gray.opacity(0.3)
            }
            .frame(height: 150)
            .clipped()
            
            VStack(alignment: .leading, spacing: 4) {
                Text(product.name)
                    .font(.headline)
                Text(product.price.formatted(.currency(code: "JPY")))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 12)
            .padding(.bottom, 12)
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

// MARK: - テスト用スタブ（Preview と Test で共有）

extension ProductCard {
    /// テスト・Preview用のスタブパターン
    enum Stub {
        /// 標準的な商品
        static var standard: ProductCard {
            ProductCard(
                product: Product(
                    id: "1",
                    name: "サンプル商品",
                    price: 1980,
                    imageURL: nil
                ),
                onTap: {}
            )
        }
        
        /// 長い商品名
        static var longName: ProductCard {
            ProductCard(
                product: Product(
                    id: "2",
                    name: "とても長い商品名がここに入りますこれは省略されるべきです",
                    price: 1980,
                    imageURL: nil
                ),
                onTap: {}
            )
        }
        
        /// 高額商品
        static var expensive: ProductCard {
            ProductCard(
                product: Product(
                    id: "3",
                    name: "高級商品",
                    price: 999999,
                    imageURL: nil
                ),
                onTap: {}
            )
        }
        
        /// セール商品（将来のバリエーション）
        static var onSale: ProductCard {
            ProductCard(
                product: Product(
                    id: "4",
                    name: "セール商品",
                    price: 500,
                    originalPrice: 1000,
                    imageURL: nil
                ),
                onTap: {}
            )
        }
    }
}

// MARK: - Preview

struct ProductCard_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ProductCard.Stub.standard
                .previewDisplayName("Standard")
            
            ProductCard.Stub.longName
                .previewDisplayName("Long Name")
            
            ProductCard.Stub.expensive
                .previewDisplayName("Expensive")
            
            ProductCard.Stub.standard
                .preferredColorScheme(.dark)
                .previewDisplayName("Dark Mode")
        }
        .previewLayout(.fixed(width: 180, height: 250))
        .padding()
    }
}

// MARK: - Snapshot Tests

import SnapshotTesting
import XCTest
@testable import MyApp

final class ProductCardSnapshotTests: XCTestCase {
    
    func test_standard() {
        assertSnapshot(
            of: ProductCard.Stub.standard,
            as: .image(layout: .fixed(width: 180, height: 250))
        )
    }
    
    func test_longName() {
        assertSnapshot(
            of: ProductCard.Stub.longName,
            as: .image(layout: .fixed(width: 180, height: 250))
        )
    }
    
    func test_expensive() {
        assertSnapshot(
            of: ProductCard.Stub.expensive,
            as: .image(layout: .fixed(width: 180, height: 250))
        )
    }
    
    func test_darkMode() {
        let view = ProductCard.Stub.standard
            .environment(\.colorScheme, .dark)
        
        assertSnapshot(
            of: view,
            as: .image(layout: .fixed(width: 180, height: 250))
        )
    }
}
```

### パターン2: PreviewProvider の allPreviews 活用

```swift
// MARK: - Preview Protocol

protocol PreviewProviding {
    associatedtype PreviewContent: View
    static var allPreviews: [(name: String, view: PreviewContent)] { get }
}

// MARK: - View with PreviewProviding

struct UserCell: View {
    let user: User
    
    var body: some View {
        HStack {
            Image(systemName: "person.circle.fill")
                .resizable()
                .frame(width: 40, height: 40)
            
            VStack(alignment: .leading) {
                Text(user.name)
                    .font(.headline)
                Text(user.email)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            if user.isVerified {
                Image(systemName: "checkmark.seal.fill")
                    .foregroundColor(.blue)
            }
        }
        .padding()
    }
}

extension UserCell: PreviewProviding {
    static var allPreviews: [(name: String, view: UserCell)] {
        [
            ("default", UserCell(user: .stub)),
            ("verified", UserCell(user: .stubVerified)),
            ("longEmail", UserCell(user: .stubLongEmail))
        ]
    }
}

struct UserCell_Previews: PreviewProvider {
    static var previews: some View {
        ForEach(UserCell.allPreviews, id: \.name) { preview in
            preview.view
                .previewDisplayName(preview.name)
                .previewLayout(.sizeThatFits)
        }
    }
}

// MARK: - Snapshot Tests

final class UserCellSnapshotTests: XCTestCase {
    
    func test_allPreviews() {
        for (name, view) in UserCell.allPreviews {
            assertSnapshot(
                of: view,
                as: .image(layout: .sizeThatFits),
                named: name
            )
        }
    }
}
```

## 高度なパターン

### パターン3: EnvironmentObject を含む View

```swift
// MARK: - ViewModel

class CartViewModel: ObservableObject {
    @Published var items: [CartItem] = []
    
    var total: Int {
        items.reduce(0) { $0 + $1.price * $1.quantity }
    }
    
    // テスト用スタブ
    static var stubEmpty: CartViewModel {
        CartViewModel()
    }
    
    static var stubWithItems: CartViewModel {
        let vm = CartViewModel()
        vm.items = [
            CartItem(id: "1", name: "商品A", price: 1000, quantity: 2),
            CartItem(id: "2", name: "商品B", price: 500, quantity: 1)
        ]
        return vm
    }
}

// MARK: - View

struct CartView: View {
    @EnvironmentObject var viewModel: CartViewModel
    
    var body: some View {
        VStack {
            if viewModel.items.isEmpty {
                Text("カートは空です")
            } else {
                List(viewModel.items) { item in
                    CartItemRow(item: item)
                }
                
                HStack {
                    Text("合計")
                    Spacer()
                    Text("\(viewModel.total)円")
                        .bold()
                }
                .padding()
            }
        }
    }
}

// MARK: - Preview用コンテナ

struct CartViewPreviewContainer: View {
    let viewModel: CartViewModel
    
    var body: some View {
        CartView()
            .environmentObject(viewModel)
    }
}

struct CartView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            CartViewPreviewContainer(viewModel: .stubEmpty)
                .previewDisplayName("Empty")
            
            CartViewPreviewContainer(viewModel: .stubWithItems)
                .previewDisplayName("With Items")
        }
    }
}

// MARK: - Snapshot Tests

final class CartViewSnapshotTests: XCTestCase {
    
    func test_empty() {
        let view = CartViewPreviewContainer(viewModel: .stubEmpty)
        assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
    }
    
    func test_withItems() {
        let view = CartViewPreviewContainer(viewModel: .stubWithItems)
        assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone15)))
    }
}
```

### パターン4: マトリクステスト

```swift
// MARK: - テストマトリクス定義

struct ViewTestMatrix<V: View> {
    let view: V
    let devices: [ViewImageConfig]
    let colorSchemes: [ColorScheme]
    let sizeCategories: [ContentSizeCategory]
    
    static var standard: ViewTestMatrix<V> {
        ViewTestMatrix(
            view: view,
            devices: [.iPhoneSe, .iPhone15],
            colorSchemes: [.light, .dark],
            sizeCategories: [.medium, .accessibilityLarge]
        )
    }
    
    func combinations() -> [(name: String, view: some View)] {
        var results: [(String, AnyView)] = []
        
        for device in devices {
            for scheme in colorSchemes {
                for category in sizeCategories {
                    let name = "\(device.description)_\(scheme)_\(category)"
                    let themedView = view
                        .environment(\.colorScheme, scheme)
                        .environment(\.sizeCategory, category)
                    
                    results.append((name, AnyView(themedView)))
                }
            }
        }
        
        return results
    }
}

// MARK: - 使用例

final class SettingsViewSnapshotTests: XCTestCase {
    
    func test_allCombinations() {
        let view = SettingsView()
        
        let matrix = ViewTestMatrix(
            view: view,
            devices: [.iPhoneSe, .iPhone15],
            colorSchemes: [.light, .dark],
            sizeCategories: [.medium]
        )
        
        for combo in matrix.combinations() {
            assertSnapshot(
                of: combo.view,
                as: .image(layout: .device(config: .iPhone15)),
                named: combo.name
            )
        }
    }
}
```

## Preview Macro（iOS 17+）

### #Preview マクロとの連携

```swift
// iOS 17+ の #Preview マクロ
#Preview("Default") {
    ProductCard.Stub.standard
}

#Preview("Long Name") {
    ProductCard.Stub.longName
}

#Preview("Dark Mode") {
    ProductCard.Stub.standard
        .preferredColorScheme(.dark)
}

// 注意: #Preview マクロは直接テストから参照できないため、
// 共有スタブパターンを使用する
```

### 移行ガイド

```swift
// 旧: PreviewProvider
struct MyView_Previews: PreviewProvider {
    static var previews: some View {
        MyView()
    }
}

// 新: #Preview マクロ（テストとの連携を考慮）
#Preview {
    MyView.Stub.standard
}

// テストコード（変更不要）
func test_myView() {
    assertSnapshot(of: MyView.Stub.standard, as: .image)
}
```

## ベストプラクティス

### 1. スタブの配置

```swift
// Good: View のextension内にスタブを配置
extension ProductCard {
    enum Stub {
        static var standard: ProductCard { ... }
    }
}

// Usage
ProductCard.Stub.standard

// Bad: 別ファイルにスタブを分散
// → 関連性がわかりにくい
```

### 2. 命名規則

```swift
// Preview名とSnapshot名を一致させる
#Preview("loading") {  // ← この名前と
    LoadingView()
}

func test_loading() {  // ← この名前を合わせる
    assertSnapshot(of: LoadingView(), as: .image, named: "loading")
}
```

### 3. レイアウト設定の共有

```swift
extension SwiftUISnapshotLayout {
    // Previewと同じレイアウトを使用
    static var productCard: SwiftUISnapshotLayout {
        .fixed(width: 180, height: 250)
    }
}

// Preview
.previewLayout(.fixed(width: 180, height: 250))

// Test
assertSnapshot(of: view, as: .image(layout: .productCard))
```

### 4. CI での Preview ビルド確認

```yaml
# .github/workflows/preview-check.yml
name: Preview Check

on: pull_request

jobs:
  build-previews:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      
      - name: Build for Previews
        run: |
          xcodebuild build \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -configuration Debug \
            SWIFT_ACTIVE_COMPILATION_CONDITIONS="DEBUG PREVIEW_BUILD"
```

## トラブルシューティング

### Preview は表示されるが Snapshot が失敗する

**原因**: Environment の設定差異

**対策**:
```swift
// Preview と同じ Environment を設定
func test_view() {
    let view = MyView()
        .environment(\.colorScheme, .light)
        .environment(\.locale, Locale(identifier: "ja"))
    
    assertSnapshot(of: view, as: .image)
}
```

### Preview でのみ表示されるコンテンツ

**原因**: `#if DEBUG` や `ProcessInfo` による分岐

**対策**:
```swift
// テスト時にも同じ条件を再現
#if DEBUG
struct MyView: View {
    var isPreview: Bool = false
    // ...
}
#endif
```

### 非同期データの読み込み

**原因**: Preview では Mock データ、テストでは実データを参照

**対策**:
```swift
// 共通のスタブを使用
extension MyView {
    enum Stub {
        static var loaded: MyView {
            MyView(data: .stubData)  // 両方で同じスタブを使用
        }
    }
}
```
