---
name: flutter-widget-splitting
context: fork
description: Flutter Widgetの肥大化を、責務分離・共通化・Riverpod境界の整理でリファクタリングする。build()が長い、Widgetを分割したい、Riverpodのwatch/read/listen/select境界を見直したい、共通化したい、Flutter UIを整理したい時に使用。
---

# Flutter Widget Splitting

Flutter + Riverpod の Widget 分割と共通化を、実装までつながる形で支援する。

## 対象

- Flutter UI
- `flutter_riverpod` / `riverpod`
- 巨大な `build()` / `ConsumerWidget` / 画面単位のリファクタ
- helper method ベースの UI を Widget 化したいケース

## 開始時に確認する

1. 対象ファイル、画面、Widget を特定する
2. 状態管理が Flutter ローカル state か Riverpod かを確認する
3. 変更目的を1行で固定する。可読性、再利用、再ビルド境界、テスト性のどれを優先するか明確にする
4. 分割位置の判定に迷う場合は references/decomposition-checklist.md を読む
5. Riverpod の `watch/read/listen/select` 境界に迷う場合は references/riverpod-boundaries.md を読む

## 基本原則

- 行数ではなく、責務と変化の境界で分割する
- 再利用や再ビルド最適化が欲しい UI は helper method ではなく Widget にする
- `ref.watch` は値を使う最小の Widget まで下ろす
- 共有された業務状態は Provider に置き、一時 UI 状態はローカルに置く
- 副作用は `ref.listen`、書き込みはイベントハンドラ内の `ref.read` に寄せる
- `const` 化と builder 系 Widget を優先する

## ワークフロー

### Step 1: `build()` の中身を4種類に色分けする

- 純 UI: `Text`, `Padding`, `Row`, `Card`, 装飾
- 共有状態: `ref.watch(...)` や ViewModel / Notifier の状態
- 一時 UI 状態: 展開、タブ、入力途中、controller、animation
- 副作用: snackbar, dialog, navigation, submit

### Step 2: 状態の置き場を固定する

- 共有された業務状態: `Provider` / `Notifier` / `AsyncNotifier`
- 一時 UI 状態: `StatefulWidget` / hooks / controller
- 副作用: `ref.listen`
- 書き込み: `ref.read(provider.notifier).method()`

一時 UI 状態を Provider に入れたくなったら、まず route をまたいで共有すべきかを疑う。
`TextEditingController` やフォーム入力途中の値は原則ローカルに置く。

### Step 3: 分割レイヤーを決める

以下の4層で切る。

- `Page`: `Scaffold` と画面全体の骨組み
- `Section`: 意味のある塊。header, list, action bar など
- `Component`: 再利用できる部品。card, row, tile, button group
- `Leaf`: `const` にしやすい最小の表示部品

### Step 4: Riverpod 境界を切る

- 画面ルートで大きく `watch` しない
- provider を読む Widget は `ConsumerWidget` / `Consumer` として局所化する
- 一部プロパティしか使わないなら `select`
- 非同期 provider の一部だけ必要なら `selectAsync`
- `ref.listen` は effect 専用 Widget か画面境界に置く

### Step 5: 下から順に抽出する

1. `const` にできる純 UI を `StatelessWidget` 化する
2. provider を読む Section を `ConsumerWidget` 化する
3. 一時 UI 状態を持つ箇所だけ `StatefulWidget` に閉じ込める
4. helper method を、責務のある Widget に置き換える
5. `build()` 内の整形や条件分岐が重い場合は Provider / Notifier 側へ移す

### Step 6: 共通化は2段階で行う

- まずは画面専用の private widget に切り出す
- 2画面目や3箇所目で再利用が見えたら shared component に昇格する

最初から `CommonCard` や `BaseTile` のような抽象度の高い共通Widgetを作らない。
変わる軸が見えた後で API を作る。

### Step 7: 仕上げに確認する

- `Page` が provider を読みすぎていないか
- `watch` が最小境界にあるか
- `listen` と `read` の役割が分かれているか
- `family` / 引数付き provider が不要に保持されていないか
- `const` と builder 系を落としていないか
- `flutter analyze` / `flutter test` があれば回す

## 典型パターン

### helper method を Widget にする

```dart
class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        ProfileHeader(),
        ProfileStats(),
      ],
    );
  }
}
```

### provider 読み取りを Section に閉じ込める

```dart
class ProfileStats extends ConsumerWidget {
  const ProfileStats({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final followers = ref.watch(profileProvider.select((it) => it.followers));
    final posts = ref.watch(profileProvider.select((it) => it.posts));

    return StatsRow(followers: followers, posts: posts);
  }
}
```

### 副作用は `listen`、更新は `read`

```dart
class SaveProfileButton extends ConsumerWidget {
  const SaveProfileButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen(saveProfileProvider, (_, next) {
      next.whenOrNull(
        data: (_) => ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Saved')),
        ),
      );
    });

    return FilledButton(
      onPressed: () => ref.read(saveProfileProvider.notifier).save(),
      child: const Text('Save'),
    );
  }
}
```

## 禁止寄りのパターン

- 画面ルートで巨大な `ConsumerWidget` を作り、複数 provider をまとめて `watch` する
- `read` で再ビルドを無理に避ける
- controller やフォーム途中値を Provider に載せる
- 副作用を `build()` や `watch` と混ぜる
- 再利用したい UI を `_buildHeader()` のような method のまま維持する
- 早すぎる汎用化で抽象度だけ高い共通Widgetを作る

## 出力

最終的に以下を返す。

- どこで分割するか
- 各 Widget の責務
- Provider / Widget の状態所有
- `watch/read/listen/select` の配置
- 必要ならリファクタ後のコード差分
