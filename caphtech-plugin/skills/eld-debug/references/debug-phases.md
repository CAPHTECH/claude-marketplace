# デバッグフェーズ詳細手順

各フェーズの具体的な実行手順とチェックポイント。

## Phase 1: Sense（症状の観測）

### 1.1 症状の初期記録

```yaml
# 症状記録テンプレート
症状ID: DEBUG-YYYY-MM-DD-NNN
報告者: <誰が発見したか>
発生日時: <いつ発生したか>

現象:
  概要: <何が起きているか（1行）>
  詳細: <詳しい説明>
  期待動作: <本来どうあるべきか>
  実際動作: <何が起きたか>

再現:
  確率: [常に | 頻繁 | 時々 | 稀 | 一度のみ]
  手順:
    1. <ステップ1>
    2. <ステップ2>
  環境: <OS、ブラウザ、バージョンなど>

影響:
  ユーザー: <影響を受けるユーザー層>
  機能: <影響を受ける機能>
  緊急度: [Critical | High | Medium | Low]
```

### 1.2 変数の観測

**観測すべき変数の種類**:

| カテゴリ | 例 | 観測方法 |
|----------|-----|----------|
| 入力値 | リクエストパラメータ、ユーザー入力 | ログ、リクエストダンプ |
| 状態変数 | DBの値、メモリ上の状態 | デバッガ、クエリログ |
| 環境変数 | 設定値、環境依存値 | 設定ダンプ、env出力 |
| タイミング | 実行順序、タイムスタンプ | トレース、タイムライン |

**観測記録フォーマット**:
```yaml
観測変数:
  - 名前: stock
    期待値: 100
    実際値: -5
    差異: 法則違反（負の在庫）
    観測方法: DBクエリ
    観測時刻: 2024-01-15T10:30:00Z

  - 名前: reserved
    期待値: ≤ stock
    実際値: 105
    差異: 法則違反（予約超過）
    観測方法: デバッガ
    観測時刻: 2024-01-15T10:30:05Z
```

### 1.3 法則候補の列挙

**法則の探し方**:

1. **明示的な法則を確認**
   - ドキュメント化されたビジネスルール
   - コード内のアサーション/バリデーション
   - テストケースの期待値

2. **暗黙の法則を推測**
   - データ整合性の制約
   - 状態遷移の制約
   - 時間的な制約

3. **過去の法則を参照**
   - pce-memoryから関連Law/Termを検索
   - 類似バグの記録を確認

```yaml
法則候補:
  - Law名: 在庫保存則
    カテゴリ: Invariant
    論理式: stock = available + reserved
    関連性: 高（観測された変数が直接関係）

  - Law名: 非負在庫制約
    カテゴリ: Invariant
    論理式: ∀t. stock(t) ≥ 0
    関連性: 高（負の在庫が観測された）

  - Law名: 予約上限制約
    カテゴリ: Pre
    論理式: reserve(amount) requires available ≥ amount
    関連性: 中（予約処理に関係しそう）
```

## Phase 2: Model（法則違反の仮説形成）

### 2.1 法則の明示化

**暗黙の法則を言語化する手順**:

1. 「常に成り立つべきこと」を列挙
2. 「この操作の前に満たすべきこと」を列挙
3. 「この操作の後に保証すべきこと」を列挙
4. 「組織として守るべきルール」を列挙

### 2.2 論理式への変換

**自然言語 → 論理式 変換パターン**:

| 自然言語 | 論理式 |
|----------|--------|
| 「すべての〜は〜である」 | ∀x. P(x) |
| 「〜ならば〜である」 | P → Q |
| 「〜かつ〜」 | P ∧ Q |
| 「〜または〜」 | P ∨ Q |
| 「〜でない」 | ¬P |
| 「いつでも〜」 | □P (時相論理) |
| 「いずれ〜になる」 | ◇P (時相論理) |

**例**:
```
自然言語: 「利用可能在庫は、総在庫から予約済み在庫を引いたもの」
論理式: ∀t. available(t) = stock(t) - reserved(t)

自然言語: 「予約は利用可能在庫を超えてはならない」
論理式: reserve(amount) → amount ≤ available
```

### 2.3 仮説の構築

**仮説構築フレームワーク**:

```yaml
仮説:
  ID: H1
  主張: <何が原因と考えるか>

  根拠（この仮説を支持する観測事実）:
    - <観測事実1>
    - <観測事実2>

  反証条件（この仮説が間違っている場合に観測されるはずのこと）:
    - <反証条件1>
    - <反証条件2>

  検証方法:
    - <この仮説を確認する方法>

  優先度: [高 | 中 | 低]
  理由: <なぜこの優先度か>
```

**複数仮説の管理**:
```yaml
仮説一覧:
  - ID: H1
    主張: 並行処理での二重加算
    優先度: 高
    状態: 検証中

  - ID: H2
    主張: トランザクション境界の誤り
    優先度: 中
    状態: 未検証

  - ID: H3
    主張: キャッシュと DB の不整合
    優先度: 低
    状態: 棄却（根拠不足）
```

## Phase 3: Predict（影響予測）

### 3.1 影響範囲の分析

**影響の分類**:

| 種類 | 説明 | 分析方法 |
|------|------|----------|
| 直接影響 | 法則違反の直接的な結果 | 観測された症状 |
| データ影響 | 不正なデータの伝播 | データフロー分析 |
| 機能影響 | 動作しなくなる機能 | 依存関係分析 |
| ユーザー影響 | ユーザーへの影響 | ユーザーストーリー分析 |

```yaml
影響分析:
  直接影響:
    - 在庫数が負になる
    - 注文処理が失敗する

  データ影響:
    - 影響するテーブル: [orders, inventory, reports]
    - 影響するレコード数: 約100件/日

  機能影響:
    - 注文機能: 一部失敗
    - 在庫表示: 不正確
    - レポート: 数値不整合

  ユーザー影響:
    - 影響ユーザー: 約1%の注文ユーザー
    - 体験への影響: 注文失敗、カスタマーサポート対応必要
```

### 3.2 修正の副作用予測

```yaml
副作用予測:
  パフォーマンス:
    - リスク: ロック導入による遅延
    - 程度: 推定10-20ms増加
    - 許容可能性: 許容範囲内

  互換性:
    - リスク: APIレスポンス形式の変更
    - 程度: 下位互換維持
    - 許容可能性: 問題なし

  他機能への影響:
    - リスク: 在庫レポート機能への影響
    - 程度: 軽微（タイミング変更のみ）
    - 許容可能性: 要確認
```

### 3.3 停止条件の設定

```yaml
停止条件:
  - 条件: テスト失敗が3回連続
    対応: アプローチの見直し、仮説の再検討

  - 条件: 予期しない機能への影響を発見
    対応: 影響分析をやり直し

  - 条件: 修正で新たな法則違反が発生
    対応: ロールバック、設計からやり直し

  - 条件: 8時間以上の調査で進展なし
    対応: 他者に相談、ペアデバッグ
```

## Phase 4: Change（法則復元）

### 4.1 変更戦略の選択

| 戦略 | 適用場面 | リスク |
|------|----------|--------|
| **直接修正** | 原因が明確、影響範囲が限定的 | 低 |
| **ラッパー追加** | 既存コードを変更したくない | 中 |
| **リファクタリング** | 構造的問題が根本原因 | 高 |
| **設定変更** | 設定値の誤りが原因 | 低 |
| **データ修正** | 不正データが原因 | 中 |

### 4.2 変更の実行

**変更前チェックリスト**:
- [ ] 仮説が十分に検証されている
- [ ] 影響範囲を把握している
- [ ] ロールバック手順がある
- [ ] 変更後の検証方法が決まっている

**変更記録**:
```yaml
変更:
  対象ファイル: src/services/inventory.ts
  変更内容: |
    予約処理をトランザクションで囲む
    - Before: 個別のDB操作
    - After: 単一トランザクション内で実行

  意図: |
    並行処理での二重加算を防ぎ、
    在庫保存則（stock = available + reserved）を維持する

  差分:
    ```diff
    - await db.update('inventory', { available: available - amount });
    - await db.update('inventory', { reserved: reserved + amount });
    + await db.transaction(async (tx) => {
    +   await tx.update('inventory', { available: available - amount });
    +   await tx.update('inventory', { reserved: reserved + amount });
    + });
    ```
```

## Phase 5: Ground（証拠による検証）

### 5.1 検証計画

```yaml
検証計画:
  L0_静的検証:
    - 型チェック: tsc --noEmit
    - Lint: eslint src/
    期待結果: エラー0

  L1_ユニットテスト:
    - 新規テスト: 保存則のProperty-based test
    - 既存テスト: 在庫関連テストすべて
    期待結果: 全パス

  L2_統合テスト:
    - テスト: 並行予約の統合テスト
    - 手動確認: 実際の操作で再現しないこと
    期待結果: 全パス、再現なし

  L3_異常系テスト:
    - テスト: タイムアウト時の保存則維持
    - テスト: 並行処理での競合
    期待結果: 法則維持

  L4_本番検証:
    - 監視: 保存則違反のアラート設定
    - 期間: 1週間
    期待結果: 違反検出0
```

### 5.2 テスト作成パターン

**法則を直接テストする**:
```typescript
// L1: 保存則のProperty-based test
describe('在庫保存則', () => {
  it('任意の操作後も stock = available + reserved', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: 1000 }),
      fc.array(fc.oneof(
        fc.record({ type: fc.constant('reserve'), amount: fc.integer({ min: 1, max: 100 }) }),
        fc.record({ type: fc.constant('release'), amount: fc.integer({ min: 1, max: 100 }) })
      )),
      (initial, operations) => {
        const inv = new Inventory(initial);
        operations.forEach(op => {
          try {
            if (op.type === 'reserve') inv.reserve(op.amount);
            else inv.release(op.amount);
          } catch (e) { /* 正常な拒否は無視 */ }
        });
        // Law: stock === available + reserved
        return inv.total === inv.available + inv.reserved;
      }
    ));
  });
});
```

**バグの再発を防ぐ回帰テスト**:
```typescript
// 具体的なバグケースをテスト化
describe('バグ回帰テスト', () => {
  it('DEBUG-2024-01-15-001: 並行予約で在庫が負にならない', async () => {
    const inv = new Inventory(100);

    // 並行で予約を実行
    await Promise.all([
      inv.reserve(60),
      inv.reserve(60)
    ]);

    // 法則: 在庫は非負
    expect(inv.available).toBeGreaterThanOrEqual(0);
    // 法則: 保存則
    expect(inv.total).toBe(inv.available + inv.reserved);
  });
});
```

### 5.3 検証結果記録

```yaml
検証結果:
  達成レベル: L2

  L0:
    状態: Pass
    詳細: 型エラー0、Lint警告0

  L1:
    状態: Pass
    詳細: |
      - 保存則Property-based test: 1000回実行、全パス
      - 既存ユニットテスト: 45件パス

  L2:
    状態: Pass
    詳細: |
      - 並行予約テスト: パス
      - 手動再現テスト: 再現せず

  L3:
    状態: 未実施
    理由: L2で十分と判断

  L4:
    状態: 進行中
    詳細: 本番監視中（1週間）
```

## Phase 6: Record（知識の蓄積）

### 6.1 バグパターンの記録

```yaml
バグパターン:
  ID: BUG-PATTERN-001
  名前: 並行処理での二重計上
  法則違反タイプ: Invariant

  症状:
    - 数値の不整合（負の値、超過）
    - 間欠的な発生
    - 負荷時に顕著

  根本原因:
    カテゴリ: 実装
    詳細: |
      複数の状態更新を非原子的に実行したため、
      並行実行時に中間状態が見えてしまった

  検出方法:
    静的: 状態更新の原子性をコードレビューで確認
    動的: 並行実行テスト、負荷テスト
    監視: 不変条件のリアルタイムチェック

  防止策:
    設計: 状態更新は常にトランザクション内で
    実装: STMまたは明示的ロックの使用
    レビュー: 並行処理チェックリストの適用

  関連パターン:
    - TOCTOU (Time-of-check to time-of-use)
    - Lost Update
    - Race Condition
```

### 6.2 Law/Term Cardの更新

```yaml
# 新規または更新したLaw Card
Law:
  ID: LAW-INV-001
  名前: 在庫保存則
  カテゴリ: Invariant
  スコープ: inventory-service

  定義:
    論理式: ∀t. stock(t) = available(t) + reserved(t)
    自然言語: 総在庫は利用可能在庫と予約済み在庫の和に等しい

  違反時動作:
    検出: ランタイムアサーション、メトリクス
    対応: アラート発報、ロールバック

  接地:
    L1: property-based test (inventory.spec.ts:45)
    L2: integration test (inventory.integration.spec.ts:120)
    L4: metrics (inventory_conservation_law_valid gauge)

  関連Term:
    - TERM-001: 在庫（Stock）
    - TERM-002: 利用可能在庫（Available）
    - TERM-003: 予約済み在庫（Reserved）

  履歴:
    - 2024-01-15: 作成（DEBUG-2024-01-15-001の修正時）
```

### 6.3 pce-memoryへの記録

```typescript
// バグパターンの記録
await pce.memory.upsert({
  text: "バグパターン: 並行処理での二重計上 - 複数の状態更新を非原子的に実行すると並行実行時に不整合が発生。対策: トランザクション使用、STM、明示的ロック",
  kind: "fact",
  scope: "project",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    note: "DEBUG-2024-01-15-001の修正から学習"
  }
});

// 法則の記録
await pce.memory.upsert({
  text: "Law: 在庫保存則 - ∀t. stock(t) = available(t) + reserved(t) - 総在庫は利用可能と予約済みの和。接地: Property-based test + メトリクス監視",
  kind: "fact",
  scope: "project",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    note: "inventory-service の中核法則"
  }
});
```
