# UIインベントリ収集リファレンス

既存UIの棚卸しを手動または自動（MCP連携）で行う方法。

## 目次

- [収集対象](#収集対象)
- [手動アプローチ](#手動アプローチ)
- [自動化アプローチ（MCP連携）](#自動化アプローチmcp連携)
- [不一致検出](#不一致検出)
- [Design Tokens候補の抽出](#design-tokens候補の抽出)
- [限界と注意点](#限界と注意点)

---

## 収集対象

### UI要素カテゴリ

| カテゴリ | 要素例 |
|----------|--------|
| インタラクティブ | Button, Input, Select, Checkbox, Toggle, Link |
| ナビゲーション | Header, Sidebar, Breadcrumb, Tab, Pagination |
| フィードバック | Toast, Modal, Tooltip, Badge, Alert |
| データ表示 | Table, Card, List, Avatar, Chart |
| レイアウト | Grid, Container, Divider, Spacer |

### 収集するプロパティ

```
color, background-color, border-color,
font-size, font-family, font-weight, line-height, letter-spacing,
border-radius,
padding-top, padding-right, padding-bottom, padding-left,
margin-top, margin-right, margin-bottom, margin-left, gap
```

### 状態行列

各要素について以下の状態を収集:

```
default / hover / focus / active / disabled / error / loading
```

---

## 手動アプローチ

### ステップ

1. **画面リスト作成**: routes/sitemap/Storybookから対象URLリストを作る
2. **スクリーンショット収集**: 各画面をキャプチャ
3. **要素分類**: カテゴリ（ボタン/フォーム/カード等）ごとにグルーピング
4. **不一致マーク**: 同じ意図の要素でスタイルが異なるものを印付け
5. **スプレッドシート化**: 要素名・画面・スタイル値を表形式で整理

### 手動の強み

- 意図・文脈を判断できる（同じ見た目でも意味が異なるケースを識別）
- 状態の網羅性を人間の判断で補える
- ツール不要で即開始可能

---

## 自動化アプローチ（MCP連携）

### ツールの役割

| MCP | 取得できるもの | 用途 |
|-----|-------------|------|
| Playwright MCP | スクリーンショット、DOM操作、状態再現 | 画面キャプチャ + 状態別UI撮影 |
| Chrome DevTools MCP (CDP) | computed style、DOM構造 | CSSプロパティの定量抽出 |
| Mobile MCP | UI階層XML/JSON | モバイルアプリのUI要素取得 |

### 推奨ワークフロー

```
1. 画面集合を固定
   routes/sitemap/Storybookから対象URL・画面IDリストを作成

2. 状態行列を定義
   default / hover / focus / active / disabled / error / loading
   → Playwrightで各状態を強制再現

3. 証跡を二重取得
   Playwright  → スクリーンショット（fullPage: true）
   DevTools CDP → CSS.getComputedStyleForNode で各要素のスタイル

4. 共通スキーマへ正規化
   { platform, screen_id, tag, role, className, style }

5. 自動クラスタリング
   同一intent内でスタイル指紋を比較 → 差分を不一致候補に

6. 人間が最終確定
   トークン名・semantic tokenへの割当はレビューで確定
```

### CDP APIの使い方

CSS値の抽出は `CSS.getComputedStyleForNode` を中核にする:

```js
const cdp = await context.newCDPSession(page);
await cdp.send("DOM.enable");
await cdp.send("CSS.enable");

const { root } = await cdp.send("DOM.getDocument", { depth: -1, pierce: true });
const { nodeIds } = await cdp.send("DOM.querySelectorAll", {
  nodeId: root.nodeId,
  selector: 'button,[role="button"],a,input,select,textarea'
});

for (const nodeId of nodeIds) {
  const { computedStyle } = await cdp.send("CSS.getComputedStyleForNode", { nodeId });
  // computedStyle からターゲットプロパティを抽出
}
```

広範囲を高速取得したい場合は `DOMSnapshot.captureSnapshot` も有効。

---

## 不一致検出

### アルゴリズム

1. **intent分類**: role/tag/class/aria属性から要素の意図を判定
   - `button`: role="button", tag=BUTTON, class含む"btn"
   - `input`: tag=INPUT/TEXTAREA, class含む"input"/"field"
   - `link`: tag=A
2. **スタイル指紋**: 主要CSSプロパティを連結した文字列を生成
3. **クラスタ比較**: 同一intent内で指紋が複数パターン → 不一致候補
4. **外れ値検出**: 出現頻度の低い指紋を外れ値として優先表示

### 視覚的補助

CSS値が同一でも見た目が異なるケース（親要素の影響等）を検出するため:
- pHash（知覚ハッシュ）: 要素スクリーンショットのハッシュ比較
- SSIM: 構造的類似度の定量評価

---

## Design Tokens候補の抽出

収集したCSSプロパティの出現頻度を集計し、Global Token候補を生成する。

### 抽出ロジック

1. 全要素のCSSプロパティ値を収集
2. カテゴリ別（色/フォントサイズ/スペーシング）に集計
3. 出現頻度上位を候補としてリスト化
4. 近似値をグルーピング（例: 15px と 16px を統合）
5. W3C DTCG形式で `token-candidates.tokens.json` を出力

### 候補からの確定フロー

```
自動抽出 → 候補リスト提示 → 人間レビュー → 命名確定 → tokens.json
```

命名時の判断:
- Global Token名: 「見た目」ベース（blue-500, font-size-16）
- Semantic Token名: 「用途」ベース（color-primary, text-body）

---

## 限界と注意点

| 限界 | 対策 |
|------|------|
| 自動化は「見えている事実」に強いが「意図」に弱い | 最終確定は必ず人間レビュー |
| 状態再現の漏れ（hover/error等の網羅） | 状態行列を事前に定義し、Playwrightで強制再現 |
| computed styleはコンテキスト依存 | 同じトークンでも親要素の影響で値が変わりうる |
| モバイルは色・フォント情報の制限が多い | 階層取得＋手動補完のハイブリッド |
| 動的コンテンツの収集漏れ | SPA/SSRページは適切なwait条件を設定 |

### 補完ツール

| ツール | 用途 |
|--------|------|
| Style Dictionary | 抽出候補をWeb/iOS/Android用トークンに変換 |
| css-analyzer / cssstats | CSS全体の色・タイポ分布を俯瞰 |
| axe-core | a11y情報（role/name）をintent分類に利用 |
