# Refactoring Patterns: Detection and Execution

## SOLID Principle Violations

### 1. Single Responsibility Principle (SRP) -- God Class/Module

**Detection**:
- LCOM4 > 0.2 (low cohesion), multiple distinct method/field groups
- Total CC > 50, many public methods/exports (>5), file > 400 lines
- Mixed business logic, data access, and presentation

**Refactoring**: Extract Class/Module
```typescript
// Before: God class
class UserService {
  validateUser(user: User): boolean { /* validation */ }
  saveUser(user: User): Promise<void> { /* persistence */ }
  sendWelcomeEmail(user: User): Promise<void> { /* email */ }
  generateReport(userId: string): Report { /* reporting */ }
}

// After: Separated responsibilities
class UserValidator { validate(user: User): boolean { /* ... */ } }
class UserRepository { save(user: User): Promise<void> { /* ... */ } }
class NotificationService { sendWelcomeEmail(user: User): Promise<void> { /* ... */ } }
class ReportGenerator { generateUserReport(userId: string): Report { /* ... */ } }
```

**Execution steps**:
1. Identify responsibility boundaries (map methods to distinct concerns)
2. Create interface for new class
3. Implement new class, move relevant methods
4. Update original class to delegate via dependency injection
5. Repeat for each responsibility
6. Wire dependencies at construction site
7. Verify: tests pass, no circular deps, behavior unchanged

### 2. Open/Closed Principle (OCP) -- Switch/If-Else Chains

**Detection**:
- CC > 10 in function with multiple branches
- Repeated `instanceof` or type checks
- Frequent modifications to same function (git churn)

**Refactoring**: Replace Conditional with Polymorphism (Strategy Pattern)
```typescript
// Before
class Reporter {
  report(format: string, data: Data): void {
    switch (format) {
      case 'json': /* ... */ break;
      case 'xml': /* ... */ break;
      case 'csv': /* ... */ break;
    }
  }
}

// After
interface ReportStrategy { format(data: Data): string; }
class JsonReporter implements ReportStrategy { format(data: Data): string { /* ... */ } }
class XmlReporter implements ReportStrategy { format(data: Data): string { /* ... */ } }

class Reporter {
  constructor(private strategy: ReportStrategy) {}
  report(data: Data): string { return this.strategy.format(data); }
}
```

**Execution steps**:
1. Define strategy interface capturing all variant behavior
2. Implement one strategy per branch, with tests
3. Refactor original class to accept strategy via constructor
4. Update call sites (or add factory)
5. Verify: new strategies can be added without modifying Reporter

### 3. Liskov Substitution Principle (LSP) -- Contract Violations

**Detection**:
- Subclass throws unexpected errors or changes preconditions/postconditions
- `instanceof` checks before method calls
- Tests failing when substituting subclass

**Refactoring**: Composition over Inheritance
```typescript
// Before: LSP violation
class Square extends Rectangle {
  setWidth(w: number): void { this.width = w; this.height = w; }
}

// After: Shared interface, separate implementations
interface Shape { area(): number; }
class Rectangle implements Shape { /* ... */ }
class Square implements Shape { /* ... */ }
```

### 4. Interface Segregation Principle (ISP) -- Fat Interfaces

**Detection**:
- Interface with >5 methods
- Implementations with empty methods or `throw new Error('Not implemented')`
- Clients depending on methods they never call

**Refactoring**: Split into focused interfaces
```typescript
// Before: Fat interface
interface SearchAdapter {
  search(query: string): Results;
  warmup(): Promise<void>;
  stop(): Promise<void>;
  getStats(): Stats;
  configure(config: Config): void;
  healthCheck(): boolean;
}

// After: Segregated
interface SearchAdapter { search(query: string): Results; }
interface WarmableAdapter { warmup(): Promise<void>; }
interface MonitorableAdapter { getStats(): Stats; healthCheck(): boolean; }
// Implementations compose only needed interfaces
```

### 5. Dependency Inversion Principle (DIP) -- Concrete Dependencies

**Detection**:
- Import count of concrete types > 4
- Direct `new` calls in business logic
- Difficulty mocking in tests

**Refactoring**: Dependency Injection
```typescript
// Before
class EvaluationRunner {
  private adapter = new KiriSearchAdapter();
  async run(queries: Query[]): Promise<Results> { return this.adapter.search(queries); }
}

// After
class EvaluationRunner {
  constructor(private adapter: SearchAdapter) {}
  async run(queries: Query[]): Promise<Results> { return this.adapter.search(queries); }
}
```

---

## Common Code Smells

### Long Method (>40 lines, >60 for initialization)

**Refactoring**: Extract Method

**Execution steps**:
1. Identify extract target with clear boundaries and single responsibility
2. Create new function with explicit parameters and return type
3. Replace original code with function call
4. Add tests for extracted function
5. Verify: no type errors, no `any` introduced, tests pass

**Rollback**: `git restore <file>` if step fails

### Long Parameter List (>4 parameters)

**Refactoring**: Introduce Parameter Object

**Execution steps**:
1. Create parameter object type with all fields
2. Add function overload accepting both old and new signatures (temporary)
3. Update call sites gradually to new signature
4. Remove old signature once all callers migrated
5. Verify: both styles work during transition, no breaking changes

### Feature Envy

Method uses more data from another class than its own.

**Refactoring**: Move Method

**Execution steps**:
1. Identify move target (method uses 0 fields from current class, many from another)
2. Copy method to target class, adapt `this` references
3. Update original class to delegate temporarily
4. Update all call sites to use new location
5. Remove delegating method
6. Verify: no references to old method remain

### Primitive Obsession

Using primitives instead of small value objects.

**Refactoring**: Introduce Value Object
```typescript
class Email {
  private constructor(private readonly value: string) {
    if (!value.includes('@')) throw new Error('Invalid email');
  }
  static from(value: string): Email { return new Email(value); }
  toString(): string { return this.value; }
}
```

---

## Pattern Execution: Split Phase

Separate computation from side effects.

**When to apply**: Function mixes pure computation with I/O.

**Execution steps**:
1. Identify computation phase (pure) and side effect phase (I/O)
2. Extract computation to pure function with explicit return type
3. Extract side effects to separate async function
4. Compose: `const result = compute(input); await persist(result);`
5. Verify: computation function is testable without mocks

---

## Pattern Execution: Encapsulate Field

**When to apply**: Public fields accessed directly, need validation or may change representation.

**Execution steps**:
1. Add getter and setter (syntax unchanged: `user.email` still works)
2. Add validation in setter if needed
3. Make backing field private
4. Verify: no direct field access outside class

---

## Pattern Execution: Rename Symbol

**Execution steps**:
1. Find all references: `grep -r "oldName" src/` or IDE find-all-references
2. Rename symbol at declaration
3. Update all references (imports, call sites, tests, documentation)
4. Verify: no compilation errors, tests pass

---

## Type Safety Checklist (Apply to Every Pattern)

- Return types explicit (not inferred for public API)
- Parameter types explicit
- No `any` types introduced
- No circular dependencies created
- Public API contracts preserved
- Dependency injection is type-safe

## Rollback Protocol

- Uncommitted changes: `git restore <file>`
- Last commit: `git reset --hard HEAD~1`
- Specific commit range: `git revert <commit-range>`
- Always investigate failure cause before re-attempting

---

## TypeScript-Specific Patterns

**Type Guards**: Replace `instanceof` chains with type predicates
```typescript
function isSearchAdapter(obj: unknown): obj is SearchAdapter {
  return typeof obj === 'object' && obj !== null && 'search' in obj;
}
```

**Discriminated Unions**: Replace type switches with exhaustive pattern matching
```typescript
type Result = { success: true; data: Data } | { success: false; error: Error };
```

**Readonly**: Prevent mutation at the type level
```typescript
interface Config { readonly timeout: number; readonly retries: number; }
```

---

## Common Pitfalls

1. **Breaking tests accidentally**: Revert immediately, add characterization test, re-attempt with smaller steps
2. **Introducing type errors**: Run `tsc --noEmit` after each step, fix before proceeding
3. **Hidden dependencies**: Identify all dependencies before extraction, pass as explicit parameters
4. **Over-refactoring**: Follow YAGNI, only extract when pattern is clear, measure complexity before/after
5. **Losing test coverage**: Add tests for extracted functions, track coverage changes
