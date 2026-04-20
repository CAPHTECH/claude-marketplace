# TypeScript / JavaScript Profile

Read this file when the current refactor target is TypeScript or JavaScript.

## Contract Consolidation

- If multiple interfaces or types are structurally identical, keep one existing declaration and update imports or re-exports around it.
- Never import a type and redeclare the same name locally.
- Delete copy-only DTO or record mappers when the source and target shapes are identical.
- When unifying mirrored contracts, keep the existing publicly exported name if one exists; otherwise use the shortest domain-neutral concept name (e.g. `User`, `Profile`) and drop layer suffixes like `Dto`, `Row`, `Record`, `Model`.

### Example: mirror mapper removal

Before (three files, two identical shapes plus an identity mapper):

```ts
// src/api/userDto.ts
export interface UserDto { id: string; name: string; email: string }

// src/domain/user.ts
export interface User { id: string; name: string; email: string }

// src/api/mapUser.ts
import type { UserDto } from "./userDto";
import type { User } from "../domain/user";
export const mapUser = (d: UserDto): User => ({ id: d.id, name: d.name, email: d.email });
```

After (one canonical type, two files deleted, imports updated to `User`):

```ts
// src/domain/user.ts
export interface User { id: string; name: string; email: string }
```

`UserDto` drops the `Dto` suffix because the shape is identical; `mapUser` disappears because mapping was identity.

## Ownership

- Keep storage, transport, and runtime primitives in the low-level module that already owns them.
- Do not flatten everything upward into a service layer just to reduce file count.
- Thin public entrypoints are acceptable if they preserve a required API boundary.

## Async Refactors

- Consolidate duplicated retry loops near the low-level fetch primitive.
- Prefer explicit concrete wrappers over generic helpers that widen to unions and force casts later.
- If a helper must stay generic, keep the call boundary concrete and verifiable.

## Verification

Use the repository's existing commands when available. Typical checks include:

- `npx tsc --noEmit`
- `tsc -p tsconfig.json --noEmit`
- `npm test`
- `pnpm test`
- `vitest`
- `jest`

Do not stop on a passed smoke test if the TypeScript compile is broken.
