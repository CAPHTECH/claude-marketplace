---
name: design-system-builder
context: fork
description: "デザインシステムの構築・運用を体系的に行うスキル。ドキュメント（要件定義・ブランドガイドライン）からDesign Tokens・コンポーネント体系・ガバナンスまでを一貫して設計する。思考フレームワーク（Double Diamond・Atomic Design・Design Tokens 3層）の適用、暗黙的デザイン判断の形式知化（DDR/QOC/RFC）、UIインベントリ収集（手動+MCP自動化）を統合する。Use when: 「デザインシステムを構築して」「デザインシステムを設計して」「デザイントークンを定義して」「デザイン原則を策定して」「UIインベントリを作って」「デザインガバナンスを設計して」「デザイン判断を記録して」と言われた時。"
---

# Design System Builder

デザインシステムの構築・運用を体系的に行う。Double Diamondの発散→収束モデルで進行し、各フェーズの成果物を契約として管理する。

## ワークフロー概要

```
Phase 1: 発見（Discover）  → UIインベントリ、課題洗い出し
  → Phase 2: 定義（Define） → 設計原則、判断基準の収束
    → Phase 3: 基盤設計（Develop） → Design Tokens、Foundation定義
      → Phase 4: コンポーネント構築（Deliver） → Atomic Design構造化
        → Phase 5: 採用・移行（Adopt） → 段階リリース、既存UIの移行
          → Phase 6: 運用（Operate） → ガバナンス、継続改善
```

---

## Phase 1: 発見（Discover）

**目的**: 現状の設計資産と課題を発散的に収集する。

### Entry Criteria
- デザインシステム構築の意思決定がある
- 対象プロダクト・スコープが特定されている

### Step 1.1: UIインベントリ（棚卸し）

既存UIの全要素をスクリーンショット＋CSSプロパティで収集・分類する。

**手動アプローチ**:
1. 対象画面リストを作成（routes/sitemap/主要ユーザーフロー）
2. 各画面のUI要素をスクリーンショットで記録
3. ボタン、フォーム、ナビゲーション、モーダル等をカテゴリ別に分類
4. 不一致（同じ目的の要素が異なるスタイル）をマーク

**自動化アプローチ**（MCP連携）:
Playwright MCP + Chrome DevTools MCP で定量的に収集可能。
自動収集を使う場合に参照 → [references/ui-inventory.md](references/ui-inventory.md)

### Step 1.2: 入力ドキュメントの分解

要件定義・ブランドガイドラインを3カテゴリに分離:

| カテゴリ | 内容 | 例 |
|----------|------|-----|
| 事実 | 変更不可の制約 | ブランドカラー #003366、フォント Noto Sans |
| 制約 | 技術的・ビジネス的制限 | WCAG 2.1 AA必須、iOS/Android両対応 |
| 解釈 | チームの判断が必要 | 「親しみやすい」トーンの具体化 |

### Step 1.3: 組織横断的な課題収集

デザイナー・エンジニア・PM・マーケティング等から課題を収集する:
- どこでデザインの不一致が発生しているか
- どのUIパターンが頻繁に作り直されているか
- チーム間のコミュニケーション上の齟齬

### Exit Criteria / 成果物
- `ui-inventory.json` — UI要素の棚卸し結果
- `design-brief.md` — 対象・スコープ・制約・課題の要約

---

## Phase 2: 定義（Define）

**目的**: 発散した情報を収束させ、判断基準を確立する。

### Entry Criteria
- UIインベントリが完了している
- 主要な課題が特定されている

### Step 2.1: 設計判断カードの作成

暗黙のデザイン判断を形式知化する:

```
カード名:   [判断の名前]
意図:       なぜこの判断をしたか
適用条件:   いつ使うか
禁止条件:   いつ使わないか
例外:       例外的に許容するケース
根拠:       エビデンス（ユーザーテスト結果、a11y基準等）
```

### Step 2.2: デザイン原則の収束

3〜5個のデザイン原則に収束させる。衝突時の優先順位を明示する。

例:
```
1. アクセシビリティ > 美しさ
2. 一貫性 > 個別最適
3. シンプルさ > 機能の網羅性
```

### Step 2.3: Design Decision Record（DDR）の運用開始

設計判断を記録するプロセスを確立する。
DDRの書き方・QOC・RFC運用が必要な場合に参照 → [references/design-decision-records.md](references/design-decision-records.md)

### Exit Criteria / 成果物
- `design-principles.md` — 優先順位付きデザイン原則
- `decision-log/DDR-NNN.md` — DDRファイル（DDRテンプレートに準拠）

---

## Phase 3: 基盤設計（Develop）

**目的**: Design Tokensと基盤要素を定義する。

### Entry Criteria
- デザイン原則が確定している
- カラー・タイポグラフィの入力ドキュメントがある

### Step 3.1: Design Tokens 3層アーキテクチャ

```
Layer 1: Global Tokens（基盤）
  色の生値、フォントサイズの生値
  例: blue-500: #3B82F6, font-size-16: 16px

Layer 2: Semantic Tokens（意味）
  意図を表現するエイリアス
  例: color-primary: {blue-500}, text-body: {font-size-16}

Layer 3: Component Tokens
  コンポーネント固有のバインディング
  例: button-bg-primary: {color-primary}
```

**原則**: コンポーネントはLayer 3のみ参照する。Layer 1の直参照は禁止。

### Step 3.2: Foundation定義

| 要素 | 定義内容 | トークン例 |
|------|----------|-----------|
| カラー | Primary/Secondary/Semantic + 明度スケール(50-950) | `color-primary-500` |
| タイポグラフィ | フォント、サイズスケール、行間、ウェイト | `font-size-lg` |
| スペーシング | 4px/8pxベースのスケール | `space-4: 16px` |
| エレベーション | シャドウ、レイヤリング | `shadow-md` |
| ボーダーラディウス | 角丸スケール | `radius-md: 8px` |
| モーション | デュレーション、イージング | `duration-fast: 150ms` |
| ブレークポイント | レスポンシブ基準 | `breakpoint-md: 768px` |

### Step 3.3: トークンファイルの出力

W3C Design Tokens Format（2025.10安定版）に準拠した `tokens.json` を生成する。

フレームワーク間の関係性やW3C DTCG仕様の詳細が必要な場合に参照 → [references/thinking-frameworks.md](references/thinking-frameworks.md)

### Exit Criteria / 成果物
- `tokens.json` — W3C DTCG準拠のDesign Tokensファイル
- `foundation-spec.md` — Foundation定義書

---

## Phase 4: コンポーネント構築（Deliver）

**目的**: Atomic Design階層でコンポーネント体系を構築する。

### Entry Criteria
- Design Tokensが定義済み
- Foundation仕様が確定している

### Step 4.1: コンポーネント階層の設計

| 階層 | 定義 | 具体例 |
|------|------|--------|
| Atoms | 最小UI要素 | Button, Input, Icon, Badge |
| Molecules | Atomsの組み合わせ | SearchBar, FormField, NavItem |
| Organisms | Moleculesの複合体 | Header, Sidebar, DataTable |
| Templates | ページ構造 | DashboardLayout, AuthLayout |
| Pages | 実コンテンツを含む完成形 | DashboardPage, LoginPage |

### Step 4.2: コンポーネント仕様書

各コンポーネントに以下を定義する:
- 名前（PascalCase）、説明（1文）
- Props（型・デフォルト値・必須/任意）
- 状態（Idle/Hover/Active/Focused/Disabled/Loading/Error）
- バリアント（size, variant）
- アクセシビリティ要件（ARIA属性、キーボード操作）
- 使用するDesign Tokens

### Step 4.3: Doneness Matrix

コンポーネントの完成度を軸ごとに管理:

| 軸 | チェック項目 |
|----|-------------|
| デザイン | Figmaコンポーネント作成、バリアント定義 |
| コード | 実装完了、ユニットテスト通過 |
| ドキュメント | 使用ガイドライン、Do/Don't |
| アクセシビリティ | WAI-ARIA準拠、キーボード操作対応 |
| レビュー | デザインレビュー、コードレビュー完了 |

### Exit Criteria / 成果物
- `component-spec.md` — コンポーネント仕様書
- Doneness Matrixのスコアが全軸で基準を満たす

---

## Phase 5: 採用・移行（Adopt）

**目的**: デザインシステムを組織に段階的に展開する。

### Entry Criteria
- 最低限のFoundation + 主要コンポーネントが完成している

### Step 5.1: 段階リリース

| ステージ | 基準 | 対象 |
|----------|------|------|
| Alpha | 方針実証、フィードバック収集 | 1チームのみ |
| Beta | プロダクション利用可能な品質 | 早期採用チーム |
| GA | 全機能が安定 | 全チーム |

### Step 5.2: 既存UIの移行計画

1. 優先順位付け: 高頻度画面・高不一致画面から着手
2. 互換レイヤの設計: 旧スタイルとの共存期間を定義
3. 非推奨（deprecate）期限の設定: 旧コンポーネントの廃止日を明示
4. 移行ガイドの提供: Before/Afterの対応表

### Step 5.3: 教育・オンボーディング

- チーム向けワークショップ
- 「いつ・どのコンポーネントを使うか」のクイックリファレンス
- 例外申請プロセスの周知

### Exit Criteria / 成果物
- `migration-plan.md` — 移行計画書（優先順位、互換レイヤ、deprecate期限）
- `adoption-metrics.json` — 採用率KPI（採用率、一貫性違反、例外申請数、修正リードタイムを含む）

---

## Phase 6: 運用（Operate）

**目的**: デザインシステムを継続的に維持・改善する。

### Entry Criteria
- GA リリース済み

### Step 6.1: ガバナンスモデルの選択

| モデル | 特徴 | 適する組織 |
|--------|------|-----------|
| 中央集権型 | 専任チームが全管理 | 小〜中規模 |
| フェデレーテッド型 | 専任+各チームがコントリビューション | 中〜大規模 |
| コミュニティ駆動型 | オープンな協調管理 | 大規模・OSS |

### Step 6.2: KPI

| KPI | 説明 | 目標例 |
|-----|------|--------|
| 採用率 | DSコンポーネント利用率 | >80% |
| 一貫性違反件数 | DSから逸脱したUI数 | 月次減少 |
| 例外申請数 | DS外コンポーネントの例外申請 | <5件/月 |
| 修正リードタイム | バグ報告→修正の平均時間 | <5営業日 |

コントリビューションフロー・バージョニング・監査の設計が必要な場合に参照 → [references/governance.md](references/governance.md)

### Exit Criteria
- ガバナンスプロセスが運用開始されている
- KPIのモニタリング体制が確立されている

---

## 連携スキル

| スキル | 連携タイミング |
|--------|---------------|
| web-app-designer | DSの成果物（原則・トークン・コンポーネント仕様）を入力として個別画面を設計する |
| mobile-app-designer | モバイル固有のDS拡張（タッチターゲット、プラットフォーム適応）を設計する |
| spec-gen | DS構築後、実装仕様書を生成する |
| architecture-reviewer | DSのアーキテクチャをレビューする |

## 注意事項

- DSは「プロジェクト」ではなく「継続的プロセス」として扱う
- 全フェーズを一度に完了しようとしない。Phase 1-2で十分な合意を取ってからPhase 3以降に進む
- web-app-designerが提供する個別デザイン実行（レイアウト・カラー・タイポの具体設計）はこのスキルの範囲外。本スキルは「設計の設計」に集中する
- 既存DSがある場合はPhase 1のUIインベントリからDS監査として開始する
