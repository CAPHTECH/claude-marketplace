# Inspection Rules

要件検査は、まず静的に壊れていないかを見て、その後で差分不整合を見る。

## Lint Rules

1. 必須欄がすべてある
2. `observable` が空ではない
3. `positive_examples` と `negative_examples` がある
4. `status` と `unknowns` が矛盾しない
5. 同一IDの重複がない
6. `superseded` 要件に置換先がある

## Diff / Consistency Rules

組み合わせ矛盾の判定と差分不整合の判定基準は `/requirements-consistency` の references/ai-diff-rules.md を単一の情報源とする。

## Severity

- `high`: 誤実装や誤運用につながりやすい
- `medium`: 下流検査やレビューを阻害する
- `low`: 今すぐは壊れないが運用負債になる

## Handoff Rules

- 時間制約、状態遷移、相互矛盾が絡むなら `/requirements-consistency`
- テストの鋭さや抜け漏れが気になるなら `/test-design-audit`
- リンク切れや孤立が多いなら `/requirements-traceability`
