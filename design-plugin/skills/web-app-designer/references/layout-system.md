# レイアウト・視覚設計リファレンス

レイアウトシステム、カラー、タイポグラフィ、コンポーネント状態、アクセシビリティの参照情報。

---

## グリッドシステム

### 12カラムグリッド

12は2, 3, 4, 6で割り切れるため柔軟なレイアウトが可能。

| 設定 | 推奨値 |
|------|--------|
| コンテナ幅 | 1200px〜1440px |
| ガター（溝） | 16px〜32px（8pxの倍数） |
| カラム配分 | 1/12単位 |

**典型的なレイアウトパターン**:

| パターン | カラム配分 | 用途 |
|----------|-----------|------|
| フルワイド | 12 | ヒーローセクション、LP |
| メイン + サイド | 8 + 4 | ブログ、設定画面 |
| 3分割 | 2 + 8 + 2 | 管理画面（ナビ + メイン + パネル） |
| 2カラム | 6 + 6 | 比較、サインアップ |
| 3カラム | 4 + 4 + 4 | カードグリッド |
| 4カラム | 3 + 3 + 3 + 3 | ダッシュボードKPI |

**CSS実装**:
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### 8pxグリッド（8-point Grid）

すべてのスペーシングとサイジングを8pxの倍数で統一するシステム。

**スペーシングスケール**:

| トークン | 値 | 用途 |
|----------|-----|------|
| space-0.5 | 4px | 微調整用（補助単位） |
| space-1 | 8px | アイコンとテキストの間隔 |
| space-2 | 16px | コンポーネント内パディング |
| space-3 | 24px | カード内パディング |
| space-4 | 32px | セクション間マージン |
| space-6 | 48px | 大セクション間 |
| space-8 | 64px | ページセクション間 |
| space-12 | 96px | ヒーロー・フッター前 |

**適用ルール**:
- コンポーネント内パディング: 8px, 12px, 16px
- コンポーネント間マージン: 16px, 24px, 32px
- タッチターゲット間の最低間隔: 8px以上

### CSS Grid / Flexbox 使い分け

| 基準 | CSS Grid | Flexbox |
|------|----------|---------|
| 方向 | 2次元（行と列の同時制御） | 1次元（行または列の一方向） |
| 設計起点 | レイアウト（外側）から | コンテンツ（内側）から |
| 適用対象 | ページ全体構造、カードグリッド | ナビゲーション、アイテム配置 |
| 基本方針 | ページ構造 = Grid | コンポーネント内部 = Flexbox |

**ページレイアウトの例**:
```css
.app-layout {
  display: grid;
  grid-template-areas:
    "nav header"
    "nav main"
    "nav footer";
  grid-template-columns: 240px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}
```

**コンポーネント内部の例**:
```css
.nav-items {
  display: flex;
  gap: 8px;
  align-items: center;
}
```

---

## ブレークポイント一覧表

### 推奨ブレークポイント（モバイルファースト）

| 名前 | min-width | 対象デバイス | 典型的な幅 |
|------|-----------|-------------|-----------|
| base | 0px | スマートフォン（ポートレート） | 320px〜480px |
| sm | 640px | スマートフォン（ランドスケープ） | 481px〜767px |
| md | 768px | タブレット | 768px〜1023px |
| lg | 1024px | デスクトップ | 1024px〜1279px |
| xl | 1280px | 大画面デスクトップ | 1280px〜1535px |
| 2xl | 1536px | ワイドスクリーン | 1536px〜 |

**CSS実装（モバイルファースト）**:
```css
/* base: モバイル（デフォルト） */
.container { padding: 16px; }

@media (min-width: 640px) {
  /* sm: スマートフォン横 */
  .container { padding: 24px; }
}

@media (min-width: 768px) {
  /* md: タブレット */
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  /* lg: デスクトップ */
  .container { max-width: 1024px; }
}

@media (min-width: 1280px) {
  /* xl: 大画面 */
  .container { max-width: 1280px; }
}

@media (min-width: 1536px) {
  /* 2xl: ワイドスクリーン */
  .container { max-width: 1536px; }
}
```

### レスポンシブレイアウトパターン

| ブレークポイント | カラム数 | ナビゲーション | サイドバー |
|----------------|----------|---------------|-----------|
| base (モバイル) | 1 | ハンバーガーメニュー | 非表示（ドロワー） |
| sm | 1 | ハンバーガーメニュー | 非表示 |
| md (タブレット) | 2 | タブバー or ハンバーガー | 折りたたみ（アイコンのみ） |
| lg (デスクトップ) | 3 | 常時表示 | 常時表示 |
| xl+ | 3-4 | 常時表示 | 常時表示（拡張） |

---

## カラー設計

### 60-30-10ルール

| 比率 | 役割 | 適用箇所 | 典型的な色 |
|------|------|----------|-----------|
| 60% | ドミナント（背景・ベース） | 背景色、大面積コンテナ、ホワイトスペース | 白 / ライトグレー |
| 30% | セカンダリ（補助） | カード背景、サイドバー、セクション区切り | ライトグレー / ニュートラル |
| 10% | アクセント（強調） | CTAボタン、リンク、重要通知、ブランドカラー | プライマリカラー |

### セマンティックカラー体系

各カラーに明度スケール（50〜950）を用意する。500がメインカラー。

#### Primary（CTA、リンク、選択状態）

| スケール | HEX | 用途 |
|----------|-----|------|
| 50 | #EFF6FF | 背景ハイライト |
| 100 | #DBEAFE | ホバー背景 |
| 200 | #BFDBFE | アクティブ背景 |
| 300 | #93C5FD | ボーダー |
| 400 | #60A5FA | アイコン |
| 500 | #3B82F6 | メインカラー |
| 600 | #2563EB | ホバー状態 |
| 700 | #1D4ED8 | アクティブ状態 |
| 800 | #1E40AF | テキスト |
| 900 | #1E3A8A | 強調テキスト |
| 950 | #172554 | 最暗 |

#### その他のセマンティックカラー

| セマンティック名 | 500値 | 用途 |
|-----------------|-------|------|
| Secondary | #6366F1 (Indigo) | 二次アクション、アクティブでない選択 |
| Success | #22C55E (Green) | 成功、完了、肯定的な状態 |
| Warning | #F59E0B (Amber) | 注意、警告 |
| Error | #EF4444 (Red) | エラー、削除、破壊的アクション |
| Info | #06B6D4 (Cyan) | 情報提供 |

#### Neutral（テキスト、ボーダー、背景）

| スケール | HEX | 用途 |
|----------|-----|------|
| 50 | #F9FAFB | ページ背景 |
| 100 | #F3F4F6 | カード背景、入力フィールド背景 |
| 200 | #E5E7EB | ボーダー（軽め） |
| 300 | #D1D5DB | ボーダー（標準） |
| 400 | #9CA3AF | プレースホルダテキスト |
| 500 | #6B7280 | 補助テキスト |
| 600 | #4B5563 | セカンダリテキスト |
| 700 | #374151 | テキスト |
| 800 | #1F2937 | 見出し |
| 900 | #111827 | 強調テキスト |
| 950 | #030712 | 最暗 |

### CSS変数定義の例

```css
:root {
  /* Primary */
  --color-primary-50: #EFF6FF;
  --color-primary-500: #3B82F6;
  --color-primary-700: #1D4ED8;

  /* Semantic */
  --color-success-500: #22C55E;
  --color-warning-500: #F59E0B;
  --color-error-500: #EF4444;
  --color-info-500: #06B6D4;

  /* Neutral */
  --color-neutral-50: #F9FAFB;
  --color-neutral-100: #F3F4F6;
  --color-neutral-300: #D1D5DB;
  --color-neutral-500: #6B7280;
  --color-neutral-700: #374151;
  --color-neutral-900: #111827;
}
```

---

## タイポグラフィスケール

### 比率別スケール

ベースサイズ: 16px（1rem）

#### Major Third（1.25倍）— 一般的なWebアプリに最適

| トークン | rem | px | 用途 |
|----------|-----|-----|------|
| text-xs | 0.8rem | 12.8px | キャプション、注釈 |
| text-sm | 0.889rem | 14.2px | 補助テキスト、ラベル |
| text-base | 1rem | 16px | 本文 |
| text-lg | 1.25rem | 20px | サブ見出し |
| text-xl | 1.563rem | 25px | セクション見出し |
| text-2xl | 1.953rem | 31.25px | ページ見出し |
| text-3xl | 2.441rem | 39.06px | ヒーロー見出し |

#### Perfect Fourth（1.333倍）— 見出しの存在感を出したい時

| トークン | rem | px |
|----------|-----|-----|
| text-xs | 0.75rem | 12px |
| text-sm | 0.875rem | 14px |
| text-base | 1rem | 16px |
| text-lg | 1.333rem | 21.33px |
| text-xl | 1.777rem | 28.43px |
| text-2xl | 2.369rem | 37.9px |
| text-3xl | 3.157rem | 50.52px |

#### 選択基準

| スケール | 比率 | 適した場面 |
|----------|------|-----------|
| Minor Third | 1.2 | 情報密度の高いUI、ダッシュボード |
| Major Third | 1.25 | 一般的なWebアプリ（推奨デフォルト） |
| Perfect Fourth | 1.333 | 見出しの存在感が必要な場面 |
| Augmented Fourth | 1.414 | LP、マーケティングサイト |

### 行間・字間設計

| 要素 | line-height | letter-spacing | 備考 |
|------|-------------|---------------|------|
| 本文テキスト | 1.5〜1.75 | 0〜0.01em | WCAGでは1.5以上を推奨 |
| 見出し（大） | 1.1〜1.3 | -0.01〜-0.02em | 大きいフォントは狭い行間でOK |
| UIラベル・ボタン | 1.0〜1.25 | 0em | コンパクトに |
| キャプション（小） | 1.5 | 0.02〜0.05em | 小サイズは広いトラッキングで可読性向上 |
| オールキャップス | — | 0.05〜0.1em | 大文字のみの場合は必ず広げる |

**段落幅**: 最適な読みやすさは1行あたり45〜75文字（`max-width: 65ch` が目安）

### CSS変数定義の例

```css
:root {
  /* Font Family */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Size (Major Third) */
  --text-xs: 0.8rem;
  --text-sm: 0.889rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.563rem;
  --text-2xl: 1.953rem;
  --text-3xl: 2.441rem;

  /* Line Height */
  --leading-none: 1;
  --leading-tight: 1.15;
  --leading-snug: 1.3;
  --leading-normal: 1.6;
  --leading-relaxed: 1.75;

  /* Letter Spacing */
  --tracking-tighter: -0.02em;
  --tracking-tight: -0.01em;
  --tracking-normal: 0em;
  --tracking-wide: 0.01em;
  --tracking-wider: 0.03em;
  --tracking-widest: 0.08em;
}
```

---

## コンポーネント状態設計

### 基本6状態

すべてのインタラクティブコンポーネントが持つべき状態。

| 状態 | 視覚表現 | CSS実装 | 備考 |
|------|----------|---------|------|
| Idle（デフォルト） | 通常の見た目 | 基本スタイル | 最初に定義する |
| Hover | 背景色変化、カーソル変更 | `:hover` | タッチデバイスでは不要 |
| Active/Pressed | 押し込み表現 | `:active` | scale(0.98) や shadow変化 |
| Focused | アウトライン表示 | `:focus-visible` | `outline: 3px solid #0066CC; outline-offset: 2px` |
| Disabled | グレーアウト | `[disabled]`, `[aria-disabled="true"]` | `opacity: 0.5; pointer-events: none` |
| Loading | スピナー / スケルトン | カスタムクラス | テキストを残しつつスピナーを表示 |

### 追加状態

| 状態 | 視覚表現 | 用途 |
|------|----------|------|
| Error | 赤枠 + エラーメッセージ | フォームバリデーション失敗 |
| Success | 緑チェック | 操作完了の確認 |
| Skeleton | プレースホルダ表示 | 初期ロード時のコンテンツ占有 |
| Selected | ハイライト背景 | リスト項目の選択 |
| Dragging | シャドウ + 半透明 | ドラッグ&ドロップ中 |

### 状態遷移パターン

```
フォーム送信ボタンの例:

  idle → (hover) → (click) → loading → success
                                     ↘ error → idle
```

### アニメーション指針

| カテゴリ | デュレーション | イージング |
|----------|---------------|-----------|
| ボタンフィードバック | 16ms以内に開始 | — |
| マイクロインタラクション | 100〜200ms | ease-in-out |
| UI遷移（モーダル等） | 200〜300ms | ease-out（表示）/ ease-in（非表示） |
| ナビゲーション遷移 | 300〜500ms | ease-in-out |

**原則**: 300ms以下で応答性を維持する。`linear` は避ける（機械的に見える）。

```css
/* モーダル表示 */
.modal-enter { animation: slideUp 250ms ease-out; }
/* モーダル非表示 */
.modal-exit { animation: slideDown 200ms ease-in; }

/* prefers-reduced-motionの尊重 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## WCAG 2.1 AA チェックリスト

### コントラスト

| 対象 | 最低コントラスト比 |
|------|-------------------|
| 通常テキスト（<18px太字, <24px） | 4.5:1 |
| 大テキスト（≥18px太字 or ≥24px） | 3:1 |
| UIコンポーネント・グラフィックス | 3:1 |
| フォーカスインジケーター | 3:1 |

### キーボードナビゲーション

| チェック項目 | 基準 |
|-------------|------|
| すべての機能がキーボードで操作可能 | Tab, Enter, Space, Esc, 矢印キーで操作 |
| フォーカス順序が論理的 | DOM順序と視覚的順序が一致 |
| フォーカスインジケーターが見える | `outline: 3px solid #0066CC; outline-offset: 2px` |
| フォーカストラップ | モーダル内でTabがループ、Escで閉じる |
| スキップリンク | メインコンテンツへのスキップリンクを提供 |

### セマンティックHTML

| 要素 | 用途 |
|------|------|
| `<header>` | ページまたはセクションのヘッダー |
| `<nav>` | ナビゲーションリンクのグループ |
| `<main>` | ページの主要コンテンツ（1ページに1つ） |
| `<aside>` | サイドバー、補助コンテンツ |
| `<footer>` | ページまたはセクションのフッター |
| `<section>` | テーマ的に関連するコンテンツのグループ |
| `<article>` | 独立したコンテンツ |
| `<h1>`〜`<h6>` | 見出し階層（レベルを飛ばさない） |

### ARIA属性

| 属性 | 用途 | 例 |
|------|------|-----|
| `aria-label` | 可視テキストがない要素のラベル | `<button aria-label="メニューを閉じる">` |
| `aria-describedby` | 補足説明の関連付け | `<input aria-describedby="email-hint">` |
| `aria-expanded` | 展開/折りたたみ状態 | `<button aria-expanded="false">` |
| `aria-hidden` | 支援技術から隠す | `<span aria-hidden="true">` |
| `aria-live` | 動的に更新される領域 | `<div aria-live="polite">` |
| `role` | セマンティックHTMLが使えない時の代替 | `<div role="alert">` |

**原則**: セマンティックHTMLを優先し、ARIAは補助的に使用する。「ARIAなし > 間違ったARIA」。

### フォーム

| チェック項目 | 実装 |
|-------------|------|
| ラベルと入力の関連付け | `<label for="email">` + `<input id="email">` |
| 必須フィールドの明示 | `aria-required="true"` + 視覚的な「*」マーク |
| エラーメッセージの具体性 | 「入力エラー」ではなく「メールアドレスの形式が正しくありません」 |
| エラーの関連付け | `aria-describedby` でエラーメッセージと入力を接続 |
| 入力補助 | プレースホルダーだけでなく常時表示のラベルを使用 |

### 画像・メディア

| チェック項目 | 基準 |
|-------------|------|
| 意味のある画像 | `alt` テキストで内容を説明 |
| 装飾画像 | `alt=""` または CSS背景 |
| 複雑な画像 | `aria-describedby` で詳細説明を提供 |
| 動画 | キャプション（字幕）の提供 |
| 自動再生 | 5秒以上の自動再生は停止手段を提供 |

### 動きとアニメーション

| チェック項目 | 基準 |
|-------------|------|
| `prefers-reduced-motion` | アニメーションを無効化するメディアクエリを実装 |
| 点滅コンテンツ | 1秒に3回以上の点滅を禁止 |
| 自動スクロール | 停止手段を提供 |
