# 導入順序

最初から完全形式化に振り切らない。差分で効く順に導入する。

## 推奨順序

1. 要件原子化、要件ID付与、トレーサビリティ表
2. property-based test、stateful test、mutation testing
3. 高リスク領域だけ形式仕様化
4. OpenTelemetry などで要件IDを持つ観測
5. 変更差分ベースの自動再検査

## 各段階の完了条件

### 1. 要件原子化

- 高リスク要件に `REQ-xxx` が振られている
- `observable` と `negative_examples` が埋まっている

### 2. テスト強化

- 例示テストだけでなく property-based test がある
- mutation survivor を一覧で見られる

### 3. 形式仕様化

- 高リスク要件に少なくとも一つの `F_i` がある
- 二重形式化差分を試せる

### 4. 実行時観測

- `req.id` を trace または event に付与している
- 要件違反を追えるクエリまたはルールがある

### 5. 自動再検査

- Rule A と Rule B を差分ゲートに入れている
- witness bundle を CI 出力として残せる
