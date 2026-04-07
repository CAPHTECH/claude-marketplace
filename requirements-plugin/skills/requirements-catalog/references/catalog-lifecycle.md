# Requirements Catalog Lifecycle

カタログでは、各要件を単なる一覧ではなく状態付きの資産として扱う。

## Status

- `draft`: まだ議論中。下流リンクは空でもよい
- `reviewed`: レビュー済み。下流リンク作成の準備ができている
- `active`: 現行。少なくとも観測方法と下流リンク候補がある
- `deprecated`: 使わなくなる予定。既存リンクの撤去計画が必要
- `superseded`: 別の要件に置き換え済み。`supersedes` を明示する

## Priority

- `p0`: ビジネス継続や法令順守に直結
- `p1`: 主要機能や顧客価値に直結
- `p2`: 品質改善や補助機能
- `p3`: 望ましいが後回し可能

## Edge Types

- `depends_on`: この要件の成立前提
- `blocks`: この要件が成立しないと進めない後続
- `supersedes`: 別要件を置き換える
- `related_to`: 参照は必要だが依存ではない

## 更新ルール

- `active` を `deprecated` に変える時は、撤去対象のリンクも列挙する
- `superseded` に変える時は、新しい要件IDを必ず書く
- `draft` が長く残る要件は `unknowns` と `questions_for_review` を再確認する
- 同じタイトルで複数の `active` 要件がある場合は重複疑いとして扱う
