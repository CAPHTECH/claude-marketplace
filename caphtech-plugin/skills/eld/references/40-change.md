# Change（変更）フェーズ

最小単位で変更し、Pure/IO分離を優先する。

## 目的

- 微小ステップで確実に前進
- 副作用を局所化してテスト容易性を確保
- Lawを実装レベルで保証

## 変更の原則

### 1. 最小単位で変更

1ステップ = 1概念の変更

```
❌ 一度に複数の概念を変更
   「認証ロジック変更 + DB スキーマ変更 + UI 更新」

✅ 概念ごとに分離して変更
   Step 1: 認証ロジック変更
   Step 2: DB スキーマ変更
   Step 3: UI 更新
```

### 2. Pure/IO分離

```
Law判定（Pure） → IO境界（副作用）
```

**Pure関数の特徴**:
- 同じ入力に対して常に同じ出力
- 外部状態を変更しない
- テストが容易

**IO境界の特徴**:
- DB/API/ファイル等の外部アクセス
- 副作用を集約
- モックが必要

### 3. 即時静的診断

変更ごとに以下を確認:
- 型チェック
- lint
- 依存関係

## 実装パターン

### Law実装パターン

```typescript
// Pure: Law判定
function validateOrderQuantity(qty: number): Result<OrderQuantity, ValidationError> {
  // LAW-order-quantity-range の実装
  if (qty < 1 || qty > 100) {
    return Err(new ValidationError('注文数量は1〜100の範囲'));
  }
  return Ok(OrderQuantity.of(qty));
}

// IO境界: 外部アクセス
async function createOrder(input: OrderInput): Promise<Result<Order, Error>> {
  // Pure: 入力検証
  const qtyResult = validateOrderQuantity(input.quantity);
  if (qtyResult.isErr()) return qtyResult;
  
  // IO: DB保存
  const order = await orderRepository.save({
    quantity: qtyResult.value,
    ...
  });
  
  return Ok(order);
}
```

### Term実装パターン

```typescript
// TERM-order-quantity の実装

// 1. ブランド型で型レベルの区別
type OrderQuantity = Brand<number, 'OrderQuantity'>;

// 2. スマートコンストラクタで検証
const OrderQuantity = {
  of(value: number): Result<OrderQuantity, ValidationError> {
    if (value < 1 || value > 100) {
      return Err(new ValidationError('注文数量は1〜100の範囲'));
    }
    return Ok(value as OrderQuantity);
  },
  
  // 3. 境界での検証
  fromInput(input: unknown): Result<OrderQuantity, ValidationError> {
    const parsed = z.number().min(1).max(100).safeParse(input);
    if (!parsed.success) {
      return Err(new ValidationError(parsed.error.message));
    }
    return Ok(parsed.data as OrderQuantity);
  }
};
```

### 違反時動作パターン

```typescript
// 違反分類に応じた処理
type ViolationType = 
  | 'Bug'           // プログラムエラー → 500 + アラート
  | 'UserError'     // ユーザー入力エラー → 400 + メッセージ
  | 'BusinessException' // ビジネスルール違反 → 422 + 説明
  | 'DataDrift'     // データ整合性崩れ → 500 + 緊急対応
  | 'Compliance'    // コンプライアンス違反 → 500 + 監査ログ

function handleViolation(violation: LawViolation): Response {
  // ログ記録（すべての違反）
  logger.error('Law violation', {
    lawId: violation.lawId,
    type: violation.type,
    context: violation.context
  });
  
  // テレメトリ送信（S0/S1）
  if (violation.severity <= 1) {
    telemetry.increment(`law.violation.${violation.lawId}`);
  }
  
  // 違反タイプに応じた応答
  switch (violation.type) {
    case 'Bug':
      return internalError('予期せぬエラーが発生しました');
    case 'UserError':
      return badRequest(violation.message);
    case 'BusinessException':
      return unprocessableEntity(violation.message);
    case 'DataDrift':
      alertOps(violation);
      return internalError('データ整合性エラー');
    case 'Compliance':
      auditLog(violation);
      return internalError('コンプライアンスエラー');
  }
}
```

## 変更手順テンプレート

```markdown
## 変更計画

### 前提条件
- [ ] Predictフェーズの影響分析完了
- [ ] 関連するLaw/Termの確認完了
- [ ] テスト環境の準備完了

### Step 1: <変更内容>

**変更ファイル**:
- `path/to/file.ts`

**変更内容**:
- <具体的な変更>

**検証**:
- [ ] 型チェック通過
- [ ] lint通過
- [ ] 既存テスト通過

**ロールバック**:
- `git checkout path/to/file.ts`

---

### Step 2: <次の変更内容>
...
```

## 禁止パターン

### 1. 型システムの回避

```typescript
// ❌ 禁止
const value = input as any;
// @ts-ignore
const result = unsafeOperation();

// ✅ 代わりに
const result = safeOperation(input);
if (result.isErr()) {
  // エラーハンドリング
}
```

### 2. 例外の握り潰し

```typescript
// ❌ 禁止
try {
  riskyOperation();
} catch {
  // 何もしない
}

// ✅ 代わりに
try {
  riskyOperation();
} catch (error) {
  logger.error('Operation failed', { error });
  throw new DomainError('操作に失敗しました', { cause: error });
}
```

### 3. 警告の無効化

```typescript
// ❌ 禁止
// eslint-disable-next-line
const result = deprecatedFunction();

// ✅ 代わりに
// 新しいAPIに移行
const result = newFunction();
```

### 4. 後方互換性ハック

```typescript
// ❌ 禁止（使われていないなら削除）
const _unusedVar = legacyValue;  // 後方互換性のため
export { OldName }; // 再エクスポート
// removed: oldFunction

// ✅ 代わりに
// 本当に必要なら段階的deprecation
/** @deprecated Use newFunction instead */
export function oldFunction() {
  return newFunction();
}
```

## チェックリスト

### 変更前
- [ ] Predictフェーズの分析結果を確認したか
- [ ] 関連するLaw/Termを確認したか
- [ ] 変更計画を作成したか

### 変更中
- [ ] 1ステップ = 1概念の変更を守っているか
- [ ] Pure/IO分離を維持しているか
- [ ] 各ステップで静的診断を実行しているか
- [ ] 禁止パターンに該当していないか

### 変更後
- [ ] 型チェック通過
- [ ] lint通過
- [ ] 既存テスト通過
- [ ] 新規テスト追加（必要な場合）
