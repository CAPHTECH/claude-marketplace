---
name: design-system-backflow
description: Use this skill after creating or reviewing a design artifact to extract reusable design-system knowledge: semantic tokens, components, variants, interaction rules, copy patterns, accessibility constraints, and governance notes. This only backflows structure out of an artifact that already exists — to build or govern a design system from scratch (Design Tokens layers, Atomic Design, DDR/QOC/RFC, UI inventory), use design-plugin's design-system-builder instead.
context: fork
---

# Design System Backflow Skill

Your job is to turn one-off design output into reusable design-system structure.

## Workflow

1. Read the artifact and related trace decisions.
2. Identify repeated or reusable design intentions.
3. Separate token, component, pattern, copy, and interaction layers.
4. Mark what should become part of the system and what should remain local.
5. Preserve trace dependencies.
6. Produce a migration plan.

## Backflow categories

```yaml
backflow:
  tokens:
    semantic_color:
    spacing:
    typography:
    motion:
  components:
    new_components:
    variants:
    composition_rules:
  patterns:
    information_patterns:
    trust_patterns:
    reversibility_patterns:
  copy_rules:
  interaction_rules:
  accessibility_rules:
  anti_patterns:
```

## Rules

- Do not create tokens for one-off decoration.
- Do not create components before identifying repeated responsibility.
- Do not name components by appearance only.
- Component names should express responsibility or relation, not surface style.
- Preserve why the pattern exists.

For established relation-based pattern and component names, read references/backflow-catalog.md first.

## Example

Bad:

```text
GoldCard
```

Better:

```text
EvidenceCard
RiskExplanationPanel
ReversibleActionPreview
```

## Output format

```markdown
## Backflow scope
## Candidate tokens
## Candidate components
## Candidate patterns
## Copy and interaction rules
## Accessibility constraints
## What should remain local
## Migration plan
## Trace dependencies
```
