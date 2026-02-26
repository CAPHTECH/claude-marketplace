# Refactoring Plan: {{MODULE_NAME}}

**Date**: {{DATE}}
**Author**: {{AUTHOR}}
**Target**: `{{FILE_PATH}}`
**Current Health Score**: {{CURRENT_SCORE}}/100
**Target Health Score**: {{TARGET_SCORE}}/100

---

## Problem Statement

### Current Issues

{{#ISSUES}}
- **{{ISSUE_TYPE}}**: {{DESCRIPTION}}
  - Metric: {{METRIC_NAME}} = {{CURRENT_VALUE}} (threshold: {{THRESHOLD}})
  - Impact: {{IMPACT}}
  - **Detection Evidence**:
    - Tool: {{DETECTION_TOOL}}
    - Query: `{{DETECTION_QUERY}}`
    - Validation: {{VALIDATION_STATUS}}
{{/ISSUES}}

### Root Cause Analysis

**Hypothesis**: {{ROOT_CAUSE_HYPOTHESIS}}

**Evidence**:
{{#ROOT_CAUSE_EVIDENCE}}
- {{EVIDENCE_ITEM}}
{{/ROOT_CAUSE_EVIDENCE}}

**Confirmed By**:
- Static analysis: {{STATIC_ANALYSIS_FINDINGS}}
- Git history: {{GIT_HISTORY_FINDINGS}}
- Team feedback: {{TEAM_FEEDBACK}}

{{ROOT_CAUSE}}

---

## Goals

### Primary Goals
1. {{GOAL_1}}
2. {{GOAL_2}}
3. {{GOAL_3}}

### Success Criteria
- [ ] Cyclomatic complexity ≤ {{TARGET_CC}}
- [ ] File length ≤ {{TARGET_LOC}} lines
- [ ] LCOM4 ≤ {{TARGET_LCOM4}}
- [ ] All existing tests pass
- [ ] New tests added for refactored code
- [ ] No performance regression

---

## Approach

### Strategy: {{STRATEGY_NAME}}

**Why this approach**:
{{STRATEGY_RATIONALE}}

**Alternatives considered**:
{{#ALTERNATIVES}}
- {{ALTERNATIVE_NAME}}: {{REASON_NOT_CHOSEN}}
{{/ALTERNATIVES}}

---

## Refactoring Steps

### Phase 1: Preparation

**Estimated time**: {{PHASE_1_TIME}}

1. **Write characterization tests** (if missing)
   - [ ] Test current behavior
   - [ ] Cover edge cases
   - [ ] Establish baseline performance

2. **Document current behavior**
   - [ ] Map data flow
   - [ ] Identify dependencies
   - [ ] Note any assumptions

3. **Create feature branch**
   ```bash
   git checkout -b refactor/{{BRANCH_NAME}}
   ```

### Phase 2: Extract Methods/Classes

**Estimated time**: {{PHASE_2_TIME}}

{{#EXTRACTIONS}}
#### Step {{STEP_NUMBER}}: Extract {{EXTRACT_NAME}}

**From**: `{{SOURCE_FILE}}:{{SOURCE_LINE}}`
**To**: `{{TARGET_FILE}}`

**Code to extract**:
```typescript
{{CODE_BEFORE}}
```

**New structure**:
```typescript
{{CODE_AFTER}}
```

**Tests to update**:
- {{TEST_FILE_1}}
- {{TEST_FILE_2}}

**Verification**:
- [ ] Tests pass
- [ ] Metrics improved
- [ ] No breaking changes

---
{{/EXTRACTIONS}}

### Phase 3: Introduce Abstractions

**Estimated time**: {{PHASE_3_TIME}}

{{#ABSTRACTIONS}}
#### Step {{STEP_NUMBER}}: {{ABSTRACTION_NAME}}

**Pattern**: {{PATTERN}} (e.g., Strategy, Factory, etc.)

**New interface**:
```typescript
{{INTERFACE_CODE}}
```

**Implementations**:
```typescript
{{IMPLEMENTATION_CODE}}
```

**Migration**:
```typescript
// Before
{{OLD_CODE}}

// After
{{NEW_CODE}}
```

**Verification**:
- [ ] Interface segregation principle satisfied
- [ ] Dependencies inverted
- [ ] Tests pass

---
{{/ABSTRACTIONS}}

### Phase 4: Clean Up

**Estimated time**: {{PHASE_4_TIME}}

1. **Remove dead code**
   - [ ] Unused imports
   - [ ] Commented code
   - [ ] Redundant functions

2. **Improve naming**
   - [ ] Rename unclear variables
   - [ ] Update function names
   - [ ] Clarify type names

3. **Update documentation**
   - [ ] Add/update JSDoc comments
   - [ ] Update README if needed
   - [ ] Document architectural decisions

4. **Final verification**
   - [ ] All tests pass
   - [ ] Linter passes
   - [ ] Type checker passes
   - [ ] Build succeeds

5. **Re-run analysis**
   - [ ] Verify metrics improved
   - [ ] Confirm issue resolved in detection tool
   - [ ] Update baseline thresholds if needed

---

## Validation Plan

### Pre-Refactoring Validation

1. **Confirm issue exists**:
   - [ ] Re-run detection tool
   - [ ] Verify metrics match report
   - [ ] Check if context justifies the violation

2. **Stakeholder buy-in**:
   - [ ] Reviewed by {{REVIEWER_1}}
   - [ ] Approved by {{APPROVER}}
   - [ ] Team consensus on approach

### Post-Refactoring Validation

1. **Metric verification**:
   - [ ] Re-run static analysis
   - [ ] Confirm all target metrics met
   - [ ] No new issues introduced

2. **Functional verification**:
   - [ ] All tests pass
   - [ ] No performance regression
   - [ ] No behavior changes

3. **Evidence documentation**:
   - [ ] Before/after screenshots
   - [ ] Tool output comparison
   - [ ] Code diff reviewed

---

## Testing Strategy

### Unit Tests

{{#UNIT_TESTS}}
- **Test**: {{TEST_NAME}}
  - **Covers**: {{COVERAGE}}
  - **File**: `{{TEST_FILE}}`
{{/UNIT_TESTS}}

### Integration Tests

{{#INTEGRATION_TESTS}}
- **Test**: {{TEST_NAME}}
  - **Covers**: {{COVERAGE}}
  - **File**: `{{TEST_FILE}}`
{{/INTEGRATION_TESTS}}

### Performance Tests

- **Baseline**: {{BASELINE_PERFORMANCE}}
- **Target**: {{TARGET_PERFORMANCE}}
- **Measurement**: {{MEASUREMENT_METHOD}}

---

## Risk Assessment

### High Risks
{{#HIGH_RISKS}}
- **Risk**: {{RISK}}
  - **Probability**: {{PROBABILITY}}
  - **Impact**: {{IMPACT}}
  - **Mitigation**: {{MITIGATION}}
{{/HIGH_RISKS}}

### Medium Risks
{{#MEDIUM_RISKS}}
- **Risk**: {{RISK}}
  - **Mitigation**: {{MITIGATION}}
{{/MEDIUM_RISKS}}

---

## Dependencies & Blockers

### Dependencies
{{#DEPENDENCIES}}
- {{DEPENDENCY}}: {{STATUS}}
{{/DEPENDENCIES}}

### Blockers
{{#BLOCKERS}}
- {{BLOCKER}}: {{RESOLUTION_PLAN}}
{{/BLOCKERS}}

---

## Rollback Plan

If issues arise:

1. **Immediate rollback**
   ```bash
   git checkout main
   git branch -D refactor/{{BRANCH_NAME}}
   ```

2. **Partial rollback** (if some changes are safe)
   - Revert specific commits
   - Keep test improvements
   - Document what to retry

3. **Communication**
   - Notify team
   - Document issues encountered
   - Update plan based on learnings

---

## Metrics Tracking

### Before Refactoring

| Metric | Current | Threshold | Status |
|--------|---------|-----------|--------|
| Cyclomatic Complexity | {{CC_BEFORE}} | {{CC_THRESHOLD}} | {{CC_STATUS}} |
| File Length (LOC) | {{LOC_BEFORE}} | {{LOC_THRESHOLD}} | {{LOC_STATUS}} |
| Function Avg Length | {{FN_BEFORE}} | {{FN_THRESHOLD}} | {{FN_STATUS}} |
| LCOM4 | {{LCOM4_BEFORE}} | {{LCOM4_THRESHOLD}} | {{LCOM4_STATUS}} |
| Import Count | {{IMP_BEFORE}} | {{IMP_THRESHOLD}} | {{IMP_STATUS}} |

### After Refactoring

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Cyclomatic Complexity | {{CC_TARGET}} | {{CC_AFTER}} | {{CC_RESULT}} |
| File Length (LOC) | {{LOC_TARGET}} | {{LOC_AFTER}} | {{LOC_RESULT}} |
| Function Avg Length | {{FN_TARGET}} | {{FN_AFTER}} | {{FN_RESULT}} |
| LCOM4 | {{LCOM4_TARGET}} | {{LCOM4_AFTER}} | {{LCOM4_RESULT}} |
| Import Count | {{IMP_TARGET}} | {{IMP_AFTER}} | {{IMP_RESULT}} |

---

## Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Preparation | {{PREP_TIME}} | {{PREP_START}} | {{PREP_END}} | ⏳ |
| Extract Methods | {{EXTRACT_TIME}} | {{EXTRACT_START}} | {{EXTRACT_END}} | ⏳ |
| Abstractions | {{ABSTRACT_TIME}} | {{ABSTRACT_START}} | {{ABSTRACT_END}} | ⏳ |
| Clean Up | {{CLEANUP_TIME}} | {{CLEANUP_START}} | {{CLEANUP_END}} | ⏳ |
| **Total** | **{{TOTAL_TIME}}** | {{TOTAL_START}} | {{TOTAL_END}} | ⏳ |

---

## Review Checklist

### Code Review
- [ ] Complexity reduced to target levels
- [ ] No new SOLID violations introduced
- [ ] Consistent with project architecture
- [ ] All edge cases handled
- [ ] Error handling improved

### Testing
- [ ] All existing tests pass
- [ ] New tests added for new abstractions
- [ ] Coverage maintained or improved
- [ ] Performance benchmarks met

### Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] Architecture decisions documented
- [ ] Migration guide (if needed)

### Quality Gates
- [ ] Linter passes
- [ ] Type checker passes
- [ ] Build succeeds
- [ ] CI/CD pipeline green

---

## Lessons Learned

**To be filled after completion**:

### What went well
-

### What could be improved
-

### What to avoid next time
-

### Recommendations for future refactoring
-

---

## References

- Design Standards: `references/design-standards.md`
- Refactoring Patterns: `references/refactoring-patterns.md`
- Related Issues: {{RELATED_ISSUES}}
- ADRs: {{RELATED_ADRS}}
