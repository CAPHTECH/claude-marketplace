# Visual Elements 詳細ガイド

## Typography

### System Fonts

#### SF Pro
iOS/macOSの標準システムフォント。9つのウェイト（Ultralight〜Black）と可変幅・等幅バリエーション。

```swift
// Text Styles（推奨）
.largeTitle    // 34pt Bold
.title         // 28pt Bold
.title2        // 22pt Bold
.title3        // 20pt Semibold
.headline      // 17pt Semibold
.body          // 17pt Regular
.callout       // 16pt Regular
.subheadline   // 15pt Regular
.footnote      // 13pt Regular
.caption       // 12pt Regular
.caption2      // 11pt Regular
```

#### SF Pro Rounded
角が丸いバリアント。フレンドリーな印象に。

```swift
Text("Rounded")
    .font(.system(.title, design: .rounded))
```

#### SF Mono
等幅フォント。コード、数値、技術的コンテンツに。

```swift
Text("code")
    .font(.system(.body, design: .monospaced))
```

#### New York
セリフ体。長文の読み物、エディトリアルコンテンツに。

```swift
Text("Article Title")
    .font(.system(.title, design: .serif))
```

### Typography Best Practices

1. **Text Styles使用**: 固定サイズではなくText Stylesを使う
2. **Dynamic Type対応**: すべてのテキストがスケール可能に
3. **行間**: 長文では適切な行間（lineSpacing）を設定
4. **文字間**: 大きなタイトルではtrackingを調整

```swift
Text("Long article content...")
    .font(.body)
    .lineSpacing(4)

Text("HEADER")
    .font(.largeTitle)
    .tracking(2)
```

## Color System

### Semantic Colors

```swift
// Label Colors
.primary           // 主要テキスト
.secondary         // 二次的テキスト
.tertiary          // 三次的テキスト
.quaternary        // プレースホルダー等

// Background Colors
.background        // 主要背景
.secondaryBackground
.tertiaryBackground

// System Colors
.systemRed, .systemBlue, .systemGreen...

// Accent
.accent            // アプリのアクセントカラー
.tint              // コントロールのティント
```

### Adaptive Colors

Asset Catalogで定義：
```
ColorSet/
├── Any Appearance → Light mode color
├── Dark Appearance → Dark mode color
└── High Contrast → Optional high contrast variants
```

### Color Contrast Requirements

| WCAG Level | Contrast Ratio | 用途 |
|------------|----------------|------|
| AA (Normal) | 4.5:1 | 通常テキスト |
| AA (Large) | 3:1 | 18pt以上/14pt Bold以上 |
| AAA | 7:1 | 高いアクセシビリティ要件 |

### Vibrancy & Materials

```swift
// Materials（背景ぼかし）
.regularMaterial
.thinMaterial
.ultraThinMaterial
.thickMaterial
.ultraThickMaterial

// 使用例
VStack {
    content
}
.background(.regularMaterial)
```

## SF Symbols

### 基本使用

```swift
// 基本
Image(systemName: "star.fill")

// サイズ調整
Image(systemName: "star.fill")
    .font(.title)
    
Image(systemName: "star.fill")
    .imageScale(.large)
```

### Rendering Modes

```swift
// Monochrome（単色）
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.monochrome)

// Hierarchical（階層的な透明度）
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.hierarchical)

// Palette（カスタム色の組み合わせ）
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.palette)
    .foregroundStyle(.blue, .yellow)

// Multicolor（元のマルチカラー）
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.multicolor)
```

### Variable Symbols

```swift
// 可変値シンボル（0.0〜1.0）
Image(systemName: "speaker.wave.3.fill")
    .symbolVariableValue(volume)
```

### Symbol Effects (iOS 17+)

```swift
// バウンス
Image(systemName: "arrow.down.circle")
    .symbolEffect(.bounce, value: downloadCount)

// パルス
Image(systemName: "antenna.radiowaves.left.and.right")
    .symbolEffect(.variableColor.iterative)

// 置き換え
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
    .contentTransition(.symbolEffect(.replace))
```

## Spatial Design

### Spacing System

```swift
// 8ptグリッドシステム
enum Spacing {
    static let xxs: CGFloat = 2
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}
```

### Layout Margins

```swift
// Safe Area
.ignoresSafeArea()           // 全画面
.ignoresSafeArea(.keyboard)  // キーボードのみ無視

// Padding
.padding()                   // 標準16pt
.padding(.horizontal)        // 水平のみ
.padding(.vertical, 24)      // 縦に24pt

// Scene Padding（読みやすい幅）
.scenePadding()
.scenePadding(.horizontal)
```

### Content Margins

```swift
// iOS 17+ コンテンツマージン
List {
    content
}
.contentMargins(.horizontal, 20, for: .scrollContent)
```

## Iconography Guidelines

### Custom Icon Design

1. **24x24 or 28x28**: 標準サイズ
2. **2pt stroke**: 線の太さ
3. **Round caps/joins**: 丸い端点
4. **Optical alignment**: 視覚的なバランス
5. **Consistent metaphors**: 一貫したメタファー

### Icon States

```swift
// Normal, Highlighted, Disabled
Image(systemName: "heart")
    .foregroundStyle(isEnabled ? .primary : .tertiary)
    
// Filled variant for selected
Image(systemName: isSelected ? "heart.fill" : "heart")
```
