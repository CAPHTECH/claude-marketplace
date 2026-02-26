# Discovery Patterns

## Vocabulary Discovery Sources

| Source | Target | Extraction Method |
|--------|--------|-------------------|
| Type definitions | Entity/Value Object | Search interface/type/class |
| Zod schemas | Value constraints | Parse z.object/z.string etc. |
| Brand types | Semantic distinction | Search Brand/Newtype definitions |
| Domain models | Concepts | Analyze domain/models directory |
| API definitions | IO boundary vocabulary | Parse Request/Response types |

## Law Discovery Sources

| Source | Target | Extraction Method |
|--------|--------|-------------------|
| Zod schemas | Input constraints | Parse schema definitions |
| Assertions | Invariant conditions | Search assert/invariant statements |
| Test expectations | Postconditions | Parse expect/assert |
| Catch clauses | Exception policies | Extract error handling |
| Business logic | Domain rules | Analyze conditionals |
| Incident history | Defensive conditions | Extract from past bugs |

## Vocabulary Patterns

| Pattern | Term Kind | Example |
|---------|-----------|---------|
| `interface Entity` | Term (Entity) | `interface Order` |
| `type Brand<T>` | Type (Brand) | `type OrderId = Brand<string>` |
| `z.number().min().max()` | Value (Constraint) | `z.number().min(1).max(100)` |
| `// Context: XXX` | Context | Comment extraction |

## Law Patterns

| Pattern | Law Type | Example |
|---------|----------|---------|
| `if (!condition) throw` | Pre | Input validation |
| `assert(a === b)` | Invariant | State consistency |
| `expect(result).toBe(x)` | Post | Output guarantee |
| `if (role === 'admin')` | Policy | Authorization decision |

## Search Commands

```bash
# Vocabulary discovery
grep -r "interface\|type\|class\|Brand" src/
grep -r "z\.object\|z\.string\|z\.number" src/

# Law discovery
grep -r "assert\|invariant\|validate" src/
grep -r "throw new.*Error\|reject\|fail" src/
```

## Zod Extraction Example

```typescript
// Source
const OrderSchema = z.object({
  quantity: z.number().min(1).max(100),
  price: z.number().positive(),
});

// Extracted Term candidates:
// TERM-order-quantity: Order quantity (1-100 integer)
// TERM-order-price: Order price (positive number)

// Extracted Law candidates:
// LAW-pre-order-quantity: 1 <= quantity <= 100
//   Terms: [TERM-order-quantity]
// LAW-pre-order-price: price > 0
//   Terms: [TERM-order-price]
```

## Assertion Extraction Example

```typescript
// Source
class Inventory {
  reserve(qty: number) {
    assert(this.available >= qty, 'Insufficient stock');
    // ...
    assert(this.available === this.total - this.reserved);
  }
}

// Extracted Term candidates:
// TERM-inventory-available, TERM-inventory-total, TERM-inventory-reserved

// Extracted Law candidates:
// LAW-pre-reserve-stock: available >= qty
// LAW-inv-available-balance: available = total - reserved
```
