---
name: pce
description: "PCE 3.0 entry point for work. Shape an instruction to AI as a Transition Contract (a contract for a permitted state transition) rather than a work order, prevent canonical changes without a Warrant, and judge good continuation. Use when receiving a work request such as 'implement this issue', 'fix this bug', or 'add this feature', before a commit or merge, or when asked to 'proceed with PCE', 'write a Transition Contract', or 'check the Warrant'."
argument-hint: "the work or issue to carry out (optional)"
---

# PCE 3.0: Transition Contract Driven Work

PCE 3.0 is a development discipline for designing the conditions under which work continues well. Its central concept is good continuation. This skill is the entry point for treating a work request not as a task name but as a responsible state transition.

## Principles (recall first)

Do not execute a work request as-is. First convert it into: "from which state, to which state, under which contract, may this move?"

- Continuation first: before asking which process to run, ask which continuation can change the future state.
- Warrant first / no canonical change without a warrant: adoption, promotion, integration, closing, resumption, commit, and merge all require a Warrant.
- State humility: durable state is not reality itself; it is a projection of deltas produced by good continuation.
- Situation before context: before deciding what to show, decide what may be done, what may be decided, and what must be returned.
- Accountability over presence: high-impact continuations need an accountability anchor (a human or an institution).

Full principles and background: references/good-continuation.md

## Calibrate the weight (decide first)

PCE does not impose the same weight on every task. Layer the continuation candidate by Target / Severity / Pace and match the weight of the contract and the warrant to it.

- Target: what is changed (UI copy / domain / API / schema / canonical records...).
- Severity: how much the work is damaged if it is wrong (low / medium / high / incident).
- Pace: over what time span it should move (immediate / normal / delayed / hold).

If Severity is low and Target does not reach canonical state, a one-sentence contract is enough (what changes, what is left untouched).
If Severity is high/incident, or Target reaches canonical state or a shared interface, make the contract and the Warrant explicit and get agreement before executing.

## Procedure

### 1. Write the Transition Contract

Convert the work request into a Transition Contract. At minimum, fill:

- current_state / desired_state
- allowed_operations / forbidden_operations
- invariants (invariants to preserve)
- evidence_required (evidence to return)
- uncertainty_handling / stop_conditions

Schema, template, and the list of process stages: references/transition-contract.md

### 2. Proceed with roles separated

Do not mix design, implementation, and evaluation in a single response. Switch roles per stage. Delegating context binding and evaluation to isolated-context subagents prevents role violations structurally.

- Context Binding -> pce-context-binder agent (read-only; produces no design or implementation).
- Contract Formation / Candidate Generation / Selection / Execution -> proceed in this skill's main context.
- Review -> pce-evaluator agent (read-only; reports only contract violations, forbidden transitions, invariant violations, and missing evidence; does not propose fixes).

Always evaluate in a context different from the one that did the implementation. Evaluating your own output in the same context lets corrupt success slip through.

### 3. Handle uncertainty

Inference is allowed. But an inference under may_commit_inference: false must not enter the implementation, the canonical record, or the completion judgment.

- Uncertainty that affects the implementation -> stop it as an Obstruction and return the decision it needs.
- Uncertainty that does not affect it -> return it as a Completion Candidate and keep it out of the implementation.

### 4. Gate canonical changes with a Warrant

Before changing state that future work will rely on (commit / merge / canonicalizing a spec), check the Warrant.
A Warrant is not just an evaluation result; it binds goal fit, scope compliance, evidence, authority, risk acceptance, recoverability, and freshness.

Schema and verdicts: references/warrant.md
This plugin's hook prompts for a Warrant check before canonical git operations (commit / push / merge).

### 5. Return the result as evidence

Do not assert completion. Return the result of the continuation as a Process Delta.

- Changed files / test results / impact scope.
- Correspondence to the Transition Contract (allowed operations touched, forbidden operations left untouched, invariants preserved).
- Remaining Obstructions / Completion Candidates.

Do not merge apparent success (corrupt success) into canonical state.

## Output shape

When you carry out the work, make at least the following explicit.

- The Transition Contract applied (or its essentials).
- The allowed_operations performed, and the forbidden_operations left untouched.
- The invariants preserved.
- Evidence (changed files / tests / impact scope).
- Remaining Obstructions / Completion Candidates.
- If a canonical change is made, its Warrant verdict.
