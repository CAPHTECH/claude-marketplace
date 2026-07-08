# Operational Model

## Mode selection

Relational Design は、すべてのタスクを同じ重さで扱わない。

## Light mode

対象:

- 小さな UI 文言修正
- 既存 component の軽微な調整
- 余白・状態表示・ラベルの修正

必要出力:

- assumptions
- design decisions
- brief critique

使う agent:

- context-reader
- design-critic
- trace-archivist

## Standard mode

対象:

- 画面設計
- LP section 設計
- dashboard / form / onboarding flow
- 既存 UI の再構成

必要出力:

- brief decomposition
- relation map
- design hypotheses
- chosen direction
- artifact
- critique
- revision plan
- trace record

使う agent:

- context-reader
- relation-mapper
- hypothesis-generator
- variant-designer
- design-critic
- trace-archivist

## Deep mode

対象:

- 主要導線
- 価格ページ
- onboarding
- 高リスク action
- design system 変更を伴う UI
- 経営・ブランド・事業上の意味が大きい landing page

必要出力:

- Standard mode の全出力
- 仮説別 variant
- isolated worktree variant if needed
- implementation verification
- retraction impact map
- design-system backflow

使う agent:

- context-reader
- relation-mapper
- hypothesis-generator
- variant-designer-isolated
- design-critic
- implementation-verifier
- retraction-analyst
- trace-archivist

## Orchestration rule

`design-trace` Skill は以下の順に進む。

```text
1. Determine mode
2. Call context-reader
3. Call relation-mapper when relation structure matters
4. Call hypothesis-generator before any non-trivial artifact
5. Call variant-designer only with declared hypotheses
6. Call design-critic before finalizing
7. Call implementation-verifier when files or code are edited
8. Call trace-archivist to write or update trace records
9. Suggest design-system-backflow when the pattern is reusable
```

## Stopping rule

Agent は、完全な情報がない場合でも作業を止めすぎない。ただし、推定した前提は isolated assumption として扱う。

```text
Do not block progress just because inputs are incomplete.
Do isolate low-confidence assumptions.
Do mark all downstream decisions that depend on them.
```
