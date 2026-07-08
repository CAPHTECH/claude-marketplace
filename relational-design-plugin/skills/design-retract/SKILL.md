---
name: design-retract
description: Use this skill when a design assumption, user segment, business goal, constraint, or product requirement has changed and you need to analyze which design hypotheses, decisions, artifacts, copy, or components should be retracted or revised. Requires a Relational Design trace session with recorded observations/relations/hypotheses/decisions to analyze against — not a general "redo this design" request.
context: fork
---

# Design Retract Skill

Retraction is not the same as revision.

Revision changes an artifact.
Retraction invalidates a premise or decision and traces its downstream impact.

## Workflow

For common retraction triggers and how they map to downstream impact, read references/retraction-playbook.md first.

1. Identify the changed or invalidated node.
2. Classify it as observation, assumption, constraint, relation, hypothesis, or decision.
3. Find all dependent nodes.
4. Classify impact severity.
5. Decide whether to keep, revise, or retract each dependent decision.
6. Propose replacement hypotheses when needed.
7. Update trace records.

## Retraction impact format

```yaml
retraction:
  invalidated_node:
    id:
    previous_claim:
    new_claim:
  affected_relations: []
  affected_hypotheses: []
  affected_decisions: []
  affected_artifacts: []
  recommended_actions:
    keep: []
    revise: []
    retract: []
    unresolved: []
```

## Rules

- Do not patch the UI before understanding dependency impact.
- Do not preserve a design decision only because it looks good.
- If a low-confidence assumption becomes false, remove its downstream effects.
- If an assumption becomes true, upgrade confidence and simplify fallback UI if appropriate.

## Output format

```markdown
## Invalidated premise
## Dependency impact
## Keep / revise / retract
## Replacement hypotheses
## Artifact changes
## Trace updates
```
