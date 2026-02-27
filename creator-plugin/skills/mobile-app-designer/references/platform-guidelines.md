# プラットフォームガイドライン参照

## Apple Human Interface Guidelines（HIG）

### 主要原則（2025年版）

| 原則 | 説明 |
|------|------|
| Clarity（明瞭さ） | テキストは読みやすく、アイコンは正確で明快、装飾は適切で機能に沿う |
| Deference（控えめさ） | UIはコンテンツの理解を助け、競合しない。流動的なモーションでコンテンツを引き立てる |
| Depth（奥行き） | 視覚的な階層と現実的なモーションが理解を促し、コンテンツとの関わり方を伝える |
| Consistency（一貫性） | システムUIコンポーネントとアイコンの一貫した使用、予測可能なインタラクション |

### Liquid Glass（iOS 26〜）

iOS 26 / iPadOS 26 / macOS Tahoe 26 / watchOS 26 / tvOS 26に統一展開される新デザイン言語。

**特徴**:
- 半透明のガラス素材を模したUI。光を反射・屈折し、背景コンテンツに動的に反応
- Tab Bar、Sidebar、コントロール、ウィジェット、アプリアイコンすべてに適用
- コンテンツとコントロールの階層を明確にし、環境に自動適応

**設計時の考慮点**:
- 背景コンテンツが変化してもUI要素の視認性を確保する
- 光の反射・屈折によるアニメーションが加わるため、Reduce Motion対応を考慮する
- iOS 26未満をサポートする場合は従来のUIとの分岐が必要

### SF Symbols

数千の一貫したシンボルアイコンセット。

| 属性 | 仕様 |
|------|------|
| フォント整合 | San Franciscoシステムフォントと自動整列 |
| ウェイト | 9段階（ultralight / thin / light / regular / medium / semibold / bold / heavy / black） |
| スケール | 3段階（small / medium / large） |
| Dynamic Type連動 | テキストサイズ設定に応じて自動スケーリング |

### Dynamic Type

| フォント | 適用範囲 |
|----------|---------|
| SF Pro Text | 19pt以下 |
| SF Pro Display | 20pt以上 |

- ユーザーが制御可能なテキストサイズスケーリング
- Bold Text設定への対応も必要
- すべてのテキスト要素がDynamic Typeに対応し、コンテンツ欠損なくスケーリングすること

---

## Material Design 3（M3）

### 主要原則

| 原則 | 説明 |
|------|------|
| Adaptive（適応型） | 画面サイズ・入力方法・コンテキストに適応するUI |
| Accessible（アクセシブル） | すべてのユーザーが使えるインクルーシブなデザイン |
| Personal（個人化） | Dynamic Colorでユーザーの好みに適応 |

### Dynamic Color（Material You）

Android 12+で利用可能。ユーザーの壁紙からアルゴリズムでカスタムカラーを生成。

| カラーロール | 用途 |
|-------------|------|
| Primary | 主要ボタン、アクティブ状態 |
| Secondary | フィルターチップ等の補助要素 |
| Tertiary | アクセントカラー |
| Surface | 背景、大面積 |
| Container | ボタン等の前景要素の塗りつぶし |
| Outline | 区切り線、ボーダー |
| "On"プレフィックス | 対応する親カラーの上に置くテキスト・アイコン（例: onPrimary） |

- アクセシビリティ基準のコントラストをデフォルトで担保

### M3 Expressive（2025年〜）

| 特徴 | 説明 |
|------|------|
| Variable fonts | 動的カスタマイズ可能なタイポグラフィ |
| リッチカラーパレット | より多彩な色の表現 |
| スプリングアニメーション | 自然な弾みのあるアニメーション |
| シェイプモーフィング | 形状の滑らかな変形 |

---

## ナビゲーションパターン比較表

| 要素 | iOS | Android |
|------|-----|---------|
| **メインナビ** | Tab Bar（画面下部、49pt） | Bottom Navigation（コンテナ56dp） |
| **アイコン** | SF Symbols | Material Icons |
| **項目数** | 3〜5 | 3〜5 |
| **タブ切替時** | 前回位置を保持 | スクリーン状態をリセット |
| **階層遷移** | Navigation Stack + スワイプバック | Top App Bar + システムバック |
| **モーダル** | Bottom Sheet（Detent: medium/large/custom） | Bottom Sheet / Dialog |
| **サイドメニュー** | Sidebar（iPad向けSplit View） | Navigation Drawer（スライドイン） |
| **大画面** | Sidebar + Split View | Navigation Rail（画面左端縦型） |
| **スワイプバック** | 画面左端からの右スワイプ | システムジェスチャー（Android 10+） |

---

## 単位系比較

### iOS単位系

| 単位 | 説明 | 対応 |
|------|------|------|
| pt（ポイント） | 抽象的な測定単位 | 160dpi画面で1pt = 1px |
| @1x | 1pt = 1px | レガシーデバイス |
| @2x | 1pt = 2px | Retina Display（iPhone SE/6/7/8等） |
| @3x | 1pt = 3px | Super Retina（iPhone 12〜16 Pro等） |

アセットは@1x、@2x、@3xの3サイズで書き出し。

### Android単位系

| 単位 | 説明 | 対応 |
|------|------|------|
| dp | density-independent pixel | 160dpi画面で1dp = 1px |
| sp | scale-independent pixel（テキスト専用） | dpと同サイズ + ユーザーフォント設定でスケール |

| 密度バケット | DPI | dpとの比率 |
|-------------|-----|-----------|
| mdpi | 160 | 1dp = 1px |
| hdpi | 240 | 1dp = 1.5px |
| xhdpi | 320 | 1dp = 2px |
| xxhdpi | 480 | 1dp = 3px |
| xxxhdpi | 640 | 1dp = 4px |

### iOS / Android 単位対応表

| iOS | Android | 備考 |
|-----|---------|------|
| 1pt | ≈ 1dp | 論理的にほぼ同等（ともに160dpiベース） |
| @2x | xhdpi | ともに320dpi |
| @3x | xxhdpi | iOS 3px/pt ≈ Android 3px/dp |
| - | sp | iOS相当はDynamic Typeで制御 |

---

## タッチターゲットサイズ基準

| 基準 | 最小サイズ | 備考 |
|------|-----------|------|
| Apple HIG | 44×44pt | これ以下だと25%以上のユーザーが誤タップ |
| Material Design | 48×48dp | 7mm以上を保証。要素間スペース最低8dp |
| WCAG | 最低24×24 CSS px / 推奨44×44 CSS px | Web基準だがモバイルにも参考 |

---

## Safe Area / WindowInsets対応

### iOS Safe Area

| 項目 | 説明 |
|------|------|
| 定義 | ステータスバー、ナビゲーションバー、タブバー、Dynamic Island、ホームインジケーターに遮られない画面領域 |
| Top目安 | 44-47pt（デバイスにより異なる） |
| Bottom目安 | 34pt（ホームインジケーター領域） |
| SwiftUI動作 | デフォルトでSafe Area内に配置 |
| 拡張 | `safeAreaInset(edge:alignment:spacing:content:)` で追加コンテンツ挿入可能 |
| 注意 | 回転やステータスバー変更で実行時にインセット値が変化 |

### Android WindowInsets

| WindowInsets種別 | 説明 |
|-----------------|------|
| `WindowInsets.safeDrawing` | システムUIと重ならない描画領域 |
| `WindowInsets.safeGestures` | ジェスチャーと競合しない領域 |
| `WindowInsets.safeContent` | safeDrawing + safeGesturesの組み合わせ |

**Edge-to-Edge対応**:
- ステータスバー・ナビゲーションバーを透明/半透明にし、背面にコンテンツを描画
- `WindowInsetsCompat.getDisplayCutout()` でカットアウト領域を取得
- カットアウト領域にインタラクティブ要素を配置しない（タッチ感度が低い）

---

## アクセシビリティ基準

### プラットフォーム別対応

| 機能 | iOS | Android |
|------|-----|---------|
| スクリーンリーダー | VoiceOver | TalkBack |
| ラベル設定 | accessibilityLabel / accessibilityHint / accessibilityTraits | contentDescription |
| テキストスケーリング | Dynamic Type（SF Pro連動） | Font Scale（sp単位で自動対応） |
| 太字テキスト | Bold Text設定対応 | - |
| モーション抑制 | 「視差効果を減らす」設定 | 「アニメーションを無効にする」設定 |
| モーション検出 | `@Environment(\.accessibilityReduceMotion)` | `Settings.Global.ANIMATOR_DURATION_SCALE` |
| ダークモード | ライト/ダークモード両対応 | ライト/ダークテーマ両対応 |
| 高コントラスト | - | 高コントラストテーマ対応 |
| 外部デバイス | - | Switch Access対応 |

### カラーコントラスト基準（WCAG）

| レベル | 通常テキスト | 大テキスト |
|--------|------------|-----------|
| AA（必須） | 4.5:1以上 | 3:1以上 |
| AAA（推奨） | 7:1以上 | 4.5:1以上 |

### テスト必須項目

1. VoiceOver / TalkBack での全画面操作確認
2. Dynamic Type / Font Scale 最大設定でのレイアウト確認
3. 高コントラストモードでの表示確認
4. 色のみに依存しない情報伝達の確認
5. タッチターゲットサイズの計測
