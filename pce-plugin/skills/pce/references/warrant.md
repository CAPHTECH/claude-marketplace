# Reference: Warrant

A Warrant is the bundle of grounds for judging that a continuation candidate may proceed.
Passing an evaluation is not enough. It also includes goal fit, scope compliance, evidence, authority, risk acceptance, recoverability, projection, and freshness.

## When it is required (no canonical change without a Warrant)

Required when changing canonical state that future work will rely on. In practice, this covers:

- commit / push / merge (reflecting into history or a shared branch)
- canonicalizing a spec, design, or decision (finalizing a document or ADR)
- memory promotion (adopting a provisional finding as canonical)
- closing, redefining the goal, or rolling back

A Warrant is a necessary condition for proceeding, not a sufficient one.
It must not only be permitted to proceed; proceeding must make the work better (it must be a good continuation).

## Vary the weight by decision layer (Layered Warrant)

Vary the weight of the grounds by Target / Severity / Pace.

- Severity low, Target local: evidence and a scope check are often enough.
- Severity high/incident, Target reaching canonical state or a shared interface: make authority, risk acceptance, recovery path, and accountability anchor explicit.

## Reference form

```yaml
warrant:
  id: WR-001
  continuation_candidate: CC-001
  decision_layer:
    target:
    severity: low | medium | high | incident
    pace: immediate | normal | delayed | hold
  verdict: warranted | rejected | conditional | insufficient_evidence | escalate
  goal_fit:
    claim:
    evidence_refs:
      - ref:
  scope_fit:
    in_scope:
      - item:
    out_of_scope:
      - item:
    violations:
      - item:
  evidence:
    eval_contract_refs:
      - ref:
    verdict_refs:
      - ref:
    missing_evidence:
      - item:
  authority:
    required:
      - authority:
    approval_refs:
      - ref:
    accountability_anchor:
  risk:
    risk_delta:
    accepted_risks:
      - risk:
    unresolved_risks:
      - risk:
  recoverability:
    rollback_path:
    recovery_point:
    if_irreversible:
  projection:
    destination:
    canonical_or_provisional: canonical | provisional
    provenance:
    supersedes:
  freshness:
    valid_from:
    valid_until:
    invalidated_by:
      - condition:
```

Required fields: id / continuation_candidate / decision_layer / verdict / goal_fit / evidence /
authority / risk / projection / freshness.

## Meaning of each verdict

- warranted: with the weight appropriate to the decision layer, the conditions on evidence, authority, risk, recoverability, projection, and freshness are met.
- conditional: warranted if the stated conditions are met. Do not proceed while conditions remain open.
- insufficient_evidence: evidence is lacking. Do not make the canonical change until evaluation is added.
- rejected: not a good continuation. Discard or redesign the candidate.
- escalate: this continuation needs the judgment of its accountability anchor (a human or an institution).

## Note

Keep the Warrant for audit, rollback, and supersession. Once you issue `warranted`, keep its grounds (evidence refs, approvals, accepted risks, recovery path) traceable together with the Process Delta.
