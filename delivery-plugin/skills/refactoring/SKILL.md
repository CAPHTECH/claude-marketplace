---
name: refactoring
context: fork
description: 言語横断で過剰抽象化や AI 生成コードの構造重複を安全にリファクタリングする。duplicated contract、pass-through layer、mirror mapper、split async path、half-migration を見つけ、最小の一貫した end-state に収束させる。TS/JS、Dart/Flutter、Elixir/Phoenix は専用 profile あり。「リファクタリングして」「AI生成コードを整理して」「重複型を統合して」「wrapperを潰して」で使用。
---

# Refactoring

Use this skill for refactors across languages, especially code with structural duplication, unstable abstractions, or unfinished migrations.

When refactoring code:
- First identify the structural smells that matter: duplicated contracts, pass-through layers, mirror mappers, split async paths, half-migrations.
- Choose the smallest end-state that removes those smells without changing the required behavior.
- Collapse pass-through layers, duplicated contracts, mirror mappers, one-use factories, and generic dispatchers called from only a couple of concrete sites.
- For split async paths (parallel success/error/loading branches, duplicated await chains, or the same request issued from multiple owners), consolidate into one flow that returns a single result type.
- Prefer one coherent owner per behavior and one canonical data shape per concept. One owner means one module per concept; when the public name differs from the internal name, do the alias re-export from the package entry, not from a dedicated facade file.
- Export only what the public API requires. If a function becomes internal-only after consolidation, drop its export.
- Delete dead abstractions before adding helpers.
- Finish the migration in one pass. Do not keep legacy and replacement structures alive together.
- Before stopping, run the native compile, test, or lint command that already exists in the repo and fix failures you introduced.

## Rule priority

When rules compete, apply in this order:

1. Preserve the public API surface the repo actually exercises.
2. Keep the native compile, test, or lint command green.
3. Remove the structural smell.
4. Reduce file count or line count.

Example: consolidating two mirror mappers into one canonical type is correct at step 3, but if it breaks a publicly imported name, step 1 wins — keep an alias re-export from the package entry until callers migrate.

## Language Profiles

- For TypeScript or JavaScript module, type, and async pitfalls, read [typescript-javascript.md](references/typescript-javascript.md).
- For Dart or Flutter type, widget, state, and async pitfalls, read [dart-flutter.md](references/dart-flutter.md).
- For Elixir, Phoenix, or LiveView boundary ownership and generated middle-layer cleanup, read [elixir-phoenix.md](references/elixir-phoenix.md).
- For other languages, keep the generic core above and follow the repository's native ownership boundaries, type system, and verification commands.

## Notes

- Prefer the minimum concept set, not the minimum file count.
- Preserve externally required behavior while simplifying internals.
- A passed smoke test does not excuse a broken compile.
- If you finish with no substantive diff, the task is not complete.

Read [failure-patterns.md](references/failure-patterns.md) when a first refactor attempt regresses or stalls.
Read [playbook.md](references/playbook.md) when you want the edit sequence for each smell family.

## Not this skill

This skill does not:

- Change externally observable behavior (that is behavior-change work, not refactoring).
- Redesign the public API surface (API change, separate task).
- Add tests where none existed (test authoring, separate task).
- Apply cosmetic renames without dedup (if there is no structural smell, do not touch names).
- Review code for bugs, security, or performance (use `critical-code-review` instead).
