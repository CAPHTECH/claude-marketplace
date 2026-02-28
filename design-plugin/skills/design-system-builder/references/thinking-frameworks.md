# 思考フレームワーク詳細リファレンス

デザインシステム構築に適用する思考フレームワークの詳細と関係性。

## 目次

- [フレームワークの組み合わせ](#フレームワークの組み合わせ)
- [Double Diamond](#double-diamond)
- [Atomic Design](#atomic-design)
- [Design Tokens 3層モデル](#design-tokens-3層モデル)
- [補助フレームワーク](#補助フレームワーク)

---

## フレームワークの組み合わせ

単一フレームワークでは不十分。以下の4軸を重ねるのが最も効果的:

```
問題定義: Double Diamond — 正しい問題を見つけ、正しい解決策を作る
構造化:   Atomic Design  — UIを分解/再構成する共通言語
実装契約: Design Tokens  — デザイン判断をコードに直結させる
判断記録: DDR/QOC/RFC    — 判断の再現性と引き継ぎ性を確保
```

### DS構築フェーズとの対応

| DSフェーズ | Double Diamond | Atomic Design | Design Tokens |
|-----------|---------------|---------------|---------------|
| Phase 1: 発見 | Discover（発散） | — | — |
| Phase 2: 定義 | Define（収束） | — | — |
| Phase 3: 基盤設計 | Develop（発散） | Sub-atomic粒子 | Layer 1-2 定義 |
| Phase 4: コンポーネント | Deliver（収束） | Atoms→Pages | Layer 3 定義 |
| Phase 5: 採用 | — | — | トークン配布 |
| Phase 6: 運用 | — | 階層メンテナンス | トークン更新 |

---

## Double Diamond

英国Design Council（2003年）提唱。発散→収束を2回繰り返す。

```
      Diamond 1              Diamond 2
(正しい問題を見つける)    (正しい解決策を作る)

    ╱  ╲                    ╱  ╲
   ╱    ╲                  ╱    ╲
  ╱      ╲                ╱      ╲
 ╱        ╲              ╱        ╲
Discover  Define       Develop   Deliver
(発散)    (収束)       (発散)    (収束)
```

### DS構築での適用

**Diamond 1（問題側）**: DS構築の「何を」を決める
- Discover: UIインベントリ、課題収集、ステークホルダーインタビュー
- Define: デザイン原則の収束、優先順位の確定、DDR初期記録

**Diamond 2（解決側）**: DS構築の「どう」を決める
- Develop: 複数のトークン設計案を検討、Foundation要素の選定
- Deliver: 最終的なトークン体系の確定、コンポーネント仕様の固定

### 実務上の注意

- 「良い議論」で終わらせない。Deliverの成果物仕様を事前に決める
- Diamond間を行き来する柔軟性を持つ。Phase 3で新たな問題が見つかればPhase 2に戻る

---

## Atomic Design

Brad Frost（2013年）提唱。UIを化学のメタファーで5階層に構成する。

### DS構築における位置づけ

Atomic Designは**厳密な分類体系ではなく思考モデル**として使う（Brad Frost自身が明言）。チームに合わせてラベルやルールを調整してよい。

### 5階層 + Sub-atomic

| 階層 | 定義 | DS構築での役割 |
|------|------|--------------|
| Sub-atomic（Design Tokens） | Atomsより下位の値。単独では機能しない | Foundation定義 |
| Atoms | 最小UI要素 | コンポーネントカタログの最小単位 |
| Molecules | Atomsの組み合わせ | 基本的なUIパターン |
| Organisms | 独立したUIセクション | 再利用可能なUIブロック |
| Templates | ページレイアウト | レイアウトシステム |
| Pages | 実コンテンツ | 検証・テスト |

### 階層判定の基準

迷った場合の判断フロー:

```
これ以上分解できるか？
├── NO → Atom
└── YES → 独立して再利用できるか？
    ├── NO → Molecule
    └── YES → ページ構造を定義しているか？
        ├── YES → Template
        └── NO → Organism
```

### ディレクトリ構造への反映

```
components/
  atoms/       → Button, Input, Icon, Badge, Label
  molecules/   → SearchBar, FormField, NavItem
  organisms/   → Header, Sidebar, DataTable
  templates/   → DashboardLayout, AuthLayout
  pages/       → DashboardPage, SettingsPage
```

---

## Design Tokens 3層モデル

### 層の定義と参照ルール

```
Layer 1: Global Tokens（基盤トークン）
  プラットフォーム非依存の生値。命名は「見た目」で。
  例: blue-500, font-size-16, spacing-4

     ↓ エイリアス参照

Layer 2: Semantic Tokens（意味トークン）
  意図・役割を表現。命名は「用途」で。
  例: color-primary, color-error, text-body, space-component-gap

     ↓ エイリアス参照

Layer 3: Component Tokens（コンポーネントトークン）
  特定コンポーネント固有のバインディング。
  例: button-bg-primary, card-padding, input-border-color
```

**鉄則**: コンポーネントはLayer 3のみ参照する。Layer 1の直参照を禁止することで、テーマ切り替え（ダーク/ライト、ブランドバリアント）が安全に行える。

### W3C Design Tokens Format（2025.10安定版）

```json
{
  "color": {
    "blue": {
      "500": {
        "$type": "color",
        "$value": "#3B82F6"
      }
    },
    "primary": {
      "$type": "color",
      "$value": "{color.blue.500}"
    }
  },
  "button": {
    "bg": {
      "primary": {
        "$type": "color",
        "$value": "{color.primary}"
      }
    }
  }
}
```

- `{token.name}` 構文でエイリアス参照
- `$extends` プロパティでテーマ管理（ライト/ダーク）
- ベンダー中立フォーマット（ツールのサポート状況はバージョン依存。変換レイヤ前提で設計する）

### 命名規則

| 層 | パターン | 例 |
|-----|---------|-----|
| Global | `{category}-{variant}-{scale}` | `blue-500`, `font-size-16` |
| Semantic | `{category}-{role}` | `color-primary`, `color-error` |
| Component | `{component}-{property}-{variant}` | `button-bg-primary` |

### トレーサビリティ表

デザイン原則からコンポーネントまでの追跡:

```
原則: アクセシビリティ > 美しさ
  → Semantic Token: color-text-primary (contrast 7:1)
    → Component Token: button-text-primary
      → 画面: ダッシュボードCTAボタン
```

---

## 補助フレームワーク

### Nathan Curtisの「Doneness Matrix」

コンポーネント完成度を多軸で評価するフレームワーク。Phase 4で使用。

### 60-30-10ルール（カラー比率）

Foundation定義時のカラーバランス指針:
- 60%: ドミナント（背景）
- 30%: セカンダリ（補助）
- 10%: アクセント（強調）

### タイプスケール比率

| 比率 | 用途 |
|------|------|
| Minor Third (1.2) | 情報密度の高いUI |
| Major Third (1.25) | 一般的なWebアプリ（推奨） |
| Perfect Fourth (1.333) | 見出し重視のUI |

## 参考文献

- W3C Design Tokens Format 2025.10: https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/
- Atomic Design: https://atomicdesign.bradfrost.com/chapter-2/
- Design Council Double Diamond: https://www.designcouncil.org.uk/our-resources/framework-for-innovation/
