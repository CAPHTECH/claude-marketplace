# Initial Build

Use this route for first implementations, prototypes, greenfield modules, and new app surfaces.

## Plan Priorities

- define the smallest valid architecture
- name the main module boundaries
- define the core data model and invariants
- define the acceptance checks that prove the build is real
- keep sequencing simple enough that another agent can implement without guessing

## Include

- intended app or module shape
- file or module boundaries
- important interfaces or contracts
- behavior invariants
- minimal but sufficient validation plan
- out-of-scope assumptions

## Avoid

- architecture essays
- multiple competing designs unless the user explicitly asked for options
- vague work units like "build the backend"
- over-layering for a small task

## Good Shape

For interactive apps, the plan should normally separate:

- core domain or state rules
- use-case orchestration
- persistence or external boundary
- UI rendering and event binding
- runtime bootstrap

Only collapse these if the task is truly tiny and the reason is explicit.
