# Law/Term Card Templates

ELD (Evidence-Loop Development) のLaw Card / Term Card雛形。

---

## Law Card Template

```markdown
# LAW-{domain}-{name}

## 基本情報
- **ID**: LAW-{domain}-{name}
- **Type**: Pre | Post | Invariant | Policy
- **Severity**: S0 (Critical) | S1 (High) | S2 (Medium) | S3 (Low)
- **Created**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD


## Statement（自然言語）
<!-- 日本語での記述 -->


## Formal（疑似式）
<!-- 形式的な表現 -->
```
例: 1 ≤ orderQty ≤ 100
例: ∀t: token.expiry > now → token.valid
```


## Scope（適用範囲）
<!-- どこで適用されるか -->
- モジュール:
- 関数/メソッド:
- レイヤー:


## Terms（参照する語彙）
<!-- このLawが参照するTerm。孤立禁止 -->
- TERM-xxx
- TERM-yyy


## Exceptions（例外）
<!-- Lawが適用されないケース -->
-


## Violation Behavior（違反時動作）
<!-- 違反した場合の振る舞い -->
- エラー種別:
- 回復戦略:
- 通知先:


## Grounding（接地）
<!-- どうやって検証/観測するか -->

### 検証（Verification）
| 手段 | 対象 | 状態 |
|------|------|------|
| Unit Test | `test_xxx` | 接地済/未接地 |
| Integration Test | | |
| Runtime Assert | | |

### 観測（Observation）
| 手段 | メトリクス名 | 状態 |
|------|-------------|------|
| Telemetry | | |
| Log | | |
| Alert | | |


## Source（発見元）
- ファイル:
- 行:
- パターン:


## Notes
<!-- 補足事項 -->

```

---

## Term Card Template

```markdown
# TERM-{domain}-{name}

## 基本情報
- **ID**: TERM-{domain}-{name}
- **Type**: Entity | Value | Context | Boundary
- **Severity**: S0 (Critical) | S1 (High) | S2 (Medium) | S3 (Low)
- **Created**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD


## Meaning（意味）
<!-- このTermが表すもの -->


## Synonyms（同義語）
<!-- 同じ意味で使われる別の言葉 -->
-


## Boundary（境界）
<!-- どこで使われる言葉か。使用文脈 -->
- 使用モジュール:
- 使用レイヤー:
- 使用インターフェース:


## Type/Shape（型表現）
<!-- 型定義やスキーマ -->
```typescript
// 例
type OrderQuantity = Brand<number, 'OrderQuantity'>;
// または
z.number().min(1).max(100)
```


## Observable Fields（観測写像）
<!-- このTermをどう観測するか -->
| フィールド | 型 | 説明 |
|-----------|-----|------|
| | | |


## I/O Boundaries（境界での扱い）
<!-- 入出力境界での検証/正規化 -->

### 入力時
- 検証:
- 正規化:

### 出力時
- シリアライズ:


## Related Laws（関連Law）
<!-- このTermを参照するLaw。S0/S1は必須 -->
- LAW-xxx
- LAW-yyy


## Source（発見元）
- ファイル:
- 行:
- パターン:


## Notes
<!-- 補足事項 -->

```

---

## 相互拘束チェックリスト

### Law → Term
- [ ] すべてのLawがTerms欄に参照するTermを持つ
- [ ] 孤立したLaw（Term参照なし）がない

### Term → Law
- [ ] S0/S1のTermがRelated Laws欄に関連Lawを持つ
- [ ] 孤立したS0/S1 Termがない

### Grounding
- [ ] S0 Lawは検証（Test + Runtime）と観測（Telemetry）が両方ある
- [ ] S1 Lawは検証（Test or Runtime）と観測（Telemetry）がある
- [ ] S0/S1 Termは境界での検証/正規化とObservable Fieldsがある

---

## Link Map形式

```yaml
# law-term-link-map.yaml
laws:
  LAW-order-quantity-range:
    terms: [TERM-order-quantity]
    grounding:
      tests: [test_order_quantity_validation]
      telemetry: [order.quantity.out_of_range]

  LAW-inventory-balance:
    terms: [TERM-inventory-available, TERM-inventory-total, TERM-inventory-reserved]
    grounding:
      tests: [test_inventory_balance_invariant]
      runtime: [Inventory.assertInvariant]

terms:
  TERM-order-quantity:
    laws: [LAW-order-quantity-range, LAW-order-total-limit]
    boundaries:
      input: OrderSchema.quantity
      output: OrderResponse.quantity

  TERM-inventory-available:
    laws: [LAW-inventory-balance, LAW-reserve-stock]
    boundaries:
      input: InventoryAdjustment.quantity
      observable: Inventory.available
```
