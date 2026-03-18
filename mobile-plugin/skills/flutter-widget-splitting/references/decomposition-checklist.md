# Decomposition Checklist

分割位置に迷った時だけ読む。
目的は「どこを Widget に切るか」を最短で決めること。

## 速見表

| 症状 | 抽出先 | 状態の持ち主 | メモ |
|------|--------|-------------|------|
| `build()` が長く、見た目の塊が3つ以上ある | `Section` Widget | 親か Section | まず意味のある塊で切る |
| 同じ UI が同一画面で複数回出る | private `StatelessWidget` | 呼び出し元 | helper method より Widget |
| 同じ UI が複数画面で出る | shared `Component` | 呼び出し元 | 2回目までは private でもよい |
| 一部だけ provider を読む | `ConsumerWidget` | Provider | `watch` を局所化する |
| 開閉、タブ、hover、focus を持つ | `StatefulWidget` / hooks | Widget ローカル | Provider に上げない |
| snackbar、dialog、navigation を含む | effect 用境界 | `listen` | `watch` と混ぜない |
| 巨大リストを直書きしている | builder 系 Widget | 親 | `ListView.builder` を優先 |
| `if` が増え、UIツリーが読みにくい | 複数 Widget に分岐 | ケースごと | loading/error/empty/data を分離 |

## 分割順序

1. 変わらない純 UI を `const` Widget として切る
2. provider を読む箇所を `ConsumerWidget` に寄せる
3. 一時 UI 状態をローカル Widget に閉じ込める
4. 重い整形や業務ロジックを Provider / Notifier に逃がす
5. 複数ファイルで使うものだけ shared component に昇格する

## 切るかどうかの判定質問

- この部分は別名を付けられるか
- この部分だけ差し替えたい場面があるか
- この部分だけ別のタイミングで再ビルドしたいか
- この部分だけテストしたいか
- この部分の入力値はまとまっているか

1つでも強く yes なら切る候補にする。

## helper method を残してよい場面

- 本当に一度しか出ず、責務境界にもならない
- `context` やテーマ参照をその場で薄く補助するだけ
- provider を読まない
- `const` 化や再利用性を求めていない

それ以外は Widget 化を優先する。

## PR レビュー観点

- `Page` が provider を読みすぎていないか
- 新しい Widget 名が責務を表しているか
- `ConsumerWidget` が広すぎないか
- `StatefulWidget` の state が route をまたぐ共有状態になっていないか
- 共通化が先走って API 過多になっていないか
- `const` を落としていないか

## 公式原則の要点

- Flutter は大きな単一 Widget より、変化境界で分けた複数 Widget を推奨する
- 再利用したい UI は helper method より Widget を推奨する
- `build()` コストを抑えるため、`setState()` や再ビルド境界は葉に寄せる

参考:
- https://docs.flutter.dev/perf/best-practices
- https://api.flutter.dev/flutter/widgets/StatefulWidget-class.html
- https://docs.flutter.dev/ui
