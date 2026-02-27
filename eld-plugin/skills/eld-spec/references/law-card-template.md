# Law Card Template

```md
## LAW-<domain>-<name> (ID)
- Type: Invariant | Pre | Post | Policy
- Scope: <module/usecase/endpoint/job>
- Statement: <自然言語 1〜3行>
- Formal-ish: <疑似式 / 型 / predicate（任意だが曖昧さ削減に有効）>

- Terms (required):
  - <このLawが参照するTerm ID。最低1つ必須>

- Exceptions:
  - <例外条件と理由。無ければ "None">

- Violation Handling:
  - Severity: S0|S1|S2|S3
  - When Violated: reject | compensate | warn | quarantine | audit
  - Owner: <責任者/チーム>

- Verification (at least one):
  - Test: <unit/property/test-case>
  - Runtime Check: <assertion/guard>

- Observability (at least one):
  - Telemetry: law.<domain>.<law_name>.(applied|violated|latency_ms|coverage)
  - Log/Event: <event name / fields>
```

## Severity

| Level | Description |
|-------|------------|
| S0 | Business-critical (service halt) |
| S1 | Major functional failure |
| S2 | Partial degradation |
| S3 | Minor / improvement |

## Law Type Classification

| Type | Definition | Example |
|------|-----------|---------|
| Invariant | Always holds in any state | `available = total - reserved` |
| Pre | Required before operation | `orderQty <= available` |
| Post | Guaranteed after operation | `reserved' = reserved + orderQty` |
| Policy | Discretionary/contextual rule | "VIP gets limit relaxation" |

## Example: Inventory Balance Invariant

```md
## LAW-inv-available-balance
- Type: Invariant
- Scope: `inventory.reserveStock` / `inventory.releaseStock`
- Statement: 利用可能在庫は総在庫から予約済み在庫を引いた値に等しい
- Formal-ish: `∀t: available(t) = total(t) - reserved(t)`

- Terms:
  - TERM-inventory-available
  - TERM-inventory-total
  - TERM-inventory-reserved

- Exceptions:
  - None

- Violation Handling:
  - Severity: S1
  - When Violated: quarantine | audit
  - Owner: inventory-team

- Verification:
  - Test: `prop_inventory_balance` (PBT)
  - Runtime Check: `assert_balance()` in post-commit hook

- Observability:
  - Telemetry: `law.inventory.available_balance.violated_total`
  - Log/Event: `inventory.balance.violation` with `{expected, actual, diff}`
```
