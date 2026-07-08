# Critique Rubric

## Severity

- critical: user cannot complete the intended task, or trust/action risk is mishandled.
- high: design likely causes wrong action, hesitation, misunderstanding, or implementation fragility.
- medium: design weakens clarity, confidence, or consistency but does not break the flow.
- low: local improvement with limited behavioral impact.

## Critique language

Prefer:

```text
Because relation R says users need consequence clarity before committing, decision DD-003 places the destructive action too early.
```

Avoid:

```text
This feels weak.
```
