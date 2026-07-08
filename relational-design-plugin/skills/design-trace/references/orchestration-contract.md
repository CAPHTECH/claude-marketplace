# Orchestration Contract

The orchestrator must preserve phase boundaries.

```text
context-reader -> relation-mapper -> hypothesis-generator -> variant-designer -> design-critic -> trace-archivist
```

Allowed shortcuts:

- Light mode may skip relation-mapper if the change is local and low-risk.
- Deep mode may run multiple `variant-designer-isolated` agents for hypothesis variants.
- A review-only task may skip artifact generation.
- A retraction-only task should use `design-retract` instead.

Never ask `variant-designer` to create a UI from raw brief alone for non-trivial tasks.
