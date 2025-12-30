# スナップショットテスト戦略

## スナップショット戦略の種類

### 1. 画像スナップショット

```swift
// 基本
assertSnapshot(of: view, as: .image)

// サイズ指定
assertSnapshot(of: view, as: .image(size: CGSize(width: 375, height: 812)))

// トレイト指定
assertSnapshot(of: view, as: .image(traits: .init(userInterfaceStyle: .dark)))
```

### 2. 階層スナップショット

```swift
// ビュー階層をテキストで
assertSnapshot(of: view, as: .recursiveDescription)
```

### 3. JSONスナップショット

```swift
// Codableオブジェクト
assertSnapshot(of: user, as: .json)
```

### 4. ダンプスナップショット

```swift
// Swift dumpの出力
assertSnapshot(of: viewModel, as: .dump)
```

## デバイス設定

### 主要デバイスサイズ

```swift
enum Device {
    static let iPhoneSE = CGSize(width: 375, height: 667)
    static let iPhone15 = CGSize(width: 393, height: 852)
    static let iPhone15ProMax = CGSize(width: 430, height: 932)
    static let iPadMini = CGSize(width: 744, height: 1133)
    static let iPadPro11 = CGSize(width: 834, height: 1194)
    static let iPadPro12_9 = CGSize(width: 1024, height: 1366)
}
```

### トレイト組み合わせ

```swift
func makeTraits(
    style: UIUserInterfaceStyle = .light,
    contentSize: UIContentSizeCategory = .large,
    idiom: UIUserInterfaceIdiom = .phone
) -> UITraitCollection {
    UITraitCollection(traitsFrom: [
        UITraitCollection(userInterfaceStyle: style),
        UITraitCollection(preferredContentSizeCategory: contentSize),
        UITraitCollection(userInterfaceIdiom: idiom)
    ])
}
```

## 差分許容設定

### precision（ピクセル単位の一致率）

```swift
// 99%のピクセルが一致すれば合格
assertSnapshot(of: view, as: .image(precision: 0.99))
```

### perceptualPrecision（知覚的な一致率）

```swift
// 視覚的に98%一致すれば合格（アンチエイリアス等を許容）
assertSnapshot(of: view, as: .image(perceptualPrecision: 0.98))
```

## 動的コンテンツの処理

### 日時のモック

```swift
// 固定日時でテスト
func testWithFixedDate() {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd"
    
    let viewModel = ViewModel(dateProvider: { formatter.date(from: "2024-01-01")! })
    let view = ContentView(viewModel: viewModel)
    
    assertSnapshot(of: view, as: .image)
}
```

### ランダムデータの固定

```swift
// シード固定の乱数
func testWithFixedRandom() {
    var rng = RandomNumberGeneratorWithSeed(seed: 42)
    let items = generateItems(using: &rng)
    
    assertSnapshot(of: ListView(items: items), as: .image)
}
```

## CI/CD設定

### スナップショットの保存場所

```
MyAppTests/
└── __Snapshots__/
    └── ViewTests/
        ├── testView.1.png
        └── testView_dark.1.png
```

### Git LFS設定

```gitattributes
*/__Snapshots__/**/*.png filter=lfs diff=lfs merge=lfs -text
```

### 失敗時のアーティファクト

```yaml
- name: Upload Failed Snapshots
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: failed-snapshots
    path: "**/Failures/**"
```
