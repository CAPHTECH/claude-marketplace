# Profiles

## `hybrid`

両方の path を残す。

- conventional regression / integration checks
- agent trace / grader checks

最初に profile を決め切れない場合はこれを使う。

## `software`

次の状況で使う。

- CLI / API / DB / browser の回帰検証が主目的
- trace artifact は不要
- stdout / exit code / fixture state で十分

残す sample:

- `smoke/software-smoke.json`
- `regression/software-regression.json`

## `agent-eval`

次の状況で使う。

- agent trace と grader を中心に運用する
- input/output だけでなく中間ステップも観測したい
- adversarial / edge prompts を継続的に回したい

残す sample:

- `edge/agent-eval-edge.json`
- `adversarial/agent-eval-adversarial.json`
