# 原子タスクの定義（Atomic Task Definition）

原子タスク = **5-10分で完了する最小単位のタスク**

## 原子性の5つの基準

### 1. 単一の概念変更

1つのシンボル、Law、Termに集中したタスク。

**Good**:
```
タスク: User型にemail: stringフィールドを追加
  - 1つの型定義に1つのフィールド追加
  - スコープが明確
```

**Bad**:
```
タスク: User型を拡張してバリデーションを追加
  - 型定義+バリデーションロジック（2つの概念）
  - スコープが曖昧
```

### 2. 独立してテスト可能

他のタスクに依存せず、単独でテスト・検証できる。

**Good**:
```
タスク: calculateDiscount()関数の実装
  - 関数単体でユニットテスト可能
  - 依存する型定義は既に存在
```

**Bad**:
```
タスク: calculateDiscount()とapplyDiscount()の実装
  - 2つの関数が相互に依存
  - 単独テストが困難
```

### 3. ロールバック可能

git checkout で簡単に元に戻せる粒度。

**Good**:
```
タスク: ProductRepository.findById() メソッド追加
  - 1つのメソッド追加のみ
  - git checkout で即座に戻せる
```

**Bad**:
```
タスク: ProductRepositoryリファクタリング
  - 複数メソッドの変更
  - ロールバック時に部分的な変更が残る可能性
```

### 4. Evidence Ladder L0以上で検証可能

最低でもL0（型チェック、lint）で検証できる。

**Evidence Ladderレベル**:
- **L0**: 型チェック、lint（静的検証）
- **L1**: ユニットテスト
- **L2**: 統合テスト
- **L3**: 失敗注入テスト
- **L4**: 本番Telemetry

**Good**:
```
タスク: OrderStatus型の定義
  - Evidence Level: L0（tsc型チェック）
  - Verification: enum定義の型チェック通過
```

**Bad**:
```
タスク: 全体的なコード品質改善
  - 検証方法が不明
  - Evidence Levelが不明確
```

### 5. 1タスク = 1コミット の原則

原子タスク1つにつき、1つのコミット。

**Good**:
```
1. タスク: User型にemailフィールド追加
   → コミット: "Add email field to User type"

2. タスク: emailのバリデーション関数追加
   → コミット: "Add email validation function"
```

**Bad**:
```
1. タスク: User型とバリデーションをまとめて実装
   → コミット: "Add user features" (範囲が広すぎる)
```

## 粒度の目安

| タスクサイズ | 時間目安 | 行数目安 | 例 |
|------------|---------|---------|-----|
| **原子タスク** | 5-10分 | 10-50行 | 型定義追加、1関数の実装、1テスト追加 |
| **子タスク** | 20-40分 | 50-200行 | モジュール実装、API層実装 |
| **親タスク** | 2-4時間 | 200-1000行 | 機能全体の実装 |

### 時間の内訳（原子タスク）

```
5-10分の内訳:
  - コード作成: 3-5分
  - テスト実行: 1-2分
  - 確認・リファクタリング: 1-2分
  - コミット: 30秒-1分
```

## 原子タスクの実践例

### 例1: 型定義の追加

```yaml
task:
  name: TERM-jwt-payload 型定義追加
  level: L0
  verification: tsc型チェック通過
  law_term: [TERM-jwt-payload]
  time_estimate: 5min

steps:
  1. src/auth/types.ts に JwtPayload interface 定義
  2. tsc --noEmit で型チェック
  3. コミット: "Add JwtPayload type definition"
```

**実際のコード（~20行）**:
```typescript
// src/auth/types.ts
export interface JwtPayload {
  userId: string;
  email: string;
  iat: number;  // issued at
  exp: number;  // expiration
}
```

### 例2: ユニットテスト付き関数実装

```yaml
task:
  name: calculateDiscount() 関数実装
  level: L1
  verification: ユニットテスト（正常系+境界値）
  law_term: [LAW-discount-rate-max-50]
  time_estimate: 8min

steps:
  1. src/pricing/discount.ts に関数実装
  2. tests/pricing/discount.test.ts にテスト追加
  3. npm test で検証
  4. コミット: "Implement calculateDiscount function"
```

**実際のコード（~40行）**:
```typescript
// src/pricing/discount.ts
export function calculateDiscount(price: number, rate: number): number {
  if (rate < 0 || rate > 0.5) {
    throw new Error('Discount rate must be between 0 and 0.5');
  }
  return price * (1 - rate);
}

// tests/pricing/discount.test.ts
describe('calculateDiscount', () => {
  it('正常系: 20%割引', () => {
    expect(calculateDiscount(1000, 0.2)).toBe(800);
  });

  it('境界値: 50%割引（上限）', () => {
    expect(calculateDiscount(1000, 0.5)).toBe(500);
  });

  it('異常系: 50%超の割引は拒否', () => {
    expect(() => calculateDiscount(1000, 0.6)).toThrow('Discount rate');
  });
});
```

## 原子タスク分解のパターン

### パターン1: 型ファースト分解

```
親タスク: User認証機能
  ↓
子タスク: JWT認証コア
  ↓
原子タスク:
  1. TERM-jwt-payload 型定義（5min, L0）
  2. TERM-jwt-secret 型定義（5min, L0）
  3. generateToken() 実装（8min, L1）
  4. verifyToken() 実装（8min, L1）
```

### パターン2: Law駆動分解

```
親タスク: 在庫管理機能
  ↓
子タスク: 在庫引当処理
  ↓
原子タスク（Lawごと）:
  1. LAW-stock-non-negative: 在庫チェック実装（7min, L1）
  2. LAW-reservation-atomic: トランザクション実装（9min, L1）
  3. LAW-concurrent-reserve: 排他制御実装（10min, L1）※時間オーバー注意
```

## アンチパターン

### ❌ アンチパターン1: 粒度が粗すぎる

```yaml
# Bad: 30分超のタスク
task:
  name: ユーザー認証機能を実装
  time_estimate: 2時間  # 原子タスクではない
```

**修正**: 子タスク→原子タスクに分解
```yaml
# Good: 原子タスクに分解
子タスク: JWT認証コア（30-40min）
  原子タスク:
    - JWT型定義（5min）
    - トークン生成（8min）
    - トークン検証（8min）
```

### ❌ アンチパターン2: 複数の概念を含む

```yaml
# Bad: 複数の概念
task:
  name: User型とバリデーションを追加
  law_term: [TERM-user, LAW-email-format]  # 2つの概念
```

**修正**: 概念ごとに分離
```yaml
# Good: 概念を分離
task1:
  name: TERM-user 型定義追加
  law_term: [TERM-user]

task2:
  name: LAW-email-format バリデーション実装
  law_term: [LAW-email-format]
```

### ❌ アンチパターン3: Evidence不明

```yaml
# Bad: 検証方法が不明
task:
  name: パフォーマンス改善
  verification: ???
```

**修正**: Evidence Levelと検証方法を明示
```yaml
# Good: Evidence明示
task:
  name: calculateTotal()のキャッシュ追加
  level: L1
  verification: ユニットテスト（パフォーマンステスト含む）
  law_term: [LAW-response-time-200ms]
```

## 原子タスクの停止条件

以下の場合、タスクが大きすぎる可能性：

1. **15分を超える**: タスクを2つに分割
2. **複数のLaw/Termに依存**: Law/Termごとに分割
3. **ロールバックが複雑**: 変更範囲を小さく
4. **テストが書きにくい**: 責務が不明確、分割が必要

## 原子タスク完了チェックリスト

- [ ] 5-10分で完了した
- [ ] 単一の概念変更のみ
- [ ] Evidence L0以上で検証済み
- [ ] Law/Termに紐付いている
- [ ] 独立したコミットを作成
- [ ] ロールバック可能な状態
- [ ] 次のタスクに影響を与えない

## まとめ

### 原子タスクの核心原則

1. **時間**: 5-10分で完了
2. **単一性**: 1つの概念、1つのシンボル、1つのLaw/Term
3. **検証可能性**: Evidence L0以上で検証
4. **独立性**: 他タスクに依存しない
5. **可逆性**: git checkout で簡単に戻せる

### 原子タスク分解の恩恵

- 手戻りコストの最小化（10分以内のロールバック）
- 並列作業の可能性（独立タスク）
- 進捗の可視化（細かい粒度でのコミット）
- コードレビューの容易さ（小さな変更）
- テストの信頼性（単一概念のテスト）
