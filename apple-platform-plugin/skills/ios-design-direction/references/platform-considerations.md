# Platform-Specific Design Considerations

## iOS (iPhone)

### 画面とSafe Area

```swift
// Safe Areaを尊重（デフォルト）
VStack {
    content
}

// 背景のみSafe Area無視
VStack {
    content
}
.background(.blue)
.ignoresSafeArea()

// キーボード対応
.ignoresSafeArea(.keyboard)
```

### 片手操作の考慮

```
画面下部: 最もアクセスしやすい（重要なアクション）
画面中央: アクセスしやすい（主要コンテンツ）
画面上部: アクセスしにくい（ナビゲーション、タイトル）
```

```swift
// 重要なアクションは下部に
VStack {
    Spacer()
    content
    Spacer()
    
    Button("メインアクション") { }
        .buttonStyle(.borderedProminent)
        .padding(.bottom)
}
```

### Navigation

```swift
// 標準的なナビゲーション
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationTitle("アイテム")
    .navigationDestination(for: Item.self) { item in
        ItemDetail(item: item)
    }
}

// Tab Bar（5項目以下）
TabView {
    HomeView()
        .tabItem {
            Label("ホーム", systemImage: "house")
        }
    SearchView()
        .tabItem {
            Label("検索", systemImage: "magnifyingglass")
        }
}
```

## iPadOS

### マルチタスキング

```swift
// Size Classに応じた対応
@Environment(\.horizontalSizeClass) var horizontalSizeClass

var body: some View {
    if horizontalSizeClass == .regular {
        // Split View対応レイアウト
        NavigationSplitView {
            Sidebar()
        } detail: {
            DetailView()
        }
    } else {
        // Compact時はStack
        NavigationStack {
            ListView()
        }
    }
}
```

### Sidebar

```swift
NavigationSplitView(columnVisibility: $columnVisibility) {
    // Sidebar
    List(selection: $selection) {
        Section("メイン") {
            ForEach(mainItems) { item in
                NavigationLink(value: item) {
                    Label(item.title, systemImage: item.icon)
                }
            }
        }
    }
    .listStyle(.sidebar)
    .navigationTitle("メニュー")
} content: {
    // Content (Optional)
    ContentList(selection: selection)
} detail: {
    // Detail
    DetailView(item: selectedItem)
}
```

### ポインタ（トラックパッド/マウス）対応

```swift
// ホバー効果
Button("Action") { }
    .hoverEffect(.highlight)

// カスタムホバー
.onHover { isHovering in
    withAnimation(.easeInOut(duration: 0.15)) {
        self.isHovered = isHovering
    }
}

// ポインタスタイル
.pointerStyle(.link)
.pointerStyle(.frameResize(position: .trailing))
```

### キーボードショートカット

```swift
Button("保存") { save() }
    .keyboardShortcut("s", modifiers: .command)

Button("新規") { createNew() }
    .keyboardShortcut("n", modifiers: .command)
```

## watchOS

### 画面サイズと情報密度

```swift
// グランス可能なデザイン
VStack(spacing: 4) {
    Text("心拍数")
        .font(.caption2)
        .foregroundStyle(.secondary)
    Text("72")
        .font(.system(.title, design: .rounded, weight: .bold))
    Text("BPM")
        .font(.caption2)
}
```

### Digital Crown

```swift
@State private var selectedIndex = 0

ScrollView {
    VStack {
        ForEach(items.indices, id: \.self) { index in
            ItemRow(item: items[index])
        }
    }
}
.focusable()
.digitalCrownRotation($selectedIndex, from: 0, through: items.count - 1)
```

### 簡潔なインタラクション

```swift
// シンプルなアクション
List {
    ForEach(workouts) { workout in
        NavigationLink {
            WorkoutDetail(workout: workout)
        } label: {
            WorkoutRow(workout: workout)
        }
    }
}
.listStyle(.carousel)  // watchOS特有
```

### Complications

```swift
// WidgetKit for watchOS
struct WorkoutComplication: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "Workout", provider: Provider()) { entry in
            ComplicationView(entry: entry)
        }
        .configurationDisplayName("ワークアウト")
        .supportedFamilies([.accessoryCircular, .accessoryRectangular])
    }
}
```

## visionOS

### 空間デザインの原則

```swift
// WindowGroup（2Dウィンドウ）
WindowGroup {
    ContentView()
}
.windowStyle(.plain)

// Volumetric（3Dコンテンツ）
WindowGroup(id: "volume") {
    Model3D(named: "Globe")
}
.windowStyle(.volumetric)

// Immersive Space
ImmersiveSpace(id: "immersive") {
    ImmersiveView()
}
```

### 視線 + ジェスチャー

```swift
// ホバー効果（視線ターゲティング）
Model3D(named: "object")
    .hoverEffect()

// タップ（ピンチジェスチャー）
Model3D(named: "button")
    .gesture(TapGesture().onEnded { _ in
        performAction()
    })
```

### 奥行きとレイヤー

```swift
// Glass material
ZStack {
    content
}
.glassBackgroundEffect()

// Ornaments（浮遊UI）
WindowGroup {
    MainContent()
        .ornament(attachmentAnchor: .scene(.bottom)) {
            ToolbarView()
        }
}
```

### 人間工学

```
- 快適な視野角: 正面から左右30度
- 適切な距離: 1-3メートル
- コンテンツの高さ: 目線より少し下
- テキストサイズ: 物理的な読みやすさを考慮
```

## クロスプラットフォーム対応

### 条件分岐

```swift
#if os(iOS)
// iOS固有のコード
#elseif os(watchOS)
// watchOS固有のコード
#elseif os(visionOS)
// visionOS固有のコード
#endif
```

### 共通コンポーネント

```swift
struct AdaptiveButton: View {
    let title: String
    let action: () -> Void
    
    var body: some View {
        #if os(watchOS)
        Button(title, action: action)
            .buttonStyle(.bordered)
        #else
        Button(title, action: action)
            .buttonStyle(.borderedProminent)
        #endif
    }
}
```

### プラットフォーム別アセット

```
Assets.xcassets/
├── AppIcon.appiconset/
│   ├── iPhone icons
│   ├── iPad icons
│   ├── watchOS icons
│   └── visionOS icons
├── Colors/
│   └── Adaptive colors
└── Images/
    ├── iOS/
    ├── watchOS/
    └── visionOS/
```
