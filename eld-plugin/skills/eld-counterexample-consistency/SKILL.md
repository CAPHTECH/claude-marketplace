---
name: eld-counterexample-consistency
context: fork
argument-hint: "scan | design | gate | full (default: full)"
description: requirements-consistency 導入前の既存利用者向け互換スキル。新規利用では requirements-plugin の requirements-consistency を使い、ELD 文脈の既存参照だけをこの名前で受ける。
---

# ELD Counterexample Consistency

このスキルは後方互換の入口である。
新規利用では `requirements-plugin` の `/requirements-consistency` を使う。

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `scan` | 現状診断のみ | 既存の要件、テスト、コード、観測点を棚卸しし、欠落と不整合を洗い出す |
| `design` | 設計のみ | 要件原子、トレーサビリティグラフ、検出器、報告形式を設計する |
| `gate` | 判定のみ | 変更差分に対して AI 向け判定ルールを適用し、整合性の可否を返す |
| `full` | 設計、診断、判定 | 上記を順に実行する。省略時の既定値 |

## Migration Note

- 新規利用者:
  `requirements-plugin` の `/requirements-consistency` を使う
- 既存の ELD 文脈:
  このスキル名を使ってもよい
- 目的:
  要件管理を `requirements-plugin` で完結して使えるようにする

## Compatibility Contract

- 検査観点、判定ルール、witness bundle の考え方はこのスキルに残す
- 実際の新規運用説明は `/requirements-consistency` を正とする
- 既存文書や既存チャットからこの名前で参照されても成立するよう、引き続き同じ引数体系を維持する

## Legacy References

既存の ELD 文書から参照される資料はこの場所にも残す。
新規利用では `requirements-plugin` 側の同名資料を優先してよい。

- [requirements-atom.md](references/requirements-atom.md)
- [traceability-graph.md](references/traceability-graph.md)
- [detectors.md](references/detectors.md)
- [ai-diff-rules.md](references/ai-diff-rules.md)
- [witness-bundle.md](references/witness-bundle.md)
- [adoption-roadmap.md](references/adoption-roadmap.md)

## Outputs

- `req-catalog` または要件原子一覧
- `traceability matrix` またはグラフ
- detector ごとの結果
- witness bundle 一式
- 導入順序または CI ゲート案

## Hand-offs

- `/requirements-consistency`: 新規利用の正面入口
- `/test-design-audit`: 要件からテスト条件への監査
- `/systematic-test-design`: property-based test と反例回収

## Stop Conditions

以下のどれかに当たったら、成立したとは言わずに不足を明示して止まる。

- スコープ内要件の 20% 以上で `observable` がない
- 高リスク要件に要件IDがない
- 検出器の出力が文章だけで、反例か差分証拠がない
- 実行時観測がなく、運用整合性を判断できない
