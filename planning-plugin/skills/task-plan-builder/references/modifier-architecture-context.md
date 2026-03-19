# Modifier: Architecture Context

Read this modifier when the task depends on an existing codebase, documented architecture, ADRs, or team conventions.

## What To Change In The Plan

- anchor changes in the current architecture instead of inventing a clean-room design
- identify the existing components or modules that own the relevant behavior
- preserve stable interfaces unless the task explicitly authorizes changing them
- name the documents or code areas that should be treated as the current source of truth

## Include

- existing boundaries to respect
- existing abstractions to reuse
- deviations from current architecture, if any, with a reason

## Avoid

- replacing the current structure with an idealized architecture
- moving ownership casually across modules
- ignoring documented invariants or conventions
