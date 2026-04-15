# Failure Patterns

Use this file when a first refactor attempt regresses or stalls.

## Contract Collision

Symptoms:
- Imported or shared declarations are duplicated locally
- Consolidation copies multiple equivalent contracts into one place and breaks verification

Correction:
- Keep one existing declaration
- Update imports, aliases, or re-exports instead of cloning the contract
- If the system already has a stable owner, consolidate around that owner

## Upward Flattening

Symptoms:
- Runtime state, storage logic, or request primitives are copied into a higher layer
- File count drops, but ownership becomes less clear

Correction:
- Move simplification toward the lowest module that already owns the primitive
- Keep higher layers thin or delete them entirely

## Shared Helper Widening

Symptoms:
- A shared helper broadens result shapes or error semantics too much
- Callers need casts, assertions, or unsafe conversions to recover concrete behavior

Correction:
- Keep boundary wrappers concrete
- Use overloads, separate low-level wrappers, or language-native specialization if needed
- Prefer one shared primitive plus concrete boundary functions

## No-Op Refactor

Symptoms:
- Checks pass but diff is empty or trivial
- Structural smell remains untouched

Correction:
- Re-state the primary smell
- Name the exact wrapper, mapper, or duplicate contract to remove
- Make one structural deletion before considering the task complete
