---
name: task-plan-builder
context: fork
description: Build task-appropriate planning artifacts by routing to the right reference for initial implementation, feature extension, refactoring, investigation, documentation, or review work. Use when Codex should produce a plan before acting, especially when different task types need different plan shapes or when interactive UI separation and existing architecture context may matter.
---

# Task Plan Builder

## Overview

Route the request to one primary planning reference and zero or more modifier references.
Read only the references that materially apply. Do not bulk-load every reference.

The goal is not to produce a single universal plan style.
The goal is to produce the smallest plan shape that fits the task.

## Workflow

1. Classify the request into one primary task type.
2. Add modifier references only when they clearly apply.
3. Produce a self-contained plan artifact.
4. If the user asked to execute as well as plan, use that plan as the working contract for implementation, investigation, refactoring, documentation, or review.

## Primary Route Selection

Pick exactly one of these first:

- references/task-initial-build.md
  Use for new screens, new tools, prototypes, greenfield modules, or first implementation of a task.
- references/task-feature-extension.md
  Use for adding behavior inside an existing system without rewriting its structure.
- references/task-refactor.md
  Use for structural improvement where behavior should remain materially unchanged.
- references/task-investigation.md
  Use for debugging, root-cause analysis, uncertainty reduction, or feasibility checks.
- references/task-documentation.md
  Use for spec extraction, onboarding docs, architecture docs, or change guides.
- references/task-review.md
  Use for code review, risk review, design review, or validating an existing change.

## Modifier Selection

Add these only when needed:

- references/modifier-architecture-context.md
  Read when the task depends on an existing architecture, existing docs, current module boundaries, ADRs, or team conventions.
- references/modifier-ui-separation.md
  Read when the task has an interactive UI and the plan should prevent DOM/rendering/browser bootstrap from collapsing into core logic.

It is normal to use:

- one primary reference only
- or one primary reference plus one modifier
- or one primary reference plus both modifiers

## Output Contract

Unless the user asked for a different format, the plan should usually include:

- `goal`
- `task_type`
- `assumptions`
- `selected_references`
- `constraints`
- `module_or_change_boundaries`
- `behavior_or_validation_contract`
- `execution_or_investigation_steps`
- `risks`
- `acceptance_or_exit_checks`
- `escalation_rules`

Adjust the names if a different structure is clearer.
Do not force implementation-oriented sections onto investigation or review work when they do not fit.

## Routing Rules

- Prefer the user's real intent over file type.
- If the request is "change existing code safely", prefer `feature-extension` or `refactor`, not `initial-build`.
- If the request is primarily "understand what is happening", prefer `investigation`.
- If the request is primarily "summarize or explain", prefer `documentation`.
- If the request is primarily "find problems", prefer `review`.
- If the request is "build something new", prefer `initial-build`.

## Context Discipline

- Read only the references that matter for the chosen route.
- If modifier references are not needed, skip them.
- When existing architecture context exists, plan around it rather than inventing a clean-room design.
- When UI separation matters, name the view/render/bootstrap boundaries explicitly.

## Quality Bar

A good result is not a generic plan template.
A good result is a task-shaped plan that reduces drift for the actual work being requested.
