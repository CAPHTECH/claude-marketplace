# Inspection Rules

要件検査は、まず静的に壊れていないかを見て、その後で差分不整合を見る。

## Lint Rules

1. 必須欄がすべてある
2. `observable` が空ではない
3. `positive_examples` と `negative_examples` がある
4. `status` と `unknowns` が矛盾しない
5. 同一IDの重複がない
6. `superseded` 要件に置換先がある

## Consistency Rules

次のような組み合わせは矛盾疑いとして扱う。

- 同じ `context` と `trigger` で、互いに排他的な `guarantee`
- 同じ対象に対し、片方は必須、片方は禁止
- 成立時刻の上限と外部依存条件が明らかに両立しない

## Diff Rules

- コード変更あり、関連要件変更なし
- 要件変更あり、関連テスト変更なし
- Telemetry 変更あり、要件ID付与なし
- `deprecated` になったのに下流の現行リンクが残る

## Severity

- `high`: 誤実装や誤運用につながりやすい
- `medium`: 下流検査やレビューを阻害する
- `low`: 今すぐは壊れないが運用負債になる

## Handoff Rules

- 時間制約、状態遷移、相互矛盾が絡むなら `/requirements-consistency`
- テストの鋭さや抜け漏れが気になるなら `/test-design-audit`
- リンク切れや孤立が多いなら `/requirements-traceability`
