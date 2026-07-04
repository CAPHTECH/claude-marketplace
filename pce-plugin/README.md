# pce-plugin

A Claude Code plugin that materializes the PCE 3.0 development discipline.

PCE 3.0 treats an instruction to an AI not as a work order but as a **Transition Contract** (a contract for a permitted state transition), and forbids **canonical changes without a Warrant**. Its central concept is *good continuation*: proceeding only when doing so makes the outcome, understanding, judgment, responsibility, state, and downstream work better.

This plugin gives that discipline teeth inside Claude Code.

## What it provides

| Component | Role in PCE 3.0 |
| --- | --- |
| `pce` skill | Entry point. Converts a work request into a Transition Contract, calibrates weight by Target / Severity / Pace, runs the staged loop, gates canonical changes on a Warrant, and returns results as a Process Delta. |
| `pce-context-binder` agent | The Context Binding stage as a **read-only** agent. Fixes the referenceable context without leaking design or implementation -- enforced structurally by tool restriction. |
| `pce-evaluator` agent | The Review stage as a **read-only** agent. Reports contract violations, forbidden transitions, invariant violations, and missing evidence, without fixing anything -- so it cannot manufacture corrupt success. |
| Warrant guard hook | A `PreToolUse` hook on `Bash` that prompts for a Warrant check before canonical git operations (commit / push / merge). The one deterministic guardrail for "no canonical change without a Warrant." |

The two agents are deliberately read-only: PCE asks that roles not be mixed in one context, and tool restriction turns that from advice into a structural guarantee (a binder with no write tools cannot emit code; an evaluator with no write tools cannot "helpfully fix" during review).

## Usage

Once installed, the `pce` skill triggers on work requests ("implement this issue", "fix this bug"), before commits/merges, or on explicit asks ("proceed with PCE", "write a Transition Contract", "check the Warrant"). You can also invoke it directly with `/pce`.

The skill loads its detailed schemas on demand from:

- `skills/pce/references/transition-contract.md` -- the contract schema and the seven process stages.
- `skills/pce/references/warrant.md` -- the Warrant schema, when it is required, and its verdicts.
- `skills/pce/references/good-continuation.md` -- the loop, Target/Severity/Pace, the principles, and the object model.

## The Warrant guard hook

The hook (`hooks/hooks.json` + `scripts/warrant-guard.sh`) inspects each `Bash` command and, when it detects a canonical git operation (commit / push / merge), returns `permissionDecision: "ask"` with a reminder to confirm the Warrant. Matching is a lightweight, dependency-free heuristic (POSIX `sh`); read-only git commands such as `status`, `diff`, and `log` are not affected. If it is too strict for your workflow, remove the `PreToolUse` entry from `hooks/hooks.json`.

## Layering

PCE calibrates weight to the change. For a low-severity, local change, a one-sentence contract is enough -- the plugin is not meant to impose ceremony on trivial fixes. The full contract and Warrant discipline is for changes that reach canonical state or a shared interface.
