# モバイルコンポーネント・パターン参照

## コンポーネント比較表

| 共通概念 | iOS（SwiftUI） | Android（Compose） | 備考 |
|----------|---------------|-------------------|------|
| ボタン（Primary） | `.buttonStyle(.borderedProminent)` | `Button` (Filled) | 最重要アクション |
| ボタン（Secondary） | `.buttonStyle(.bordered)` | `OutlinedButton` | 代替アクション |
| ボタン（Tertiary） | `.buttonStyle(.borderless)` | `TextButton` | 低優先度 |
| FAB | - | `FloatingActionButton` | Android固有 |
| テキスト入力 | `TextField` | `OutlinedTextField` / `FilledTextField` | - |
| パスワード入力 | `SecureField` | `OutlinedTextField` + `visualTransformation` | - |
| トグル | `Toggle` | `Switch` | - |
| チェックボックス | - (Toggleで代替) | `Checkbox` | - |
| スライダー | `Slider` | `Slider` | - |
| ピッカー | `Picker` | `DropdownMenu` / `ExposedDropdownMenuBox` | - |
| リスト | `List` | `LazyColumn` | - |
| グリッド | `LazyVGrid` / `LazyHGrid` | `LazyVerticalGrid` | - |
| カード | GroupedListスタイル | `Card` / `ElevatedCard` / `OutlinedCard` | - |
| Bottom Sheet | `.sheet` + `.presentationDetents` | `ModalBottomSheet` | - |
| ダイアログ | `Alert` / `.confirmationDialog` | `AlertDialog` | - |
| Snackbar | - (カスタム実装) | `Snackbar` | Android標準 |
| Toast | - | `Toast` (レガシー) | 非推奨（Snackbar推奨） |
| Action Sheet | `.confirmationDialog` | - (Dialogで代替) | iOS標準 |
| ナビゲーションバー | `NavigationStack` + `.navigationTitle` | `TopAppBar` / `CenterAlignedTopAppBar` | - |
| タブバー | `TabView` | `NavigationBar` (M3) | - |
| Navigation Rail | - | `NavigationRail` | 大画面用 |
| Sidebar | `NavigationSplitView` | `NavigationDrawer` | - |
| プログレス | `ProgressView` | `CircularProgressIndicator` / `LinearProgressIndicator` | - |
| セグメント | `Picker` (.segmented) | `SingleChoiceSegmentedButtonRow` | - |
| チップ | - (カスタム) | `FilterChip` / `AssistChip` / `InputChip` / `SuggestionChip` | M3標準 |

---

## ボタン階層のプラットフォーム別仕様

### Primary（Filled）

| 属性 | iOS | Android（M3） |
|------|-----|--------------|
| 外観 | 塗りつぶし、角丸 | 塗りつぶし、角丸20dp |
| 高さ | 44pt推奨 | 40dp（タッチターゲット48dp） |
| パディング | 水平16pt / 垂直12pt | 水平24dp / 垂直0dp |
| フォント | SF Pro Text 17pt (Body) | Roboto Medium 14sp (Label Large) |
| 用途 | 画面の最重要アクション。1画面に1つ推奨 | 同左 |

### Secondary（Outlined）

| 属性 | iOS | Android（M3） |
|------|-----|--------------|
| 外観 | ボーダー、透明背景 | 1dpボーダー、透明背景、角丸20dp |
| 高さ | 44pt推奨 | 40dp（タッチターゲット48dp） |
| 用途 | Primaryの代替アクション。Primaryより控えめ | 同左 |

### Tertiary（Text）

| 属性 | iOS | Android（M3） |
|------|-----|--------------|
| 外観 | テキストのみ | テキストのみ |
| 高さ | 44pt推奨 | 40dp（タッチターゲット48dp） |
| 用途 | 低優先度アクション | 同左 |

### FAB（Floating Action Button）- Android固有

| サイズ | 寸法 | 用途 |
|--------|------|------|
| Small FAB | 40dp | 補助的フローティングアクション |
| 通常FAB | 56dp | 標準フローティングアクション |
| Large FAB | 96dp | 強調されたフローティングアクション |
| Extended FAB | 高さ56dp + テキスト | テキスト付きフローティングアクション |

**配置原則**:
- 画面右下が標準位置
- Snackbarの上に表示（重ならないよう配慮）
- スクロール時の挙動（表示/非表示/縮小）を設計する

---

## フォーム・入力フィールドのプラットフォーム別設計

### テキスト入力

| 属性 | iOS（TextField） | Android（OutlinedTextField） |
|------|-----------------|---------------------------|
| ラベル | placeholder（入力時に消える） | ラベルが上部に浮く（フローティングラベル） |
| ボーダー | 下線 or 角丸枠（スタイルによる） | アウトラインボーダー |
| エラー表示 | 赤テキスト + 赤ボーダー | supportingText + isError |
| ヘルパーテキスト | カスタム実装 | supportingText |
| 文字数カウンター | カスタム実装 | supportingText（右寄せ） |
| クリアボタン | `.textFieldStyle(.roundedBorder)` + overlay | trailingIcon |

### キーボードタイプ指定

| 入力内容 | iOS | Android |
|----------|-----|---------|
| メールアドレス | `.keyboardType(.emailAddress)` | `KeyboardType.Email` |
| 電話番号 | `.keyboardType(.phonePad)` | `KeyboardType.Phone` |
| 数値 | `.keyboardType(.numberPad)` | `KeyboardType.Number` |
| URL | `.keyboardType(.URL)` | `KeyboardType.Uri` |
| パスワード | `SecureField` | `KeyboardType.Password` + `visualTransformation` |

### フォーム設計原則

1. ラベルは常時表示（placeholder のみに依存しない）
2. エラーメッセージはフィールド直下に即時表示
3. 必須フィールドを明示
4. フィールド間の論理的グループ化
5. 適切なキーボードタイプ・自動補完の設定
6. 送信ボタンはフォーム末尾に配置

---

## モーションパターン

### iOS Spring Animation

SwiftUIのデフォルトアニメーション。物理的なバネの動きを模倣。

| パラメータ | 説明 | 典型値 |
|-----------|------|--------|
| response | アニメーション周期（秒） | 0.3〜0.6 |
| dampingFraction | 減衰率（0=永続振動、1=臨界減衰） | 0.7〜0.9 |
| blendDuration | ブレンド期間 | 0 |

**Easing関数**:

| タイプ | 用途 |
|--------|------|
| easeIn | 開始がゆっくり（退出アニメーション） |
| easeOut | 終了がゆっくり（進入アニメーション） |
| easeInOut | 開始・終了がゆっくり（汎用） |
| linear | 等速（プログレスバー等） |

### Android Material Motion 4パターン

#### 1. Container Transform

2つのUI要素間の視覚的接続。要素をシームレスに変形。

| 属性 | 値 |
|------|-----|
| 用途 | リストアイテム→詳細画面、FAB→画面展開 |
| 構成 | 背景コンテナ + 開始ビューコンテナ + 終了ビューコンテナ |
| 動作 | サイズ・位置・形状が滑らかに変形 |

#### 2. Shared Axis

空間的・ナビゲーション的関係を持つ要素間の遷移。

| 属性 | 値 |
|------|-----|
| 用途 | タブ切替、ステップフォーム、ページング |
| 軸 | X軸（水平）/ Y軸（垂直）/ Z軸（前後） |
| 移動量 | 30dp |
| Duration | 300ms |

#### 3. Fade Through

関係性の弱い要素間の遷移。

| 属性 | 値 |
|------|-----|
| 用途 | Bottom Navigation間の画面切替 |
| 動作 | 順次フェードアウト → フェードイン + スケール |

#### 4. Fade

シンプルなフェード遷移。

| 属性 | 値 |
|------|-----|
| 用途 | ツールバーアイコンの出入り、ダイアログの表示/非表示 |
| 動作 | 不透明度の変化 |

### Motion System（Duration & Easing）

| パターン | Duration | Easing | モーションパス |
|----------|----------|--------|--------------|
| シンプル＆機能的 | 短い | Standard easing | リニア |
| ドラマチック＆強調 | 長い | Emphasized easing | アークモーション |

---

## オフライン状態・Empty State・エラー状態パターン

### スケルトンスクリーン

ページの最終UIの簡略版を表示し、読み込み中であることを示す。

**表示順序**:
1. コンテナベースコンポーネントのスケルトン
2. テキストのスケルトン（幅はランダムに変化させリアル感を出す）
3. 画像・インタラクティブ要素のスケルトン

**設計原則**:
- スピナーや空白よりも体感待ち時間が改善される
- 最終UIに近い形状を使用
- アニメーション（パルス/シマー）で読み込み中であることを伝える

### プログレッシブローディング

| バッチ | 内容 |
|--------|------|
| 第1バッチ | ページ基本構造（スケルトン）+ データベーステキスト + 非データテキスト |
| 第2バッチ | 画像 |
| 第3バッチ | ビューポート外コンテンツ |
| 第4バッチ | インタラクティブコンポーネント + 残りのデータ |

### オプティミスティックUI

- 操作成功を仮定し、期待結果を即座に表示
- 失敗時はエレガントにロールバック + エラーメッセージ
- 適用例: いいね、ブックマーク、コメント投稿、設定変更

### Empty State パターン

```
┌─────────────────────────┐
│                         │
│      [イラスト/         │
│       アイコン]          │
│                         │
│   まだ○○がありません    │
│                         │
│  ○○を追加すると        │
│  ここに表示されます      │
│                         │
│  ┌─────────────────┐   │
│  │  ○○を追加する    │   │
│  └─────────────────┘   │
│                         │
└─────────────────────────┘
```

**構成要素**:
1. イラストまたはアイコン（状況を視覚的に伝える）
2. メインメッセージ（現在の状態を説明）
3. サブメッセージ（次のアクションを提案）
4. CTAボタン（具体的なアクションへ誘導）

### エラー状態パターン

| エラー種別 | 表示方法 | アクション |
|-----------|---------|-----------|
| ネットワークエラー | フルスクリーン or Snackbar | リトライボタン |
| サーバーエラー | フルスクリーン | リトライボタン + サポート連絡 |
| 入力エラー | フィールド直下にインライン表示 | エラー箇所ハイライト |
| 権限エラー | ダイアログ | 設定画面へ遷移 |
| タイムアウト | Snackbar | リトライボタン |

---

## プッシュ通知設計のベストプラクティス

### プラットフォーム差異

| 項目 | iOS | Android |
|------|-----|---------|
| 許可モデル | 明示的opt-in（常に必要） | 自動許可（Android 12以前）/ 明示的許可（Android 13+） |
| 平均opt-in率 | 43.9% | 81.5% |

### パーミッションリクエスト設計

**タイミング**: 初回起動時ではなく、4〜6回目のセッション後が推奨

**Pre-permission Prompt（推奨パターン）**:

```
┌─────────────────────────┐
│                         │
│   お気に入りの商品が     │
│   セールになった時に     │
│   お知らせしますか？     │
│                         │
│  ┌─────┐  ┌──────────┐ │
│  │後で  │  │お知らせする│ │
│  └─────┘  └──────────┘ │
│                         │
└─────────────────────────┘
```

1. ユーザーが価値を実感した後にリクエスト
2. 送信予定の通知内容を具体的に説明
3. ユーザーが「後で」を選べるようにする（拒否≠永久拒否）
4. アプリ設定内で通知のオン/オフ切替を提供

### 通知内容の設計原則

| 原則 | 説明 |
|------|------|
| パーソナライゼーション | パーソナライズされた通知は259%高いエンゲージメント率 |
| 価値提供 | 価格変動、新機能、個人的マイルストーン等の明確で価値ある内容 |
| 頻度管理 | 過度な通知を避け、ユーザーが管理できる仕組みを提供 |
| 適切なタイミング | ユーザーのタイムゾーン・行動パターンを考慮 |
