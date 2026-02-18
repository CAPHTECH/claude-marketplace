---
name: mobile-app-designer
context: fork
description: "iOS/Androidモバイルアプリのデザインを体系的に行うスキル。Apple HIG・Material Design 3などプラットフォームガイドラインに準拠し、ナビゲーション・レイアウト・コンポーネント・モーション・アクセシビリティを適切に設計する。Use when: 「モバイルアプリをデザインして」「iOSアプリのUIを設計して」「Androidアプリの画面を作って」「モバイルのナビゲーションを設計して」「タッチUIを改善して」「アプリのアクセシビリティを対応して」と言われた時。"
---

# Mobile App Designer（モバイルアプリデザイナー）

iOS/Androidモバイルアプリのデザインを、プラットフォームガイドラインに準拠して体系的に行う。

## ワークフロー概要

```
Phase 1: 要件・プラットフォーム確認
    ↓
Phase 2: デザイン手法・ガイドラインの選択
    ↓
Phase 3: デザイン実行
    ↓
Phase 4: アウトプット生成
```

---

## Phase 1: 要件・プラットフォーム確認

ユーザーに以下を確認し、デザインの前提条件を明確化する。

### Step 1.1: プラットフォーム特定

| 確認項目 | 選択肢 | デザインへの影響 |
|----------|--------|-----------------|
| ターゲットOS | iOS / Android / 両方 / クロスプラットフォーム（Flutter/RN） | 適用ガイドライン決定 |
| デバイス種別 | Phone / Tablet / Foldable / 全対応 | レイアウト戦略決定 |
| 最小OSバージョン | iOS 15+ / iOS 16+ / iOS 26+ / Android 12+ / Android 13+ 等 | 利用可能APIと機能範囲 |

### Step 1.2: アプリカテゴリ・目的

- アプリカテゴリ（SNS / EC / ツール / ゲーム / ビジネス / ヘルスケア / 教育 等）
- 主要ユーザーアクション（閲覧中心 / 入力中心 / コミュニケーション中心）
- オフライン利用の必要性

### Step 1.3: 既存デザイン資産の確認

- 既存デザインシステム・ブランドガイドラインの有無
- カラーパレット・タイポグラフィの指定
- 既存アプリからのリデザインか新規か

---

## Phase 2: デザイン手法・ガイドラインの選択

Phase 1の回答に基づき、以下のマトリクスから適用するガイドライン・手法を選定する。

### ガイドライン選定マトリクス

| ユーザーの要求 | 適用ガイドライン | 主要ツール・トークン | 参照 |
|---------------|-----------------|--------------------|----|
| iOSアプリ | Apple HIG | SF Symbols / Dynamic Type / Safe Area | [platform-guidelines.md](references/platform-guidelines.md) |
| Androidアプリ | Material Design 3 | Dynamic Color / Material Icons / WindowInsets | [platform-guidelines.md](references/platform-guidelines.md) |
| iOS 26以降 | Apple HIG + Liquid Glass | 半透明ガラス素材 / 光反射・屈折UI | [platform-guidelines.md](references/platform-guidelines.md) |
| Android（M3 Expressive） | M3 Expressive | Variable fonts / Spring animation / Shape morphing | [platform-guidelines.md](references/platform-guidelines.md) |
| 両OS対応 | 共通UI + OS別UI分離 | 下記の分離判断基準を適用 | [mobile-components.md](references/mobile-components.md) |
| ナビゲーション設計 | iOS: Tab Bar / Android: Bottom Navigation | プラットフォーム別パターン | [mobile-components.md](references/mobile-components.md) |
| モーション設計 | iOS: Spring / Android: Material Motion | プラットフォーム別モーション仕様 | [mobile-components.md](references/mobile-components.md) |
| アクセシビリティ | iOS: VoiceOver+Dynamic Type / Android: TalkBack+Font Scale | WCAG AA基準 | [platform-guidelines.md](references/platform-guidelines.md) |
| タブレット・大画面 | iOS: Sidebar+Split View / Android: Navigation Rail+Canonical Layouts | レスポンシブレイアウト | [platform-guidelines.md](references/platform-guidelines.md) |
| クロスプラットフォーム（Flutter） | 独自レンダリング（Skia） | ピクセルパーフェクトUI / OS慣習との乖離に注意 | - |
| クロスプラットフォーム（React Native） | ネイティブコンポーネント使用 | `.ios.js`/`.android.js`で分岐 | - |

### 両OS対応時の分離判断基準

| UI要素 | 共通化可能 | OS別にすべき |
|--------|-----------|-------------|
| カラーパレット基本定義 | ○ | - |
| タイポグラフィ | - | ○（San Francisco vs Roboto） |
| アイコン | 汎用アイコンのみ | ○（SF Symbols vs Material Icons） |
| ナビゲーション構造 | - | ○（Tab Bar vs Bottom Navigation の挙動差） |
| アニメーション | - | ○（Spring vs Material Motion） |
| レイアウト基本構造 | ○ | - |
| システムUI統合 | - | ○（通知・ウィジェット・共有シート） |
| ジェスチャー | - | ○（スワイプバック等の挙動差） |

---

## Phase 3: デザイン実行

Phase 2で選定した手法に基づき、以下の各領域を設計する。

### Step 3.1: 画面レイアウト設計

**Safe Area / WindowInsets対応**:
- iOS: Safe Area内にコンテンツを配置（Top 44-47pt / Bottom 34pt目安）
- Android: `WindowInsets.safeDrawing`で描画領域を確保、Edge-to-Edge対応
- Display Cutout / Dynamic Island領域にインタラクティブ要素を配置しない

**タッチターゲット**:
- iOS: 最小44×44pt
- Android: 最小48×48dp、要素間スペース最低8dp

**単位系**:
- iOS: pt（@1x/@2x/@3x）でアセット書き出し
- Android: dp（レイアウト）/ sp（テキスト）で指定

**レスポンシブ対応**:
- Phone: シングルカラム、ボトムナビゲーション
- Tablet（iOS）: Sidebar + Split View
- Tablet（Android）: Navigation Rail + Canonical Layouts（list-detail等）
- Foldable: 展開時/折りたたみ時の2レイアウト

### Step 3.2: ナビゲーション設計

プラットフォーム別にナビゲーション構造を設計する。

**iOS**:
1. Tab Bar（3-5項目、画面下部49pt、SF Symbols使用）
2. Navigation Stack（階層遷移、スワイプバック対応）
3. Modal Sheet（Detent: medium/large/custom）
4. Sidebar（iPad向けSplit View）

**Android**:
1. Bottom Navigation（3-5項目、コンテナ高さ56dp、Material Icons使用）
2. Navigation Drawer（多数のデスティネーション対応）
3. Top App Bar（タイトル・ナビ・アクション配置）
4. Navigation Rail（タブレット・大画面用、画面左端）

**挙動の違いに注意**:
- iOS Tab Bar: タブ切替時に前回位置を保持
- Android Bottom Navigation: タブ切替時にスクリーン状態をリセット

### Step 3.3: コンポーネント設計

[references/mobile-components.md](references/mobile-components.md) のコンポーネント比較表を参照し、プラットフォームに適したコンポーネントを選択する。

**ボタン階層の設計**:
1. Primary（Filled）: 画面の最重要アクション。1画面に1つ推奨
2. Secondary（Outlined）: 代替アクション
3. Tertiary（Text）: 低優先度アクション
4. FAB（Android固有）: 画面上の最重要アクション（56dp / 40dp / 96dp / Extended）

**フォーム・入力フィールド**:
- 適切なキーボードタイプを指定（email / phone / number 等）
- ラベルは常時表示
- エラーメッセージは即時表示
- iOS: TextField / SecureField / Picker / Toggle
- Android: OutlinedTextField / FilledTextField / Checkbox / Switch

### Step 3.4: モーション設計

**iOS**:
- Spring Animation（SwiftUIデフォルト）: `response` / `dampingFraction` で制御
- iOS 26 Liquid Glass: 光の反射・屈折に基づく動的アニメーション

**Android Material Motion 4パターン**:
1. Container Transform: 2要素間の視覚的接続（シームレス変形）
2. Shared Axis: 空間的関係を持つ要素間の遷移（X/Y/Z軸共有、30dp/300ms）
3. Fade Through: 関係性の弱い要素間（フェードアウト→フェードイン+スケール）
4. Fade: シンプルなフェード

**Reduce Motion対応**:
- iOS: `@Environment(\.accessibilityReduceMotion)` で検出、Spring→easeInOutに置換
- Android: `Settings.Global.ANIMATOR_DURATION_SCALE` で検出
- 意味を持つモーションはdissolve/fade/色変化で代替（完全除去しない）

### Step 3.5: オフライン・エラー・Empty State設計

3状態すべてを設計すること:

| 状態 | 設計方針 | パターン |
|------|---------|---------|
| ローディング | スケルトンスクリーン（スピナーより体感待ち時間が改善） | コンテナ→テキスト→画像の順で表示 |
| Empty State | 次のアクションを明確に提示 | イラスト + 説明テキスト + CTAボタン |
| エラー | 原因と対処法を分かりやすく提示 | エラーメッセージ + リトライボタン |

**オプティミスティックUI**: 操作が成功すると仮定し期待結果を即座に表示。失敗時はエレガントにロールバック。

**プログレッシブローディング**: ページ基本構造→テキスト→画像→インタラクティブ要素の順。

### Step 3.6: アクセシビリティ対応

**iOS**:
- VoiceOver: 全UI要素にアクセシビリティラベル・ヒント・トレイトを設定
- Dynamic Type: コンテンツ欠損なくスケーリング（SF Symbolsも連動）
- Bold Text対応
- ライト/ダークモード両対応

**Android**:
- TalkBack: `contentDescription` の設定必須
- Font Scale: sp単位使用で自動対応
- 高コントラストモード対応
- Switch Access対応

**共通基準（WCAG）**:
- カラーコントラスト: AA基準（通常テキスト4.5:1以上、大テキスト3:1以上）
- 色のみに依存しない情報伝達
- POUR原則: Perceivable / Operable / Understandable / Robust

---

## Phase 4: アウトプット形式

デザイン結果を以下の形式で出力する。

### 4.1 画面レイアウト仕様

```markdown
## 画面名: [画面名]

- プラットフォーム: iOS / Android
- 画面サイズ: [幅]×[高]pt(dp)
- Safe Area: Top [値] / Bottom [値] / Left [値] / Right [値]
- レイアウトタイプ: シングルカラム / Split View / list-detail

### レイアウト構造
[ASCII図またはセクション説明]

### コンテンツ領域
- ヘッダー: [高さ]pt(dp)
- コンテンツ: スクロール可能 / 固定
- フッター: [高さ]pt(dp) / なし
```

### 4.2 コンポーネント仕様

```markdown
## コンポーネント: [名前]

| 属性 | iOS | Android |
|------|-----|---------|
| SwiftUI/Compose名 | [名前] | [名前] |
| サイズ | [幅]×[高]pt | [幅]×[高]dp |
| タッチターゲット | 44×44pt以上 | 48×48dp以上 |
| 角丸 | [値]pt | [値]dp |
| 状態 | default / pressed / disabled / focused |

### 状態別仕様
- Default: [色・スタイル]
- Pressed: [色・スタイル]
- Disabled: [色・スタイル・opacity]
- Focused: [色・スタイル・ボーダー]
```

### 4.3 ナビゲーション構造図

```markdown
## ナビゲーション構造

### メインナビゲーション
- Tab 1: [名前] → [画面一覧]
- Tab 2: [名前] → [画面一覧]
- Tab 3: [名前] → [画面一覧]

### 画面遷移
[画面A] → push → [画面B] → push → [画面C]
[画面A] → modal → [画面D]（Detent: medium）

### ジェスチャー
- スワイプバック: [画面B] → [画面A]
- スワイプダウン: [画面D] dismiss
```

### 4.4 モーション仕様

```markdown
## モーション: [名前]

| 属性 | iOS | Android |
|------|-----|---------|
| タイプ | Spring / easeInOut | Container Transform / Shared Axis / Fade Through / Fade |
| Duration | [値]s | [値]ms |
| Easing | spring(response:0.5, dampingFraction:0.8) | emphasizedDecelerate |
| Reduce Motion代替 | easeInOut / dissolve | fade / 即時切替 |
```

### 4.5 アクセシビリティチェックリスト

| カテゴリ | チェック項目 | iOS | Android | 状態 |
|----------|------------|-----|---------|------|
| スクリーンリーダー | 全要素にラベル設定 | VoiceOver | TalkBack | ☐ |
| スクリーンリーダー | 操作ヒント設定 | accessibilityHint | contentDescription | ☐ |
| テキストスケーリング | Dynamic Type対応 | Dynamic Type | Font Scale (sp) | ☐ |
| テキストスケーリング | レイアウト崩れなし | 最大カテゴリで確認 | 最大スケールで確認 | ☐ |
| コントラスト | WCAG AA準拠（4.5:1） | 全テキスト | 全テキスト | ☐ |
| タッチターゲット | 最小サイズ準拠 | 44×44pt | 48×48dp | ☐ |
| モーション | Reduce Motion対応 | 視差効果を減らす | アニメーション無効 | ☐ |
| カラー | 色以外でも情報伝達 | - | - | ☐ |
| ダークモード | 両モードで正常表示 | - | - | ☐ |

---

## 注意事項

- プラットフォームガイドラインの最新版を常に参照する。特にiOS 26（Liquid Glass）とM3 Expressive は仕様が進化中のため、公式ドキュメントで確認すること
- 両OS対応時は共通化できる部分とOS別にすべき部分を明確に分離する（Phase 2の分離判断基準参照）
- アクセシビリティは後付けではなく設計初期から組み込む
- タッチターゲットサイズは最低基準であり、重要なアクションにはより大きなサイズを使用する
- オフライン状態・Empty State・エラー状態の3状態は必ず設計する

## 連携スキル

| スキル | 連携タイミング |
|--------|--------------|
| `/app-idea-workshop` | アプリアイデアの具体化・機能定義 |
| `/spec-gen` | デザイン仕様からコード仕様への変換 |
| `/ai-readability-analysis` | 生成コードの可読性検証 |
| `/systematic-test-design` | UIテスト設計 |
