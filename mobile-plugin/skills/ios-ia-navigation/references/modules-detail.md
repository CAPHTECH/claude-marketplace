# 設計モジュール詳細

各モジュールの詳細定義。目的 → 入力 → 出力 → 品質ゲート → 典型質問。

## Module 0: ドキュメント根拠化（Evidence Mapping）

### 目的
設計の"拠り所"を明示し、推測と根拠を分離する。

### 入力
- PRD、要件定義書
- ユーザーストーリー
- 既存分析データ
- ブランドガイドライン

### 出力

#### Evidence Map
```yaml
evidence_map:
  requirements:
    - id: REQ-001
      source: "PRD v1.2, Section 3.1"
      content: "ユーザーは商品を検索・閲覧・購入できる"
      category: functional
    - id: REQ-002
      source: "PRD v1.2, Section 4.2"
      content: "オフライン時も閲覧履歴を参照可能"
      category: non-functional

  constraints:
    - id: CON-001
      source: "運用要件書"
      content: "ログイン必須（ゲスト閲覧不可）"
      impact: [authentication_flow, onboarding]

  success_metrics:
    - id: MET-001
      source: "KPI定義"
      content: "購入完了率 > 3%"
      primary: true

  target_users:
    - persona: "一般消費者"
      characteristics: ["スマホ中心", "隙間時間利用"]
      priority: primary

  target_devices:
    - device: "iPhone"
      priority: primary
    - device: "iPad"
      priority: secondary
```

#### 用語集
| 用語 | 定義 | 同義語 | 注意 |
|------|------|--------|------|
| アイテム | 販売対象の商品 | 商品、プロダクト | 「商品」に統一 |
| カート | 購入予定リスト | バスケット | 「カート」に統一 |

### 品質ゲート
- [ ] 重要な意思決定が「どの記述に基づくか」追跡できる
- [ ] 曖昧な用語が統一されている

### 典型質問
- 「最優先の成功指標は何か（継続率/完了率/購入/投稿など）？」
- 「対象デバイスはiPhone中心か、iPadも主要ターゲットか？」
- 「"商品"と"アイテム"は同じ意味か？」

---

## Module 1: タスクモデル化（User Jobs & Task Hierarchy）

### 目的
画面遷移を"機能の羅列"で作らず、「人が何をしに来るか」で骨格を作る。

### 入力
- Evidence Map
- ユーザーインタビュー結果
- アクセス解析データ

### 出力

#### 主要タスク Top3-7
```yaml
primary_tasks:
  - rank: 1
    name: "商品を探して購入する"
    frequency: daily
    importance: critical
    trigger: "欲しいものがある時"
    success_state: "購入完了、配送待ち"

  - rank: 2
    name: "注文状況を確認する"
    frequency: weekly
    importance: high
    trigger: "購入後、届くか気になる時"
    success_state: "配送状況を把握"

  - rank: 3
    name: "お気に入りを管理する"
    frequency: weekly
    importance: medium
    trigger: "後で買いたいものを保存"
    success_state: "リストに追加/削除完了"
```

#### タスク分解
```yaml
task_breakdown:
  task: "商品を探して購入する"
  steps:
    - step: 1
      action: "検索/カテゴリから商品を探す"
      screen_hint: "検索画面 or カテゴリ一覧"

    - step: 2
      action: "商品詳細を確認する"
      screen_hint: "商品詳細画面"
      decision_point: "購入するか判断"

    - step: 3
      action: "カートに追加する"
      screen_hint: "商品詳細画面（アクション）"

    - step: 4
      action: "カートを確認して購入手続きへ"
      screen_hint: "カート画面"

    - step: 5
      action: "配送先・支払い情報を入力"
      screen_hint: "チェックアウト（モーダル推奨）"

    - step: 6
      action: "注文を確定する"
      screen_hint: "確認画面"
      success_state: "購入完了"
```

### 品質ゲート
- [ ] 主要タスクが"トップレベル構造（タブ/サイドバー）"に反映される準備ができている
- [ ] タスクの開始条件→中間状態→完了条件が明確

### 典型質問
- 「ユーザーがアプリを開いて最初にやる3つの行動は？」
- 「"必ず毎回見るべき情報"はあるか？」
- 「このタスクはどのくらいの頻度で行われる？」

---

## Module 2: コンテンツモデル＆情報の関係設計

### 目的
一覧→詳細、関連、検索、フィルタの自然な"関係"を定義し、誤った階層化を防ぐ。

### 入力
- タスク分解結果
- データベース設計（あれば）
- 既存画面（あれば）

### 出力

#### エンティティ定義
```yaml
entities:
  - name: Product
    description: "販売対象の商品"
    attributes:
      - name: id
        type: UUID
        required: true
      - name: title
        type: String
        required: true
      - name: price
        type: Decimal
        required: true
      - name: images
        type: "[URL]"
        required: true
      - name: description
        type: String
        required: false
    display:
      list_view: [title, price, images[0]]
      detail_view: all

  - name: Order
    description: "購入注文"
    attributes:
      - name: id
        type: UUID
        required: true
      - name: status
        type: Enum[pending, shipped, delivered]
        required: true
      - name: items
        type: "[OrderItem]"
        required: true
```

#### 関係定義
```yaml
relations:
  - source: Product
    target: Category
    type: "N:1"
    navigation: true  # カテゴリ→商品一覧の遷移に使用
    label: "belongs_to"

  - source: Order
    target: Product
    type: "N:N"
    via: OrderItem
    navigation: true  # 注文→商品詳細の遷移に使用

  - source: User
    target: Product
    type: "N:N"
    via: Favorite
    navigation: true  # お気に入り一覧→商品詳細
```

#### 階層候補
```yaml
hierarchy_candidates:
  - path: "Category → Product List → Product Detail"
    reasoning: "カテゴリは商品の親概念"
    navigation_type: push

  - path: "Order List → Order Detail → Product Detail"
    reasoning: "注文から商品へは参照関係"
    navigation_type: push (or modal for product)
```

### 品質ゲート
- [ ] 「この画面がこの画面の子である理由」が関係として説明できる
- [ ] すべての1:Nまたは親子関係がナビゲーション候補として検討済み

### 典型質問
- 「この情報とこの情報の関係は？（親子/関連/独立）」
- 「一覧で見せるべき属性は？」
- 「検索対象になる属性は？」

---

## Module 3: トップレベル情報設計（Tab/Sidebar設計）

### 目的
トップレベル（タブ／サイドバー）を、情報階層の"写像"として設計する。

### 規範（HIG/WWDC根拠）
- タブバーは情報階層を反映し、トップレベルのカテゴリを表す
- タブを"なんでも入るHome"にして機能を重複させると混乱する
- タブは「セクションの意味」を持たせ、機能を一つのタブに詰め込みすぎない
- タブ強制移動は"jarring / disorienting"として避ける

### 入力
- タスクモデル
- コンテンツモデル
- Evidence Map

### 出力

#### Top-levelセクション案
```yaml
top_level_sections:
  - tab: Home
    icon: house
    responsibility:
      include:
        - "パーソナライズされたおすすめ"
        - "最近閲覧した商品"
        - "セール情報"
      exclude:
        - "検索機能（Searchタブへ）"
        - "注文履歴（Ordersタブへ）"
    root_screen: HomeScreen
    navigation_style: NavigationStack

  - tab: Search
    icon: magnifyingglass
    responsibility:
      include:
        - "キーワード検索"
        - "カテゴリブラウズ"
        - "フィルタ・ソート"
      exclude:
        - "おすすめ（Homeへ）"
    root_screen: SearchScreen
    navigation_style: NavigationStack

  - tab: Cart
    icon: cart
    responsibility:
      include:
        - "カート内容確認"
        - "数量変更"
        - "チェックアウトへの導線"
      exclude:
        - "商品検索（Searchへ）"
    root_screen: CartScreen
    navigation_style: NavigationStack
    badge: item_count

  - tab: Orders
    icon: shippingbox
    responsibility:
      include:
        - "注文履歴"
        - "配送状況"
      exclude:
        - "新規注文（Cart経由）"
    root_screen: OrderListScreen
    navigation_style: NavigationStack

  - tab: Account
    icon: person
    responsibility:
      include:
        - "プロフィール"
        - "お気に入り"
        - "設定"
        - "ヘルプ"
      exclude: []
    root_screen: AccountScreen
    navigation_style: NavigationStack
```

#### 分類ルール
```yaml
classification_rules:
  - rule: "商品発見系 → Search"
  - rule: "購入フロー系 → Cart"
  - rule: "購入後系 → Orders"
  - rule: "ユーザー設定系 → Account"
  - rule: "パーソナライズ・ホーム系 → Home"
```

### 品質ゲート
- [ ] "どのタブに属するか"が毎回悩まない（分類ルールがある）
- [ ] 機能重複がない
- [ ] タブ強制移動を前提にしない
- [ ] 5タブ以下（推奨）

### 典型質問
- 「トップで常に切り替えたい"領域"は何か？」
- 「Homeのような"総合"が必要な理由は何か？」
- 「検索はタブとして独立すべきか、Homeに含めるか？」

---

## Module 4: 遷移設計（Push vs Modal）

### 目的
画面遷移を、ユーザーの期待する"意味"に揃える。

### 規範（HIG/WWDC根拠）
- **push**: 階層を掘る、関係を強化する
- **modal**: 文脈を切り替える、自己完結したタスク
- modalは下から現れ、タブバーを覆う＝意図的な中断
- "modals over modals" は過度に積むと過剰・不快

### 入力
- 画面インベントリ（ドラフト）
- タスク分解

### 出力

#### 遷移種別ルール
```yaml
navigation_rules:
  push:
    - pattern: "一覧 → 詳細"
      example: "ProductList → ProductDetail"
      reason: "階層関係、戻りで一覧に復帰"

    - pattern: "親 → 子"
      example: "Category → SubCategory → ProductList"
      reason: "情報階層の掘り下げ"

    - pattern: "関連アイテムへの遷移"
      example: "ProductDetail → RelatedProduct"
      reason: "同階層の横移動"

  modal:
    - pattern: "作成・編集"
      example: "→ EditProfile, → AddToCart(量選択)"
      reason: "自己完結タスク、完了/キャンセルで閉じる"
      presentation: sheet

    - pattern: "設定・フィルタ"
      example: "→ FilterOptions"
      reason: "一時的な設定変更"
      presentation: sheet

    - pattern: "認証フロー"
      example: "→ Login, → SignUp"
      reason: "アプリ全体の前提条件"
      presentation: fullScreenCover

    - pattern: "チェックアウト"
      example: "→ Checkout"
      reason: "集中すべき重要フロー"
      presentation: fullScreenCover
```

#### Modal内ナビゲーション
```yaml
modal_navigation:
  header_actions:
    cancel: "左上、変更破棄"
    save: "右上、変更保存"
    close: "右上×、情報表示のみの場合"

  dismiss_rules:
    - condition: "未保存の変更あり"
      action: "確認ダイアログ表示"
    - condition: "変更なし"
      action: "即座に閉じる"

  nested_navigation:
    allowed: "Modal内でのpushは可（ステップ遷移）"
    avoid: "Modal over Modalは原則禁止"
```

### 品質ゲート
- [ ] すべての画面に「出口（戻り方）」が定義
- [ ] push/modalの使い分けが一貫
- [ ] 親状態がどう保持されるか説明できる
- [ ] Modal over Modalを避けている

### 典型質問
- 「"作成/編集"は、親画面を参照しながらやる必要がある？」
- 「入力中断（キャンセル）時の扱い：破棄確認が必要な条件は？」
- 「この遷移は"掘り下げ"か"別タスク"か？」

---

## Module 5: タブの持続と状態保持設計

### 目的
タブ移動が"文脈保存の道具"として機能するようにする。

### 規範（HIG/WWDC根拠）
- タブバーは"常にアクセスできること"が価値
- タブを維持し、他タブの状態も保つから複数階層を行き来できる

### 入力
- タブ構成
- 画面インベントリ

### 出力

#### 状態保持ポリシー
```yaml
state_preservation:
  Home:
    scroll_position: preserve
    selected_item: preserve
    filter_state: preserve
    reset_trigger: "pull-to-refresh"

  Search:
    scroll_position: preserve
    search_query: preserve
    filter_state: preserve
    search_results: preserve
    reset_trigger: "新規検索時"

  Cart:
    scroll_position: preserve
    item_quantities: preserve  # サーバー同期
    reset_trigger: "購入完了時"

  Orders:
    scroll_position: preserve
    selected_order: preserve
    reset_trigger: "none"

  Account:
    scroll_position: reset  # 毎回トップ表示
    reset_trigger: "タブ選択時"
```

#### リセットルール
```yaml
reset_rules:
  - event: "ログアウト"
    action: "全タブ状態リセット"

  - event: "アプリ強制終了"
    action: "オプションで状態復元（State Restoration）"

  - event: "バックグラウンド30分以上"
    action: "検索結果のみリセット"
```

### 品質ゲート
- [ ] タブを跨いだ時に「どこにいたか」が失われにくい
- [ ] リセット条件が明確

### 典型質問
- 「検索結果はタブを離れても保持すべき？」
- 「どのタイミングで状態をリセットする？」

---

## Module 6: iPad/大画面適応（Split View設計）

### 目的
iPhoneだけでなく、iPad/横画面/将来拡張で破綻しない骨格にする。

### 規範（HIG/WWDC根拠）
- NavigationSplitViewは2〜3カラム
- 先行カラムの選択が後続カラムの表示を制御
- iPhoneでは自動的に単一カラムへ適応

### 入力
- 情報階層マップ
- 画面インベントリ

### 出力

#### カラム割り当て
```yaml
split_view_design:
  Search:
    columns: 2
    sidebar: "カテゴリ一覧"
    content: null
    detail: "商品一覧 → 商品詳細"
    compact_behavior: "カテゴリ→一覧→詳細のstack"

  Orders:
    columns: 2
    sidebar: "注文一覧"
    content: null
    detail: "注文詳細"
    compact_behavior: "一覧→詳細のstack"

  Account:
    columns: 2
    sidebar: "設定メニュー"
    content: null
    detail: "各設定画面"
    compact_behavior: "メニュー→設定のstack"

  Home:
    columns: 1
    note: "スクロールコンテンツ、Split不要"

  Cart:
    columns: 1
    note: "単一リスト、Split不要"
```

#### 並列表示方針
```yaml
parallel_display:
  - scenario: "商品一覧と詳細を同時表示"
    enabled: true
    condition: "iPad Regular幅"

  - scenario: "複数注文の比較表示"
    enabled: false
    reason: "ユースケースが稀"
```

### 品質ゲート
- [ ] "iPad化"が後付けでなく、構造として成立
- [ ] Compact時の縮退が自然
- [ ] カラム間の選択→表示関係が明確

### 典型質問
- 「iPadで一覧と詳細を同時に見せる価値はある？」
- 「3カラム（Sidebar+Content+Detail）が必要なケースは？」

---

## Module 7: ディープリンク／状態復元

### 目的
「通知から詳細へ」「リンクから特定画面へ」など、入口が増えても破綻しない遷移設計。

### 規範（HIG/WWDC根拠）
- NavigationStackのpathを操作してdeep link可能
- 状態復元（ナビ状態を保持/復帰）を扱う

### 入力
- 画面インベントリ
- 通知種別一覧
- URL scheme要件

### 出力

#### ルーティング表
```yaml
deep_link_routes:
  - url: "myapp://product/{id}"
    destination:
      tab: Search
      path: [ProductDetail(id)]
    fallback: "商品が見つからない場合→Search root"

  - url: "myapp://order/{id}"
    destination:
      tab: Orders
      path: [OrderDetail(id)]
    fallback: "注文が見つからない場合→Orders root"

  - url: "myapp://cart"
    destination:
      tab: Cart
      path: []

  - url: "myapp://search?q={query}"
    destination:
      tab: Search
      path: [SearchResults(query)]

notification_routes:
  - type: "order_shipped"
    destination:
      tab: Orders
      path: [OrderDetail(order_id)]

  - type: "price_drop"
    destination:
      tab: Search
      path: [ProductDetail(product_id)]
```

#### 状態復元規則
```yaml
state_restoration:
  enabled: true
  scope:
    - "各タブのNavigation path"
    - "スクロール位置（オプション）"

  reconstruction:
    strategy: "pathからViewを再構築"
    validation: "データ存在確認後に復元"

  back_button_behavior:
    from_deep_link: "親階層を補完してpop可能にする"
    example: "ProductDetail直接表示 → back で ProductList へ"
```

### 品質ゲート
- [ ] 直リンクで入っても"現在地"が説明可能
- [ ] 戻り方が破綻しない（親階層の補完）
- [ ] 全ルートが定義済み

### 典型質問
- 「通知タップでどの画面に入る？」
- 「deep linkで直接詳細に入った時、戻るボタンはどこへ行く？」
- 「未ログイン時にdeep linkが来たら？」
