# Accessibility 詳細ガイド

アクセシビリティは「追加機能」ではなく、設計の基盤。

## VoiceOver

### 基本的なラベル付け

```swift
// accessibilityLabel - 要素の説明
Button(action: share) {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("共有")

// accessibilityHint - 追加のコンテキスト
.accessibilityHint("この記事を他のアプリと共有します")

// accessibilityValue - 現在の値
Slider(value: $volume, in: 0...100)
    .accessibilityValue("\(Int(volume))パーセント")
```

### 要素のグループ化

```swift
// 複数要素を1つとして読み上げ
HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(123件のレビュー)")
}
.accessibilityElement(children: .combine)

// カスタムラベル
.accessibilityElement(children: .ignore)
.accessibilityLabel("評価4.5、123件のレビュー")
```

### アクションの追加

```swift
// カスタムアクション
ItemRow(item: item)
    .accessibilityAction(named: "削除") {
        deleteItem(item)
    }
    .accessibilityAction(named: "お気に入りに追加") {
        favoriteItem(item)
    }
```

### Traits

```swift
// 要素の性質を伝える
Text("設定")
    .accessibilityAddTraits(.isHeader)

Button("詳細を見る") { }
    .accessibilityAddTraits(.isLink)

// 選択状態
.accessibilityAddTraits(isSelected ? .isSelected : [])
```

### Rotor Actions

```swift
// 見出しジャンプ用
Text("セクション1")
    .accessibilityHeading(.h1)

Text("サブセクション")
    .accessibilityHeading(.h2)
```

## Dynamic Type

### 基本対応

```swift
// システムフォントは自動対応
Text("Body text")
    .font(.body)

// カスタムサイズでも対応
@ScaledMetric var iconSize: CGFloat = 24

Image(systemName: "star")
    .font(.system(size: iconSize))
```

### サイズ範囲の制限

```swift
// 最大サイズを制限（レイアウトが崩れる場合）
Text("Title")
    .dynamicTypeSize(...DynamicTypeSize.accessibility2)

// 最小サイズを保証
Text("Important")
    .dynamicTypeSize(DynamicTypeSize.large...)
```

### レイアウト適応

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        // 大きいサイズでは縦積み
        VStack(alignment: .leading) {
            icon
            labels
        }
    } else {
        // 通常は横並び
        HStack {
            icon
            labels
        }
    }
}
```

### ScaledMetric

```swift
struct IconButton: View {
    @ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 20
    @ScaledMetric(relativeTo: .body) var padding: CGFloat = 12
    
    var body: some View {
        Image(systemName: "gear")
            .font(.system(size: iconSize))
            .padding(padding)
    }
}
```

## Color & Contrast

### コントラスト比の確保

```swift
// ✅ 高コントラストの組み合わせ
Text("Important")
    .foregroundStyle(.primary)
    .background(.background)

// ✅ High Contrast対応
@Environment(\.colorSchemeContrast) var contrast

var textColor: Color {
    contrast == .increased ? .black : .primary
}
```

### 色だけに依存しない

```swift
// ❌ 色のみで状態を表現
Circle()
    .fill(isError ? .red : .green)

// ✅ 色 + アイコン + テキスト
HStack {
    Image(systemName: isError ? "xmark.circle" : "checkmark.circle")
    Text(isError ? "エラー" : "成功")
}
.foregroundStyle(isError ? .red : .green)
```

### Differentiate Without Color

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

var body: some View {
    if differentiateWithoutColor {
        // 色以外の視覚的区別を追加
        statusView
            .overlay(
                statusIcon
            )
    } else {
        statusView
    }
}
```

## Motor Accessibility

### タップターゲット

```swift
// 最小44pt x 44ptを確保
Button(action: action) {
    Image(systemName: "plus")
        .frame(minWidth: 44, minHeight: 44)
}

// 小さいアイコンでも領域を確保
Image(systemName: "info.circle")
    .contentShape(Rectangle())
    .frame(width: 44, height: 44)
```

### ジェスチャーの代替

```swift
// スワイプの代替としてボタンを提供
List {
    ForEach(items) { item in
        ItemRow(item: item)
            .swipeActions {
                Button("削除", role: .destructive) {
                    delete(item)
                }
            }
            // コンテキストメニューも提供
            .contextMenu {
                Button("削除", role: .destructive) {
                    delete(item)
                }
            }
    }
}
```

### Switch Control対応

```swift
// フォーカス可能な要素を明確に
.focusable()
.focused($focusedField, equals: .username)

// フォーカス順序の制御
.accessibilitySortPriority(1)
```

## Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    content
        .animation(reduceMotion ? nil : .spring(), value: isExpanded)
}

// トランジションも考慮
.transition(reduceMotion ? .opacity : .scale.combined(with: .opacity))
```

## Reduce Transparency

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

var background: some ShapeStyle {
    reduceTransparency ? AnyShapeStyle(.background) : AnyShapeStyle(.regularMaterial)
}
```

## Bold Text

```swift
@Environment(\.legibilityWeight) var legibilityWeight

var fontWeight: Font.Weight {
    legibilityWeight == .bold ? .bold : .regular
}
```

## Testing Checklist

### VoiceOver
- [ ] すべての要素が適切に読み上げられる
- [ ] 論理的な読み上げ順序
- [ ] カスタムアクションが必要な箇所に設定
- [ ] 動的コンテンツの更新が通知される

### Dynamic Type
- [ ] xxxLargeでレイアウトが崩れない
- [ ] テキストが切り捨てられない
- [ ] スクロール可能な領域で全コンテンツにアクセス可能

### Color
- [ ] 4.5:1以上のコントラスト比
- [ ] 色のみに依存しない情報伝達
- [ ] High Contrastモードで確認

### Motor
- [ ] 44pt以上のタップターゲット
- [ ] ジェスチャーの代替手段
- [ ] Switch Controlでナビゲート可能

### General
- [ ] Reduce Motionでアニメーション制御
- [ ] Reduce Transparencyで視認性確保
- [ ] 横向き・縦向き両対応
