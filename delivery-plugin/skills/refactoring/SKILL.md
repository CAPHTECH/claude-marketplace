---
name: refactoring
context: fork
argument-hint: "[analyze|execute] [scope]"
description: Analyze code for refactoring opportunities (complexity, coupling, SOLID violations) and safely execute improvements with test-first verification. Use when auditing code quality, investigating design problems, or performing incremental refactoring with continuous validation. Supports analyze-only mode or full execution with rollback. (project, gitignored)
---

# Refactoring

Analyze codebases for refactoring opportunities and safely execute improvements with test-first verification. Operates in two modes based on `$ARGUMENTS`:

- **analyze** -- Discover issues, generate prioritized report (Phase 1 only)
- **execute** -- Full pipeline: analyze, plan, and execute with validation (Phase 1-3)

Default to **analyze** if `$ARGUMENTS` is empty or unspecified.

## Phase 1: Analysis (Discovery)

Systematically identify refactoring opportunities by measuring complexity, coupling, cohesion, and SOLID principle violations.

### 1.1 Gather Context

1. Read architecture docs, CLAUDE.md, and project-specific standards
2. Identify design patterns (pluggable, layered, etc.) and project scale
3. Load [design-standards.md](references/design-standards.md) for metric thresholds -- read when applying consistent evaluation criteria

### 1.2 Define Scope

Clarify with the user:
- Target files/directories (or entire project)
- Depth: quick scan vs. deep analysis
- Specific concerns (complexity, coupling, specific SOLID violations)

### 1.3 Static Analysis

Execute multi-tool analysis chain. Select tools available in the project:

**Code Pattern Discovery (KIRI MCP)**:
```
mcp__kiri__context_bundle({ goal: "complex functions high cyclomatic complexity nested conditionals" })
mcp__kiri__context_bundle({ goal: "import statements concrete dependencies circular imports" })
```

**Dependency Analysis** (depcruise / madge):
```bash
npx depcruise --config .dependency-cruiser.js src
npx madge --circular --extensions ts src/
```

**Dead Code Detection** (ts-prune):
```bash
npx ts-prune
npx depcheck
```

**Git Change Analysis**:
```bash
git log --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn
```

**Coverage Correlation**:
```bash
npx vitest run --coverage
```

For each file/module, evaluate:
1. **Complexity**: Cyclomatic/Cognitive complexity per function, nesting depth, TypeScript-specific (conditional types, generics)
2. **Coupling**: Import count, concrete vs interface dependencies, circular deps, instability metric, change coupling
3. **Cohesion**: LCOM4, responsibility focus, field usage patterns
4. **Dead Code**: Unused exports, unreachable code, orphaned types
5. **Architecture**: Layer violations, dependency rule compliance
6. **SOLID Violations**: Load [refactoring-patterns.md](references/refactoring-patterns.md) for detection patterns -- read when identifying code smells and recommending specific techniques

### 1.4 Prioritize

Calculate: **Priority Score = (Impact x Risk Reduction) / Effort**

- **Impact** (1-10): Maintainability effect, bug likelihood, velocity impact
- **Risk Reduction** (1-10): Bug history, change frequency, blast radius
- **Effort** (1-10): Time, dependency complexity, test requirements

Contextual adjustments:
- Files with past bugs: +20 impact
- High churn files: +15 risk reduction
- Coverage < 50%: +10 risk reduction
- Core modules: +10 impact

Categories:
- **Critical** (Score >= 50): Circular deps, architecture violations, high complexity + low coverage + bug history
- **Medium** (Score 20-49): SOLID violations, high coupling in stable modules, dead code
- **Low** (Score < 20): Minor style, moderate complexity, documentation

### 1.5 Validate Findings

Reduce false positives before reporting:

1. **Sample validate**: Top 3 critical, 5 random medium, 2 low
2. **False positive check**: Framework patterns, test files, generated code, barrel imports
3. **Threshold adjustment**: If false positive rate > 20%, re-calibrate using median + 2sigma
4. **Evidence collection**: For each confirmed issue, record detection tool, metric values, code snippets, git history

### 1.6 Generate Output

Select format based on need:

- **Periodic Audit**: Use [report-template.md](assets/report-template.md) -- comprehensive report with health score, metrics, top files, refactoring sequence
- **Module Improvement**: Use [refactoring-plan-template.md](assets/refactoring-plan-template.md) -- problem statement, goals, phased steps, risk assessment, metrics tracking
- **Quick Review**: Concise list with file path, issue type, key metrics, one-line recommendation

**If `$ARGUMENTS` is "analyze", stop here and deliver the report.**

## Phase 2: Execution Planning

Transition from analysis to actionable plan.

### 2.1 Select Target

From the analysis report:
1. Ask user to select target issue (or auto-select highest priority)
2. Analyze dependencies and affected files
3. Verify no scope conflicts

### 2.2 Pre-Refactoring Validation

All gates must pass before proceeding:

```bash
# Tests green
pnpm test --run

# No type errors
pnpm tsc --noEmit

# Capture baselines
pnpm eslint src/ --format=json > baseline-lint.json
```

Load [safety-checkpoints.md](references/safety-checkpoints.md) for the complete checkpoint protocol -- read when enforcing validation gates and rollback triggers throughout execution.

**Mandatory gates**:
- All tests pass (100% green)
- Zero type errors
- Clean git working directory
- Baseline metrics captured (test time, test count, lint warnings, bundle size)

### 2.3 Plan Characterization Tests

Identify code paths lacking coverage in the refactoring target. Plan tests using [characterization-test-template.md](assets/characterization-test-template.md) -- template for locking down existing behavior before structural changes.

Generate execution plan using [execution-plan-template.md](assets/execution-plan-template.md) -- structured plan with steps, verification commands, and rollback procedures.

## Phase 3: Incremental Execution

### 3.1 Add Characterization Tests

1. Write tests capturing current behavior (Given/When/Then)
2. Cover edge cases and invariants
3. Verify all new tests pass
4. Commit characterization tests separately

### 3.2 Execute Refactoring Steps

Break refactoring into the smallest possible changes. For each step:

1. **Apply one refactoring pattern** from [refactoring-patterns.md](references/refactoring-patterns.md)
2. **Verify** (all must pass):
   ```bash
   pnpm vitest run --reporter=json
   pnpm tsc --noEmit
   pnpm eslint --format=json <affected-files>
   ```
3. **If verification fails**: Immediately revert, investigate, re-attempt with smaller step
4. **If verification passes**: Commit with descriptive message, log results

Load [tooling-playbook.md](references/tooling-playbook.md) for tool integration details -- read when using ts-morph, vitest, eslint, or git for automated refactoring and verification.

**Supported patterns**: Extract Method, Extract Class, Move Method, Rename Symbol, Introduce Parameter Object, Replace Conditional with Polymorphism, Encapsulate Field, Split Phase.

### 3.3 Safety Principles

- **Never break tests**: Revert immediately on failure
- **One intent per change**: Rename, then update usages, then delete dead code
- **Characterization tests first**: Lock behavior before structural changes
- **Preserve contracts**: Maintain API and non-functional requirements
- **Type-driven safety**: Use TypeScript strict mode as safety net

### 3.4 Post-Refactoring Report

1. Run full test suite, capture final metrics
2. Compare final vs. baseline metrics
3. Generate execution log using [execution-log-template.md](assets/execution-log-template.md) -- log template tracking each step's changes, validation results, and before/after metrics
4. Update discovery report with completion status

## Reference Materials

### references/

- [design-standards.md](references/design-standards.md) -- Metric thresholds for complexity, coupling, cohesion, LOC, responsibility count, and adaptive normalization. Read during Phase 1 analysis.
- [refactoring-patterns.md](references/refactoring-patterns.md) -- SOLID violation detection patterns, code smell catalog, and step-by-step execution guides for each refactoring pattern. Read when identifying issues (Phase 1) and executing changes (Phase 3).
- [safety-checkpoints.md](references/safety-checkpoints.md) -- Mandatory/advisory/optional checkpoints per stage, rollback decision matrix, emergency procedures, and automation scripts. Read during Phase 2-3.
- [tooling-playbook.md](references/tooling-playbook.md) -- Concrete usage examples for tsc, vitest, eslint, ts-morph, and git including failure diagnostics and integration scripts. Read during Phase 3.

### assets/

- [report-template.md](assets/report-template.md) -- Markdown report with executive summary, findings by priority, metrics tables, and recommended sequence
- [refactoring-plan-template.md](assets/refactoring-plan-template.md) -- Phased plan with problem statement, goals, steps, risk assessment, and metrics tracking
- [execution-plan-template.md](assets/execution-plan-template.md) -- Execution plan with verification commands and rollback procedures per step
- [execution-log-template.md](assets/execution-log-template.md) -- Step-by-step execution tracking with before/after comparison
- [characterization-test-template.md](assets/characterization-test-template.md) -- Template and guidelines for writing behavior-locking tests
