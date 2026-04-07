# Witness Bundle 形式

議論を感想戦にしないために、finding は必ず witness bundle で返す。

## 必須項目

```yaml
req_id: REQ-<domain>-<number>
requirement_text: <元の要件文>
artifact_links:
  formal_spec:
    - <file or id>
  tests:
    - <file or id>
  contracts:
    - <symbol or assertion>
  code_symbols:
    - <function or api>
  runtime_rules:
    - <trace rule or query>
counterexample:
  type: counterexample | mutation_survivor | contract_violation | trace_violation | missing
  data: <最小失敗入力、反例トレース、違反属性など>
change_scope:
  commits:
    - <commit or diff range>
  files:
    - <path>
runtime_context:
  trace_id: <trace id or none>
  span_ids:
    - <span id>
assessment:
  primary_fault: requirement | formalization | test | implementation | observability
  severity: high | medium | low
next_action: <最初に直すべき場所>
```

## 判定のしかた

`primary_fault` は最初に直す場所を示す。責任の押し付け先ではない。

- `requirement`: 要件文か要件原子が曖昧
- `formalization`: 形式化が分岐または不足
- `test`: テストが弱い、またはリンク不足
- `implementation`: 契約違反や反例が実装で再現
- `observability`: 実行時証拠が不足

## 良い bundle の条件

- 反例を再実行できる
- どの要件にひも付くか一目で分かる
- どこから直し始めるかが決まる
- 変更差分と実行時証拠の両方が含まれる

## 返し方の例

```markdown
## Witness Bundle: REQ-order-102

- 判定: implementation
- 反例種別: mutation_survivor
- 最小失敗条件: retry path ignores idempotency key
- 関連コード: reserveInventory, finalizeOrder
- 関連テスト: test_order_retry_idempotency
- 実行時証拠: trace 7fd... で reservation_count=2
- 次の修正候補: retry path の契約と property-based test を先に補強
```
