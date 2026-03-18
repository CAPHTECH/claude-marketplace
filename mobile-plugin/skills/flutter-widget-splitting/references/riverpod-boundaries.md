# Riverpod Boundaries

対象画面が Riverpod を使っている時だけ読む。
目的は `watch/read/listen/select` の責務を混ぜないこと。

## API の置き場所

| やりたいこと | 使う API | 置く場所 | 避けること |
|--------------|----------|----------|------------|
| 画面表示を状態に追従させる | `ref.watch` | 値を使う最小 Widget | ルートでまとめて watch |
| 更新操作を呼ぶ | `ref.read(provider.notifier)` | `onPressed` などのイベント | `build()` で read |
| snackbar / dialog / navigation | `ref.listen` | effect 用の境界 | `watch` 内で副作用 |
| オブジェクトの一部だけ使う | `select` | `watch` する Widget | オブジェクト全体を watch |
| AsyncValue の一部だけ使う | `selectAsync` | provider / async logic | `future` と UI ロジックの混在 |

## 状態所有の原則

- Provider は共有された業務状態に使う
- 一時 UI 状態は Widget ローカルに置く
- `TextEditingController`、フォーム途中値、hover、focus、animation は原則 local
- 「戻る」で元の状態に戻るべき情報を Provider に置く時は特に注意する

## Notifier 設計

- 読み取り状態は `Provider` / `FutureProvider` / `StreamProvider`
- 書き込みや状態変更は `Notifier` / `AsyncNotifier`
- 初期化ロジックを constructor に置かず `build` に置く
- UI からは `ref.read(provider.notifier).method()` だけを呼ぶ

## dispose / caching

- 引数付き provider は基本 `autoDispose` 前提で考える
- `keepAlive` は理由がある時だけ使う
- 「速くしたいから keepAlive」ではなく、保持要件があるかで決める

## 静的参照

- provider は top-level `final` で静的に分かる形を優先する
- Widget 引数や配列から動的に provider を組み立てすぎない
- lint が効く形を崩さない

## よくある失敗

- ルート `ConsumerWidget` が5個以上の provider を `watch` している
- `read` で見た目更新まで済ませようとする
- provider にフォーム状態を入れて戻る操作を壊す
- `listen` を置かず、`AsyncValue` の分岐に副作用を書いてしまう
- `select` で mutable な `List` を返してしまう

## 公式原則の要点

- Riverpod は `ConsumerWidget` / `ConsumerStatefulWidget` を基本にする
- 一時 UI 状態に Provider を多用しない
- `watch/read/listen` を役割で分ける
- `select` は再ビルド削減に有効だが、必要な場所だけに使う

参考:
- https://riverpod.dev/docs/concepts2/consumers
- https://riverpod.dev/docs/root/do_dont
- https://riverpod.dev/docs/concepts2/providers
- https://riverpod.dev/docs/how_to/select
- https://riverpod.dev/docs/how_to/eager_initialization
