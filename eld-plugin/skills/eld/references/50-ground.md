# Ground（接地）フェーズ

テスト/Telemetry/再現手順でLaw/Termを観測可能にする。2軸評価（Evidence Level × Evaluator Quality）。

> v2.3: Evidence Level（L0-L4）に加え、Evaluator Quality（E0-E3）軸を追加。
> Review Hybrid導入（Artifact-Based + 行レビュー必須領域）。

## 目的

- Lawを検証可能・観測可能にする
- L0だけで完了扱いしない
- 検証手段自体の品質を保証する（Evaluator Quality）
- 本番環境での違反検知を可能にする

## テスト設計には `/test-design-audit` を使用

体系的なテスト設計には `/test-design-audit` スキルを使用する。

## 2軸評価モデル（v2.3）

### 軸1: Evidence Level（証拠の梯子）L0-L4

| Level | 内容 | 必須条件 | 備考 |
|-------|------|----------|------|
| L0 | 静的整合（型/lint） | 全Law | **ここで完了扱いしない** |
| L1 | ユニットテスト | S0/S1 Law | Law/Termの観測写像の最小 |
| L2 | 統合テスト・再現手順 | S0 Law | 境界越えの因果 |
| L3 | 失敗注入/フェイルセーフ | S0 Law | 違反時動作の確認 |
| L4 | 本番Telemetry | S0/S1 Law | 実運用でのLaw違反検知 |

### 軸2: Evaluator Quality（検証者品質）E0-E3

| Level | 内容 | 説明 |
|-------|------|------|
| E0 | テストなし/手動のみ | 再現性のない検証 |
| E1 | テスト存在（カバレッジ不問） | 自動検証はあるが品質は不明 |
| E2 | changed-lines coverage ≥ 80% OR mutation score ≥ 60% | 変更行に対する十分なカバレッジ |
| E3 | E2 + 独立レビュー(別担当/別AIモデル) + 汚染チェック記録 | 最高品質。独立した第三者検証 |

### Severity↔E要件マトリクス

| Severity | 最低E要件 | 備考 |
|----------|----------|------|
| S0 + セキュリティ | **E3必須** | 独立レビュー+汚染チェック必須 |
| S0（非セキュリティ） | E2推奨 | E1は要正当化 |
| S1 | **E2必須** | changed-lines coverage確認 |
| S2 | **E1必須** | テスト存在が最低条件 |
| S3 | **E1必須** | テスト存在が最低条件 |

### 2軸マトリクス表記

```
Ground結果: L2/E2
  → Evidence Level 2（統合テスト済み）
  → Evaluator Quality 2（カバレッジ80%以上）
```

## Grounding要件

### Lawの接地

| Severity | 検証（Verification） | 観測（Observation） | 最低E要件 |
|----------|---------------------|---------------------|-----------|
| S0 | Unit + Integration + Runtime | Telemetry + Alert | E2（セキュリティはE3） |
| S1 | Unit + (Integration or Runtime) | Telemetry | E2 |
| S2 | Unit | Log | E1 |
| S3 | (推奨) | (推奨) | E1 |

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
    expect(validateOrderQuantity(100).isOk()).toBe(true);
  });

  it('should reject invalid quantity', () => {
    expect(validateOrderQuantity(0).isErr()).toBe(true);
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
    const input = { productId: 'P001', quantity: 5 };
    const result = await orderService.createOrder(input);
    expect(result.isOk()).toBe(true);

    const saved = await orderRepository.findById(result.value.id);
    expect(saved.quantity).toBe(5);
  });
});
```

### Runtime Assert

実行時の不変条件チェック（コード例は40-change.mdのLaw実装パターンを参照）。

## 観測手段（Observation）

### Telemetry

```typescript
telemetry.increment('law.violation', {
  lawId: 'LAW-order-quantity-range',
  severity: 'S0',
  type: 'UserError'
});
```

### Structured Logging

```typescript
logger.info('Order created', {
  orderId: order.id,
  lawChecks: [
    { lawId: 'LAW-order-quantity-range', passed: true }
  ]
});
```

### Alert

S0違反は即時アラート。

## Review Hybrid（v2.3新設）

PRレビューを2つの方式の組み合わせで行う:

### Artifact-Based Review（デフォルト）

Evidence Packの完全性で判断:
- [ ] 証拠の梯子の達成レベルが適切か
- [ ] Evaluator Qualityが要件を満たすか
- [ ] Law/Termの孤立がないか
- [ ] テスト結果が全て通過しているか
- [ ] カバレッジが要件を満たすか

### 行レビュー必須領域

以下の領域はArtifact-Basedに加え、コード行単位の詳細レビューが**必須**:

| 領域 | 理由 | チェック観点 |
|------|------|-------------|
| セキュリティ | インジェクション、認証バイパス | 入力検証、エスケープ、権限チェック |
| 並行処理 | デッドロック、レースコンディション | ロック順序、トランザクション分離 |
| 永続化 | データ損失、不整合 | マイグレーション安全性、ロールバック |
| 認証 | 認証バイパス、セッション固定 | トークン検証、セッション管理 |
| マイグレーション | データ移行失敗、後方互換 | 段階的移行、フォールバック |
| 課金 | 金額計算誤り | 丸め処理、通貨換算、冪等性 |

### レビュー方式の決定

```
if 変更が行レビュー必須領域に該当:
  → Artifact-Based + 行レビュー
else:
  → Artifact-Based のみ
```

## Grounding Map

Law/Term → Test/Telemetry の対応表:

```yaml
# grounding-map.yaml
laws:
  LAW-order-quantity-range:
    severity: S0
    evidence_level: L2
    evaluator_quality: E2
    verification:
      unit:
        - test_order_quantity_validation
      integration:
        - test_order_creation_flow
    observation:
      telemetry:
        - law.violation{lawId="LAW-order-quantity-range"}
      alert:
        - s0_law_violation
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

### Evaluator Quality（v2.3）
- [ ] Severity↔E要件マトリクスを満たしている
- [ ] S0+セキュリティはE3を達成している
- [ ] changed-lines coverageを確認している（E2要件時）

### Review Hybrid（v2.3）
- [ ] 行レビュー必須領域を特定している
- [ ] Artifact-Based Reviewのチェックを完了している
- [ ] 必須領域の行レビューを完了している

### ドキュメント
- [ ] Grounding Map が更新されている
- [ ] Law Card の Grounding 欄が記入されている
- [ ] Term Card の Observable Fields が記入されている
