# Law/Term 発見ガイド

対話から Law（守るべき条件）と Term（語彙）を体系的に抽出するガイド。

## Law/Term とは

### Law（守るべき条件）

システムが**常に満たすべき不変条件**。ビジネスルール、制約、ポリシー。

```yaml
Law の4タイプ:
  1. Invariant: 常に真でなければならない条件
  2. Precondition: 操作実行前に満たすべき条件
  3. Postcondition: 操作実行後に保証される条件
  4. Policy: 許可/禁止を定めるルール
```

### Term（語彙）

ドメイン固有の概念を表す語彙。チーム内で共通理解が必要な用語。

```yaml
Term の4タイプ:
  1. Entity: 識別子を持つ概念（ユーザー、注文、商品）
  2. Value Object: 値で区別される概念（メールアドレス、金額、日付範囲）
  3. Context: 状態や条件を表す概念（認証済み、有効期限内、処理中）
  4. Boundary: 範囲や境界を表す概念（許可IP範囲、営業時間、在庫閾値）
```

## 抽出パターン

### Law 抽出パターン

#### パターン1: 「〜しなければならない」→ Invariant

```
User の発言:
「注文確定時、在庫数は必ず0以上でなければならない」

抽出される Law:
LAW-stock-non-negative (Severity: S0)
- Type: Invariant
- 内容: 注文確定時、在庫数 >= 0
- 違反時: 注文を拒否し、エラーを通知
- 検証方法: 注文確定前の在庫チェック
- 観測方法: 在庫テーブルの CHECK制約
```

#### パターン2: 「〜の前に〜が必要」→ Precondition

```
User の発言:
「ユーザーがコメント投稿する前に、必ず認証済みでなければならない」

抽出される Law:
LAW-comment-requires-auth (Severity: S1)
- Type: Precondition
- 内容: コメント投稿には有効な認証トークンが必要
- 違反時: 401 Unauthorized を返す
- 検証方法: ミドルウェアでトークン検証
- 観測方法: 認証エラーメトリクス
```

#### パターン3: 「〜した後は〜が保証される」→ Postcondition

```
User の発言:
「決済完了後、注文ステータスは必ず"支払済み"になる」

抽出される Law:
LAW-payment-sets-status (Severity: S0)
- Type: Postcondition
- 内容: 決済API成功時、order.status = "paid"
- 違反時: ロールバック + アラート
- 検証方法: 決済処理後の status チェック
- 観測方法: ステータス遷移ログ
```

#### パターン4: 「〜してはいけない」→ Policy

```
User の発言:
「一般ユーザーは他人の個人情報にアクセスしてはいけない」

抽出される Law:
LAW-pii-access-restriction (Severity: S0)
- Type: Policy
- 内容: 一般ユーザーは user_id = 自分 のデータのみアクセス可
- 違反時: 403 Forbidden + 監査ログ記録
- 検証方法: 認可チェック
- 観測方法: アクセスログ + アラート
```

#### パターン5: 「〜の範囲内」→ Boundary Constraint

```
User の発言:
「パスワードは8文字以上64文字以下」

抽出される Law:
LAW-password-length (Severity: S1)
- Type: Invariant
- 内容: 8 <= password.length <= 64
- 違反時: バリデーションエラー
- 検証方法: 入力バリデーション
- 観測方法: バリデーションエラーカウント
```

### Term 抽出パターン

#### パターン1: ドメイン固有の名詞 → Entity/Value Object

```
User の発言:
「JWTトークンで認証する」

抽出される Term:
TERM-jwt-token (Type: Value Object)
- 定義: JSON Web Token形式の認証トークン
- 構造: Header.Payload.Signature（Base64エンコード）
- 有効期限: 1時間
- 発行元: /api/auth/login エンドポイント
- 検証方法: 署名検証 + 有効期限チェック
```

```
User の発言:
「注文には複数の商品が含まれる」

抽出される Term:
TERM-order (Type: Entity)
- 定義: 顧客が商品を購入する取引単位
- 識別子: order_id (UUID)
- ライフサイクル: 下書き → 確定 → 支払済み → 発送済み → 完了
- 関連 Law: LAW-stock-non-negative, LAW-payment-sets-status
```

#### パターン2: 状態を表す語 → Context

```
User の発言:
「認証済みユーザーのみアクセス可能」

抽出される Term:
TERM-authenticated-user (Type: Context)
- 定義: 有効なアクセストークンを持つユーザー
- 条件:
  - トークン有効期限内
  - トークン署名が正しい
  - ユーザーアカウントがアクティブ
- 観測方法: 認証ミドルウェアの通過
- 関連 Law: LAW-comment-requires-auth
```

#### パターン3: 範囲を表す語 → Boundary

```
User の発言:
「営業時間内のみ注文受付」

抽出される Term:
TERM-business-hours (Type: Boundary)
- 定義: 注文を受け付ける時間範囲
- 範囲: 平日 9:00-18:00 JST
- 例外: 祝日は休業
- 判定方法: 現在時刻とカレンダーAPI
- 関連 Law: LAW-order-business-hours-only
```

## Severity 判定基準

Law の重要度を S0/S1/S2 で分類。

### S0: ビジネスクリティカル

**基準**: 違反すると金銭損失、法令違反、データ破壊が発生

```yaml
S0 の例:
  - 在庫がマイナスにならない
  - 決済処理が二重実行されない
  - 個人情報が不正アクセスされない
  - 監査ログが改ざんされない
```

**Evidence 要件**:
- L1（ユニットテスト）: 必須
- L2（統合テスト）: 必須
- L3（失敗注入）: 推奨
- L4（本番Telemetry）: 必須

### S1: 機能要件

**基準**: 違反すると機能が正しく動作しない

```yaml
S1 の例:
  - 認証済みユーザーのみコメント投稿可能
  - パスワードは8文字以上
  - メールアドレスは一意
  - ステータス遷移が正しい順序
```

**Evidence 要件**:
- L1（ユニットテスト）: 必須
- L2（統合テスト）: 推奨
- L3（失敗注入）: オプション
- L4（本番Telemetry）: 推奨

### S2: 品質要件

**基準**: 違反するとUXが低下するが、機能は動作する

```yaml
S2 の例:
  - レスポンスタイムが200ms以内
  - エラーメッセージがユーザーフレンドリー
  - ページネーションが効率的
```

**Evidence 要件**:
- L1（ユニットテスト）: オプション
- L2（統合テスト）: オプション
- L4（本番Telemetry）: 推奨

## 抽出ワークフロー

### ステップ1: 対話ログのマーキング

対話ログを読み、Law/Term候補にマーキング:

```
User: ユーザーが認証されていれば、自分のプロフィールを編集できる
      ^^^^^^^^^^^^^^           ^^^^^^^^^^^^^^^^^

Claude:
[Law候補] 認証が必要
[Term候補] 認証されたユーザー、プロフィール
```

### ステップ2: 候補の分類

抽出した候補を Law/Term に分類:

```yaml
Law候補:
  - 「認証が必要」→ Precondition

Term候補:
  - 「認証されたユーザー」→ Context
  - 「プロフィール」→ Entity
```

### ステップ3: 詳細化

Law は SKILL.md の Issue Contract フォーマットで記述:

```yaml
LAW-profile-edit-requires-auth (Severity: S1)
- Type: Precondition
- 内容: プロフィール編集には有効な認証トークンが必要
- 違反時: 401 Unauthorized を返す
- 検証方法: 認証ミドルウェア
- 観測方法: 認証エラーメトリクス
```

Term は定義と境界を記述:

```yaml
TERM-authenticated-user (Type: Context)
- 定義: 有効なアクセストークンを持つユーザー
- 条件: トークン有効期限内 + 署名正しい
- 観測方法: 認証ミドルウェアの通過

TERM-user-profile (Type: Entity)
- 定義: ユーザーの公開プロフィール情報
- 識別子: user_id
- 含まれる属性: 名前、アバター、自己紹介
```

### ステップ4: 相互参照の確立

Law と Term を相互参照:

```yaml
LAW-profile-edit-requires-auth:
  - 参照 Term: TERM-authenticated-user, TERM-user-profile

TERM-authenticated-user:
  - 関連 Law: LAW-profile-edit-requires-auth, LAW-comment-requires-auth
```

## 抽出チェックリスト

以下をすべて満たしていることを確認:

### Law の完全性

- [ ] Type が明示されている（Invariant/Precondition/Postcondition/Policy）
- [ ] Severity が判定されている（S0/S1/S2）
- [ ] 違反時の挙動が定義されている
- [ ] 検証方法が明示されている（どこでチェックするか）
- [ ] 観測方法が明示されている（どうやって測るか）

### Term の完全性

- [ ] Type が明示されている（Entity/Value Object/Context/Boundary）
- [ ] 定義が具体的（抽象語がない）
- [ ] 境界が明確（どこまでが含まれるか）
- [ ] 観測写像がある（どうやって存在を確認するか）

### 最低数の確認

- [ ] Law候補が3個以上
- [ ] Term候補が3個以上
- [ ] Law と Term が相互参照されている（孤立がない）

## 典型的な抽出例

### 例1: 認証機能

```yaml
Law:
  LAW-token-expiry (S0):
    - アクセストークンは1時間で失効する
    - Type: Invariant

  LAW-failed-login-limit (S1):
    - 3回ログイン失敗でアカウント一時ロック
    - Type: Policy

  LAW-refresh-token-rotation (S0):
    - リフレッシュトークン使用時、新しいトークンを発行し古いものを無効化
    - Type: Postcondition

Term:
  TERM-access-token (Value Object):
    - JWT形式の認証トークン
    - 有効期限: 1時間

  TERM-refresh-token (Value Object):
    - リフレッシュ用のランダムトークン
    - 有効期限: 7日間

  TERM-authenticated-user (Context):
    - 有効なアクセストークンを持つユーザー

  TERM-locked-account (Context):
    - 3回以上ログイン失敗したアカウント
    - 解除: 30分経過または管理者による手動解除
```

### 例2: 在庫管理

```yaml
Law:
  LAW-stock-non-negative (S0):
    - 在庫数は常に0以上
    - Type: Invariant

  LAW-stock-reservation (S0):
    - 注文確定時、在庫を予約し引き落とす
    - Type: Postcondition

  LAW-low-stock-alert (S2):
    - 在庫が10以下になったら管理者に通知
    - Type: Policy

Term:
  TERM-product-stock (Value Object):
    - 商品の在庫数
    - 単位: 個数（整数）

  TERM-reserved-stock (Value Object):
    - 注文で予約済みの在庫
    - カート追加後15分間予約

  TERM-available-stock (Boundary):
    - 実在庫 - 予約済み在庫
    - 注文可能な在庫数
```

## `/eld-model-law-discovery` への引き継ぎ

要件ブレインストーミングで抽出した候補は、次のスキルでさらに詳細化:

### 引き継ぎフォーマット

```yaml
Law/Term候補リスト:
  Law:
    - id: LAW-xxx
      initial_description: [ブレストで抽出した内容]
      severity: S0/S1/S2
      type: Invariant/Precondition/Postcondition/Policy
      source: [ユーザーの発言]

  Term:
    - id: TERM-yyy
      initial_description: [ブレストで抽出した内容]
      type: Entity/Value Object/Context/Boundary
      source: [ユーザーの発言]
```

`/eld-model-law-discovery` で以下を追加:

- Law の論理式化
- Term の観測写像定義
- 相互参照の完全性チェック
- Link Map への登録

## よくある間違いと修正例

### 間違い1: Law と Term の混同

```
❌ 悪い例:
LAW-authenticated-user: ユーザーが認証されている

✅ 良い例:
TERM-authenticated-user: 有効なトークンを持つユーザー（Context）
LAW-comment-requires-auth: コメント投稿には認証が必要（Precondition）
```

**理由**: 状態は Term、条件は Law

### 間違い2: Severity の過大評価

```
❌ 悪い例:
LAW-username-max-length (S0): ユーザー名は20文字以下

✅ 良い例:
LAW-username-max-length (S1): ユーザー名は20文字以下
```

**理由**: 違反してもビジネス損失は発生しない → S1

### 間違い3: 検証方法の欠如

```
❌ 悪い例:
LAW-stock-non-negative (S0):
- 内容: 在庫数 >= 0

✅ 良い例:
LAW-stock-non-negative (S0):
- 内容: 在庫数 >= 0
- 検証方法: 注文確定前のSELECT FOR UPDATE + チェック
- 観測方法: CHECK制約 + 在庫マイナスアラート
```

**理由**: 検証・観測方法がないと Grounding（接地）できない

### 間違い4: 抽象語の残存

```
❌ 悪い例:
TERM-active-user: アクティブなユーザー

✅ 良い例:
TERM-active-user (Context):
- 定義: 過去30日以内にログインしたユーザー
- 判定: last_login_at >= NOW() - INTERVAL '30 days'
```

**理由**: 「アクティブ」は抽象的。具体的な条件が必要
