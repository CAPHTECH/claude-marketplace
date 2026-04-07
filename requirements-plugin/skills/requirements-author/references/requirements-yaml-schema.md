# Requirements YAML Schema

要件レコードは、下の最小形を基準にする。
細かい拡張は許すが、必須欄は欠かさない。

## 最小スキーマ

```yaml
id: REQ-domain-001
title: 短い要件名
status: draft
priority: p1
context:
  actor: end-user
  state: signed-in
  external_conditions: []
trigger: submit_order
precondition:
  - payment_authorized
guarantee:
  - order_id is returned
forbid:
  - duplicate_reservation
timing:
  response_within_ms: 5000
observable:
  events:
    - order.confirmed
  logs:
    - order_id
  metrics:
    - checkout.duration
positive_examples:
  - single checkout returns one order id
negative_examples:
  - retry without idempotency must not reserve twice
links:
  laws: []
  tests: []
  code: []
  telemetry: []
  manual_checks: []
unknowns: []
assumptions: []
questions_for_review: []
```

## 必須欄

- `id`: 一意な要件ID。既定は `REQ-<domain>-<nnn>`
- `title`: 1行で読める要件名
- `status`: `draft | reviewed | active | deprecated | superseded`
- `priority`: `p0 | p1 | p2 | p3`
- `context`: だれが、どの状態で、どの外部条件で使うか
- `trigger`: 何を起点に成立するか
- `guarantee`: 何を保証するか
- `forbid`: 起きてはいけないこと
- `observable`: どう観測するか
- `positive_examples`: 成立する具体例
- `negative_examples`: 成立しない具体例
- `links`: 下流アーティファクトへの接続点

## 推奨欄

- `precondition`: 成立前提
- `timing`: 時間制約、順序制約
- `unknowns`: 未確定事項
- `assumptions`: 仮定
- `questions_for_review`: レビュー時に確認したい点

## 記述ルール

- `guarantee` は観測可能な文にする
- `forbid` は禁止したい振る舞いを具体的に書く
- `positive_examples` と `negative_examples` はテストや手動確認に転用できる粒度にする
- `observable` はイベント、ログ、戻り値、画面表示など実際に確認できるものを書く
- `unknowns` がある要件は、原則 `active` にしない

## アンチパターン

- 「適切に処理する」のような観測不能な表現だけで終わる
- 1レコードの中に別機能の要件を混ぜる
- `links` を推測で埋める
- `negative_examples` を空にする
