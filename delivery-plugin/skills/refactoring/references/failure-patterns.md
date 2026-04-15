# Failure Patterns

Use this file when a first refactor attempt regresses or stalls.

## Contract Collision

Symptoms:
- Imported type name is redeclared locally
- Consolidation copies multiple contracts into one file and causes compile failure

Correction:
- Keep one existing declaration
- Update imports and re-exports instead of cloning the type
- If the system already has a stable type owner, consolidate around that owner

## Upward Flattening

Symptoms:
- Runtime state, storage logic, or request primitives are copied into a service layer
- File count drops, but ownership becomes less clear

Correction:
- Move simplification toward the lowest module that already owns the primitive
- Keep higher layers thin or delete them entirely

## Generic Async Widening

Symptoms:
- Shared helper returns `string | string[]` or another broad union
- Callers need casts and compile breaks

Correction:
- Keep section-specific wrappers concrete
- Use overloads or separate low-level wrappers if needed
- Prefer one shared retry primitive plus concrete boundary functions

## No-Op Refactor

Symptoms:
- Checks pass but diff is empty or trivial
- Structural smell remains untouched

Correction:
- Re-state the primary smell
- Name the exact wrapper, mapper, or duplicate contract to remove
- Make one structural deletion before considering the task complete
