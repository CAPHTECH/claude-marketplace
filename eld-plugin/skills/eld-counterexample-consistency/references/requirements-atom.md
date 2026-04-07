# 要件原子テンプレート

自然言語の要件を、そのまま比較しない。まず、比較可能で観測可能な原子へ正規化する。

## 必須欄

```yaml
req_id: REQ-<domain>-<number>
context:
  actor: <誰か>
  state: <どの状態か>
  external_conditions:
    - <外部条件>
trigger: <何が起点か>
precondition:
  - <事前条件>
guarantee:
  - <保証すること>
forbid:
  - <起きてはいけないこと>
timing:
  start_event: <いつから測るか>
  deadline: <いつまでに成立するか>
observable:
  return_value: <戻り値または応答>
  events:
    - <イベント名>
  telemetry:
    - <属性またはメトリクス>
positive_examples:
  - <満たす具体例>
negative_examples:
  - <満たさない具体例>
```

## 必須にする理由

- `observable` がない要件は、テストにも監視にも落ちない。
- `negative_examples` がない要件は、禁止条件の境界が固定されない。
- `timing.start_event` がない時間要件は、形式化が分岐しやすい。

## 完成条件

- 要件文を読まなくても、欄だけで検査対象が分かる。
- `forbid` がテスト失敗か監視違反として観測できる。
- 少なくとも1つの `positive_examples` と 1つの `negative_examples` がある。

## 例

```yaml
req_id: REQ-order-102
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
