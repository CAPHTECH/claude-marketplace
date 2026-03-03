# SwiftUI アクセシビリティガイド

## 基本原則

1. **知覚可能**: すべての情報がユーザーに知覚できる
2. **操作可能**: すべての機能がユーザーに操作できる
3. **理解可能**: 情報と操作が理解しやすい
4. **堅牢**: 様々な支援技術で利用できる

## VoiceOver対応

### アクセシビリティラベル
```swift
// 画像には必ずラベルを付ける
Image("profile")
    .accessibilityLabel("プロフィール画像")

// アイコンボタン
Button(action: { /* ... */ }) {
    Image(systemName: "trash")
}
.accessibilityLabel("削除")

// 装飾的な画像は非表示
Image("decorative-pattern")
    .accessibilityHidden(true)
```

### アクセシビリティヒント
```swift
Button("購入") {
    purchase()
}
.accessibilityHint("ダブルタップで購入を確定します")
```

### 要素の結合
```swift
// 関連する要素を1つにまとめる
HStack {
    Image("product")
    VStack(alignment: .leading) {
        Text("iPhone 15")
        Text("¥139,800")
    }
}
.accessibilityElement(children: .combine)
// 読み上げ: "iPhone 15 ¥139,800"

// または明示的にラベルを設定
.accessibilityElement(children: .ignore)
.accessibilityLabel("iPhone 15、139,800円")
```

### Traits（特性）
```swift
// ボタンであることを示す
Text("タップして続行")
    .onTapGesture { /* ... */ }
    .accessibilityAddTraits(.isButton)

// 見出しであることを示す
Text("設定")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)

// 選択可能な要素
RowView(item: item)
    .accessibilityAddTraits(isSelected ? .isSelected : [])

// 更新中の要素
ContentView()
    .accessibilityAddTraits(isLoading ? .updatesFrequently : [])
```

### カスタムアクション
```swift
struct MessageRow: View {
    let message: Message

    var body: some View {
        MessageContent(message: message)
            .accessibilityAction(named: "返信") {
                reply()
            }
            .accessibilityAction(named: "転送") {
                forward()
            }
            .accessibilityAction(named: "削除") {
                delete()
            }
    }
}
```

## Dynamic Type対応

### 基本対応
```swift
// システムフォントは自動対応
Text("Hello")
    .font(.body)  // 自動的にスケール

// カスタムフォントの場合
Text("Custom")
    .font(.custom("MyFont", size: 17, relativeTo: .body))
```

### レイアウト調整
```swift
struct AdaptiveLayout: View {
    @Environment(\.sizeCategory) var sizeCategory

    var body: some View {
        if sizeCategory.isAccessibilityCategory {
            // 大きいサイズ: 縦並び
            VStack(alignment: .leading, spacing: 8) {
                iconAndTitle
                subtitle
            }
        } else {
            // 通常サイズ: 横並び
            HStack {
                iconAndTitle
                Spacer()
                subtitle
            }
        }
    }

    private var iconAndTitle: some View {
        HStack {
            Image(systemName: "star.fill")
            Text("Title")
        }
    }

    private var subtitle: some View {
        Text("Subtitle")
            .foregroundStyle(.secondary)
    }
}
```

### 最小タップ領域
```swift
// 44x44ポイント以上を確保
Button("Small Text") {
    action()
}
.frame(minWidth: 44, minHeight: 44)
```

## カラーコントラスト

### コントラスト比の確保
```swift
// 背景に対して十分なコントラストを確保
// 通常テキスト: 4.5:1以上
// 大きいテキスト: 3:1以上

Text("重要な情報")
    .foregroundStyle(.primary)  // 適切なコントラスト

// カスタムカラーの場合
Text("Alert")
    .foregroundColor(Color.red)  // コントラスト比を確認
    .accessibilityIgnoresInvertColors()  // 色反転時も維持
```

### 色だけに頼らない
```swift
// Bad: 色だけで状態を示す
Circle()
    .fill(isSuccess ? .green : .red)

// Good: アイコンも併用
HStack {
    Image(systemName: isSuccess ? "checkmark.circle" : "xmark.circle")
    Text(isSuccess ? "成功" : "失敗")
}
.foregroundStyle(isSuccess ? .green : .red)
```

## Reduce Motion対応

```swift
struct AnimatedView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        if reduceMotion {
            // アニメーションなし
            content
        } else {
            // アニメーションあり
            content
                .transition(.slide)
        }
    }
}

// または明示的に制御
withAnimation(reduceMotion ? nil : .default) {
    isExpanded.toggle()
}
```

## Reduce Transparency対応

```swift
struct BlurredBackground: View {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency

    var body: some View {
        if reduceTransparency {
            // 不透明な背景
            Color.black
        } else {
            // ぼかし効果
            Color.black.opacity(0.3)
                .background(.ultraThinMaterial)
        }
    }
}
```

## フォーカス管理

### AccessibilityFocusState
```swift
struct FormView: View {
    @AccessibilityFocusState var focusedField: FormField?

    var body: some View {
        Form {
            TextField("Name", text: $name)
                .accessibilityFocused($focusedField, equals: .name)

            TextField("Email", text: $email)
                .accessibilityFocused($focusedField, equals: .email)
        }
        .onChange(of: validationError) { _, error in
            if let error {
                // エラーのあるフィールドにフォーカス
                focusedField = error.field
            }
        }
    }
}
```

### スクリーンリーダー通知
```swift
// 重要な変更を通知
func updateStatus() {
    status = "完了しました"
    AccessibilityNotification.Announcement(status).post()
}

// レイアウト変更を通知
func toggleExpansion() {
    isExpanded.toggle()
    AccessibilityNotification.LayoutChanged(nil).post()
}
```

## チェックリスト

### 必須項目
- [ ] すべてのインタラクティブ要素にアクセシビリティラベル
- [ ] 画像に適切なラベルまたは非表示設定
- [ ] Dynamic Typeでレイアウトが崩れない
- [ ] 最小タップ領域44x44ポイント
- [ ] 十分なカラーコントラスト

### 推奨項目
- [ ] カスタムアクションの実装
- [ ] Reduce Motion対応
- [ ] スクリーンリーダー通知
- [ ] フォーカス管理
- [ ] ローター対応

### テスト方法
1. VoiceOverをオンにして操作
2. Dynamic Typeを最大サイズに設定
3. Reduce Motionをオンに設定
4. カラーフィルタ（グレースケール）で確認
5. Accessibility Inspectorでチェック
