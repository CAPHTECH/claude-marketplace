# Refactor

Use this route when the goal is structural improvement with materially preserved behavior.

## Plan Priorities

- make the preservation target explicit
- define move order and checkpoints
- prefer reversible steps
- lock behavior with tests or other evidence before deeper changes

## Include

- preserved behaviors and invariants
- target structural improvement
- staged change sequence
- rollback or stop conditions
- validation at each stage

## Avoid

- silent feature additions
- mixing behavior changes into the same plan without calling them out
- large all-at-once rewrites when an incremental sequence exists

## Good Shape

The plan should make it obvious:

- what stays the same
- what gets rearranged
- how to tell whether the refactor drifted from intended behavior
