# デザイン判断の記録手法

暗黙的なデザイン判断を明示的な技術として定義・文書化するための手法群。

## 目次

- [Design Decision Record (DDR)](#design-decision-record-ddr)
- [QOC (Questions, Options, Criteria)](#qoc-questions-options-criteria)
- [RFC運用](#rfc運用)
- [トレーサビリティ表](#トレーサビリティ表)
- [機械検証による判断の自動化](#機械検証による判断の自動化)
- [廃止ポリシー](#廃止ポリシー)

---

## Design Decision Record (DDR)

Architecture Decision Record（ADR）のデザイン版。設計判断を構造化して記録する。

### テンプレート

```markdown
# DDR-001: [判断のタイトル]

## ステータス
Proposed | Accepted | Rejected | Superseded by DDR-XXX

## コンテキスト
- 判断が必要になった背景
- 関連するデザイン原則
- 影響を受けるコンポーネント/画面

## 判断内容
選択した方針の明確な記述。

## 検討した代替案
1. [代替案A] — 不採用理由
2. [代替案B] — 不採用理由

## 理由
- 技術的根拠
- ユーザビリティ根拠
- ビジネス要件との整合
- アクセシビリティへの影響

## 影響
### ポジティブ
- [良い影響]

### ネガティブ
- [悪い影響・技術的負債]

### 緩和策
- [ネガティブ影響への対処]

## レビュー
- 再評価トリガー: [条件]
- 次回レビュー: [日付]
```

### DDR運用ルール

1. 新しいFoundation要素やコンポーネントの追加時に必ず作成
2. 既存DDRの変更は `Superseded by DDR-XXX` で新DDRに移行（直接編集しない）
3. DDRはコードリポジトリで管理し、PRレビューの対象にする
4. ステータスは `Proposed → Accepted` のフローを必ず通す

---

## QOC (Questions, Options, Criteria)

MacLean et al.（1991年）提唱。判断を「問い・選択肢・評価基準」で構造化する。DDRより軽量で、判断の初期段階に適する。

### テンプレート

```markdown
## Q: [設計上の問い]
例: ダークモードのカラー反転は自動計算か手動定義か？

### Options
| # | 選択肢 | 説明 |
|---|--------|------|
| 1 | 自動反転 | HSLのLightness反転で自動生成 |
| 2 | 手動定義 | ダーク用のGlobal Tokensを別途定義 |
| 3 | ハイブリッド | 基本は自動、セマンティック色は手動 |

### Criteria
| 基準 | 重み | Opt 1 | Opt 2 | Opt 3 |
|------|------|-------|-------|-------|
| 保守コスト | 高 | ◎ | △ | ○ |
| 色の品質 | 高 | △ | ◎ | ○ |
| 実装の複雑さ | 中 | ○ | ○ | △ |

### 決定: Option 3（ハイブリッド）
理由: 保守コストと色の品質のバランスが最良。
```

### DDRとの使い分け

| 場面 | 手法 |
|------|------|
| 初期の判断探索 | QOCで選択肢と評価基準を整理 |
| 最終的な判断記録 | DDRで決定を正式に記録 |
| 軽微な判断 | QOCのみで十分 |
| 重大な判断（Foundation変更等） | QOC → DDR の2段階 |

---

## RFC運用

変更提案をPRベースで公開レビューする。Rust RFCプロセスが参考。

### RFCテンプレート

```markdown
# RFC: [提案タイトル]

## 概要
1-2文で変更内容を要約。

## 動機
なぜこの変更が必要か。

## 詳細設計
具体的な変更内容（トークン定義、コンポーネント仕様等）。

## 代替案
検討した他のアプローチ。

## 破壊的変更
既存コンポーネントへの影響と移行計画。

## 未解決の問題
議論が必要な点。
```

### RFC運用ルール

1. 破壊的変更は必ずRFCを通す
2. 新規コンポーネントの追加はRFC推奨（必須ではない）
3. レビュー期間は最低3営業日
4. 承認にはDS管理チーム + 利用チーム代表の合意が必要

---

## トレーサビリティ表

デザイン原則 → トークン → コンポーネント → 画面の対応関係を追跡する。

```markdown
| 原則 | Semantic Token | Component Token | 適用画面 |
|------|---------------|-----------------|---------|
| アクセシビリティ優先 | color-text-primary (7:1) | button-text-primary | 全CTAボタン |
| 一貫性 | space-component-gap: 16px | card-gap, list-gap | カード一覧、リスト |
| シンプルさ | font-size-body: 16px | — | 全本文テキスト |
```

### 運用

1. Foundation変更時にトレーサビリティ表で影響範囲を確認
2. 新コンポーネント追加時に対応する原則を明記
3. 原則に紐づかないトークンは正当性を再検討

---

## 機械検証による判断の自動化

判断の一部をCI/CDで自動検証する。

| ツール | 検証内容 |
|--------|---------|
| stylelint / eslint | トークン直参照の禁止、命名規則の強制 |
| axe-core | コントラスト比、ARIA属性の検証 |
| BackstopJS / Loki | Visual Regression（見た目の回帰検出） |
| css-analyzer | CSS全体のカラー/タイポ分布の俯瞰 |

### lint設定例（カスタムルール実装が前提）

```json
{
  "rules": {
    "custom/no-global-token-direct-use": true,
    "custom/semantic-token-naming": "^(color|font|space|shadow|radius|duration|breakpoint)-",
    "custom/component-token-naming": "^[a-z]+-[a-z]+-"
  }
}
```

---

## 廃止ポリシー

DDR/トークン/コンポーネントの寿命管理。

### ライフサイクル

```
Active → Deprecated（非推奨） → Removed（削除）
```

### 廃止ルール

1. `Deprecated` 宣言時に移行先を必ず明記する
2. 非推奨期間は最低2スプリント（または1ヶ月）
3. 利用箇所がゼロになるまで `Removed` にしない
4. DDRの `Superseded by DDR-XXX` で判断の移行先を追跡

## 参考文献

- MADR: https://adr.github.io/madr/
- QOC: MacLean et al., 1991 https://doi.org/10.1080/07370024.1991.9667168
- Rust RFCs: https://github.com/rust-lang/rfcs
- GOV.UK Contribution Criteria: https://design-system.service.gov.uk/community/contribution-criteria/
