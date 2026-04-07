---
name: requirements-consistency
context: fork
argument-hint: "scan | design | gate | full (default: full)"
description: 要件、仕様、テスト、コード、実行時観測を要件IDで結び、反例、変異、契約違反、トレース違反で多層整合性を検査する。要件からコードまでの整合性を確認したい、トレーサビリティを設計したい、「反例駆動でチェックして」「多層整合性を見て」と言われた時に使用する。
---

# Requirements Consistency

自然言語の文章同士を比較して結論を出さない。要件、形式仕様、テスト、コード、実行時観測を、反例を返せる表現へ変換し、要件ID付きで循環照合する。

このスキルは `requirements-plugin` における高度な整合性検査の正面入口である。
日常の欠落検査や lint は `/requirements-inspector`、反例と証拠束まで掘る検査は本スキルで扱う。

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `scan` | 現状診断のみ | 既存の要件、テスト、コード、観測点を棚卸しし、欠落と不整合を洗い出す |
| `design` | 設計のみ | 要件原子、トレーサビリティグラフ、検出器、報告形式を設計する |
| `gate` | 判定のみ | 変更差分に対して AI 向け判定ルールを適用し、整合性の可否を返す |
| `full` | 設計、診断、判定 | 上記を順に実行する。省略時の既定値 |

## Core Rule

- 文章同士のレビューで終わらせず、必ず実行可能な成果物に落とす。
- 各要件は `REQ-xxx` として一意に識別する。
- 各要件に `observable` と `negative_examples` を必須とする。
- 出力は「怪しい」という感想ではなく、`witness bundle` にする。

## Workflow

### Phase 1: 要件を比較可能な原子へ正規化する

`REQ` の形は [requirements-atom.md](references/requirements-atom.md) を読み、次の欄を最低限そろえる。

- `context`
- `trigger`
- `precondition`
- `guarantee`
- `forbid`
- `timing`
- `observable`
- `positive_examples`
- `negative_examples`

`observable` か `negative_examples` が欠ける要件は、その時点で未接地として扱う。

### Phase 2: 実行可能ビューを要件IDで結ぶ

各 `REQ_i` から、少なくとも次のビューを定義する。リンクの作り方と変更影響の見方は [traceability-graph.md](references/traceability-graph.md) を読む。

- `F_i`: 形式仕様
- `T_i`: 実行テスト
- `K_i`: コード内契約
- `C_i`: 実装シンボル
- `M_i`: 実行時監視

基本グラフは次の形に固定する。

```text
REQ_i ↔ F_i ↔ T_i ↔ K_i ↔ C_i ↔ M_i
```

存在しないノードや辺は、矛盾より先に「欠落」として報告する。

### Phase 3: 6つの検出器を順に実行する

検出器の入力、最小出力、代表的な証拠は [detectors.md](references/detectors.md) を読む。

1. 欠落検出器
2. 二重形式化差分検出器
3. 仕様内部矛盾検出器
4. テスト妥当性検出器
5. 契約違反検出器
6. 実行時観測整合性検出器

検出器が返すのは、反例、変異生存、契約違反、トレース違反、未接地のいずれかであること。文章だけの指摘は補助情報に下げる。

### Phase 4: AI が作った変更に特有の判定ルールを適用する

差分ベースの判定ルールは [ai-diff-rules.md](references/ai-diff-rules.md) を読む。特に次の5つを既定ルールとする。

- コードだけ変わり、関連する要件、仕様、テストが変わっていないなら不整合疑い
- 要件だけ変わり、形式仕様と property-based test が変わっていないなら形式化漏れ
- テストがすべて成功していても、mutation survivor が多いなら保証不十分
- 実行時 trace に要件IDがない機能は、要件適合を主張しない
- 独立に作った二つの形式化が一致しない要件は、要件自体が曖昧

### Phase 5: witness bundle で返す

報告形式は [witness-bundle.md](references/witness-bundle.md) を読む。必ず次を含める。

- 要件ID
- 元の要件文
- 対応する形式式または制約
- 反例トレースまたは最小失敗入力
- 関連コードシンボル
- 関連テスト
- 変更範囲
- 実行時 trace または span
- 判定
- 次の修正候補

### Phase 6: 小さく導入し、差分で再検査する

導入順序は [adoption-roadmap.md](references/adoption-roadmap.md) を読む。最初から完全形式化を目指さず、要件IDと観測可能性から始める。

## Outputs

- `req-catalog` または要件原子一覧
- `traceability matrix` またはグラフ
- detector ごとの結果
- witness bundle 一式
- 導入順序または CI ゲート案

## Hand-offs

- `/requirements-inspector`: 入口の lint と差分確認
- `/requirements-traceability`: 要件IDと下流成果物の接続整理
- `/test-design-audit`: 要件からテスト条件への監査
- `/systematic-test-design`: property-based test と反例回収

## Stop Conditions

以下のどれかに当たったら、成立したとは言わずに不足を明示して止まる。

- スコープ内要件の 20% 以上で `observable` がない
- 高リスク要件に要件IDがない
- 検出器の出力が文章だけで、反例か差分証拠がない
- 実行時観測がなく、運用整合性を判断できない
