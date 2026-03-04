---
name: disposable-cycle
context: fork
argument-hint: "[mode:auto|manual] <requirements>"
description: Orchestrate the full H-DGM (Hybrid Disposable Generation Method) disposable prototyping cycle. Manages spike-autopsy-distill iterations with Mode A (auto) or Mode B (manual) control. Tracks cycle history and graduation readiness. Use to start or continue a disposable prototyping session.
---

# Disposable Cycle — Orchestrator

Manage the full disposable prototyping lifecycle: spike → autopsy → distill → iterate or graduate.

## Modes

### Mode A: Automatic (default)
Full cycle runs automatically: spike → autopsy → distill → decision.
User intervenes only at graduation decision or FAIL verdict.

### Mode B: Manual
Each phase runs independently. User triggers each step:
- `/disposable-spike` → `/disposable-autopsy` → `/disposable-distill`

Mode is determined by `$ARGUMENTS` prefix (`mode:auto` or `mode:manual`) or `.disposable/config.json`.

## Procedure

### Step 1: Initialize Session

1. Check for existing `.disposable/` state:
   - If exists, load `history.json` and show cycle summary
   - If not, create `.disposable/` with initial structure
2. Write/update `.disposable/config.json`:
   ```json
   {
     "mode": "auto|manual",
     "maxCycles": 5,
     "qualityGates": {}
   }
   ```
3. Parse requirements from `$ARGUMENTS` (after mode prefix)

### Step 2: Cycle Loop (Mode A)

```
while cycle_count < maxCycles:
  1. Run disposable-spike with current requirements/spec
  2. Run disposable-autopsy on completed spike
  3. Check verdict:
     - PASS → Run disposable-distill → Check graduation → maybe exit
     - CALIBRATE → Run calibration (targeted fix + re-evaluate)
     - FAIL → Run disposable-distill → Prepare next spike input
  4. If graduating → exit loop
  5. Prepare next cycle: distill-spec becomes input for next spike
```

### Step 3: Cycle Loop (Mode B)

Report current state and available next action:
- After initialization → suggest `/disposable-spike`
- After spike → suggest `/disposable-autopsy`
- After autopsy → suggest `/disposable-distill`
- After distill → suggest next `/disposable-spike` or graduation

### Step 4: History Tracking

Update `.disposable/history.json` after each phase:

```json
{
  "cycles": [
    {
      "id": "cycle_1",
      "startedAt": "ISO8601",
      "phases": {
        "spike": { "completedAt": "ISO8601", "metricsRef": "spike-complete.json" },
        "autopsy": { "completedAt": "ISO8601", "verdict": "CALIBRATE" },
        "distill": { "completedAt": "ISO8601" }
      },
      "verdict": "CALIBRATE",
      "graduated": false
    }
  ],
  "currentCycle": "cycle_2",
  "totalCycles": 2
}
```

### Step 5: Graduation Decision

When autopsy verdict is PASS, evaluate graduation criteria:

1. No unaddressed `must` constraints across all cycles
2. Architecture decisions stable (no reversals in last 2 cycles)
3. All interface contracts validated
4. Open questions resolved

If criteria met:
- Present graduation summary to user
- Ask: graduate to production or iterate once more?
- If graduating:
  1. Compile final distill spec with all cycle learnings
  2. Switch to base branch: `git checkout main` (or the branch active before the cycle)
  3. Clean up spike branches: `git branch --list 'disposable/cycle_*' | sed 's/^[* ]*//' | xargs -r git branch -D`
  3. Archive `.disposable/` state
  4. Output production-ready specification

### Step 6: Cleanup

On completion or user abort:
- Release `.disposable/.lock`
- Update `history.json`
- Report session summary:
  - Total cycles run
  - Verdict progression
  - Key learnings extracted
  - Final recommendation

## References

- references/metrics-schema.json — Unified metrics contract
- references/autopsy-schema.json — Autopsy report contract
- references/distill-template.md — Distill specification template
- references/quality-gates.md — Quality gate definitions and calibration mode
- references/security-policy.md — Security boundary enforcement
- references/tool-profiles.yml — Language-specific tool allowlist

## Configuration

`.disposable/config.json` options:

| Key | Default | Description |
|-----|---------|-------------|
| mode | "auto" | "auto" or "manual" |
| maxCycles | 5 | Maximum spike-autopsy-distill iterations |
| qualityGates | {} | Override quality gate thresholds (see quality-gates.md) |
| triangulation | true | Use Codex MCP for triangulated review in autopsy |

## Safety

- All code generation happens on isolated `disposable/cycle_{N}` branches
- No network access during spike generation (see security-policy.md)
- Sensitive data masked in all artifacts (see mask-sensitive.mjs)
- Lock file prevents concurrent cycles
- Maximum cycle limit prevents infinite loops
