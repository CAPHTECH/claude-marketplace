# 要件原子テンプレート

自然言語の要件を、そのまま比較しない。まず、比較可能で観測可能な原子へ正規化する。

正準スキーマは /requirements-author の requirements-yaml-schema.md を参照する。
`id`、`context`、`trigger`、`precondition`、`guarantee`、`forbid`、`positive_examples`、`negative_examples` は正準スキーマのとおり埋める。

## 検出器向けの追加欄

多層整合性の検出器は、正準スキーマの `timing` と `observable` だけでは比較に使えない。次の欄を追加で埋める。

```yaml
timing:
  start_event: <いつから測るか>
  deadline: <いつまでに成立するか>
observable:
  return_value: <戻り値または応答>
  events:
    - <イベント名>
  telemetry:
    - <属性またはメトリクス>
```

## 追加欄が必要な理由

- `timing.start_event` がない時間要件は、形式化が分岐しやすい。
- `observable.return_value` がない要件は、契約違反検出器が比較対象を作れない。

## 例

```yaml
id: REQ-order-102
context:
  actor: authenticated_user
  state: payment_authorized
  external_conditions:
    - inventory service reachable
trigger: user confirms order
precondition:
  - order is not finalized
guarantee:
  - reserve inventory exactly once
  - return order_id within 5 seconds
forbid:
  - double reservation
timing:
  start_event: confirm button accepted
  deadline: 5 seconds
observable:
  return_value: order_id
  events:
    - order.confirmed
    - inventory.reserved
  telemetry:
    - req.id=REQ-order-102
    - reservation_count
positive_examples:
  - first confirmation returns order_id and creates one reservation
negative_examples:
  - retry without idempotency causes second reservation
```

## 先に確認する曖昧点

- 時間をどの瞬間から測るか
- 外部サービス失敗時に保証が縮退するか
- 禁止条件が局所契約で止める対象か、本番監視で見る対象か
