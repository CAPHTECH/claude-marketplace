# Refactoring Execution Log

**Project**: {{PROJECT_NAME}}
**Issue ID**: {{ISSUE_ID}}
**Execution Date**: {{START_DATE}} - {{END_DATE}}
**Executor**: {{EXECUTOR_NAME}}
**Status**: {{STATUS}} (⏳ In Progress / ✅ Completed / ❌ Failed)

---

## Executive Summary

**Objective**: {{OBJECTIVE}}

**Outcome**: {{OUTCOME_SUMMARY}}

**Metrics Improvement**:
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cyclomatic Complexity | {{CC_BEFORE}} | {{CC_AFTER}} | {{CC_IMPROVEMENT}} |
| File LOC | {{LOC_BEFORE}} | {{LOC_AFTER}} | {{LOC_IMPROVEMENT}} |
| LCOM4 (Cohesion) | {{LCOM4_BEFORE}} | {{LCOM4_AFTER}} | {{LCOM4_IMPROVEMENT}} |
| Test Coverage | {{COV_BEFORE}}% | {{COV_AFTER}}% | {{COV_IMPROVEMENT}}% |

**Time Spent**: {{ACTUAL_HOURS}} hours (Estimated: {{ESTIMATED_HOURS}} hours)

---

## Baseline Capture

**Date**: {{BASELINE_DATE}}

### Test Results
```bash
pnpm vitest run --reporter=json
```
- Total tests: {{BASELINE_TEST_COUNT}}
- Pass rate: 100% ✅
- Execution time: {{BASELINE_TEST_TIME}}s

### Type Check
```bash
pnpm tsc --noEmit
```
- Type errors: 0 ✅

### Lint Check
```bash
pnpm eslint src/ --format=json
```
- Errors: {{BASELINE_LINT_ERRORS}}
- Warnings: {{BASELINE_LINT_WARNINGS}}

---

## Execution Steps

### Step 1: {{STEP_1_NAME}}

**Date**: {{STEP_1_DATE}}
**Duration**: {{STEP_1_DURATION}} minutes
**Pattern**: {{STEP_1_PATTERN}}

**Objective**: {{STEP_1_OBJECTIVE}}

**Changes Made**:
{{#STEP_1_CHANGES}}
- {{CHANGE}}
{{/STEP_1_CHANGES}}

**Files Modified**:
{{#STEP_1_FILES}}
- `{{FILE_PATH}}` (+{{LINES_ADDED}} -{{LINES_REMOVED}})
{{/STEP_1_FILES}}

**Commands Executed**:
```bash
{{STEP_1_COMMANDS}}
```

**Validation Results**:
- Tests: {{STEP_1_TEST_RESULT}} ({{STEP_1_TEST_COUNT}} tests, {{STEP_1_TEST_TIME}}s)
- Types: {{STEP_1_TYPE_RESULT}}
- Lint: {{STEP_1_LINT_RESULT}} ({{STEP_1_LINT_ERRORS}} errors, {{STEP_1_LINT_WARNINGS}} warnings)
- Build: {{STEP_1_BUILD_RESULT}}

**Metrics After Step**:
- CC: {{STEP_1_CC}}
- LOC: {{STEP_1_LOC}}

**Commit**: `{{STEP_1_COMMIT_HASH}}`
**Commit Message**:
```
{{STEP_1_COMMIT_MESSAGE}}
```

**Issues Encountered**: {{STEP_1_ISSUES}}

**Rollback**: {{STEP_1_ROLLBACK_STATUS}} (✅ Not needed / ⚠️ Rolled back)

---

### Step 2: {{STEP_2_NAME}}

**Date**: {{STEP_2_DATE}}
**Duration**: {{STEP_2_DURATION}} minutes
**Pattern**: {{STEP_2_PATTERN}}

**Objective**: {{STEP_2_OBJECTIVE}}

**Changes Made**:
{{#STEP_2_CHANGES}}
- {{CHANGE}}
{{/STEP_2_CHANGES}}

**Files Modified**:
{{#STEP_2_FILES}}
- `{{FILE_PATH}}` (+{{LINES_ADDED}} -{{LINES_REMOVED}})
{{/STEP_2_FILES}}

**Commands Executed**:
```bash
{{STEP_2_COMMANDS}}
```

**Validation Results**:
- Tests: {{STEP_2_TEST_RESULT}}
- Types: {{STEP_2_TYPE_RESULT}}
- Lint: {{STEP_2_LINT_RESULT}}
- Build: {{STEP_2_BUILD_RESULT}}

**Metrics After Step**:
- CC: {{STEP_2_CC}}
- LOC: {{STEP_2_LOC}}

**Commit**: `{{STEP_2_COMMIT_HASH}}`

**Issues Encountered**: {{STEP_2_ISSUES}}

**Rollback**: {{STEP_2_ROLLBACK_STATUS}}

---

{{#ADDITIONAL_STEPS}}
### Step {{STEP_NUMBER}}: {{STEP_NAME}}

**Date**: {{STEP_DATE}}
**Duration**: {{STEP_DURATION}} minutes
**Pattern**: {{STEP_PATTERN}}

**Objective**: {{STEP_OBJECTIVE}}

**Changes Made**:
{{#STEP_CHANGES}}
- {{CHANGE}}
{{/STEP_CHANGES}}

**Files Modified**:
{{#STEP_FILES}}
- `{{FILE_PATH}}` (+{{LINES_ADDED}} -{{LINES_REMOVED}})
{{/STEP_FILES}}

**Validation Results**:
- Tests: {{STEP_TEST_RESULT}}
- Types: {{STEP_TYPE_RESULT}}
- Lint: {{STEP_LINT_RESULT}}

**Commit**: `{{STEP_COMMIT_HASH}}`

**Rollback**: {{STEP_ROLLBACK_STATUS}}

---
{{/ADDITIONAL_STEPS}}

---

## Final Validation

**Date**: {{FINAL_VALIDATION_DATE}}

### Full Test Suite
```bash
pnpm vitest run --coverage
```
- Total tests: {{FINAL_TEST_COUNT}}
- Pass rate: {{FINAL_PASS_RATE}}%
- Execution time: {{FINAL_TEST_TIME}}s
- Coverage: {{FINAL_COVERAGE}}%

**Result**: {{FINAL_TEST_RESULT}}

### Type Check
```bash
pnpm tsc --noEmit
```
**Result**: {{FINAL_TYPE_RESULT}}

### Lint Check
```bash
pnpm eslint src/
```
- Errors: {{FINAL_LINT_ERRORS}}
- Warnings: {{FINAL_LINT_WARNINGS}}

**Result**: {{FINAL_LINT_RESULT}}

### Build Check
```bash
pnpm build
```
**Result**: {{FINAL_BUILD_RESULT}}

---

## Before/After Comparison

### Code Structure
**Before**:
```typescript
{{CODE_BEFORE}}
```

**After**:
```typescript
{{CODE_AFTER}}
```

### Metrics Comparison
| Metric | Before | After | Change | Status |
|--------|--------|-------|--------|--------|
| Cyclomatic Complexity | {{CC_BEFORE}} | {{CC_AFTER}} | {{CC_CHANGE}} | {{CC_STATUS}} |
| File LOC | {{LOC_BEFORE}} | {{LOC_AFTER}} | {{LOC_CHANGE}} | {{LOC_STATUS}} |
| Function Avg LOC | {{FN_LOC_BEFORE}} | {{FN_LOC_AFTER}} | {{FN_LOC_CHANGE}} | {{FN_LOC_STATUS}} |
| LCOM4 | {{LCOM4_BEFORE}} | {{LCOM4_AFTER}} | {{LCOM4_CHANGE}} | {{LCOM4_STATUS}} |
| Import Count | {{IMP_BEFORE}} | {{IMP_AFTER}} | {{IMP_CHANGE}} | {{IMP_STATUS}} |
| Test Coverage | {{COV_BEFORE}}% | {{COV_AFTER}}% | {{COV_CHANGE}}% | {{COV_STATUS}} |

**Legend**: ✅ Improved | ➡️ Maintained | ⚠️ Degraded

---

## Decisions and Rationale

{{#DECISIONS}}
### Decision {{DECISION_NUMBER}}: {{DECISION_TITLE}}

**Context**: {{DECISION_CONTEXT}}

**Options Considered**:
{{#DECISION_OPTIONS}}
- {{OPTION}}
{{/DECISION_OPTIONS}}

**Decision**: {{DECISION_MADE}}

**Rationale**: {{DECISION_RATIONALE}}

---
{{/DECISIONS}}

---

## Issues and Resolutions

{{#ISSUES}}
### Issue {{ISSUE_NUMBER}}: {{ISSUE_TITLE}}

**Description**: {{ISSUE_DESCRIPTION}}

**Discovered**: {{ISSUE_DATE}} (Step {{ISSUE_STEP}})

**Impact**: {{ISSUE_IMPACT}}

**Resolution**: {{ISSUE_RESOLUTION}}

**Time Lost**: {{ISSUE_TIME_LOST}} minutes

---
{{/ISSUES}}

---

## Rollbacks

{{#ROLLBACKS}}
### Rollback {{ROLLBACK_NUMBER}}

**Date**: {{ROLLBACK_DATE}}
**Step**: {{ROLLBACK_STEP}}
**Reason**: {{ROLLBACK_REASON}}

**Command**:
```bash
{{ROLLBACK_COMMAND}}
```

**Recovery**: {{ROLLBACK_RECOVERY}}

---
{{/ROLLBACKS}}

**Total Rollbacks**: {{TOTAL_ROLLBACKS}}

---

## Lessons Learned

### What Went Well
{{#WENT_WELL}}
- {{ITEM}}
{{/WENT_WELL}}

### What Could Be Improved
{{#COULD_IMPROVE}}
- {{ITEM}}
{{/COULD_IMPROVE}}

### Surprises
{{#SURPRISES}}
- {{ITEM}}
{{/SURPRISES}}

### Recommendations for Future Refactoring
{{#RECOMMENDATIONS}}
- {{ITEM}}
{{/RECOMMENDATIONS}}

---

## Pull Request

**Branch**: `{{GIT_BRANCH}}`
**PR URL**: {{PR_URL}}
**PR Title**: {{PR_TITLE}}

**PR Description**:
```markdown
{{PR_DESCRIPTION}}
```

**Reviewers**: {{REVIEWERS}}
**Status**: {{PR_STATUS}} (⏳ Pending / ✅ Approved / ❌ Changes Requested / 🎉 Merged)

---

## References

- **Refactoring Discovery Report**: `{{DISCOVERY_REPORT_PATH}}`
- **Execution Plan**: `{{EXECUTION_PLAN_PATH}}`
- **Commits**: {{GIT_COMMIT_RANGE}}
- **Related Issues**: {{RELATED_ISSUES}}

---

## Sign-Off

**Executor**: {{EXECUTOR_NAME}}
**Date**: {{COMPLETION_DATE}}
**Status**: {{FINAL_STATUS}}

**Reviewer**: {{REVIEWER_NAME}}
**Review Date**: {{REVIEW_DATE}}
**Approval**: {{APPROVAL_STATUS}}

---

**Notes**: {{ADDITIONAL_NOTES}}
