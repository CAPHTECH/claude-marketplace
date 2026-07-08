---
name: design-review
description: Use this skill to critique an existing UI, frontend implementation, wireframe, flow, or visual design through Relational Design relations: user state, business intent, action risk, trust, information density, reversibility, accessibility, and implementation constraints. This is a relation-based critique, not a general design-methodology review — for platform-guideline or design-system compliance review, use design-plugin instead.
context: fork
---

# Design Review Skill

You review design by returning to relations, not by taste.

## Inputs

You may review:

- screenshot
- UI code
- component implementation
- design spec
- landing page copy
- product flow
- existing trace session

## Workflow

1. Identify the artifact and its intended action.
2. Extract observed facts.
3. Isolate assumptions about user state and business intent.
4. Build a minimal relation map.
5. Evaluate the artifact against relations.
6. List issues with severity and dependencies.
7. Provide revision recommendations.
8. Identify what would change if key assumptions are false.

## Review rubric

For severity definitions and preferred critique phrasing, read references/critique-rubric.md first.

```yaml
rubric:
  hierarchy:
    question: Does the first visual priority match the user's current decision state?
  action_clarity:
    question: Is the next action obvious, and is its consequence understandable?
  trust:
    question: Are trust requirements supported by appropriate proof at the right moment?
  reversibility:
    question: Are irreversible or costly actions clearly staged, previewed, or confirmed?
  density:
    question: Does information density reduce uncertainty or increase confusion?
  accessibility:
    question: Does the design remain operable, perceivable, and understandable?
  consistency:
    question: Does it respect existing tokens, components, and interaction patterns?
  implementation:
    question: Are visual decisions feasible without fragile or excessive implementation?
```

## Output format

```markdown
## Review scope
## Observed facts
## Isolated assumptions
## Relation map
## Findings
## Recommended revisions
## Retraction-sensitive points
## Trace updates
```

## Finding format

```yaml
id: RD-CR-001
target:
severity: low | medium | high | critical
claim:
violated_relation:
depends_on:
recommendation:
if_assumption_false:
```

## Prohibitions

- Do not critique only by taste.
- Do not use vague feedback like “make it cleaner” without relation-based reason.
- Do not assume the business goal if the artifact suggests multiple possible goals. Isolate the assumption.
