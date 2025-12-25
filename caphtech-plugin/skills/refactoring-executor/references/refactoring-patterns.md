# Refactoring Patterns: Step-by-Step Execution Guides

## Overview

This document provides detailed, executable instructions for each supported refactoring pattern. Each pattern includes prerequisites, incremental steps, type safety checklists, and rollback procedures.

---

## Pattern 1: Extract Method / Extract Function

### When to Apply
- Function/method exceeds 40 lines
- Code block has clear purpose and can be named
- Code block is used multiple times (DRY violation)
- Cyclomatic complexity > 10

### Prerequisites
- [ ] Function has existing test coverage
- [ ] Function behavior is well-understood
- [ ] No hidden dependencies on outer scope (除: parameters)

### Incremental Steps

#### Step 1: Identify Extract Target
```typescript
// Before: Long method with identifiable block
function processOrder(order: Order): void {
  // Validation block (10 lines) ← Extract target
  if (!order.id) throw new Error('Invalid ID');
  if (!order.items || order.items.length === 0) throw new Error('Empty order');
  if (order.total < 0) throw new Error('Negative total');

  // Processing logic (20 lines)
  // ...
}
```

**Verification**:
- [ ] Extract target has clear boundaries
- [ ] Extract target has single responsibility
- [ ] Dependencies are explicit (no hidden state)

#### Step 2: Create Extracted Function
```typescript
// New function with explicit parameters
function validateOrder(order: Order): void {
  if (!order.id) throw new Error('Invalid ID');
  if (!order.items || order.items.length === 0) throw new Error('Empty order');
  if (order.total < 0) throw new Error('Negative total');
}
```

**Verification**:
- [ ] Function compiles (no type errors)
- [ ] Function signature is clear and minimal
- [ ] Function has single responsibility

#### Step 3: Replace Original Code
```typescript
// After: Simplified method
function processOrder(order: Order): void {
  validateOrder(order); // ← Replaced with extracted function

  // Processing logic (20 lines)
  // ...
}
```

**Verification**:
- [ ] Tests pass (no behavior change)
- [ ] No duplicate code remains
- [ ] Function call is clear and readable

#### Step 4: Add Tests for Extracted Function
```typescript
describe('validateOrder', () => {
  it('throws error for missing ID', () => {
    expect(() => validateOrder({} as Order)).toThrow('Invalid ID');
  });

  it('throws error for empty items', () => {
    expect(() => validateOrder({ id: '1', items: [] } as Order))
      .toThrow('Empty order');
  });

  it('throws error for negative total', () => {
    expect(() => validateOrder({ id: '1', items: [{}], total: -1 } as Order))
      .toThrow('Negative total');
  });
});
```

**Verification**:
- [ ] New tests pass
- [ ] Edge cases covered
- [ ] Test coverage maintained or improved

### Type Safety Checklist
- [ ] Return type explicit (not inferred)
- [ ] Parameter types explicit
- [ ] No `any` types introduced
- [ ] Function is pure (if applicable)

### Rollback Procedure
```bash
# If Step 3 fails
git restore <file>

# If tests fail after Step 4
git reset --hard HEAD~1
```

---

## Pattern 2: Extract Class / Extract Module

### When to Apply
- Class exceeds 200 lines
- LCOM4 > 0.2 (low cohesion)
- Class has multiple distinct responsibilities
- File exceeds 400 lines with multiple classes

### Prerequisites
- [ ] Class has comprehensive test coverage
- [ ] Responsibilities can be clearly separated
- [ ] Dependencies can be injected

### Incremental Steps

#### Step 1: Identify Responsibility Boundaries
```typescript
// Before: God class with multiple responsibilities
class UserService {
  // Responsibility 1: Validation
  validateUser(user: User): boolean { /* ... */ }

  // Responsibility 2: Persistence
  saveUser(user: User): Promise<void> { /* ... */ }

  // Responsibility 3: Notifications
  sendWelcomeEmail(user: User): Promise<void> { /* ... */ }
}
```

**Analysis**:
- Responsibility 1: User validation (domain logic)
- Responsibility 2: User persistence (data access)
- Responsibility 3: Email notifications (integration)

**Verification**:
- [ ] Responsibilities are distinct and separable
- [ ] Each responsibility has clear interface
- [ ] Dependencies between responsibilities are minimal

#### Step 2: Create Interface for New Class
```typescript
// New interface
interface UserValidator {
  validate(user: User): boolean;
}
```

**Verification**:
- [ ] Interface compiles
- [ ] Interface is cohesive (single responsibility)
- [ ] Interface has no implementation leaks

#### Step 3: Implement New Class
```typescript
// New class implementing interface
class DefaultUserValidator implements UserValidator {
  validate(user: User): boolean {
    // Moved validation logic
    return /* validation logic */;
  }
}
```

**Verification**:
- [ ] Class compiles
- [ ] Class has single responsibility
- [ ] Tests pass (copy tests from original class)

#### Step 4: Update Original Class to Use New Class
```typescript
// Refactored original class
class UserService {
  constructor(private validator: UserValidator) {}

  // Responsibility 2: Persistence
  saveUser(user: User): Promise<void> {
    if (!this.validator.validate(user)) {
      throw new Error('Invalid user');
    }
    // Save logic
  }

  // Responsibility 3: Notifications
  sendWelcomeEmail(user: User): Promise<void> { /* ... */ }
}
```

**Verification**:
- [ ] Tests pass (no behavior change)
- [ ] Dependencies are injected (not hard-coded)
- [ ] Original class is simpler

#### Step 5: Repeat for Remaining Responsibilities
Extract UserRepository and NotificationService similarly.

#### Step 6: Wire Dependencies
```typescript
// Dependency injection setup
const validator = new DefaultUserValidator();
const repository = new UserRepository();
const notificationService = new NotificationService();
const userService = new UserService(validator, repository, notificationService);
```

**Verification**:
- [ ] All tests pass
- [ ] Dependencies are explicit
- [ ] System behavior unchanged

### Type Safety Checklist
- [ ] All interfaces have explicit types
- [ ] No circular dependencies introduced
- [ ] Dependency injection is type-safe
- [ ] Public API contracts preserved

### Rollback Procedure
```bash
# Rollback to before extraction
git revert <commit-range>

# Or reset to last good state
git reset --hard <last-good-commit>
```

---

## Pattern 3: Move Method / Move Field

### When to Apply
- Method uses more data from another class (Feature Envy)
- Method logically belongs to different class
- Reducing coupling between classes

### Prerequisites
- [ ] Target class exists and is accessible
- [ ] Method has test coverage
- [ ] Dependencies can be passed as parameters

### Incremental Steps

#### Step 1: Identify Move Target
```typescript
// Before: Method in wrong class
class Report {
  generate(metrics: Metrics): string {
    // Feature Envy: Uses more from Metrics than Report
    const precision = metrics.getTruePositives() /
      (metrics.getTruePositives() + metrics.getFalsePositives());
    const recall = metrics.getTruePositives() /
      (metrics.getTruePositives() + metrics.getFalseNegatives());
    return `Precision: ${precision}, Recall: ${recall}`;
  }
}
```

**Analysis**:
- Method uses 4 methods from Metrics class
- Method uses 0 fields from Report class
- → Method should move to Metrics class

#### Step 2: Copy Method to Target Class
```typescript
// Add method to Metrics class
class Metrics {
  // ... existing methods ...

  getSummary(): string {
    const precision = this.getTruePositives() /
      (this.getTruePositives() + this.getFalsePositives());
    const recall = this.getTruePositives() /
      (this.getTruePositives() + this.getFalseNegatives());
    return `Precision: ${precision}, Recall: ${recall}`;
  }
}
```

**Verification**:
- [ ] Method compiles in new location
- [ ] Tests pass for new method

#### Step 3: Update Original Class to Delegate
```typescript
// Temporary delegation in Report class
class Report {
  generate(metrics: Metrics): string {
    return metrics.getSummary(); // Delegate to moved method
  }
}
```

**Verification**:
- [ ] All tests pass
- [ ] Behavior unchanged

#### Step 4: Update Call Sites
```typescript
// Before
const report = new Report();
const summary = report.generate(metrics);

// After
const summary = metrics.getSummary();
```

**Verification**:
- [ ] All call sites updated
- [ ] Tests pass
- [ ] No compilation errors

#### Step 5: Remove Old Method
```typescript
// Remove delegating method from Report class
class Report {
  // generate() method removed
}
```

**Verification**:
- [ ] No references to old method remain
- [ ] All tests pass
- [ ] Code is simpler

### Type Safety Checklist
- [ ] Method signature preserved or improved
- [ ] Return type explicit
- [ ] Access modifiers appropriate (public/private)

### Rollback Procedure
```bash
# If delegation fails
git reset --hard HEAD~1

# If call site updates fail
git restore <files>
```

---

## Pattern 4: Rename Symbol

### When to Apply
- Name is unclear or misleading
- Name doesn't match current purpose
- Name violates naming conventions

### Prerequisites
- [ ] Symbol is used consistently
- [ ] Tests cover all usages
- [ ] No ambiguous references

### Incremental Steps

#### Step 1: Find All References
```bash
# Using grep or IDE search
grep -r "oldName" src/

# Or use TypeScript's find-all-references
npx ts-morph-rename --symbol oldName --to newName
```

**Verification**:
- [ ] All references found
- [ ] No false positives in search

#### Step 2: Rename Symbol
```typescript
// Before
function calc(data: number[]): number { /* ... */ }

// After
function calculateAverage(data: number[]): number { /* ... */ }
```

**Verification**:
- [ ] New name is clearer
- [ ] New name follows conventions
- [ ] No name conflicts introduced

#### Step 3: Update All References
```typescript
// Update all call sites
const avg = calculateAverage([1, 2, 3]); // Was: calc([1, 2, 3])
```

**Verification**:
- [ ] All references updated
- [ ] Tests pass
- [ ] No compilation errors

#### Step 4: Update Tests and Documentation
```typescript
describe('calculateAverage', () => { // Was: describe('calc')
  it('calculates average of numbers', () => {
    expect(calculateAverage([1, 2, 3])).toBe(2);
  });
});
```

**Verification**:
- [ ] Test names updated
- [ ] Documentation updated
- [ ] Comments updated

### Type Safety Checklist
- [ ] Symbol type unchanged
- [ ] Exported symbols have correct export name
- [ ] Import statements updated

### Rollback Procedure
```bash
# Simple revert
git revert HEAD

# Or restore specific files
git restore <files>
```

---

## Pattern 5: Introduce Parameter Object

### When to Apply
- Function has > 4 parameters
- Parameters are logically related
- Parameter group is used in multiple functions

### Prerequisites
- [ ] Parameters are logically grouped
- [ ] Parameter group can be named meaningfully
- [ ] Tests cover all parameter combinations

### Incremental Steps

#### Step 1: Create Parameter Object Type
```typescript
// Before: Long parameter list
function createUser(
  name: string,
  email: string,
  age: number,
  address: string,
  phone: string
): User { /* ... */ }

// After: Parameter object
interface UserData {
  name: string;
  email: string;
  age: number;
  address: string;
  phone: string;
}
```

**Verification**:
- [ ] Type compiles
- [ ] Type has clear name
- [ ] All parameters included

#### Step 2: Add New Function Signature (Overload)
```typescript
// Add overload with parameter object
function createUser(userData: UserData): User;
function createUser(
  name: string,
  email: string,
  age: number,
  address: string,
  phone: string
): User;
function createUser(
  nameOrData: string | UserData,
  email?: string,
  age?: number,
  address?: string,
  phone?: string
): User {
  // Implementation handles both signatures
  const userData = typeof nameOrData === 'string'
    ? { name: nameOrData, email: email!, age: age!, address: address!, phone: phone! }
    : nameOrData;

  // Use userData for implementation
  return /* implementation */;
}
```

**Verification**:
- [ ] Both signatures work
- [ ] Tests pass with old signature
- [ ] Tests pass with new signature

#### Step 3: Update Call Sites Gradually
```typescript
// Old style (still works)
createUser('John', 'john@example.com', 30, '123 Main St', '555-1234');

// New style
createUser({
  name: 'John',
  email: 'john@example.com',
  age: 30,
  address: '123 Main St',
  phone: '555-1234'
});
```

**Verification**:
- [ ] Both styles work
- [ ] Tests pass for both
- [ ] No breaking changes

#### Step 4: Remove Old Signature (Breaking Change)
```typescript
// Final: Only parameter object signature
function createUser(userData: UserData): User {
  return /* implementation */;
}
```

**Verification**:
- [ ] All call sites use new signature
- [ ] Tests pass
- [ ] Code is cleaner

### Type Safety Checklist
- [ ] Parameter object type is explicit
- [ ] Required vs. optional fields clear
- [ ] Default values preserved (if any)
- [ ] Validation logic updated

### Rollback Procedure
```bash
# Rollback to dual-signature state
git reset --hard <commit-before-step-4>
```

---

## Pattern 6: Replace Conditional with Polymorphism

### When to Apply
- Long switch/if-else chains (> 5 branches)
- Same condition checked in multiple places
- Adding new types requires modifying existing code (OCP violation)

### Prerequisites
- [ ] Conditions are based on type/category
- [ ] Each branch can be encapsulated in a strategy
- [ ] Tests cover all branches

### Incremental Steps

#### Step 1: Define Strategy Interface
```typescript
// Before: Switch statement
class Reporter {
  report(format: string, data: Data): void {
    switch (format) {
      case 'json': /* JSON logic */ break;
      case 'xml': /* XML logic */ break;
      case 'csv': /* CSV logic */ break;
    }
  }
}

// After: Strategy interface
interface ReportStrategy {
  format(data: Data): string;
}
```

**Verification**:
- [ ] Interface compiles
- [ ] Interface captures all variants
- [ ] Interface is minimal

#### Step 2: Implement Strategies
```typescript
class JsonReporter implements ReportStrategy {
  format(data: Data): string {
    return JSON.stringify(data);
  }
}

class XmlReporter implements ReportStrategy {
  format(data: Data): string {
    // XML formatting logic
    return `<data>${/* ... */}</data>`;
  }
}

class CsvReporter implements ReportStrategy {
  format(data: Data): string {
    // CSV formatting logic
    return /* CSV string */;
  }
}
```

**Verification**:
- [ ] Each strategy compiles
- [ ] Each strategy has tests
- [ ] Behavior matches original branches

#### Step 3: Refactor Original Class
```typescript
class Reporter {
  constructor(private strategy: ReportStrategy) {}

  report(data: Data): string {
    return this.strategy.format(data);
  }
}
```

**Verification**:
- [ ] Class compiles
- [ ] Tests pass with each strategy
- [ ] Code is simpler

#### Step 4: Update Call Sites
```typescript
// Before
const reporter = new Reporter();
reporter.report('json', data);

// After
const jsonReporter = new Reporter(new JsonReporter());
jsonReporter.report(data);

// Or with factory
const reporter = ReporterFactory.create('json');
reporter.report(data);
```

**Verification**:
- [ ] All call sites updated
- [ ] Tests pass
- [ ] New strategies can be added without modifying Reporter

### Type Safety Checklist
- [ ] Strategy interface is type-safe
- [ ] Strategy implementations are type-safe
- [ ] Dependency injection is type-safe
- [ ] Factory (if used) is type-safe

### Rollback Procedure
```bash
# Rollback to switch statement
git revert <commit-range>

# Keep both implementations temporarily
# (switch delegates to strategies)
```

---

## Pattern 7: Encapsulate Field

### When to Apply
- Public fields accessed directly
- Field access needs validation or side effects
- Field representation might change

### Prerequisites
- [ ] Field is currently public
- [ ] All access points are known
- [ ] Tests cover field access

### Incremental Steps

#### Step 1: Add Getter and Setter
```typescript
// Before: Direct field access
class User {
  public email: string;
}

// After: Add getter/setter
class User {
  private _email: string;

  get email(): string {
    return this._email;
  }

  set email(value: string) {
    this._email = value;
  }
}
```

**Verification**:
- [ ] Compiles without errors
- [ ] Tests pass (behavior unchanged)
- [ ] Access syntax unchanged (`user.email`)

#### Step 2: Add Validation (if needed)
```typescript
class User {
  private _email: string;

  get email(): string {
    return this._email;
  }

  set email(value: string) {
    if (!value.includes('@')) {
      throw new Error('Invalid email');
    }
    this._email = value;
  }
}
```

**Verification**:
- [ ] Validation logic is correct
- [ ] Tests cover invalid cases
- [ ] Existing valid cases still pass

#### Step 3: Make Field Private
```typescript
// Field is now private (already done in Step 1)
// External access only through getter/setter
```

**Verification**:
- [ ] No direct field access outside class
- [ ] All tests pass
- [ ] Encapsulation achieved

### Type Safety Checklist
- [ ] Getter return type explicit
- [ ] Setter parameter type explicit
- [ ] Field type unchanged (unless intentional)

### Rollback Procedure
```bash
# Revert to public field
git revert HEAD
```

---

## Pattern 8: Split Phase

### When to Apply
- Function mixes computation and side effects
- Function is hard to test due to side effects
- Computation can be separated from I/O

### Prerequisites
- [ ] Computation is pure (deterministic)
- [ ] Side effects are identifiable
- [ ] Tests cover both phases

### Incremental Steps

#### Step 1: Identify Phases
```typescript
// Before: Mixed phases
async function processAndSaveOrder(order: Order): Promise<void> {
  // Phase 1: Computation
  const validatedOrder = validateOrder(order);
  const enrichedOrder = enrichOrder(validatedOrder);
  const pricedOrder = calculatePricing(enrichedOrder);

  // Phase 2: Side effect
  await saveToDatabase(pricedOrder);
  await sendConfirmationEmail(pricedOrder);
}
```

**Analysis**:
- Phase 1: Pure computation (validate → enrich → price)
- Phase 2: I/O side effects (database, email)

#### Step 2: Extract Computation Phase
```typescript
// Pure computation function
function computeOrderDetails(order: Order): ProcessedOrder {
  const validatedOrder = validateOrder(order);
  const enrichedOrder = enrichOrder(validatedOrder);
  const pricedOrder = calculatePricing(enrichedOrder);
  return pricedOrder;
}
```

**Verification**:
- [ ] Function is pure (no side effects)
- [ ] Function is testable without mocks
- [ ] Tests pass

#### Step 3: Extract Side Effect Phase
```typescript
// Side effect function
async function persistOrder(processedOrder: ProcessedOrder): Promise<void> {
  await saveToDatabase(processedOrder);
  await sendConfirmationEmail(processedOrder);
}
```

**Verification**:
- [ ] Function compiles
- [ ] Side effects are isolated
- [ ] Tests pass (with mocks for I/O)

#### Step 4: Compose Phases
```typescript
// Composed function
async function processAndSaveOrder(order: Order): Promise<void> {
  const processedOrder = computeOrderDetails(order); // Phase 1
  await persistOrder(processedOrder); // Phase 2
}
```

**Verification**:
- [ ] Behavior unchanged
- [ ] Tests pass
- [ ] Code is clearer

### Type Safety Checklist
- [ ] Computation phase is pure function
- [ ] Side effect phase has explicit return type (often Promise<void>)
- [ ] Intermediate data type is well-defined

### Rollback Procedure
```bash
# Revert to mixed implementation
git reset --hard HEAD~3
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Breaking Tests Accidentally
**Symptom**: Tests fail after refactoring step
**Solution**:
- Immediately revert last change
- Review change for unintended behavior modification
- Add characterization test to lock down expected behavior
- Re-attempt refactoring with smaller steps

### Pitfall 2: Introducing Type Errors
**Symptom**: TypeScript compilation fails
**Solution**:
- Run `tsc --noEmit` after each step
- Fix type errors before proceeding
- Use explicit types (avoid `any`)
- Leverage IDE's type checking

### Pitfall 3: Hidden Dependencies
**Symptom**: Extracted code fails due to missing context
**Solution**:
- Identify all dependencies before extraction
- Pass dependencies as explicit parameters
- Avoid global state and side effects
- Use dependency injection for services

### Pitfall 4: Over-Refactoring
**Symptom**: Code becomes more complex after refactoring
**Solution**:
- Follow YAGNI principle
- Only extract when pattern is clear
- Avoid premature abstraction
- Measure complexity before and after

### Pitfall 5: Losing Test Coverage
**Symptom**: Test coverage drops after refactoring
**Solution**:
- Add tests for extracted functions
- Maintain or improve coverage
- Use coverage tools to track
- Add characterization tests first

---

## Refactoring Checklist

Use this checklist for any refactoring:

### Before Starting
- [ ] All tests pass (green baseline)
- [ ] Git working directory clean
- [ ] Refactoring pattern selected
- [ ] Execution plan documented

### During Refactoring
- [ ] One small change at a time
- [ ] Run tests after each change
- [ ] Commit after successful validation
- [ ] Document decisions in commit messages

### After Each Step
- [ ] Tests pass (no regressions)
- [ ] Types are valid (`tsc --noEmit`)
- [ ] Linter passes (`eslint`)
- [ ] Behavior unchanged

### After Completion
- [ ] All tests pass
- [ ] Metrics improved or maintained
- [ ] Documentation updated
- [ ] Execution log completed

---

## Tool-Assisted Refactoring

### Using ts-morph for AST-Based Refactoring

```typescript
import { Project } from 'ts-morph';

// Extract method automatically
function extractMethod(
  sourceFile: SourceFile,
  startLine: number,
  endLine: number,
  methodName: string
): void {
  const textToExtract = sourceFile.getFullText()
    .split('\n')
    .slice(startLine - 1, endLine)
    .join('\n');

  // Create new method
  const newMethod = sourceFile.addFunction({
    name: methodName,
    statements: textToExtract
  });

  // Replace original code with method call
  // (simplified - production code needs more logic)
}
```

See `scripts/ts-morph-refactors.ts` for complete implementations.

---

## References

- Martin Fowler - "Refactoring: Improving the Design of Existing Code" (2nd Edition)
- Michael Feathers - "Working Effectively with Legacy Code"
- Joshua Kerievsky - "Refactoring to Patterns"
- TypeScript Documentation - Advanced Types and Patterns
