---
name: disposable-autopsy
context: fork
argument-hint: "[cycle_N]"
description: Analyze a disposable prototype across 10 quality axes using static analysis, test results, and Codex MCP triangulation. Produces structured autopsy report with scored findings and recommendations. Part of H-DGM cycle. Use after disposable-spike completes.
---

# Disposable Autopsy — Phase 2: Analyze

Perform 10-axis analysis of a disposable prototype, combining quantitative metrics with qualitative AI review.

## Prerequisites

- Completed spike: `.disposable/cycles/cycle_{N}/spike-complete.json` must exist
- Spike branch `disposable/cycle_{N}` must exist
- Codex MCP available for triangulated review (optional but recommended)

## Procedure

### Step 1: Load Spike Context

1. Determine cycle: use `$ARGUMENTS` if provided, otherwise read latest from `.disposable/history.json`
2. Load metrics from `.disposable/cycles/cycle_{N}/spike-complete.json`
3. Checkout spike branch: `git checkout disposable/cycle_{N}`
4. Read generated source files for analysis

### Step 2: Static Analysis (Quantitative)

Extract quantitative signals from metrics:

| Metric | Maps to Axis |
|--------|-------------|
| lint.error count | correctness, readability |
| tests.failed | correctness, error-handling |
| tests.passed / tests.total | testability |
| coverage.line.pct | testability, maintainability |
| coverage.branch.pct | error-handling |

### Step 3: Qualitative Analysis (10 Axes)

Analyze the prototype code against each axis. For each axis:

1. **correctness** — Does the code do what was specified? Check requirements coverage, logic errors
2. **architecture** — Module boundaries, dependency direction, separation of concerns
3. **security** — Input validation, injection risks, auth boundaries, secret handling
4. **performance** — Algorithmic complexity, unnecessary allocations, N+1 patterns
5. **testability** — Test isolation, mock-ability, deterministic behavior
6. **readability** — Naming, function length, cognitive complexity
7. **maintainability** — DRY, coupling metrics, change amplification risk
8. **error-handling** — Error propagation, recovery paths, fail-fast behavior
9. **dependency-hygiene** — Minimal dependencies, version constraints, license compatibility
10. **documentation** — API contracts, non-obvious behavior, setup instructions

For each axis, assign:
- `status`: `scored` | `na` | `insufficient-evidence`
- `score`: 1-5 (when scored)
  - 1 = Critical issues, fundamentally broken
  - 2 = Major issues, significant rework needed
  - 3 = Acceptable, typical for rapid prototype
  - 4 = Good, minor improvements only
  - 5 = Excellent, production-ready quality
- `findings[]`: Specific issues with severity and evidence reference
- `recommendations[]`: Actionable improvements with priority

### Step 4: Triangulated Review (Optional)

If Codex MCP is available, request independent review:

```
mcp__codex__codex(
  prompt: "Review the following disposable prototype for {axis}.
  Focus on: {axis-specific criteria}.
  Report findings as JSON array with id, severity, description, evidenceRef fields.
  Files: {file list}",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "{project_root}"
)
```

Merge Codex findings with Claude findings:
- Findings reported by both → increase confidence (severity stays or escalates)
- Findings reported by only one → keep but flag as single-source
- Contradictions → note in findings, use Claude's judgment for final score

### Step 5: Determine Verdict

Apply quality gates from references/quality-gates.md:

1. Calculate `averageScore` from all `scored` axes
2. Check each gate condition against metrics and scores
3. Assign verdict: `PASS` | `CALIBRATE` | `FAIL`

### Step 6: Generate Report

Construct autopsy report following references/autopsy-schema.json:

```json
{
  "schemaVersion": "1.0.0",
  "rubricVersion": "1.0.0",
  "cycleId": "cycle_{N}",
  "timestamp": "{ISO 8601}",
  "metricsRef": "spike-complete.json",
  "axes": { ... },
  "summary": {
    "verdict": "PASS|CALIBRATE|FAIL",
    "strengths": [...],
    "criticalIssues": [...],
    "averageScore": N.N
  }
}
```

### Step 7: Save, Validate & Mask

1. Save report to `.disposable/cycles/cycle_{N}/autopsy-report.json`
2. Validate report against schema:
   ```bash
   node {plugin_root}/scripts/dist/validate-report.mjs \
     .disposable/cycles/cycle_{N}/autopsy-report.json \
     --schema {plugin_root}/skills/disposable-cycle/references/autopsy-schema.json
   ```
3. If validation fails: fix report structure and re-validate (max 2 retries)
4. Mask sensitive data:
   ```bash
   node {plugin_root}/scripts/dist/mask-sensitive.mjs \
     .disposable/cycles/cycle_{N}/autopsy-report.json --in-place
   ```
5. Return to original branch: `git checkout -`

### Step 8: Report to User

Present summary:
- Verdict with confidence level
- Top 3 strengths
- Critical issues requiring attention
- Axis scores table
- Recommendation for next step: `/disposable-distill` or `/disposable-cycle` to iterate

## Output

- `.disposable/cycles/cycle_{N}/autopsy-report.json` — validated autopsy report
- Ready for `/disposable-distill`

## Error Handling

- If metrics file is missing: check data completeness. If tests are unavailable, set verdict to FAIL per quality-gates.md. For lint/coverage only, mark affected axes as `insufficient-evidence` and continue
- If Codex MCP is unavailable: proceed with Claude-only analysis, note in report
- If schema validation fails: fix report structure, re-validate (max 2 retries)
