# SwiftUI Implementation Patterns

## Layout Patterns

### Adaptive Layouts

```swift
// ViewThatFits - 収まるレイアウトを自動選択
ViewThatFits {
    HStack(spacing: 16) {
        icon
        title
        description
    }
    VStack(alignment: .leading, spacing: 8) {
        HStack { icon; title }
        description
    }
}

// AnyLayout - 条件付きレイアウト切り替え
let layout = isCompact ? AnyLayout(VStackLayout()) : AnyLayout(HStackLayout())

layout {
    ForEach(items) { item in
        ItemView(item: item)
    }
}
```

### Size Classes

```swift
struct AdaptiveView: View {
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.verticalSizeClass) var verticalSizeClass
    
    var body: some View {
        if horizontalSizeClass == .compact {
            CompactLayout()
        } else {
            RegularLayout()
        }
    }
}
```

### Container Relative Frames

```swift
// 親コンテナに対する相対サイズ
Image("hero")
    .containerRelativeFrame(.horizontal) { length, _ in
        length * 0.8
    }

// グリッドレイアウト
ScrollView(.horizontal) {
    LazyHStack {
        ForEach(items) { item in
            ItemCard(item: item)
                .containerRelativeFrame(.horizontal, count: 3, spacing: 16)
        }
    }
}
```

### Geometry Reader（慎重に使用）

```swift
// 必要な場合のみ使用
GeometryReader { geometry in
    let width = geometry.size.width
    
    HStack(spacing: 0) {
        SidePanel()
            .frame(width: width * 0.3)
        MainContent()
            .frame(width: width * 0.7)
    }
}
```

## Animation Patterns

### Spring Animations

```swift
// 標準的なSpring
withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
    isExpanded.toggle()
}

// Bouncy
.spring(response: 0.5, dampingFraction: 0.5, blendDuration: 0)

// Snappy
.spring(response: 0.3, dampingFraction: 0.8, blendDuration: 0)

// Smooth
.spring(response: 0.4, dampingFraction: 1.0, blendDuration: 0)
```

### Implicit vs Explicit Animation

```swift
// Implicit（推奨：特定のプロパティに紐付け）
Circle()
    .fill(isActive ? .blue : .gray)
    .animation(.spring(), value: isActive)

// Explicit（複数の変更を一括アニメーション）
Button("Toggle") {
    withAnimation(.easeInOut(duration: 0.3)) {
        isExpanded.toggle()
        selectedItem = newItem
    }
}
```

### Matched Geometry Effect

```swift
struct HeroAnimation: View {
    @Namespace private var namespace
    @State private var isExpanded = false
    
    var body: some View {
        if isExpanded {
            ExpandedView()
                .matchedGeometryEffect(id: "card", in: namespace)
        } else {
            CollapsedView()
                .matchedGeometryEffect(id: "card", in: namespace)
        }
    }
}
```

### Phase Animator (iOS 17+)

```swift
// 複数フェーズのアニメーション
PhaseAnimator([false, true]) { phase in
    Circle()
        .scaleEffect(phase ? 1.2 : 1.0)
        .opacity(phase ? 0.5 : 1.0)
}

// カスタムフェーズ
enum LoadingPhase: CaseIterable {
    case start, middle, end
}

PhaseAnimator(LoadingPhase.allCases) { phase in
    LoadingIndicator(phase: phase)
} animation: { phase in
    switch phase {
    case .start: .easeIn(duration: 0.3)
    case .middle: .linear(duration: 0.5)
    case .end: .easeOut(duration: 0.3)
    }
}
```

### Keyframe Animator (iOS 17+)

```swift
KeyframeAnimator(initialValue: AnimationValues()) { values in
    Circle()
        .scaleEffect(values.scale)
        .offset(y: values.verticalOffset)
} keyframes: { _ in
    KeyframeTrack(\.scale) {
        SpringKeyframe(1.2, duration: 0.3)
        SpringKeyframe(1.0, duration: 0.2)
    }
    KeyframeTrack(\.verticalOffset) {
        LinearKeyframe(-20, duration: 0.2)
        SpringKeyframe(0, duration: 0.3)
    }
}
```

### Reduce Motion対応

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var animation: Animation? {
    reduceMotion ? nil : .spring(response: 0.3)
}

Button("Tap") {
    withAnimation(animation) {
        isExpanded.toggle()
    }
}
```

## Transition Patterns

### Built-in Transitions

```swift
// 基本
.transition(.opacity)
.transition(.scale)
.transition(.slide)
.transition(.move(edge: .bottom))

// 組み合わせ
.transition(.opacity.combined(with: .scale))

// 非対称（入り/出で異なる）
.transition(.asymmetric(
    insertion: .scale.combined(with: .opacity),
    removal: .opacity
))
```

### Custom Transitions

```swift
extension AnyTransition {
    static var cardFlip: AnyTransition {
        .modifier(
            active: FlipModifier(angle: 90),
            identity: FlipModifier(angle: 0)
        )
    }
}

struct FlipModifier: ViewModifier {
    let angle: Double
    
    func body(content: Content) -> some View {
        content
            .rotation3DEffect(.degrees(angle), axis: (x: 0, y: 1, z: 0))
            .opacity(angle == 90 ? 0 : 1)
    }
}
```

### Navigation Transitions (iOS 16+)

```swift
NavigationStack {
    ContentView()
        .navigationDestination(for: Item.self) { item in
            DetailView(item: item)
        }
}
.navigationTransition(.zoom(sourceID: selectedItem?.id, in: namespace))
```

## Component Patterns

### Reusable Card Component

```swift
struct Card<Content: View>: View {
    let content: Content
    
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    
    var body: some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(color: .black.opacity(0.1), radius: 8, y: 4)
    }
}

// 使用
Card {
    VStack {
        Text("Title")
        Text("Description")
    }
}
```

### Button Styles

```swift
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.horizontal, 24)
            .padding(.vertical, 12)
            .background(configuration.isPressed ? .blue.opacity(0.8) : .blue)
            .clipShape(Capsule())
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.spring(response: 0.2), value: configuration.isPressed)
    }
}

// 使用
Button("Primary Action") { }
    .buttonStyle(PrimaryButtonStyle())
```

### Loading States

```swift
struct LoadingView<Content: View>: View {
    let isLoading: Bool
    let content: Content
    
    init(isLoading: Bool, @ViewBuilder content: () -> Content) {
        self.isLoading = isLoading
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            content
                .opacity(isLoading ? 0.3 : 1.0)
                .disabled(isLoading)
            
            if isLoading {
                ProgressView()
            }
        }
        .animation(.easeInOut(duration: 0.2), value: isLoading)
    }
}
```

## State Management Patterns

### @Observable (iOS 17+)

```swift
@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: Error?
    
    func load() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            items = try await fetchItems()
        } catch {
            self.error = error
        }
    }
}

struct ContentView: View {
    @State private var viewModel = ViewModel()
    
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

### Environment Values

```swift
// カスタムEnvironment Key
private struct ThemeKey: EnvironmentKey {
    static let defaultValue = Theme.default
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// 使用
@Environment(\.theme) var theme

// 設定
ContentView()
    .environment(\.theme, customTheme)
```
