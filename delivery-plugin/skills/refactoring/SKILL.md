---
name: refactoring
context: fork
description: 言語横断で過剰抽象化や AI 生成コードの構造重複を安全にリファクタリングする。duplicated contract、pass-through layer、mirror mapper、split async path、half-migration を見つけ、最小の一貫した end-state に収束させる。TS/JS と Dart/Flutter は専用 profile あり。「リファクタリングして」「AI生成コードを整理して」「重複型を統合して」「wrapperを潰して」で使用。
---

# Refactoring

Use this skill for refactors across languages, especially code with structural duplication, unstable abstractions, or unfinished migrations.

When refactoring code:
- First identify the structural smells that matter: duplicated contracts, pass-through layers, mirror mappers, split async paths, half-migrations.
- Choose the smallest end-state that removes those smells without changing the required behavior.
- Collapse pass-through wrappers, duplicated contracts, and one-use factories.
- Prefer one coherent owner per behavior and one canonical data shape per concept.
- Delete dead abstractions before adding helpers.
- Finish the migration in one pass. Do not keep legacy and replacement structures alive together.
- Before stopping, run the native compile, test, or lint command that already exists in the repo and fix failures you introduced.

## Language Profiles

- For TypeScript or JavaScript module, type, and async pitfalls, read [typescript-javascript.md](references/typescript-javascript.md).
- For Dart or Flutter type, widget, state, and async pitfalls, read [dart-flutter.md](references/dart-flutter.md).
- For other languages, keep the generic core above and follow the repository's native ownership boundaries, type system, and verification commands.

## Notes

- Prefer the minimum concept set, not the minimum file count.
- Preserve externally required behavior while simplifying internals.
- A passed smoke test does not excuse a broken compile.
- If you finish with no substantive diff, the task is not complete.

Read [failure-patterns.md](references/failure-patterns.md) when a first refactor attempt regresses or stalls.
Read [playbook.md](references/playbook.md) when you want the edit sequence for each smell family.
