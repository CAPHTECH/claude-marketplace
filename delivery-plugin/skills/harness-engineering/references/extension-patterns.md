# Extension Patterns

必要になった時だけ読む。

## External Dependencies

- まず fixture file と deterministic mock で始める
- HTTP dependency が増えたら mock server を切り出す
- 実 DB / queue / browser が必要なら service container か Testcontainers を追加する

## CI Matrix

v1 は `ubuntu-latest x node 20/22`。

広げる順序:

1. Node version
2. OS
3. dependency backend

いきなり多次元にしない。

## Trace Grading

v1 は trace file existence と stdout check で十分。

強化する時は:

- trace schema validation
- grader score extraction
- regression comparison against previous artifacts

## Root Repo Integration

root `package.json` や default devcontainer に統合したくなっても、最初はやらない。

理由:

- repo ごとの差分衝突が大きい
- skill の汎用性が落ちる
- rollback が難しくなる
