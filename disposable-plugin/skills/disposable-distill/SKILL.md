---
name: disposable-distill
context: fork
argument-hint: "[cycle_N]"
description: Distill learnings from autopsy report into an improvement specification for the next cycle or production implementation. Extracts constraints, architecture decisions, interface contracts, and rejected options. Part of H-DGM cycle. Use after disposable-autopsy completes.
---

# Disposable Distill — Phase 3: Synthesize

Transform autopsy findings into a structured improvement specification that guides the next iteration or production implementation.

## Prerequisites

- Completed autopsy: `.disposable/cycles/cycle_{N}/autopsy-report.json` must exist
- Template: references/distill-template.md in disposable-cycle skill

## Procedure

### Step 1: Load Autopsy Context

1. Determine cycle: use `$ARGUMENTS` if provided, otherwise read latest from `.disposable/history.json`
2. Load autopsy report from `.disposable/cycles/cycle_{N}/autopsy-report.json`
3. Load spike metrics from `.disposable/cycles/cycle_{N}/spike-complete.json`
4. If `parentCycleId` exists in metrics, load previous cycle's distill spec for delta analysis

### Step 2: Extract Constraints

From autopsy findings, extract discovered constraints:

1. **Hard constraints** (priority: must): From `critical` and `major` findings
   - Security violations → security constraints
   - Correctness failures → behavioral constraints
   - Architecture issues → structural constraints
2. **Soft constraints** (priority: should/could): From `minor` and `info` findings
   - Performance patterns → optimization targets
   - Readability issues → style guidelines
   - Documentation gaps → documentation requirements

Format each constraint with:
- ID: `C-{NNN}`
- Description
- Source: axis name and finding ID
- Severity: must / should / could

### Step 3: Identify Architecture Decisions

From autopsy `architecture`, `maintainability`, and `dependency-hygiene` axes:

1. Extract decisions that emerged naturally in the prototype
2. For each decision:
   - Context: Why this decision was forced or emerged
   - Decision: What the prototype chose
   - Rationale: Evidence from autopsy scores and findings
   - Trade-offs: What was sacrificed
3. Compare with previous cycle's decisions (if any) to detect:
   - Confirmed decisions (same choice, improved score)
   - Reversed decisions (different choice this cycle)
   - New decisions (not present in previous cycle)

### Step 4: Extract Interface Contracts

From the spike code and autopsy `correctness` / `testability` axes:

1. Extract type signatures, API shapes, protocol definitions
2. Mark contracts as:
   - **Validated**: Tests exist and pass
   - **Assumed**: No test coverage, derived from code
   - **Disputed**: Test failures or autopsy findings suggest issues

### Step 5: Document Rejected Options

From autopsy findings and prototype exploration:

1. List approaches that were tried or considered but rejected
2. For each:
   - What the option was
   - Why it was rejected (evidence from findings)
   - Under what conditions it might be reconsidered

### Step 6: Compile Implementation Notes

Insights that must carry forward:
- Non-obvious behaviors discovered during spike
- Gotchas and edge cases
- Environment-specific requirements
- Performance characteristics observed

### Step 7: Identify Open Questions

Unresolved items that need investigation:
- Assumptions that need validation
- Trade-offs that need user input
- Dependencies on external factors

### Step 8: Generate Distill Specification

Using references/distill-template.md, produce the specification:

1. Fill all template sections
2. Include cycle metadata (ID, timestamp, parent cycle)
3. Cross-reference finding IDs from autopsy report
4. Ensure every constraint has an evidence trail

### Step 9: Save & Report

1. Write specification to `.disposable/cycles/cycle_{N}/distill-spec.md`
2. Mask sensitive data:
   ```bash
   node {plugin_root}/scripts/dist/mask-sensitive.mjs \
     .disposable/cycles/cycle_{N}/distill-spec.md --in-place
   ```
3. Present to user:
   - Constraint count by severity
   - Architecture decisions (new / confirmed / reversed)
   - Interface contracts status
   - Open questions requiring input
   - Recommendation: iterate (another spike) or graduate (to production)

## Output

- `.disposable/cycles/cycle_{N}/distill-spec.md` — improvement specification
- Ready for next `/disposable-spike` cycle or production implementation

## Graduation Criteria

Recommend **graduating** to production when:
- Previous autopsy verdict was PASS
- No `must` constraints remain unaddressed from prior cycles
- Architecture decisions are stable (no reversals in last 2 cycles)
- Interface contracts are all `validated`
- Open questions are resolved or deferred by user decision

Otherwise recommend **iterating** with another disposable spike.
