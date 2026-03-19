# Modifier: UI Separation

Read this modifier when the task has an interactive UI and the plan should prevent core logic from collapsing into rendering or browser bootstrap code.

## What To Change In The Plan

- name the UI rendering or screen module explicitly
- keep application or use-case logic separate from DOM and event wiring
- keep browser or runtime bootstrap thin
- keep domain rules and data normalization out of the view layer

## Good Boundary Pattern

- domain: rules, invariants, normalization
- application: use-case orchestration and state transitions
- persistence or external adapter: storage, API, or other boundary
- UI or screen: rendering, event callbacks, view-state mapping
- bootstrap: instantiate dependencies and wire runtime-specific APIs

## Avoid

- putting query semantics into browser entry code
- letting the screen module own persistence or domain mutation
- hiding state transitions inside DOM handlers with no reusable application surface
