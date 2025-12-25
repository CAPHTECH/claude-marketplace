# Ground（接地）フェーズ

テスト/Telemetry/再現手順でLaw/Termを観測可能にする。

## 目的

- Lawを検証可能・観測可能にする
- L0だけで完了扱いしない
- 本番環境での違反検知を可能にする

## Evidence Ladder（証拠の梯子）

| Level | 内容 | 必須条件 | 備考 |
|-------|------|----------|------|
| L0 | 静的整合（型/lint） | 全Law | **ここで完了扱いしない** |
| L1 | ユニットテスト | S0/S1 Law | Law/Termの観測写像の最小 |
| L2 | 統合テスト・再現手順 | S0 Law | 境界越えの因果 |
| L3 | 失敗注入/フェイルセーフ | S0 Law | 違反時動作の確認 |
| L4 | 本番Telemetry | S0/S1 Law | 実運用でのLaw違反検知 |

## Grounding要件

### Lawの接地

| Severity | 検証（Verification） | 観測（Observation） |
|----------|---------------------|---------------------|
| S0 | Unit + Integration + Runtime | Telemetry + Alert |
| S1 | Unit + (Integration or Runtime) | Telemetry |
| S2 | Unit | Log |
| S3 | (推奨) | (推奨) |

### Termの接地

| Severity | 境界検証 | 観測フィールド |
|----------|----------|----------------|
| S0/S1 | 必須 | 必須 |
| S2/S3 | 推奨 | 推奨 |

## 検証手段（Verification）

### Unit Test

Lawの中核ロジックをPure関数としてテスト:

```typescript
describe('LAW-order-quantity-range', () => {
  it('should accept valid quantity', () => {
    expect(validateOrderQuantity(1).isOk()).toBe(true);
    expect(validateOrderQuantity(50).isOk()).toBe(true);
    expect(validateOrderQuantity(100).isOk()).toBe(true);
  });

  it('should reject invalid quantity', () => {
    expect(validateOrderQuantity(0).isErr()).toBe(true);
    expect(validateOrderQuantity(-1).isErr()).toBe(true);
    expect(validateOrderQuantity(101).isErr()).toBe(true);
  });

  // Property-based test for S0/S1
  it('should always be within range', () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100 }), (qty) => {
        return validateOrderQuantity(qty).isOk();
      })
    );
  });
});
```

### Integration Test

境界を越えた因果関係をテスト:

```typescript
describe('Order creation flow', () => {
  it('should create order with valid quantity', async () => {
    // Arrange
    const input = { productId: 'P001', quantity: 5 };
    
    // Act
    const result = await orderService.createOrder(input);
    
    // Assert
    expect(result.isOk()).toBe(true);
    expect(result.value.quantity).toBe(5);
    
    // DB確認
    const saved = await orderRepository.findById(result.value.id);
    expect(saved.quantity).toBe(5);
  });
});
```

### Runtime Assert

実行時の不変条件チェック:

```typescript
class Inventory {
  private _available: number;
  private _reserved: number;
  
  // LAW-inventory-balance の実行時検証
  private assertInvariant(): void {
    if (this._available < 0) {
      throw new InvariantViolation('LAW-inventory-balance', 
        'available must be non-negative');
    }
    if (this._reserved < 0) {
      throw new InvariantViolation('LAW-inventory-balance',
        'reserved must be non-negative');
    }
  }
  
  reserve(qty: number): void {
    this._available -= qty;
    this._reserved += qty;
    this.assertInvariant(); // 状態変更後に検証
  }
}
```

## 観測手段（Observation）

### Telemetry

メトリクスで違反を追跡:

```typescript
// 違反カウンター
telemetry.increment('law.violation', {
  lawId: 'LAW-order-quantity-range',
  severity: 'S0',
  type: 'UserError'
});

// 値分布
telemetry.histogram('order.quantity', quantity, {
  lawId: 'LAW-order-quantity-range'
});

// レート制限チェック
telemetry.gauge('rate_limit.remaining', remaining, {
  userId: user.id
});
```

### Structured Logging

構造化ログで追跡可能に:

```typescript
logger.info('Order created', {
  orderId: order.id,
  quantity: order.quantity,
  lawChecks: [
    { lawId: 'LAW-order-quantity-range', passed: true },
    { lawId: 'LAW-inventory-available', passed: true }
  ]
});

logger.warn('Law violation', {
  lawId: 'LAW-order-quantity-range',
  severity: 'S1',
  input: { quantity: 150 },
  message: 'Quantity exceeds maximum'
});
```

### Alert

S0違反は即時アラート:

```typescript
// S0違反は即時通知
if (violation.severity === 0) {
  alerting.critical('S0 Law Violation', {
    lawId: violation.lawId,
    context: violation.context,
    timestamp: new Date().toISOString(),
    runbook: `https://docs.example.com/runbook/${violation.lawId}`
  });
}
```

## 失敗注入（Failure Injection）

### 違反時動作の確認

```typescript
describe('LAW-order-quantity-range violation handling', () => {
  it('should return 400 for user error', async () => {
    const result = await request(app)
      .post('/orders')
      .send({ productId: 'P001', quantity: 999 });
    
    expect(result.status).toBe(400);
    expect(result.body.error).toContain('注文数量');
  });

  it('should log violation', async () => {
    await request(app)
      .post('/orders')
      .send({ productId: 'P001', quantity: 999 });
    
    expect(logger.warn).toHaveBeenCalledWith(
      'Law violation',
      expect.objectContaining({
        lawId: 'LAW-order-quantity-range'
      })
    );
  });

  it('should increment telemetry counter', async () => {
    await request(app)
      .post('/orders')
      .send({ productId: 'P001', quantity: 999 });
    
    expect(telemetry.increment).toHaveBeenCalledWith(
      'law.violation',
      expect.objectContaining({ lawId: 'LAW-order-quantity-range' })
    );
  });
});
```

## Grounding Map

Law/Term → Test/Telemetry の対応表:

```yaml
# grounding-map.yaml
laws:
  LAW-order-quantity-range:
    severity: S0
    verification:
      unit:
        - test_order_quantity_validation
        - test_order_quantity_property
      integration:
        - test_order_creation_flow
      runtime:
        - OrderQuantity.of
    observation:
      telemetry:
        - law.violation{lawId="LAW-order-quantity-range"}
        - order.quantity
      log:
        - "Order created"
        - "Law violation"
      alert:
        - s0_law_violation

  LAW-inventory-balance:
    severity: S0
    verification:
      unit:
        - test_inventory_balance_invariant
      runtime:
        - Inventory.assertInvariant
    observation:
      telemetry:
        - inventory.balance
      alert:
        - inventory_invariant_violation

terms:
  TERM-order-quantity:
    severity: S1
    boundary_validation:
      input: OrderSchema.quantity
      output: OrderResponse.quantity
    observable_fields:
      - order.quantity
```

## `/lde-grounding-check` 使用

接地状況を検証:

```
/lde-grounding-check LAW-order-quantity-range

結果:
✅ L0: 型チェック通過
✅ L1: Unit Test (3/3)
✅ L2: Integration Test (1/1)
❌ L3: 失敗注入テストなし
✅ L4: Telemetry設定済み

推奨アクション:
- 失敗注入テストを追加してください
```

## チェックリスト

### 検証（Verification）
- [ ] S0/S1 Law は Unit Test が最低1つある
- [ ] S0 Law は Integration Test が最低1つある
- [ ] S0 Law は Runtime Assert がある
- [ ] S0/S1 Term は境界で検証されている

### 観測（Observation）
- [ ] S0/S1 Law は Telemetry が設定されている
- [ ] S0 Law は Alert が設定されている
- [ ] S0/S1 Term は Observable Fields が定義されている

### 失敗注入
- [ ] S0 Law は違反時動作がテストされている
- [ ] エラー応答が適切か確認されている
- [ ] ログ/テレメトリが記録されるか確認されている

### ドキュメント
- [ ] Grounding Map が更新されている
- [ ] Law Card の Grounding 欄が記入されている
- [ ] Term Card の Observable Fields が記入されている
