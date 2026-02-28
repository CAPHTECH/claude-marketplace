---
name: critical-code-review
context: fork
description: Perform critical code review with 6-phase pipeline (context gathering, static analysis, LLM review with verification, automated fix flow). Use when reviewing code changes, pull requests, specific files, or branch diffs. Triggers on "review this code", "critical review", "code review for PR #123", or "review changes in src/". Optionally uses Codex CLI for secondary review.
---

# Critical Code Review

6-phase pipeline for context-aware critical code review with verification and automated fix execution.

```
Target Resolution → Phase 1: Context → Phase 2: Static Analysis
    → Phase 3: LLM Review → Phase 4: Verification → Phase 5: Output → Phase 6: Fix Flow
```

## Review Targets & Resolution

### Supported Targets
- Specific file: `src/main.ts`
- Branch diff: `main..feature/new-api`
- Recent commit: `HEAD~1..HEAD`
- Directory: `src/`
- PR: `#123`
- No argument: auto-detect (diff between current branch and base)

### Resolution Logic
1. If argument provided: use as review target
2. If no argument:
   - Get current branch: `git branch --show-current`
   - Find base branch (priority: main, master, develop)
   - Review diff: `git diff <base>...HEAD` (committed changes)
   - Additionally capture unstaged changes: `git diff` (merge both diffs)

---

## Phase 1: Context Gathering

Collect enriched context before review. See references/context-gathering.md for detailed commands.

### 1.1 Diff Acquisition
- Get diff for the resolved target
- Parse changed files list with `--name-only`

### 1.2 Change Intent
- If PR exists: `gh pr view <number> --json title,body,labels`
- If Issue linked: extract issue number from PR body, `gh issue view`
- Determine: bug fix / feature / refactoring / infrastructure

### 1.3 Dependency Graph
- For each changed file, detect imports (language-specific patterns)
- Detect reverse dependencies (callers of changed symbols)
- Flag files with high fan-in (many callers) as high-impact

### 1.4 File Stability
```bash
git log --since="90 days ago" --pretty=format: --name-only -- <file> | sort | uniq -c | sort -rn
```
- Unstable (10+ changes/90d): review focus target
- Stable (≤4 changes/90d): validate change necessity

### 1.5 Test Coverage
- Detect corresponding test files (language-specific patterns)
- Flag changed files without tests as `[no-test]`

### 1.6 Tool Detection
- Detect available linters, formatters, type checkers, security scanners
- Store as `[tool-detection]` for Phase 2
- See references/static-analysis-tools.md for detection table

---

## Phase 2: Static Analysis Gate

Run project's own tools before LLM review. See references/static-analysis-tools.md for tool table.

### Execution Order (language-independent)
**lint → format-check → type-check → security-scan**

### Procedure
1. Use `[tool-detection]` from Phase 1.6 to select tools
2. Run each tool against changed files only (when tool supports file-level targeting)
3. Collect results; do NOT stop on failure
4. If no tools detected: log `[no-static-analysis-tools]` and proceed to Phase 3

### Result Handling
- Tool errors become `[static-analysis]` findings (separate from LLM findings)
- Security scanner findings are elevated to Bug/Critical or Bug/Major
- Lint warnings are presented as-is (not duplicated in LLM review)

---

## Phase 3: LLM Review

### 3.1 Path-Based Focus Routing
- Match changed files against references/path-review-rules.md
- Check for `.claude/review-rules.yml` custom rules
- Route review focus per file based on matched rules

### 3.2 Self Review
Perform critical review with enriched context:
- **Input**: diff + change intent + dependency graph + file stability + test coverage + path-based focus
- **Criteria**: references/review-criteria.md (3 types × 5 severities × 8 domains)
- **Slot allocation**: Max 7 findings (see references/review-criteria.md for priority-based allocation). Critical findings are never cut.
- Exclude issues already caught by static analysis (Phase 2)

### 3.3 Codex Review (parallel)
When `mcp__codex-cli__codex` tool is available, request secondary review in parallel with self review:

```
Perform critical code review on the following code changes.

Context:
- Change intent: [intent from Phase 1.2]
- High-impact files: [files with high fan-in from Phase 1.3]
- Files without tests: [no-test files from Phase 1.5]

Focus on: security risks, data integrity, design quality, reliability, and type safety.
Provide specific issues with file:line locations and fix suggestions.
Classify each as Bug/Suggestion/Nitpick with severity Critical/Major/Minor/Trivial/Info.

[Include code diff]
```

If the tool is unavailable but Codex CLI is installed:
```bash
codex exec -c reasoning_effort=xhigh "..."
```

### 3.4 Result Merge
- Combine self review and Codex review findings
- Deduplicate by file:line + issue description similarity
- Keep the more detailed description when merging
- Re-rank by severity after merge

---

## Phase 4: Verification Gate

Validate each finding before output. See references/verification-methods.md for patterns.

### Procedure
For each finding from Phase 3:

1. **Code existence check**: Verify file:line exists and matches the described code
2. **Pattern verification**: Use grep/Read to confirm the problematic pattern
3. **False positive check**: Compare against known false positive patterns
4. **Label assignment**:
   - **Verified**: Tool/grep confirmed the issue
   - **Likely**: Context analysis supports the issue, but no tool confirmation
   - **Possible**: Circumstantial evidence only

### Filtering Rules
- Drop findings where the referenced code does not exist
- For known false positive patterns (see references/verification-methods.md): verify context before dropping. Only drop if confirmed as false positive; otherwise downgrade confidence label
- Downgrade confidence label if surrounding context provides mitigation

---

## Phase 5: Output

### 5.1 Change Walkthrough

Summary of all changes for overall understanding.

```markdown
## Change Walkthrough

| File | Change Type | Summary |
|------|------------|---------|
| `src/auth/login.ts` | Modified | Add rate limiting to login endpoint |
| `src/auth/types.ts` | Modified | Add RateLimitConfig type |
| `tests/auth/login.test.ts` | Added | Rate limiting test cases |
```

### 5.2 Static Analysis Results

Results from Phase 2 (separate from LLM findings).

```markdown
## Static Analysis

| Tool | Status | Details |
|------|--------|---------|
| ESLint | ⚠ 2 warnings | `src/api.ts:42` no-unused-vars, `src/api.ts:78` no-explicit-any |
| tsc | ✅ Pass | — |
| npm audit | ⚠ 1 moderate | lodash < 4.17.21 Prototype Pollution |
```

If no tools were available: `No static analysis tools detected.`

### 5.3 Review Findings

Max 7 LLM-based findings, ordered by severity.

````markdown
## Review Findings

### 1. [Bug/Critical] [Verified] SQL Injection in user search
**Category**: Security
**Location**: `src/api/users.ts:42`
**Issue**: User input is directly interpolated into SQL query without parameterization.
**Impact**: Attackers can execute arbitrary SQL commands, leading to data breach.
**Fix**:
```typescript
// Before
const query = `SELECT * FROM users WHERE name = '${name}'`;
// After
const query = `SELECT * FROM users WHERE name = $1`;
const result = await db.query(query, [name]);
```
````

Format per finding:
```
### N. [Type/Severity] [Confidence] Title
**Category**: Domain category
**Location**: file:line
**Issue**: Description
**Impact**: Technical and business impact
**Fix**: Code suggestion
```

---

## Phase 6: Fix Flow

### Fix Prompt
After presenting results:

```markdown
## Fix Options

Execute fixes? (y/n/select)
- y: Execute all fixable items
- n: Exit without fixing
- select: Choose items to fix (enter numbers, e.g., 1,3,5)
```

### Fix Organization
Categorize each finding for fix execution:

```markdown
## Planned Fixes

### Auto-fix Items (Bug/Critical, Bug/Major)
1. [Issue name] - file:line
   - Fix: [What will be changed]

### Items Requiring Confirmation (Bug/Minor, Bug/Trivial, Suggestion/*)
2. [Issue name] - file:line
   - Proposed fix: [Suggestion]
   - Impact scope: [Affected files/functions]

### Skip Items (Nitpick/*, Info/*)
3. [Issue name] - file:line (Manual fix recommended)
```

### Fix Execution

#### Pre-fix Verification
- Confirm current file state matches expected
- Verify fix code fits context
- Consider impacts on dependent files

#### Fix Application Rules
- **Minimal changes**: Only changes needed to solve the issue
- **Maintain consistency**: Preserve existing code style, naming, indentation
- **Check imports**: Add new dependencies appropriately
- **Type consistency**: Ensure type integrity
- **Backward compatibility**: Clarify impact when behavior/API changes

#### Quality Check
- **Syntax errors**: Ensure no syntax errors after fix
- **Logical consistency**: Ensure fix doesn't introduce new issues
- **Edge cases**: Ensure proper boundary and error handling

#### Test Implementation/Update
- Check existing tests related to fix location
- Update tests that fail due to fix
- Add regression tests for bug fixes
- Prefer test-first when feasible

#### Post-Fix Static Analysis
After applying fixes, re-run Phase 2 tools on modified files:
- If new errors introduced: report and offer to fix
- If pre-existing errors resolved: note in report

### Fix Report

```markdown
## Fix Report

### Applied
- ✅ [Issue name] - file:line
  - Changes: [Actual changes made]
  - Static analysis: [Pass/new warnings]

### Failed
- ❌ [Issue name] - file:line
  - Error: [Failure reason]
  - Workaround: [Manual fix instructions]

### Next Steps
1. Run tests to verify fixes
2. Review static analysis results
3. Confirm changes with `git diff`
4. Revert if needed: `git checkout -- <file>`
```

### Error Handling
- Do not apply fixes that fail pre-verification
- Partial success is acceptable; report clearly what was applied
- Report all errors with actionable guidance

---

## Heuristic Review Guidance

- Understand context, intent, and constraints before judging
- Imagine the code's evolution over the next year
- Use domain knowledge to validate business logic
- Look beyond listed categories; report issues of equivalent severity
- Distinguish intentional trade-offs from oversights
- Consider the reviewer's confidence — flag uncertainty rather than assert

---

## Codex Review Integration

When `mcp__codex-cli__codex` tool is available, request secondary review in Phase 3.3.

If the tool is unavailable but Codex CLI is installed:
```bash
codex exec -c reasoning_effort=xhigh "Perform critical code review on the following code changes. [Include diff]"
```

Integrate Codex findings with self review: deduplicate, keep the more detailed version, re-rank by severity.

---

## Reference Index

| Reference | Purpose |
|-----------|---------|
| references/review-criteria.md | Finding types, severity levels, domain categories, slot allocation |
| references/context-gathering.md | Phase 1 detailed commands and patterns |
| references/static-analysis-tools.md | Language-specific tool detection and execution |
| references/verification-methods.md | Phase 4 verification patterns and false positive catalog |
| references/path-review-rules.md | Path-based review focus routing rules |
