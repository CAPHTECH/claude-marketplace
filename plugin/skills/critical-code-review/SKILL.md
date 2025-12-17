---
name: critical-code-review
description: Perform critical code review with automated fix suggestions. Use when reviewing code changes, pull requests, specific files, or branch diffs. Triggers on requests like "review this code", "critical review", "code review for PR #123", or "review changes in src/". Optionally uses Codex CLI for secondary review when available.
---

# Critical Code Review

Perform context-aware critical code review with integrated fix execution.

## Review Targets

- Specific file: `src/main.ts`
- Branch diff: `main..feature/new-api`
- Recent commit: `HEAD~1..HEAD`
- Directory: `src/`
- PR: `#123`
- No argument: diff between current branch and base (main/master/develop)

## Target Resolution

1. If argument provided: use as review target
2. If no argument:
   - Get current branch: `git branch --show-current`
   - Find base branch (priority: main, master, develop)
   - Review diff: `git diff <base>...HEAD`
   - Include unstaged changes

## Review Context (Determine First)

- **Project phase**: MVP/Development/Production/Refactoring
- **Priority**: Performance/Maintainability/Extensibility
- **Tech stack**: Languages/Frameworks/Paradigms
- **File type**: Backend/Frontend/UI Component/Database/Infrastructure

## Review Criteria

### 🔴 High Priority (Critical)

1. **Security risks**: SQL/XSS injection, auth flaws, secret exposure
2. **Data corruption**: Transaction failures, race conditions, improper locking
3. **System failure**: Unhandled exceptions, resource leaks, infinite loops

### 🟡 Medium Priority (Design Quality)

4. **Type safety & Domain Modeling**: Primitive obsession, invalid state representation, missing smart constructors
5. **Functional programming violations**: Side effects, missing Result types, mutability
6. **Design principle deviations**: SOLID violations, high coupling, low cohesion
7. **Domain model inconsistencies**: Misrepresented business rules, ambiguous boundaries
8. **Maintainability issues**: Untestable design, missing documentation, implicit assumptions

### 🟢 Low Priority (Improvements)

9. **Efficiency**: N+1 queries, unnecessary computation, cache opportunities
10. **Code quality**: Duplication, naming, readability

### 🎨 UI/Frontend Specific

11. **UI state management**: Invalid state combinations, missing loading/error states
12. **Accessibility**: Missing ARIA, keyboard navigation, color-dependent information
13. **Responsive design**: Hardcoded sizes, mobile support, breakpoint inconsistencies
14. **Component boundaries**: Props drilling, excessive responsibility
15. **UI performance**: Unnecessary re-renders, heavy components, missing virtualization

## Review Process

1. **Self review**: Perform critical review based on criteria above
2. **Codex review (if available)**: Request review via `mcp__codex-cli__codex` tool with context
3. **Integrate results**: Combine self review and Codex review into final issue list
4. **Present results**: Output in the format below

## Output Format

````markdown
### 🔴/🟡/🟢 [Criterion Name]
**Issue**:
- Location (file:line)
- Detailed description

**Impact**:
- Technical: Bug/Performance degradation/Maintainability
- Business: User experience/Development velocity/Cost

**Fix**:
```[language]
// Specific fix code
```
````

## Output Constraints

- **Issue count**: Max 5 by priority (guideline: 🔴2, 🟡2, 🟢1)
- **Specificity**: Include file:line, provide code examples
- **Conciseness**: Consider CLI display, be clear
- **Practicality**: Provide realistic, implementable fixes

## Post-Review Fix Flow

After presenting review results, display:

```
## 🔧 Fix Options

Execute fixes? (y/n/select)
- y: Execute all
- n: Exit without fixing
- select: Choose items to fix

Selection:
```

### Fix Item Organization

```markdown
## 🔧 Planned Fixes

### Auto-fix Items (🔴 Critical)
1. [Issue name] - file:line
   - Issue: [Brief description]
   - Fix: [What will be changed]

### Items Requiring Confirmation (🟡 Design / 🔵 Other)
2. [Issue name] - file:line
   - Issue: [Brief description]
   - Proposed fix: [Suggestion]
   - Impact scope: [Other file impacts]

### Skip Items (🟢 Suggestions)
3. [Issue name] - file:line (Manual fix recommended)
```

### Fix Execution

#### Pre-fix Verification
- Confirm current file state
- Verify fix code fits context
- Consider impacts on other parts

#### Fix Application
- **Minimal changes**: Only changes needed to solve the issue
- **Maintain consistency**: Preserve existing code style, naming, indentation
- **Check imports**: Add new dependencies appropriately
- **Type consistency**: Ensure type integrity

#### Quality Check
- **Syntax errors**: Ensure no syntax errors after fix
- **Logical consistency**: Ensure fix doesn't introduce new issues
- **Edge cases**: Ensure proper boundary and error handling
- **Performance impact**: Ensure no performance degradation

#### Test Implementation/Update
- **Check existing tests**: Identify tests related to fix location
- **Update tests**: Update tests that fail due to fix
- **Add new tests**: Add regression tests for bug fixes, cover normal/error cases for new features

### Fix Report

```markdown
## ✅ Fix Complete Report

### Successful Fixes
- ✅ [Issue name] - file:line
  - Changes: [Actual changes made]

### Failed Fixes
- ❌ [Issue name] - file:line
  - Error: [Failure reason]
  - Workaround: [Manual fix instructions]

### Next Steps
1. **Run tests (Required)**: Verify all tests pass
2. Confirm changes with `git diff`
3. Check test coverage report
4. Restore with `git checkout -- <file>` if needed
```

## Codex Review Integration

When `mcp__codex-cli__codex` tool is available, request secondary review:

```
Perform critical code review on the following code changes.
Focus on: security risks, data integrity, design quality, and maintainability.
Provide specific issues with file:line locations and fix suggestions.

[Include code diff or file content]
```

Integrate Codex findings with self review, removing duplicates and prioritizing by severity.
