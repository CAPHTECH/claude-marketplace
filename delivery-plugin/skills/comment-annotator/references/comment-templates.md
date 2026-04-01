# Comment Templates by Role

役割別の具体的なコメント例。コメントの粒度やトーンの参考として使う。
全例はコード・テスト・コミットメッセージから読み取れる事実に基づいている。

## Table of Contents
- [Controller / Entry Point](#controller--entry-point)
- [Middleware](#middleware)
- [Service / Orchestrator](#service--orchestrator)
- [Domain Model](#domain-model)
- [Repository / Data Access](#repository--data-access)
- [Worker](#worker)
- [Migration](#migration)
- [Utility / Helper](#utility--helper)
- [Config / Infra](#config--infra)
- [UI](#ui)
- [Test](#test)

---

## Controller / Entry Point

```typescript
// POST /users に年齢バリデーションを追加。
// 13歳未満のアカウント作成を拒否する（Issue #567）。
```

```python
# 未認証リクエストの処理を経路で分岐する。
# ブラウザ: ログインページへリダイレクト。
# API経路（/api/*）: JSON 401を返す。
```

---

## Middleware

```typescript
// レート制限は認証ミドルウェアの後に適用する。
// 認証済みユーザーと未認証リクエストで閾値を分けるため。
```

```go
// ヘルスチェックパス（/healthz）はこのミドルウェアをスキップする。
// ロードバランサーの疎通確認が認証でブロックされるのを防ぐ。
```

---

## Service / Orchestrator

```typescript
// 注文確定→在庫引当→決済の順序は意図的。
// 決済前に在庫を確保することで、決済成功後に在庫切れになる事態を防ぐ。
```

```python
# このメソッドは呼び出し元が開始したトランザクション内で実行される前提。
# 単独で呼ぶとデータ不整合が起きる。
```

```java
// 外部API呼び出しのリトライは3回まで。固定間隔1秒。
```

---

## Domain Model

```typescript
// Order.status は Created→Confirmed→Shipped→Delivered の
// 一方向遷移のみ許可。逆方向遷移やスキップは不変条件違反。
```

```python
# amount=0 は有効な値。無料トライアルやクレジット相殺で発生する。
# 0を不正値として弾かないこと。
```

```go
// 金額は int64（cents単位）で保持。
// float64 は10進小数の丸め誤差があるため金額計算に不適。
```

---

## Repository / Data Access

```typescript
// JOIN ではなく2回の SELECT に分離。
// 各テーブルのインデックスを個別に活用するため。
```

```python
# LIMIT+1 で取得し、余分な1件の有無で次ページ存在を判定。
# COUNT(*) を避けてページネーションのコストを抑える。
```

```go
// このクエリはread replicaに向ける前提。
// 書き込み直後の読み取り整合性が必要な場合はprimaryを使うこと。
```

---

## Worker

```typescript
// このジョブは冪等。同じメッセージの再配信で副作用は発生しない。
// messageId で処理済み判定している。
```

```python
# 失敗時は指数バックオフで最大5回リトライ。
# 5回失敗するとデッドレターキューに移動する。
```

---

## Migration

```sql
-- この列は NULL 許可で追加し、バックフィル後に NOT NULL 制約を追加する。
-- 2段階に分けることでテーブルロックを最小化する。
```

```python
# このマイグレーションは不可逆。ロールバック時はバックアップから復元する。
```

---

## Utility / Helper

```typescript
// 空文字列は null として扱う。
// フォーム送信の空文字とフィールド未送信（undefined）を同一視する仕様。
```

```python
# 正規表現ではなく手動パースを使用。
# 入力パターンが3種のみで、正規表現は可読性に見合わない。
```

```go
// この関数はスレッドセーフではない。
// 並行呼び出し時は呼び出し元で排他制御すること。
```

---

## Config / Infra

```yaml
# タイムアウトを30sから60sに変更。
# 下流サービスのレスポンスが従来の閾値を超えるケースに対応。
```

```dockerfile
# マルチステージビルドでランタイムイメージを軽量化。
# ビルド依存はbuilderステージに閉じる。
```

---

## UI

```tsx
// このコンポーネントは非制御（uncontrolled）で動作する。
// 親から value を渡されている場合は制御モードに切り替わる。
```

```tsx
// aria-live="polite" でスクリーンリーダーに変更を通知する。
// polite はユーザーの現在の操作を中断しない。
```

---

## Test

```typescript
// Issue #345 の回帰テスト。
// UTC+14 タイムゾーンで日付計算が1日ずれるバグの再発を防止。
```

```python
# 正常系のみ検証。異常系（ネットワークエラー、タイムアウト）は
# integration test でカバー（tests/integration/payment_test.py）。
```
