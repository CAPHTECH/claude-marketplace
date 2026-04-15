# Playbook

## Duplicated Contract

1. Find all structurally identical types.
2. Pick the existing owner with the clearest domain meaning.
3. Replace duplicates with imports or re-exports from that owner.
4. Delete copy-only mappers that only shuffle identical fields.

## Pass-Through Layer

1. Find wrappers that only forward parameters and return values.
2. Inline them into the caller or remove the layer entirely.
3. Keep the public entrypoint stable unless the task explicitly allows API redesign.

## Mirror Mapper

1. Confirm the source and target shapes are actually equivalent.
2. Collapse to one shape.
3. Remove mapper functions that only copy fields.

## Split Async Path

1. Identify duplicated retry, fetch, or error normalization loops.
2. Move the shared mechanic to the low-level primitive.
3. Preserve concrete result types at each boundary wrapper.

## Half-Migration

1. Identify legacy and replacement paths that coexist.
2. Pick the winner.
3. Rewire all callers.
4. Delete the losing path in the same change.
