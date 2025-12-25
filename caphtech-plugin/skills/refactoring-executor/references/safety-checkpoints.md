# Safety Checkpoints for Refactoring Execution

## Overview

This document defines critical safety checkpoints throughout the refactoring process. Each checkpoint must be verified before proceeding to the next stage. Failure to pass any checkpoint triggers a rollback or investigation procedure.

---

## Checkpoint Categories

### 🔴 Mandatory Checkpoints
Must pass 100% - failure stops execution immediately

### 🟡 Advisory Checkpoints
Should pass - failure requires documentation and explicit approval

### 🟢 Optional Checkpoints
Nice-to-have - failure is acceptable with justification

---

## Stage 1: Pre-Refactoring Validation

### 🔴 Mandatory: All Tests Pass
**Description**: Entire test suite must be green before starting

**Verification**:
```bash
pnpm test --run
# Exit code must be 0
```

**Success Criteria**:
- [ ] 100% of tests pass
- [ ] No flaky tests detected
- [ ] Test execution time within normal range

**Failure Action**:
1. **STOP** - Do not proceed with refactoring
2. Document test failures in execution log
3. Fix failing tests before starting refactoring
4. If tests are unreliable, add to technical debt backlog

**Rationale**: Starting with failing tests makes it impossible to detect regressions introduced by refactoring.

---

### 🔴 Mandatory: No Type Errors
**Description**: TypeScript compilation must succeed

**Verification**:
```bash
pnpm tsc --noEmit
# Exit code must be 0
```

**Success Criteria**:
- [ ] Zero type errors
- [ ] No `@ts-ignore` or `@ts-expect-error` added recently
- [ ] Strict mode enabled (if applicable)

**Failure Action**:
1. **STOP** - Do not proceed
2. Fix type errors
3. Review recent commits for type safety degradation

**Rationale**: Type errors indicate existing issues that will compound during refactoring.

---

### 🔴 Mandatory: Clean Git Working Directory
**Description**: No uncommitted changes

**Verification**:
```bash
git status
# Output should show "nothing to commit, working tree clean"
```

**Success Criteria**:
- [ ] No staged changes
- [ ] No unstaged changes
- [ ] No untracked files (except intentional gitignored files)

**Failure Action**:
1. **STOP** - Do not proceed
2. Commit or stash existing changes
3. Ensure rollback capability is available

**Rationale**: Clean state enables safe rollback via `git reset --hard`.

---

### 🟡 Advisory: Lint Warnings Baseline
**Description**: Document current lint warnings for comparison

**Verification**:
```bash
pnpm eslint --format=json src/ > baseline-lint.json
# Count warnings
```

**Success Criteria**:
- [ ] Baseline captured
- [ ] Warning count documented
- [ ] No new errors (warnings acceptable)

**Failure Action**:
1. Document current warning count
2. Proceed with refactoring
3. Ensure refactoring doesn't increase warnings

**Rationale**: Refactoring shouldn't introduce new warnings, but existing warnings don't block progress.

---

### 🟡 Advisory: Performance Baseline
**Description**: Capture performance metrics if available

**Verification**:
```bash
# If performance tests exist
pnpm test:performance --json > baseline-perf.json
```

**Success Criteria**:
- [ ] Baseline captured (if tests exist)
- [ ] Key metrics documented (latency, throughput, etc.)

**Failure Action**:
1. Skip if no performance tests exist
2. Document that performance tracking is unavailable

**Rationale**: Nice to have but not critical for refactoring start.

---

### 🟢 Optional: Bundle Size Baseline
**Description**: Capture build bundle size

**Verification**:
```bash
pnpm build
du -sh dist/ > baseline-bundle.txt
```

**Success Criteria**:
- [ ] Bundle size captured

**Failure Action**:
- Skip if not applicable (e.g., not a library project)

---

## Stage 2: Characterization Testing

### 🔴 Mandatory: New Tests Pass
**Description**: All newly added characterization tests must pass

**Verification**:
```bash
pnpm test <new-test-files>
# All new tests must be green
```

**Success Criteria**:
- [ ] All new tests pass
- [ ] Tests are deterministic (no flakiness)
- [ ] Tests lock down current behavior

**Failure Action**:
1. **STOP** - Do not proceed
2. Investigate failure cause:
   - If test is incorrect: Fix test
   - If failure reveals existing bug: Document bug, decide whether to fix before refactoring
3. Do not proceed until decision is made

**Rationale**: Failing characterization tests indicate either incorrect tests or existing bugs. Both must be resolved before structural changes.

---

### 🟡 Advisory: Test Coverage Maintained
**Description**: Coverage should not decrease

**Verification**:
```bash
pnpm test --coverage
# Compare coverage to baseline
```

**Success Criteria**:
- [ ] Coverage >= baseline
- [ ] New code paths covered

**Failure Action**:
1. Document coverage gap
2. Add tests if gaps are critical
3. Proceed if coverage is acceptable

---

## Stage 3: Per-Step Validation

### 🔴 Mandatory: Tests Pass After Change
**Description**: After each incremental change, tests must pass

**Verification**:
```bash
# Run affected tests (fast)
pnpm test --filter <scope>

# Or run all tests (slower but safer)
pnpm test --run
```

**Success Criteria**:
- [ ] 100% tests pass
- [ ] Same number of tests as before (no tests accidentally deleted)
- [ ] No new test skips (`it.skip`, `describe.skip`)

**Failure Action**:
1. **IMMEDIATE ROLLBACK**:
   ```bash
   git reset --hard HEAD  # If uncommitted
   git reset --hard HEAD~1  # If committed
   ```
2. Investigate failure:
   - Review last change for unintended side effects
   - Check if test expectation needs update (rare - be cautious)
   - Identify missing edge case
3. Fix issue and re-attempt step
4. Document failure cause in execution log

**Rationale**: Failing tests = behavior regression. Refactoring must preserve behavior.

---

### 🔴 Mandatory: No New Type Errors
**Description**: Type checking must still pass

**Verification**:
```bash
pnpm tsc --noEmit
```

**Success Criteria**:
- [ ] Zero type errors (same as baseline)
- [ ] No new `any` types introduced
- [ ] No type safety compromises

**Failure Action**:
1. **IMMEDIATE ROLLBACK**
2. Fix type errors before proceeding
3. If type error is intentional (rare), document justification

**Rationale**: Type errors indicate broken contracts or incorrect refactoring.

---

### 🟡 Advisory: Lint Warnings Not Increased
**Description**: Lint warnings should not increase

**Verification**:
```bash
pnpm eslint --format=json <changed-files> > step-lint.json
# Compare warning count to baseline
```

**Success Criteria**:
- [ ] Warning count <= baseline
- [ ] No new errors

**Failure Action**:
1. If new warnings are minor: Document and proceed
2. If new warnings are significant: Fix before proceeding
3. Run `eslint --fix` to auto-fix if possible

**Rationale**: Refactoring is opportunity to improve lint compliance, not degrade it.

---

### 🟢 Optional: Performance Within Bounds
**Description**: Performance should not regress significantly

**Verification**:
```bash
pnpm test:performance --json > step-perf.json
# Compare to baseline
```

**Success Criteria**:
- [ ] Performance regression < 5% (configurable threshold)
- [ ] Key operations within expected range

**Failure Action**:
1. If regression < 10%: Document and proceed
2. If regression >= 10%: Investigate and optimize
3. If optimization not feasible: Document trade-off

**Rationale**: Minor performance variations are acceptable; major regressions require attention.

---

## Stage 4: Commit Checkpoint

### 🔴 Mandatory: Meaningful Commit Message
**Description**: Each commit must have clear, descriptive message

**Format**:
```
<type>: <subject>

<body>

<footer>
```

**Example**:
```
refactor: extract user validation to UserValidator class

- Move validation logic from UserService to new UserValidator
- Implement interface for dependency injection
- Add tests for UserValidator

Tests pass: ✅
Type check: ✅
Metrics: LOC reduced by 50 lines
```

**Success Criteria**:
- [ ] Type prefix (refactor, test, chore)
- [ ] Clear subject (what changed)
- [ ] Body explains why and what
- [ ] Verification status included

**Failure Action**:
1. Amend commit message:
   ```bash
   git commit --amend
   ```
2. Ensure commit is reviewable and revertable

**Rationale**: Good commit messages enable easy review and rollback.

---

### 🟡 Advisory: Small Diff Size
**Description**: Each commit should be small and focused

**Verification**:
```bash
git diff --stat HEAD~1
# Aim for < 200 lines changed per commit
```

**Success Criteria**:
- [ ] Single intent per commit
- [ ] Diff is reviewable (< 300 lines changed)
- [ ] No unrelated changes included

**Failure Action**:
1. If diff is large but focused: Acceptable, document complexity
2. If diff mixes concerns: Split into multiple commits

**Rationale**: Small commits are easier to review, understand, and revert.

---

## Stage 5: Full Validation Checkpoint

### 🔴 Mandatory: Full Test Suite Passes
**Description**: After completing a refactoring phase, run complete test suite

**Verification**:
```bash
pnpm test --run --coverage
# All tests must pass
```

**Success Criteria**:
- [ ] 100% tests pass
- [ ] Test execution time reasonable (< 2x baseline)
- [ ] No flaky tests observed

**Failure Action**:
1. **STOP** - Do not proceed to next phase
2. Identify failed tests
3. Rollback to last stable commit if necessary
4. Debug and fix before proceeding

**Rationale**: Phase boundaries require comprehensive validation.

---

### 🔴 Mandatory: Integration Tests Pass
**Description**: If integration tests exist, they must pass

**Verification**:
```bash
pnpm test:integration --run
```

**Success Criteria**:
- [ ] All integration tests pass
- [ ] External dependencies mocked appropriately
- [ ] No timeout issues

**Failure Action**:
1. **STOP** - Do not proceed
2. Investigate integration failures
3. Check if API contracts broken
4. Fix before proceeding

**Rationale**: Integration tests verify system-level behavior preservation.

---

### 🟡 Advisory: Code Coverage Improved or Maintained
**Description**: Coverage should not decrease

**Verification**:
```bash
pnpm test --coverage --json > final-coverage.json
# Compare to baseline
```

**Success Criteria**:
- [ ] Coverage >= baseline (e.g., 80% → 82%)
- [ ] New code is covered
- [ ] No significant gaps introduced

**Failure Action**:
1. If coverage decreased slightly (< 2%): Document and proceed
2. If coverage decreased significantly: Add tests before proceeding

**Rationale**: Refactoring often improves testability, so coverage should improve.

---

### 🟡 Advisory: Metrics Improved
**Description**: Complexity metrics should improve

**Verification**:
- Cyclomatic Complexity reduced
- File LOC reduced or maintained
- LCOM4 (cohesion) improved

**Success Criteria**:
- [ ] At least one metric improved
- [ ] No metrics significantly degraded

**Failure Action**:
1. If metrics unchanged: Acceptable if code is clearer
2. If metrics worse: Review refactoring approach

**Rationale**: Refactoring goal is to improve code quality metrics.

---

## Stage 6: Pre-Merge Checkpoint

### 🔴 Mandatory: Branch Builds Successfully
**Description**: CI/CD pipeline passes

**Verification**:
```bash
# Run CI checks locally
pnpm build
pnpm test
pnpm lint
pnpm type-check
```

**Success Criteria**:
- [ ] Build succeeds
- [ ] All tests pass in CI environment
- [ ] Lint passes
- [ ] Type checking passes

**Failure Action**:
1. **STOP** - Do not create PR
2. Fix CI failures locally
3. Ensure reproducibility

**Rationale**: Code must build and test successfully in CI before merging.

---

### 🟡 Advisory: Documentation Updated
**Description**: Documentation reflects refactoring changes

**Verification**:
- [ ] README updated (if public API changed)
- [ ] Inline comments updated
- [ ] API documentation updated
- [ ] Migration guide provided (if breaking changes)

**Failure Action**:
1. Add documentation updates to PR
2. If minor: Can be follow-up PR

**Rationale**: Documentation prevents confusion for other developers.

---

### 🟡 Advisory: Execution Log Completed
**Description**: `execution-log.md` is complete and thorough

**Verification**:
- [ ] All steps documented
- [ ] Before/after metrics recorded
- [ ] Decisions justified
- [ ] Remaining work noted

**Failure Action**:
1. Complete execution log before PR
2. Include log in PR description

**Rationale**: Execution log provides audit trail and learning resource.

---

## Emergency Rollback Procedures

### Scenario 1: Tests Fail After Commit

**Immediate Action**:
```bash
# Rollback last commit
git reset --hard HEAD~1

# Or revert specific commit
git revert <commit-hash>
```

**Investigation**:
1. Review commit diff
2. Identify changed behavior
3. Add characterization test to capture expected behavior
4. Fix and re-attempt

---

### Scenario 2: Type Errors Introduced

**Immediate Action**:
```bash
# Rollback to last good state
git reset --hard HEAD~1
```

**Investigation**:
1. Run `tsc --noEmit --pretty` for detailed errors
2. Review type changes
3. Fix type contracts before re-attempting

---

### Scenario 3: Performance Regression

**Immediate Action**:
1. If < 10% regression: Document and monitor
2. If >= 10% regression: Investigate immediately

**Investigation**:
```bash
# Profile before and after
pnpm test:performance --prof

# Compare profiles
# Identify bottleneck
```

**Options**:
1. Optimize refactored code
2. Rollback and reconsider approach
3. Accept regression if justified (document trade-off)

---

### Scenario 4: Integration Failure

**Immediate Action**:
```bash
# Rollback to last stable state
git reset --hard <last-good-commit>
```

**Investigation**:
1. Identify broken contract/API
2. Review dependency changes
3. Check if external system changed
4. Fix contract before re-attempting

---

## Rollback Decision Matrix

| Situation | Severity | Action | Timeline |
|-----------|----------|--------|----------|
| 1-2 tests fail | Low | Investigate & fix | Within 1 hour |
| >5 tests fail | High | Immediate rollback | Immediate |
| Type errors | High | Immediate rollback | Immediate |
| Build fails | Critical | Immediate rollback | Immediate |
| Integration fails | High | Rollback or hotfix | Within 30 min |
| Lint warnings +5 | Low | Fix or document | Within 1 day |
| Performance -5% | Low | Monitor | N/A |
| Performance -20% | High | Investigate | Within 2 hours |
| Coverage -2% | Low | Add tests | Within 1 day |
| Coverage -10% | Medium | Add tests immediately | Within 4 hours |

---

## Checkpoint Automation

### Automated Verification Script

Create `scripts/verify-checkpoint.sh`:
```bash
#!/bin/bash
set -e

echo "🔍 Running safety checkpoints..."

echo "✅ Running tests..."
pnpm test --run

echo "✅ Type checking..."
pnpm tsc --noEmit

echo "✅ Linting..."
pnpm eslint src/

echo "✅ Build..."
pnpm build

echo "🎉 All checkpoints passed!"
```

**Usage**:
```bash
chmod +x scripts/verify-checkpoint.sh
./scripts/verify-checkpoint.sh
```

---

### Pre-Commit Hook

Create `.husky/pre-commit`:
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run quick validation
pnpm test --run --changed
pnpm tsc --noEmit
pnpm eslint --fix
```

---

## Checkpoint Metrics Dashboard

Track checkpoint pass rates over time:

| Date | Phase | Tests Pass | Type Check | Lint | Rollbacks |
|------|-------|------------|------------|------|-----------|
| 2025-11-13 | Step 1 | ✅ 100% | ✅ | ✅ | 0 |
| 2025-11-13 | Step 2 | ✅ 100% | ✅ | ⚠️ +3 warnings | 0 |
| 2025-11-13 | Step 3 | ❌ 98% | ✅ | ✅ | 1 (reverted) |
| 2025-11-13 | Step 3 (retry) | ✅ 100% | ✅ | ✅ | 0 |

---

## References

- Michael Feathers - "Working Effectively with Legacy Code" (Chapter 8: How Do I Add a Feature?)
- Martin Fowler - "Refactoring" (Chapter 2: Principles in Refactoring)
- Kent Beck - "Test-Driven Development" (Chapter 25: Test-Driven Development Patterns)
