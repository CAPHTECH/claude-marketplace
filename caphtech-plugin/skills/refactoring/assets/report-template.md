# Refactoring Discovery Report

**Project**: {{PROJECT_NAME}}
**Analysis Date**: {{DATE}}
**Scope**: {{SCOPE}}
**Files Analyzed**: {{FILE_COUNT}}

---

## Executive Summary

{{SUMMARY}}

### Overall Health Score: {{HEALTH_SCORE}}/100

**Priority Breakdown**:
- 🔴 Critical: {{CRITICAL_COUNT}} issues
- 🟡 Medium: {{MEDIUM_COUNT}} issues
- 🟢 Low: {{LOW_COUNT}} issues

---

## Findings by Priority

### 🔴 Critical Issues

{{#CRITICAL_ISSUES}}
#### {{ISSUE_TITLE}}

**File**: `{{FILE_PATH}}:{{LINE_NUMBER}}`
**Type**: {{ISSUE_TYPE}}
**Priority Score**: {{PRIORITY_SCORE}} (Impact: {{IMPACT_SCORE}}, Risk Reduction: {{RISK_SCORE}}, Effort: {{EFFORT_SCORE}})

**Metrics**:
- Cyclomatic Complexity: {{COMPLEXITY}} (threshold: {{THRESHOLD}})
- {{ADDITIONAL_METRICS}}

**Description**:
{{DESCRIPTION}}

**Impact**:
{{IMPACT}}

**Detection Evidence**:
- **Tool**: {{DETECTION_TOOL}} (e.g., ts-morph, depcruise, KIRI)
- **Query/Command**: `{{DETECTION_QUERY}}`
- **Raw Output**:
  ```
  {{RAW_OUTPUT}}
  ```
- **Validation Status**: {{VALIDATION_STATUS}} (✅ Confirmed / ⚠️ Needs Review / ❌ False Positive)

**Code Snippet**:
```typescript
{{CODE_SNIPPET}}
```

**Change History** (if relevant):
- Last modified: {{LAST_MODIFIED_DATE}} by {{LAST_AUTHOR}}
- Modifications last 30 days: {{CHANGE_COUNT}}
- Related bugs: {{BUG_REFERENCES}}

**Recommended Action**:
{{RECOMMENDATION}}

**Estimated Effort**: {{EFFORT_ESTIMATE}} (hours/days)

---
{{/CRITICAL_ISSUES}}

### 🟡 Medium Priority Issues

{{#MEDIUM_ISSUES}}
#### {{ISSUE_TITLE}}

**File**: `{{FILE_PATH}}:{{LINE_NUMBER}}`
**Type**: {{ISSUE_TYPE}}
**Metrics**: {{METRICS}}

**Description**: {{DESCRIPTION}}

**Recommendation**: {{RECOMMENDATION}}

---
{{/MEDIUM_ISSUES}}

### 🟢 Low Priority Issues

{{#LOW_ISSUES}}
- `{{FILE_PATH}}`: {{ISSUE_SUMMARY}} ({{METRIC}})
{{/LOW_ISSUES}}

---

## Metrics Summary

### Complexity Distribution

| Metric | Min | Max | Avg | Threshold | Violations |
|--------|-----|-----|-----|-----------|------------|
| Cyclomatic Complexity | {{CC_MIN}} | {{CC_MAX}} | {{CC_AVG}} | 10 | {{CC_VIOLATIONS}} |
| File Length (LOC) | {{LOC_MIN}} | {{LOC_MAX}} | {{LOC_AVG}} | 400 | {{LOC_VIOLATIONS}} |
| Function Length | {{FN_MIN}} | {{FN_MAX}} | {{FN_AVG}} | 40 | {{FN_VIOLATIONS}} |

### Coupling Analysis

| Module | Import Count | Concrete Deps | Circular Deps | Status |
|--------|--------------|---------------|---------------|--------|
{{#COUPLING_DATA}}
| {{MODULE}} | {{IMPORTS}} | {{CONCRETE}} | {{CIRCULAR}} | {{STATUS}} |
{{/COUPLING_DATA}}

### Cohesion Analysis

| Class/Module | LCOM4 | Status | Recommendation |
|--------------|-------|--------|----------------|
{{#COHESION_DATA}}
| {{MODULE}} | {{LCOM4}} | {{STATUS}} | {{RECOMMENDATION}} |
{{/COHESION_DATA}}

---

## Architecture Patterns Analysis

### Pluggable Architecture Compliance

{{#ARCHITECTURE_ANALYSIS}}
- **{{PATTERN_NAME}}**: {{COMPLIANCE_STATUS}}
  - {{DETAILS}}
{{/ARCHITECTURE_ANALYSIS}}

### SOLID Principles Violations

{{#SOLID_VIOLATIONS}}
#### {{PRINCIPLE}} Violation

**Location**: `{{FILE_PATH}}`
**Description**: {{DESCRIPTION}}
**Example**: {{CODE_SNIPPET}}
**Fix**: {{FIX_SUGGESTION}}

---
{{/SOLID_VIOLATIONS}}

---

## Top 10 Files Requiring Attention

| Rank | File | Score | Issues | Primary Concern |
|------|------|-------|--------|-----------------|
{{#TOP_FILES}}
| {{RANK}} | `{{FILE}}` | {{SCORE}} | {{ISSUE_COUNT}} | {{PRIMARY_CONCERN}} |
{{/TOP_FILES}}

---

## Recommended Refactoring Sequence

1. **{{STEP_1_TITLE}}** (Priority: Critical)
   - Files: {{STEP_1_FILES}}
   - Estimated effort: {{STEP_1_EFFORT}}
   - Dependencies: None

2. **{{STEP_2_TITLE}}** (Priority: High)
   - Files: {{STEP_2_FILES}}
   - Estimated effort: {{STEP_2_EFFORT}}
   - Dependencies: Step 1

3. **{{STEP_3_TITLE}}** (Priority: Medium)
   - Files: {{STEP_3_FILES}}
   - Estimated effort: {{STEP_3_EFFORT}}
   - Dependencies: Step 2

{{#ADDITIONAL_STEPS}}
4. **{{TITLE}}** (Priority: {{PRIORITY}})
   - Files: {{FILES}}
   - Estimated effort: {{EFFORT}}
   - Dependencies: {{DEPENDENCIES}}
{{/ADDITIONAL_STEPS}}

---

## Code Examples

### Example: High Complexity Function

**Before** (`{{EXAMPLE_FILE}}:{{EXAMPLE_LINE}}`):
```typescript
{{BEFORE_CODE}}
```

**Metrics**: CC={{BEFORE_CC}}, LOC={{BEFORE_LOC}}

**Proposed Refactoring**:
```typescript
{{AFTER_CODE}}
```

**Metrics**: CC={{AFTER_CC}}, LOC={{AFTER_LOC}}

---

## Next Steps

1. **Review this report** with the team
2. **Prioritize** critical issues for immediate action
3. **Create issues** for each high-priority item
4. **Estimate effort** for refactoring work
5. **Schedule refactoring** in upcoming sprints
6. **Re-run analysis** after refactoring to verify improvements

---

## Validation Summary

### Sample Validation Results

**Samples Reviewed**: {{SAMPLES_REVIEWED}}
**Confirmed Issues**: {{CONFIRMED_COUNT}} ({{CONFIRMED_PERCENTAGE}}%)
**False Positives**: {{FALSE_POSITIVE_COUNT}} ({{FALSE_POSITIVE_PERCENTAGE}}%)
**Needs Further Review**: {{NEEDS_REVIEW_COUNT}}

### Threshold Adjustments Made

{{#THRESHOLD_ADJUSTMENTS}}
- **{{METRIC_NAME}}**: Original {{ORIGINAL_THRESHOLD}} → Adjusted {{ADJUSTED_THRESHOLD}}
  - Reason: {{ADJUSTMENT_REASON}}
{{/THRESHOLD_ADJUSTMENTS}}

### Excluded Patterns

The following patterns were excluded from analysis to reduce false positives:

{{#EXCLUDED_PATTERNS}}
- {{PATTERN_NAME}}: {{EXCLUSION_REASON}}
{{/EXCLUDED_PATTERNS}}

---

## Appendix

### Analysis Configuration

- Design Standards: `references/design-standards.md`
- Thresholds Applied (post-adjustment):
  - Function CC: {{FUNCTION_CC_THRESHOLD}}
  - Cognitive Complexity: {{COGNITIVE_THRESHOLD}}
  - Module CC: {{MODULE_CC_THRESHOLD}}
  - File LOC: {{FILE_LOC_THRESHOLD}}
  - Function LOC: {{FUNCTION_LOC_THRESHOLD}}
  - LCOM4: {{LCOM4_THRESHOLD}}
  - Imports: {{IMPORTS_THRESHOLD}}
  - Concrete deps: {{CONCRETE_DEPS_THRESHOLD}}
  - Instability: {{INSTABILITY_THRESHOLD}}

### Tools Used

**Analysis Tool Chain**:
1. **KIRI MCP** - Code pattern discovery and search
2. **ts-morph / TypeScript Compiler API** - AST analysis, type complexity
3. **ESLint + typescript-eslint** - Cognitive complexity, best practices
4. **depcruise** - Dependency graph analysis, circular dependencies
5. **madge** - Dependency visualization
6. **ts-prune** - Unused exports detection
7. **Git analysis** - Change coupling, hotspots, churn rate
8. **Vitest/Jest** - Test coverage correlation

**Tool Versions**:
- TypeScript: {{TS_VERSION}}
- ts-morph: {{TS_MORPH_VERSION}}
- depcruise: {{DEPCRUISE_VERSION}}

### Statistical Baseline

**Codebase-wide statistics** (for context):
- Median CC: {{MEDIAN_CC}}
- P95 CC: {{P95_CC}}
- Median LOC: {{MEDIAN_LOC}}
- Median Imports: {{MEDIAN_IMPORTS}}

### Notes

{{ADDITIONAL_NOTES}}

### Evidence Archive

All detection queries, tool outputs, and validation notes are archived at:
`{{EVIDENCE_ARCHIVE_PATH}}`
