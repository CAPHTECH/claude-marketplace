# Quality Gates

## Gate Definitions

**Evaluation order**:
1. Check **Missing Data** first (tests unavailable → immediate FAIL)
2. Check **FAIL** (any condition triggers FAIL)
3. Check **PASS** (all conditions must hold)
4. If neither FAIL nor PASS → verdict is **CALIBRATE** (fallback)

The CALIBRATE conditions below are informational (describe typical triggers); any state not matching PASS or FAIL is CALIBRATE by default.

### PASS
All of the following must be true:
- Lint errors = 0
- All tests pass (failed = 0)
- Line coverage >= 60%
- No `critical` severity findings in autopsy
- Autopsy average score >= 3.0

### CALIBRATE
Any of the following triggers calibration mode:
- Lint errors = 0 AND lint warnings <= 3
- Failed tests <= 2 AND failures are in non-critical paths
- Line coverage between 40-59%
- Autopsy has `critical` findings but average score >= 2.5
- Any axis scored `insufficient-evidence`

### FAIL
Any of the following:
- Lint errors > 3
- Failed tests > 2
- Line coverage < 40%
- Autopsy average score < 2.5
- Security axis score <= 2

## Calibration Mode

When verdict = CALIBRATE, the cycle enters calibration mode:

1. **Identify gaps**: List all gates that triggered CALIBRATE
2. **Targeted fix**: Address only the triggering conditions (no scope creep)
3. **Re-evaluate**: Run only the affected metrics/axes, not full autopsy
4. **Max calibration rounds**: 2 (after 2 rounds, force PASS or FAIL)

## Missing Data Handling

| Missing Source | Gate Behavior |
|---------------|---------------|
| Lint unavailable | Set `dataCompleteness.lint=false`; skip lint gate, add `insufficient-evidence` note |
| Tests unavailable | Automatic FAIL (tests are mandatory) |
| Coverage unavailable | Set `dataCompleteness.coverage=false`; skip coverage gate, add warning |
| Multiple sources missing | Automatic FAIL if tests missing; CALIBRATE otherwise |

## Threshold Overrides

Projects may override default thresholds via `.disposable/config.json`:

```json
{
  "qualityGates": {
    "coverage": { "pass": 80, "calibrate": 60 },
    "lintErrors": { "pass": 0, "calibrate": 5 },
    "autopsyMinScore": { "pass": 3.5, "calibrate": 3.0 }
  }
}
```

Overrides must be stricter or equal to defaults. Relaxing thresholds requires explicit `"allowRelaxed": true`.
