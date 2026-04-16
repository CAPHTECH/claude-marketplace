# Dart / Flutter Profile

Read this file when the current refactor target is Dart or Flutter.

## Shared Direction

- Start by identifying the structural smells that matter: duplicated contracts, pass-through layers, mirror mappers, split async paths, half-migrations.
- Choose the smallest end-state that removes those smells without changing the required behavior or the public surface the repo actually exercises.
- Prefer one coherent owner per behavior and one canonical data shape per concept, but stop once the remaining layers each own a real boundary.
- Collapse pass-through repositories, helpers, wrapper widgets, and one-use factories instead of moving the same logic into new names.
- Finish the migration in one pass. Do not keep legacy and replacement structures alive together.

## Dart Refactors

- Delete repository, coordinator, generated client, and mapper layers before changing transport or store signatures. Prefer collapsing middle layers over rewriting a lower boundary that is already concrete.
- Keep a transport, storage, or exported API model when it still marks a real boundary, even if the fields match. Remove duplicate middle contracts first.
- When simplifying async flows, keep retry or fallback behavior explicit in the public flow. If the shared work is only a small fetch-and-map step, prefer repeating the concrete lines over adding a new private helper.
- Do not rename store functions or add wrapper functions just to move ownership. Preserve existing concrete names unless the rename removes an actual duplicate concept.

## Flutter Refactors

- Delete wrapper widgets that only forward fields. Keep state ownership and event flow explicit in the remaining widget tree.
- Do not replace one large widget with many tiny mirror widgets unless each extracted widget owns a real visual or state boundary.
- Keep async UI states concrete and complete: idle, loading, success, and error should still behave the same after the refactor.
- Prefer subtractive cleanup over cosmetic tree reshaping. If a screen is already direct, remove forwarding layers and stop.

## Verification

Use the repository's existing commands when available. Typical checks include:

- `dart analyze`
- `flutter analyze`
- `dart test`
- `flutter test`

Do not stop on a passed manual smoke check if static analysis or tests are broken.
