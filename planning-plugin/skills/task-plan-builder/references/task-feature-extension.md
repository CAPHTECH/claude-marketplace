# Feature Extension

Use this route when behavior is being added to an existing system.

## Plan Priorities

- anchor the change in current boundaries
- identify changed surfaces instead of redesigning everything
- preserve existing contracts unless the change explicitly requires contract movement
- name the verification needed to avoid regressions

## Include

- current surfaces being extended
- new behavior to add
- compatibility constraints
- migrations or data-shape adjustments if needed
- focused test or validation coverage

## Avoid

- turning a feature request into a broad refactor
- rewriting stable modules without a stated need
- ignoring existing naming, layering, or ownership

## Good Shape

The plan should answer:

- what existing modules change
- what new modules, if any, are added
- what must remain compatible
- how the extension is verified without destabilizing the rest of the system
