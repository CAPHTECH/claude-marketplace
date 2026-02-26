# Term Card Template

```md
## TERM-<domain>-<name> (ID)

### Basic Info
- Meaning: <定義（1〜2文）>
- Context: <使用される文脈・ドメイン>
- Synonyms: <同義語があれば列挙>
- Non-goals: <この用語が意味しないもの>

### Type / Shape
- Type/Shape: <技術的な型表現>
- Constraints: <値制約>
- Example Values: <具体例>

### Boundary / Grounding
- IO Boundaries: <どこで入力/出力されるか>
- Validation: <境界での検証方法>
- Normalization: <正規化処理>
- Observable Fields: <ログ/テレメトリで観測するフィールド>

### Related Laws
- Related Laws (at least one for S0/S1 Terms):
  - <関連するLaw ID>
```

## Term Classification

| Kind | Definition | Example |
|------|-----------|---------|
| Term | Business concept/noun | "Available Stock", "Order" |
| Type | Technical type/structure | `OrderId`, `Quantity` |
| Value | Value constraint | `1 <= qty <= 100` |
| Context | Usage context | "Inventory Mgmt", "Order Processing" |

## Example: Available Stock

```md
## TERM-inventory-available

### Basic Info
- Meaning: 現時点で注文に割り当て可能な在庫数量
- Context: 在庫管理、注文処理
- Synonyms: 有効在庫、販売可能在庫
- Non-goals: 物理的な在庫数（予約済みを含む）

### Type / Shape
- Type/Shape: `AvailableStock = Brand<number, 'AvailableStock'>`
- Constraints: `available >= 0`, `available <= total`
- Example Values: 0, 50, 1000

### Boundary / Grounding
- IO Boundaries:
  - Input: 在庫API、管理画面
  - Output: 注文API、商品詳細
- Validation: `z.number().nonnegative().max(MAX_STOCK)`
- Normalization: 小数点以下切り捨て
- Observable Fields: `inventory.available`, `inventory.available_diff`

### Related Laws
- Related Laws:
  - LAW-inv-available-balance
  - LAW-pre-order-quantity
```
