# Refactoring Execution Plan

**Date**: {{DATE}}
**Author**: {{AUTHOR}}
**Project**: {{PROJECT_NAME}}
**Issue Selected**: {{ISSUE_ID}}

---

## Input Report Summary

### Source Report
- **Report File**: `{{REPORT_FILE_PATH}}`
- **Analysis Date**: {{ANALYSIS_DATE}}
- **Priority**: {{PRIORITY}} (🔴 Critical / 🟡 Medium / 🟢 Low)
- **Priority Score**: {{PRIORITY_SCORE}}

### Issue Description
{{ISSUE_DESCRIPTION}}

### Affected Files
{{#AFFECTED_FILES}}
- `{{FILE_PATH}}` ({{LOC}} lines, {{CC}} complexity)
{{/AFFECTED_FILES}}

### Recommended Actions
{{#RECOMMENDED_ACTIONS}}
- {{ACTION}}
{{/RECOMMENDED_ACTIONS}}

---

## Goals and Success Criteria

### Primary Goal
{{PRIMARY_GOAL}}

### Success Criteria

#### Metrics Targets
| Metric | Before | Target | Improvement |
|--------|--------|--------|-------------|
| Cyclomatic Complexity | {{CC_BEFORE}} | {{CC_TARGET}} | {{CC_IMPROVEMENT}} |
| File LOC | {{LOC_BEFORE}} | {{LOC_TARGET}} | {{LOC_IMPROVEMENT}} |
| LCOM4 (Cohesion) | {{LCOM4_BEFORE}} | {{LCOM4_TARGET}} | {{LCOM4_IMPROVEMENT}} |
| Import Count | {{IMPORTS_BEFORE}} | {{IMPORTS_TARGET}} | {{IMPORTS_IMPROVEMENT}} |

#### Functional Requirements
- [ ] All tests pass (100% green)
- [ ] No type errors introduced
- [ ] No new lint warnings
- [ ] Performance within 5% of baseline
- [ ] Test coverage maintained or improved

#### Non-Functional Requirements
- [ ] Code is more readable
- [ ] Single Responsibility Principle satisfied
- [ ] Open/Closed Principle satisfied (if applicable)
- [ ] Dependencies properly injected

---

## Dependencies and Constraints

### File Dependencies
{{#FILE_DEPENDENCIES}}
- `{{SOURCE_FILE}}` depends on `{{TARGET_FILE}}`
{{/FILE_DEPENDENCIES}}

### Constraints
{{#CONSTRAINTS}}
- {{CONSTRAINT}}
{{/CONSTRAINTS}}

### Blockers
{{#BLOCKERS}}
- [ ] {{BLOCKER}} (Status: {{STATUS}})
{{/BLOCKERS}}

---

## Execution Steps

### Step 1: {{STEP_1_NAME}}

**Objective**: {{STEP_1_OBJECTIVE}}

**Pattern**: {{STEP_1_PATTERN}} (e.g., Extract Method, Extract Class, Move Method)

**Actions**:
{{#STEP_1_ACTIONS}}
1. {{ACTION}}
{{/STEP_1_ACTIONS}}

**Files to Modify**:
{{#STEP_1_FILES}}
- `{{FILE_PATH}}` - {{MODIFICATION_TYPE}}
{{/STEP_1_FILES}}

**Verification Commands**:
```bash
# Tests
pnpm vitest run {{STEP_1_TEST_SCOPE}}

# Type check
pnpm tsc --noEmit {{STEP_1_FILES}}

# Lint
pnpm eslint {{STEP_1_FILES}}

# Build (if applicable)
pnpm build
```

**Expected Outcome**:
- [ ] Tests pass ({{STEP_1_TEST_COUNT}} tests)
- [ ] No type errors
- [ ] No new lint warnings
- [ ] Complexity reduced by {{STEP_1_CC_REDUCTION}}

**Rollback Procedure**:
```bash
git reset --hard HEAD~1
```

---

### Step 2: {{STEP_2_NAME}}

**Objective**: {{STEP_2_OBJECTIVE}}

**Pattern**: {{STEP_2_PATTERN}}

**Actions**:
{{#STEP_2_ACTIONS}}
1. {{ACTION}}
{{/STEP_2_ACTIONS}}

**Files to Modify**:
{{#STEP_2_FILES}}
- `{{FILE_PATH}}` - {{MODIFICATION_TYPE}}
{{/STEP_2_FILES}}

**Verification Commands**:
```bash
# Tests
pnpm vitest run {{STEP_2_TEST_SCOPE}}

# Type check
pnpm tsc --noEmit {{STEP_2_FILES}}

# Lint
pnpm eslint {{STEP_2_FILES}}

# Build
pnpm build
```

**Expected Outcome**:
- [ ] Tests pass ({{STEP_2_TEST_COUNT}} tests)
- [ ] No type errors
- [ ] No new lint warnings
- [ ] File split completed

**Rollback Procedure**:
```bash
git reset --hard HEAD~1
```

---

### Step 3: {{STEP_3_NAME}}

**Objective**: {{STEP_3_OBJECTIVE}}

**Pattern**: {{STEP_3_PATTERN}}

**Actions**:
{{#STEP_3_ACTIONS}}
1. {{ACTION}}
{{/STEP_3_ACTIONS}}

**Files to Modify**:
{{#STEP_3_FILES}}
- `{{FILE_PATH}}` - {{MODIFICATION_TYPE}}
{{/STEP_3_FILES}}

**Verification Commands**:
```bash
# Tests
pnpm vitest run {{STEP_3_TEST_SCOPE}}

# Type check
pnpm tsc --noEmit {{STEP_3_FILES}}

# Lint
pnpm eslint {{STEP_3_FILES}}

# Build
pnpm build
```

**Expected Outcome**:
- [ ] Tests pass ({{STEP_3_TEST_COUNT}} tests)
- [ ] No type errors
- [ ] No new lint warnings
- [ ] Dependencies properly injected

**Rollback Procedure**:
```bash
git reset --hard HEAD~1
```

---

{{#ADDITIONAL_STEPS}}
### Step {{STEP_NUMBER}}: {{STEP_NAME}}

**Objective**: {{STEP_OBJECTIVE}}

**Pattern**: {{STEP_PATTERN}}

**Actions**:
{{#STEP_ACTIONS}}
1. {{ACTION}}
{{/STEP_ACTIONS}}

**Files to Modify**:
{{#STEP_FILES}}
- `{{FILE_PATH}}` - {{MODIFICATION_TYPE}}
{{/STEP_FILES}}

**Verification Commands**:
```bash
pnpm vitest run {{STEP_TEST_SCOPE}}
pnpm tsc --noEmit {{STEP_FILES}}
pnpm eslint {{STEP_FILES}}
pnpm build
```

**Expected Outcome**:
- [ ] Tests pass
- [ ] No type errors
- [ ] No new lint warnings

**Rollback Procedure**:
```bash
git reset --hard HEAD~1
```

---
{{/ADDITIONAL_STEPS}}

---

## Characterization Tests Plan

### Existing Test Coverage
- **Test Files**: {{EXISTING_TEST_FILES}}
- **Test Count**: {{EXISTING_TEST_COUNT}}
- **Coverage**: {{EXISTING_COVERAGE}}%

### New Tests Required

#### Test 1: {{NEW_TEST_1_NAME}}
**Purpose**: {{NEW_TEST_1_PURPOSE}}
**File**: `{{NEW_TEST_1_FILE}}`
**Coverage Gap**: {{NEW_TEST_1_GAP}}

**Test Structure**:
```typescript
describe('{{NEW_TEST_1_DESCRIBE}}', () => {
  it('{{NEW_TEST_1_IT}}', () => {
    // Given: {{NEW_TEST_1_GIVEN}}
    // When: {{NEW_TEST_1_WHEN}}
    // Then: {{NEW_TEST_1_THEN}}
  });
});
```

---

#### Test 2: {{NEW_TEST_2_NAME}}
**Purpose**: {{NEW_TEST_2_PURPOSE}}
**File**: `{{NEW_TEST_2_FILE}}`
**Coverage Gap**: {{NEW_TEST_2_GAP}}

**Test Structure**:
```typescript
describe('{{NEW_TEST_2_DESCRIBE}}', () => {
  it('{{NEW_TEST_2_IT}}', () => {
    // Given: {{NEW_TEST_2_GIVEN}}
    // When: {{NEW_TEST_2_WHEN}}
    // Then: {{NEW_TEST_2_THEN}}
  });
});
```

---

{{#ADDITIONAL_NEW_TESTS}}
#### Test {{TEST_NUMBER}}: {{NEW_TEST_NAME}}
**Purpose**: {{NEW_TEST_PURPOSE}}
**File**: `{{NEW_TEST_FILE}}`

**Test Structure**:
```typescript
describe('{{NEW_TEST_DESCRIBE}}', () => {
  it('{{NEW_TEST_IT}}', () => {
    // Given: {{NEW_TEST_GIVEN}}
    // When: {{NEW_TEST_WHEN}}
    // Then: {{NEW_TEST_THEN}}
  });
});
```

---
{{/ADDITIONAL_NEW_TESTS}}

---

## Risk Assessment

### High Risks

{{#HIGH_RISKS}}
#### Risk: {{RISK_NAME}}
- **Probability**: {{RISK_PROBABILITY}} (Low / Medium / High)
- **Impact**: {{RISK_IMPACT}} (Low / Medium / High)
- **Mitigation**: {{RISK_MITIGATION}}
{{/HIGH_RISKS}}

### Medium Risks

{{#MEDIUM_RISKS}}
#### Risk: {{RISK_NAME}}
- **Mitigation**: {{RISK_MITIGATION}}
{{/MEDIUM_RISKS}}

---

## Timeline and Effort Estimate

### Estimated Duration
- **Total**: {{TOTAL_HOURS}} hours ({{TOTAL_DAYS}} days)
- **Breakdown**:
  - Characterization tests: {{CHAR_TEST_HOURS}} hours
  - Refactoring execution: {{REFACTOR_HOURS}} hours
  - Validation and testing: {{VALIDATION_HOURS}} hours
  - Documentation: {{DOC_HOURS}} hours

### Milestones
| Milestone | Duration | Deadline | Status |
|-----------|----------|----------|--------|
| Characterization tests added | {{MILESTONE_1_DURATION}} | {{MILESTONE_1_DEADLINE}} | ⏳ Pending |
| Step 1 completed | {{MILESTONE_2_DURATION}} | {{MILESTONE_2_DEADLINE}} | ⏳ Pending |
| Step 2 completed | {{MILESTONE_3_DURATION}} | {{MILESTONE_3_DEADLINE}} | ⏳ Pending |
| Step 3 completed | {{MILESTONE_4_DURATION}} | {{MILESTONE_4_DEADLINE}} | ⏳ Pending |
| Final validation passed | {{MILESTONE_5_DURATION}} | {{MILESTONE_5_DEADLINE}} | ⏳ Pending |
| Pull request created | {{MILESTONE_6_DURATION}} | {{MILESTONE_6_DEADLINE}} | ⏳ Pending |

---

## Pre-Execution Checklist

### Environment
- [ ] All tests pass (baseline green)
- [ ] No type errors (`pnpm tsc --noEmit`)
- [ ] Git working directory clean
- [ ] Feature branch created
- [ ] Baseline metrics captured

### Documentation
- [ ] Refactoring discovery report reviewed
- [ ] Issue fully understood
- [ ] Dependencies identified
- [ ] Risks assessed

### Tools
- [ ] TypeScript compiler available
- [ ] Test framework configured
- [ ] ESLint configured
- [ ] Git configured
- [ ] Verification script ready (`scripts/verify-step.sh`)

### Team
- [ ] Refactoring plan reviewed by team
- [ ] Stakeholders informed
- [ ] Time allocated for execution

---

## Baseline Metrics Capture

### Test Metrics
```bash
pnpm vitest run --reporter=json > baseline-tests.json
```

**Results**:
- Total tests: {{BASELINE_TEST_COUNT}}
- Pass rate: {{BASELINE_PASS_RATE}}%
- Execution time: {{BASELINE_TEST_TIME}}s

### Type Checking
```bash
pnpm tsc --noEmit 2> baseline-types.txt
```

**Results**:
- Type errors: {{BASELINE_TYPE_ERRORS}} (should be 0)

### Lint Check
```bash
pnpm eslint src/ --format=json > baseline-lint.json
```

**Results**:
- Errors: {{BASELINE_LINT_ERRORS}}
- Warnings: {{BASELINE_LINT_WARNINGS}}

### Performance Metrics
```bash
pnpm test:performance --json > baseline-perf.json
```

**Results**:
- {{PERF_METRIC_1}}: {{BASELINE_PERF_1}}
- {{PERF_METRIC_2}}: {{BASELINE_PERF_2}}

### Code Metrics
- **File LOC**: {{BASELINE_FILE_LOC}}
- **Cyclomatic Complexity**: {{BASELINE_CC}}
- **Function Count**: {{BASELINE_FUNCTION_COUNT}}
- **Import Count**: {{BASELINE_IMPORT_COUNT}}

---

## Communication Plan

### Status Updates
- **Frequency**: {{UPDATE_FREQUENCY}} (e.g., daily, after each step)
- **Channel**: {{UPDATE_CHANNEL}} (e.g., Slack, email, standup)
- **Stakeholders**: {{STAKEHOLDERS}}

### Escalation Path
1. **Issue**: Step validation fails
   - **Action**: Rollback and investigate
   - **Notify**: Team lead
   - **Timeline**: Within 1 hour

2. **Issue**: Multiple rollbacks (>3)
   - **Action**: Pause and reassess approach
   - **Notify**: Project manager
   - **Timeline**: Immediate

3. **Issue**: Blockers discovered
   - **Action**: Document blocker
   - **Notify**: Stakeholders
   - **Timeline**: Within 2 hours

---

## Success Definition

This refactoring will be considered successful when:

1. **Metrics Targets Met**:
   - [ ] Cyclomatic Complexity ≤ {{CC_TARGET}}
   - [ ] File LOC ≤ {{LOC_TARGET}}
   - [ ] LCOM4 ≤ {{LCOM4_TARGET}}

2. **Quality Gates Passed**:
   - [ ] 100% tests pass
   - [ ] No type errors
   - [ ] No new lint warnings
   - [ ] Test coverage maintained or improved

3. **Deliverables Completed**:
   - [ ] All steps executed successfully
   - [ ] Execution log generated
   - [ ] Pull request created and merged
   - [ ] Documentation updated

4. **Team Acceptance**:
   - [ ] Code review approved
   - [ ] No post-merge issues reported
   - [ ] Team finds code clearer and easier to maintain

---

## Approval

**Plan Prepared By**: {{AUTHOR}}
**Date**: {{DATE}}

**Reviewed By**: {{REVIEWER_NAME}}
**Review Date**: {{REVIEW_DATE}}
**Status**: {{REVIEW_STATUS}} (⏳ Pending / ✅ Approved / ❌ Rejected)

**Reviewer Comments**:
{{REVIEWER_COMMENTS}}

---

## Execution Log Reference

Once execution begins, track progress in:
- **Execution Log**: `{{EXECUTION_LOG_PATH}}`
- **Git Branch**: `{{GIT_BRANCH}}`
- **Pull Request**: `{{PR_URL}}` (to be created)

---

**Note**: This plan is a living document and may be updated during execution if new information or challenges arise. All significant changes should be documented in the execution log.
