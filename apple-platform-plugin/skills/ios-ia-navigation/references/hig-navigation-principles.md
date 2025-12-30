# Apple HIG ナビゲーション原則

Apple Human Interface Guidelines および WWDC セッションから抽出したナビゲーション設計の原則。

## 参照元

| 資料 | 内容 |
|------|------|
| [Apple HIG - Navigation](https://developer.apple.com/design/human-interface-guidelines/navigation) | 公式ガイドライン |
| WWDC22「Explore navigation design for iOS」 | タブ設計、push/modal使い分け |
| WWDC22「The SwiftUI cookbook for navigation」 | NavigationStack/SplitView実装 |
| WWDC24 | iOS 18のナビゲーション更新 |

---

## 1. ナビゲーションの3つの基本スタイル

### 1.1 階層型（Hierarchical）
```
一般的な情報ドリルダウン
Root → List → Detail → Sub-detail
```
- **用途**: コンテンツの閲覧、設定画面
- **実装**: `NavigationStack` with push
- **特徴**: 明確な親子関係、戻りパスが一意

### 1.2 フラット型（Flat）
```
トップレベルで並列なカテゴリ
Tab1 | Tab2 | Tab3 | Tab4 | Tab5
```
- **用途**: アプリのメインナビゲーション
- **実装**: `TabView`
- **特徴**: どのタブからも他タブへ即座にアクセス可能

### 1.3 コンテンツ駆動型（Content-driven）
```
コンテンツの関係性で遷移
Page1 ←→ Page2 ←→ Page3
```
- **用途**: ページング、ブック、ゲーム
- **実装**: カスタムナビゲーション
- **特徴**: コンテンツの論理的順序に従う

---

## 2. Tab Bar の原則

### 2.1 基本原則

| 原則 | 説明 |
|------|------|
| **情報階層の反映** | タブはアプリのトップレベルカテゴリを表す |
| **持続性** | タブバーは常に表示され、どの画面からもアクセス可能 |
| **状態保持** | 各タブは独立した状態を保持する |
| **5つ以下** | 推奨は3-5タブ。5を超える場合は「その他」タブを検討 |

### 2.2 やってはいけないこと

| アンチパターン | 理由 |
|---------------|------|
| **タブの自動切り替え** | ユーザーを混乱させる（jarring/disorienting） |
| **機能の重複** | 同じ機能を複数タブに配置しない |
| **なんでもHomeタブ** | Homeに機能を詰め込みすぎると混乱する |
| **モーダル時のタブ非表示** | フルスクリーンモーダルでのみ隠す |

### 2.3 タブ設計のベストプラクティス

```yaml
good_example:
  - tab: Home
    content: "パーソナライズされたコンテンツ"

  - tab: Search
    content: "検索・発見"

  - tab: Library
    content: "ユーザーのコレクション"

  - tab: Profile
    content: "アカウント・設定"

bad_example:
  - tab: Home
    content: "検索、お気に入り、設定、通知、全部入り"  # NG: 詰め込みすぎ
```

---

## 3. Push vs Modal の使い分け

### 3.1 Push（階層遷移）

| 特徴 | 説明 |
|------|------|
| **意味** | 階層を掘り下げる、親子関係を強化 |
| **見た目** | 右からスライドイン |
| **タブバー** | 表示を維持 |
| **戻り方** | 左上の戻るボタン、エッジスワイプ |
| **状態** | 親画面の状態は保持される |

#### Push を使うべき場面
- 一覧 → 詳細
- カテゴリ → サブカテゴリ
- 設定メニュー → 設定項目
- 関連コンテンツへの遷移

### 3.2 Modal（文脈遷移）

| 特徴 | 説明 |
|------|------|
| **意味** | 現在の文脈から切り離す、自己完結タスク |
| **見た目** | 下からスライドアップ（sheet/fullScreenCover） |
| **タブバー** | 覆われる（意図的な中断） |
| **戻り方** | 閉じる/キャンセル/保存ボタン、下スワイプ |
| **状態** | モーダル内で完結、親は影響を受けない |

#### Modal を使うべき場面
- 新規作成・編集
- フィルタ・ソート設定
- 認証フロー
- 集中すべきタスク（チェックアウトなど）
- 確認ダイアログ

### 3.3 Presentation スタイル

| スタイル | 用途 |
|----------|------|
| `.sheet` | 通常のモーダル、下部に親が見える |
| `.sheet(detents:)` | 高さ調整可能なシート（.medium, .large） |
| `.fullScreenCover` | フルスクリーン、重要なフロー |
| `.popover` | iPad向け、小さな情報表示 |

### 3.4 Modal のアンチパターン

| アンチパターン | 理由 |
|---------------|------|
| **Modal over Modal** | ユーザーを迷わせる、過剰 |
| **長い階層をModal内で** | Pushを使うべき |
| **単なる情報表示にfullScreenCover** | sheetで十分 |

---

## 4. Navigation Stack と Split View

### 4.1 NavigationStack（iOS 16+）

```swift
// 基本構造
NavigationStack {
    RootView()
        .navigationDestination(for: Item.self) { item in
            DetailView(item: item)
        }
}

// プログラム的なナビゲーション
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    // ...
}

// Deep link
path.append(targetItem)
```

### 4.2 NavigationSplitView（iPad対応）

```swift
// 2カラム
NavigationSplitView {
    Sidebar()
} detail: {
    DetailView()
}

// 3カラム
NavigationSplitView {
    Sidebar()
} content: {
    ContentList()
} detail: {
    DetailView()
}
```

#### カラムの役割
| カラム | 役割 |
|--------|------|
| Sidebar | ナビゲーションの起点、カテゴリ選択 |
| Content | 中間リスト（オプション） |
| Detail | 選択されたコンテンツの詳細 |

#### Compact時の動作
- 自動的にNavigationStackにフォールバック
- Sidebar → Content → Detail の順でpush

---

## 5. 状態保持（State Preservation）

### 5.1 タブ間の状態保持

```swift
// 各タブは独自のNavigationStackを持つ
TabView {
    NavigationStack {
        HomeView()
    }
    .tabItem { Label("Home", systemImage: "house") }

    NavigationStack {
        SearchView()
    }
    .tabItem { Label("Search", systemImage: "magnifyingglass") }
}
```

### 5.2 Scene Storage（アプリ再起動後の復元）

```swift
@SceneStorage("selectedTab") private var selectedTab = "home"
@SceneStorage("navigationPath") private var navigationPath = Data()
```

---

## 6. Deep Link

### 6.1 URL Scheme

```swift
// URL: myapp://product/123
func handleDeepLink(_ url: URL) {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
          let host = components.host else { return }

    switch host {
    case "product":
        let id = components.path.dropFirst() // "123"
        // Navigate to product
        selectedTab = .search
        navigationPath.append(Product(id: id))
    default:
        break
    }
}
```

### 6.2 親階層の補完

Deep linkで詳細画面に直接入った場合、戻るボタンで適切な親画面に戻れるようにする：

```swift
// 直接ProductDetailに入った場合
// path: [] → [ProductList, ProductDetail(id)]
// これにより、戻るボタンでProductListに行ける
```

---

## 7. iOS 18 / iOS 26 の変更点

### 7.1 Liquid Glass（visionOS起源）

- タブバーのデザインが動的に変化
- 縮小/拡大するタブバー
- **役割は変わらない**：ナビゲーションの目的は同じ

### 7.2 考慮事項

| 変更 | 対応 |
|------|------|
| タブバーの見た目が動的 | 役割は変わらないので設計に影響なし |
| より流動的なUI | コンテンツとUIの関係をより意識 |

---

## 8. チェックリスト

### ナビゲーション設計時の確認事項

#### Tab Bar
- [ ] タブは情報階層のトップレベルを反映している
- [ ] 5つ以下のタブ
- [ ] 機能の重複がない
- [ ] タブの自動切り替えを前提にしていない

#### Push vs Modal
- [ ] 階層関係にはpushを使用
- [ ] 自己完結タスクにはmodalを使用
- [ ] Modal over Modalを避けている
- [ ] すべての画面に「出口」が定義されている

#### 状態保持
- [ ] タブ間で状態が保持される
- [ ] 戻り方で状態が失われない
- [ ] リセット条件が明確

#### iPad対応
- [ ] NavigationSplitViewで構造化
- [ ] Compact時のフォールバックが自然

#### Deep Link
- [ ] すべてのルートが定義されている
- [ ] 親階層の補完が行われる
- [ ] 未認証時の動作が定義されている
