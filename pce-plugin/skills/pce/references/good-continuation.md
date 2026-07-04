# Reference: Good Continuation and the PCE 3.0 Overview

## One-sentence definition

PCE 3.0 is a development discipline for designing, in work that involves many humans, AIs, tools, and records, the conditions under which outcome, understanding, judgment, responsibility, state, and downstream work all get better -- taking as its unit not the task name but the responsible state transition.

In short: a development discipline for designing the conditions under which work continues well.

## Central concept: good continuation

Good continuation is a continuation that, by moving from the current situation to the next, improves outcome, understanding, judgment, responsibility, state, and downstream work. This single concept is the center of PCE 3.0.

A Warrant is only one necessary condition for good continuation. It is not enough to be permitted to proceed; proceeding must make the work better.

## The overall loop

```text
project reality
  -> durable state projection
  -> continuation candidate
  -> actor-local situation package
  -> layered by Target / Severity / Pace
  -> confirm the quality of the continuation
  -> good continuation / continuation to fix / continuation to stop / escalation
  -> Process Delta
  -> reflection into the durable state projection
  -> future project reality
```

Process does not disappear. It is positioned as the operational vessel for generating, confirming, branching, joining, stopping, and recovering continuation candidates.

## Decision layer: Target / Severity / Pace

A decision layer for handling good continuation with the weight and speed that fit the situation. It is not a taxonomy added for its own sake.

- Target: what is changed.
- Severity: how much the work is damaged if it is wrong.
- Pace: over what time span it should move.

## Principles

- Continuation first: the first question is not which process to run, but which continuation can change the future state.
- Warrant first: adoption, promotion, integration, closing, and resumption require a Warrant, not just the signal of a result.
- No canonical change without a Warrant: changing canonical state that future work relies on requires a Warrant.
- State humility: durable state is not reality itself; it is a projection of deltas produced by good continuation.
- Layered Warrant: vary the weight and handling of the Warrant by Target, Severity, and Pace.
- Situation before context: before deciding what to show, decide what may be done, what may be decided, and what must be returned.
- Accountability over presence: what matters is not that a human is present, but that a high-impact continuation has an accountability anchor.

## Key objects

- Project reality: the entire actual state of the project (code, specs, decisions, tacit knowledge, trust, fatigue, and more). It cannot be held in full.
- Durable state projection: a partial copy of project reality, saved in a form future work may rely on. It is not reality itself.
- Continuation candidate: a candidate for moving from the current state to the next -- integration, approval, dispatch, promotion, rollback, resumption, goal redefinition, closing, and so on.
- Warrant: the bundle of grounds for judging that a continuation candidate may proceed. -> warrant.md
- Actor-local situation package: for an actor to judge or act, the bundle of the goal cross-section, the state that may be seen, permitted actions, forbidden actions, authority boundary, required evidence, stop conditions, and the result to return.
- Responsibility geometry: how capability, obligation, authority, burden, and final acceptance are arranged among actors for a continuation.
- Accountability anchor: for a high-impact continuation, the actor or institution that finally accepts the remaining risk, exception judgment, reflection into canonical records, closure of an incident, and redefinition of the goal.

## Handling uncertainty

Inference itself is not forbidden. What is forbidden is mixing inference into canonical state.

- Uncertainty that affects the implementation -> stop it as an Obstruction and return reason / affected_contract_field / next_needed_decision.
- Uncertainty that does not affect it -> return it as a Completion Candidate and do not reflect it into the implementation, the canonical record, or the completion judgment.

## Process Delta (how to return a result)

The result of a process is not a lump of output. It expresses, per item, which continuation produced what type of change, at which boundary, as a candidate heading where, with what evidence, evaluation path, and authority requirement.

- destination distinguishes canonical / provisional / parent_only / coordination_only.
- Do not assert completion. Leave unresolved_issues and recommended_next_action.
- Do not confuse apparent success (corrupt success) with a canonical target.

## Corrupt success

A state that appears successful but must not be adopted as current truth as-is. Even if tests are green, if it has escaped the scope, broken an invariant, or lacks evidence, do not adopt it into canonical state.
