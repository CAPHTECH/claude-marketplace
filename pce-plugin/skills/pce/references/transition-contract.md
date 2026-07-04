# Reference: Transition Contract

A form for expressing an instruction given to an AI, a human, or a tool as a contract for a permitted state transition, rather than as a work order.

The Transition Contract is not a new central concept in PCE 3.0. It is a form that bundles the continuation candidate, the Warrant, and the actor-local situation package into a practical instruction.

## Why a task name is not enough

The instruction "improve the error message on login failure" alone leaves the following unseparated:

- Change only the UI copy, or may the domain layer change?
- May the error classification grow? May the API contract be affected?
- May a fallback be added? May unresolved matters be reflected into the implementation?

An AI can fill blanks. That ability is useful, but it becomes dangerous when the filling turns into an "adopted fact." The contract exists to focus the AI's ability on the permitted state transition.

## Process stages and roles

Even for the same issue, change the AI's role, permitted output, and forbidden output per stage. Do not mix multiple roles in a single response.

| Stage | Role | Permitted output | Forbidden output |
| --- | --- | --- | --- |
| Context Binding | Context Binder | related specs, related code, prior decisions, unresolved matters | design proposals, implementation proposals, code changes |
| Contract Formation | Contract Writer | current / desired state, allowed / forbidden operations, invariants | deciding the implementation approach |
| Transition Candidate Generation | Transition Designer | multiple candidates, preserved structure, lost structure, risk, evidence | code changes |
| Candidate Selection | Decision Support | candidate comparison, reasons for/against adoption, trade-offs | introducing new candidates outside the contract |
| Transition Execution | Executor | applying the adopted candidate, diff, evidence | filling in the spec, scope expansion, unrequested refactors |
| Observation | Observer | changed files, test results, impact scope, remaining obstructions | asserting completion |
| Review | Evaluator | contract violations, forbidden transitions, invariant violations, missing evidence | proposing improvements up front |

## Reference form (full)

```yaml
transition_contract:
  id: TC-001
  process_stage: Context Binding | Contract Formation | Transition Candidate Generation | Candidate Selection | Transition Execution | Observation | Review
  role: Context Binder | Contract Writer | Transition Designer | Decision Support | Executor | Observer | Evaluator | Obstruction Reporter
  target_continuation:
    candidate_id:
    target:
    severity: low | medium | high | incident
    pace: immediate | normal | delayed | hold
  current_state:
    summary:
    references:
      - ref:
  desired_state:
    summary:
    acceptance_conditions:
      - condition:
  allowed_operations:
    - operation:
  forbidden_operations:
    - operation:
  invariants:
    - invariant:
  context_sources:
    allowed:
      - ref:
    excluded:
      - ref:
        reason:
  evidence_required:
    - evidence:
  uncertainty_handling:
    may_infer: true
    may_commit_inference: false
    if_affects_implementation: stop_as_obstruction
    otherwise: return_as_completion_candidate
  obstruction_handling:
    format:
    required_fields:
      - reason
      - affected_contract_field
      - next_needed_decision
  output_format:
    type:
    required_fields:
      - field:
  stop_conditions:
    - condition:
```

Required fields: id / process_stage / role / target_continuation / current_state / desired_state /
allowed_operations / forbidden_operations / invariants / evidence_required /
uncertainty_handling / output_format / stop_conditions.

## Minimal form (Transition Execution example)

```yaml
transition_contract:
  process_stage: Transition Execution
  role: Executor
  current_state:
  desired_state:
  allowed_operations:
    - Change display copy in the presentation layer
    - Add related widget tests
  forbidden_operations:
    - Change the domain layer
    - Change the error type definitions
    - Change the API contract
    - Add a fallback
  invariants:
    - Preserve the existing error classification
    - Keep UI copy out of the domain layer
  evidence_required:
    - Changed files
    - Test results
    - Correspondence to the Transition Contract
  uncertainty_handling:
    if_affects_implementation: stop_as_obstruction
    otherwise: return_as_completion_candidate
  stop_conditions:
    - A forbidden operation became necessary
    - An invariant cannot be preserved
    - Required evidence cannot be produced
```

## Correspondence to PCE concepts

| Contract field | PCE concept |
| --- | --- |
| current_state / desired_state | continuation candidate |
| allowed / forbidden operations | actor-local situation package |
| invariants | good continuation, state humility |
| evidence_required | Warrant |
| stop_conditions | actor-local situation package, accountability anchor |
| output_format | Process Delta, durable state projection |
| obstruction | a candidate that is no longer a good continuation |

## Note

Unresolved matters may be inferred. But when may_commit_inference: false, that inference must not be reflected into the implementation, the canonical record, or the completion judgment. Return it as an Obstruction or a Completion Candidate.
