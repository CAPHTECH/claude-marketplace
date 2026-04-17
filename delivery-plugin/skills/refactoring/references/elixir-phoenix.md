# Elixir / Phoenix Profile

Read this file when the current refactor target is Elixir, Phoenix, or LiveView.

## Shared Direction

- Start by identifying the structural smells that matter: duplicated contracts, pass-through layers, mirror mappers, split async paths, half-migrations.
- Choose the smallest end-state that removes those smells without changing the required behavior or the public surface the repo actually exercises.
- Prefer one coherent owner per behavior and one canonical data shape per concept, but stop once the remaining layers each own a real boundary.
- Collapse pass-through contexts, coordinators, wrappers, and copy-only translators instead of moving the same logic into new names.
- Finish the migration in one pass. Do not keep legacy and replacement structures alive together.

## Elixir Refactors

- Delete payload, draft, generated client, and mapper layers before changing a schema, store, or exported API that already marks a real boundary.
- Keep one canonical struct per concept unless two shapes still mark distinct boundaries after the refactor.
- Prefer collapsing middle layers over rewriting a lower boundary that is already concrete.
- When simplifying async flows, keep retry, timeout, and owner-side coordination explicit. If the shared work is small, prefer repeating the concrete lines over introducing a new private helper.

## Phoenix / LiveView Boundaries

- Keep `Ecto.Changeset` owning validation. Do not move validation into contexts, controllers, or LiveViews just to delete files.
- Keep persistence in `Repo` or the persistence module that already owns writes. Do not move writes into controllers or LiveViews.
- Keep controllers owning HTTP translation and LiveViews owning assigns, events, task refs, and timeout state.
- Delete presenter, payload, and wrapper layers before changing controller JSON or LiveView socket surfaces. Remove duplicate middle contracts first.
- Thin public entrypoints are acceptable if the lower boundary is already concrete and the remaining layers still mark real ownership.

## Verification

Use the repository's existing commands when available. Typical checks include:

- `mix deps.get`
- `mix compile --warnings-as-errors`
- `mix test`

Do not stop on a passed smoke check if compile warnings or tests are broken.
