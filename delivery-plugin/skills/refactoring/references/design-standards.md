# Design Standards for Refactoring Discovery

## Project Context

These standards are tailored for TypeScript framework projects (like Assay) that follow:
- Pluggable architecture patterns
- Type safety with strict mode
- YAGNI principle (avoiding over-abstraction)
- Small to medium scale (not enterprise-heavy)

## Complexity Metrics

### Function/Method Complexity
- **Cyclomatic Complexity (CC)**:
  - **Monitor**: CC > 8
  - **Refactor**: CC > 10
  - **Target for extension points** (SearchAdapter, Reporter): CC ≤ 5

- **Cognitive Complexity** (preferred over CC for readability):
  - **Monitor**: Cognitive > 10
  - **Refactor**: Cognitive > 15
  - Penalizes nested structures and breaks in linear flow

### Class/Module Complexity
- **Total CC per file**:
  - **Refactor**: Total CC > 50
  - **Recommended for "medium hubs"** (Evaluator, Provider): Total CC ≤ 40

### TypeScript-Specific Complexity
- **Conditional type nesting depth**: ≤ 3 levels
- **Generic parameter count**: ≤ 4 per type/function
- **Decorator stack depth**: ≤ 3 decorators per class/method
- **Union/Intersection type members**: ≤ 8 branches
- **Type parameter constraints**: ≤ 2 extends/infer per parameter

## Coupling Metrics

### Import Dependencies
- **External dependencies per module**: ≤ 8 imports (excluding barrel imports and framework core)
- **Concrete type dependencies** (non-interface): ≤ 4 imports
  - Core interfaces (SearchAdapter/Reporter/BaselineProvider) don't count
- **Circular dependencies**: **Prohibited** - resolve immediately

**TypeScript-specific considerations**:
- Barrel imports (`index.ts` re-exports) don't count toward import limit
- Framework patterns (NestJS modules, Next.js pages) have relaxed limits

### Fan-out/Fan-in
- **Fan-out** (functions called directly): ≤ 6 per function
- **Fan-in** (times called by others): > 15 consistently → Consider Facade pattern or delegation

### Afferent/Efferent Coupling (Instability Metric)
- **Instability (I) = Efferent / (Afferent + Efferent)**:
  - **Stable modules** (domain, core): I ≤ 0.3
  - **Abstract modules** (interfaces): I ≤ 0.2
  - **Unstable modules** (UI, adapters): I ≤ 0.7
  - **Critical**: I > 0.8 for non-leaf modules → Refactor

### Change Coupling (Git Churn Analysis)
- **Co-change frequency**: Files modified together > 70% of commits → High coupling risk
- **Change hotspots**: > 20 changes/month → Instability indicator
- **Parallel changes**: Same developer editing 3+ files in one commit → Consider consolidation

## Cohesion Metrics

### LCOM4 (Lack of Cohesion of Methods)
- **Target**: LCOM4 ≤ 0.15
- **Refactor**: LCOM4 > 0.2
- **Critical**: Members split into ≥ 3 groups → Responsibility separation needed

## Lines of Code (LOC)

### Function/Method
- **Standard**: ≤ 40 lines
- **Exceptional** (initialization logic): ≤ 60 lines
- **Tests**: ≤ 80 lines per test case

### Class
- **Target**: ≤ 200 lines

### Module (File)
- **Target**: ≤ 400 lines

## Responsibility Count

### Module Responsibilities
- **Principle**: "1 primary + 1 auxiliary max"
- **Refactor**: > 2 auxiliary responsibilities → Split module
- **Plugin public entry points**: ≤ 2 (type definition + implementation)
  - Configuration/utilities → Extract to separate module

### Interface Stability
- **Public types/functions per file**: ≤ 5
- **Exceeds**: Create sub-modules to maintain import granularity

## Code Quality Guidelines

### Guard Clauses & Type Narrowing
- **≥ 3 consecutive levels**: Extract to helper function

### Type Reusability
- **Ratio (existing:new types)**: Maintain ≥ 7:3
- Prefer reusing existing types over creating new ones

## Advanced Metrics

### API Surface Growth Rate
- **Public exports per release**: Growth rate ≤ 10% per minor version
- **Breaking changes**: ≤ 1 per major version
- **Deprecation cycle**: Minimum 2 versions before removal

### Architectural Violations
- **Layer violations**: Domain importing from infrastructure → **Critical**
- **Circular module dependencies**: **Prohibited** at module level
- **Dependency Rule**: Dependencies point inward (UI → App → Domain)

### Dead Code Detection
- **Unused exports**: Flag for removal after 2 releases
- **Unreachable code**: Immediate removal candidate
- **Orphaned types**: Types with zero usage → Remove

## Adaptive Thresholds (Auto-normalization)

Instead of fixed thresholds, consider statistical normalization:

### Statistical Approach
- **Baseline**: Calculate median and standard deviation for each metric across codebase
- **Outlier detection**: Flag files/functions > median + 2σ
- **Percentile-based**: P95 as warning threshold, P99 as critical

### Layer-specific Thresholds

| Layer | Max CC | Max LOC | Max Imports | Instability |
|-------|--------|---------|-------------|-------------|
| UI/Presentation | 8 | 200 | 12 | ≤ 0.7 |
| Application | 10 | 300 | 8 | ≤ 0.5 |
| Domain | 12 | 400 | 6 | ≤ 0.3 |
| Infrastructure | 10 | 250 | 10 | ≤ 0.6 |

**Rationale**: UI components naturally have more conditional rendering; domain logic may be complex but stable; infrastructure adapts to external systems.

## Static Analysis Integration

### Recommended Tool Chain
1. **TypeScript Compiler API / ts-morph**: AST analysis, type complexity
2. **ESLint + TypeScript-ESLint**: Cognitive complexity, best practices
3. **depcruise / madge**: Dependency graphs, circular dependencies
4. **ts-prune / ts-unused-exports**: Dead code detection
5. **Vitest/Jest coverage**: Test coverage correlation
6. **Git analysis** (git log, git blame): Change coupling, hotspots

### Recommended CI Checks
1. **Cyclomatic/Cognitive Complexity**: Report violations
2. **Dependency Graphs**: Visualize and detect cycles
3. **Threshold Monitoring**: Track metrics against adaptive thresholds
4. **Trend Analysis**: Monitor complexity growth over time
5. **Coverage vs Complexity**: Flag high-complexity, low-coverage code

## Interpretation Notes

### When to Apply These Standards

**Do apply**:
- Code reviews before merging
- Periodic quality audits
- When planning refactoring
- When complexity causes bugs

**Don't over-apply**:
- Test files (can be more verbose)
- One-time migration scripts
- Prototype/experimental code

### Balancing Act

These thresholds aim to:
✅ Catch real design issues
✅ Prevent over-engineering
❌ Not enforce enterprise patterns on small projects
❌ Not suggest premature abstraction

### Project-Specific Adjustments

For Assay specifically:
- **Pluggable architecture**: Prioritize interface simplicity
- **Type safety**: Strict TypeScript enables higher complexity tolerance in type definitions
- **Framework nature**: Public API surface area matters more than internal complexity
- **Test-driven**: Tests can be more descriptive (longer) than production code

## References

Based on industry standards and Codex recommendations, tailored for TypeScript framework projects following modern best practices.
