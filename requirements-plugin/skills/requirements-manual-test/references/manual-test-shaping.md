# Manual Test Shaping

手動テストは、単に手順を書くのではなく、要件のどの部分を確認するかを明示する。

## 変換ルール

- `positive_examples` から正常系を作る
- `negative_examples` から禁止確認を作る
- `timing` から時間制約の確認を作る
- `observable` から証跡取得手順を作る
- `forbid` から失敗してほしい操作や起きてはいけない状態を作る

## 1ケースの最小要素

- `case_id`
- `req_id`
- `purpose`
- `preconditions`
- `steps`
- `expected_result`
- `observable_evidence`
- `notes`

## ケース分割の目安

- 正常系と否定例は同じケースに混ぜない
- 観測確認だけを独立ケースにしてよい
- 1ケースで複数の要件IDをまたがない

## 優先順位

- `p0` と `p1` は正常系、否定例、観測確認を必須
- `p2` は正常系と主要な否定例を優先
- `p3` は代表ケースから始める
