# Refactoring Patterns for SOLID Violations

## Overview

This document describes common code smells related to SOLID principles and practical refactoring patterns to address them in TypeScript projects.

## SOLID Principle Violations

### 1. Single Responsibility Principle (SRP) Violations

#### Smell: God Class/Module
**Symptoms**:
- Class/module handles multiple unrelated concerns
- High total cyclomatic complexity (>50)
- Many public methods/exports (>5)
- Mixed business logic, data access, and presentation

**Detection**:
- LCOM4 > 0.2 (low cohesion)
- Multiple distinct groups of methods/fields
- File length > 400 lines

**Refactoring**:
```typescript
// Before: God class handling multiple responsibilities
class UserService {
  validateUser(user: User): boolean { /* validation */ }
  saveUser(user: User): Promise<void> { /* persistence */ }
  sendWelcomeEmail(user: User): Promise<void> { /* email */ }
  generateReport(userId: string): Report { /* reporting */ }
}

// After: Separated responsibilities
class UserValidator {
  validate(user: User): boolean { /* validation */ }
}

class UserRepository {
  save(user: User): Promise<void> { /* persistence */ }
}

class NotificationService {
  sendWelcomeEmail(user: User): Promise<void> { /* email */ }
}

class ReportGenerator {
  generateUserReport(userId: string): Report { /* reporting */ }
}
```

### 2. Open/Closed Principle (OCP) Violations

#### Smell: Modification Required for Extension
**Symptoms**:
- Long switch/if-else chains for type discrimination
- Adding new behavior requires modifying existing code
- Hard-coded type checks

**Detection**:
- CC > 10 in single function with multiple branches
- Repeated `instanceof` or type checks
- Frequent modifications to same function

**Refactoring - Strategy Pattern**:
```typescript
// Before: Switch statement for different behaviors
class Reporter {
  report(format: string, data: Data): void {
    switch (format) {
      case 'json':
        // JSON logic
        break;
      case 'xml':
        // XML logic
        break;
      case 'csv':
        // CSV logic
        break;
    }
  }
}

// After: Strategy pattern with interface
interface ReportStrategy {
  format(data: Data): string;
}

class JsonReporter implements ReportStrategy {
  format(data: Data): string { /* JSON */ }
}

class XmlReporter implements ReportStrategy {
  format(data: Data): string { /* XML */ }
}

class CsvReporter implements ReportStrategy {
  format(data: Data): string { /* CSV */ }
}

class Reporter {
  constructor(private strategy: ReportStrategy) {}
  report(data: Data): void {
    return this.strategy.format(data);
  }
}
```

### 3. Liskov Substitution Principle (LSP) Violations

#### Smell: Subclass Violates Contract
**Symptoms**:
- Subclass throws unexpected errors
- Overridden methods have different preconditions/postconditions
- instanceof checks before method calls

**Detection**:
- Tests failing when using subclass
- Guard clauses checking specific subclass types
- Documentation stating "don't use X with Y"

**Refactoring**:
```typescript
// Before: LSP violation
class Rectangle {
  constructor(public width: number, public height: number) {}
  setWidth(width: number): void { this.width = width; }
  setHeight(height: number): void { this.height = height; }
  area(): number { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(width: number): void {
    this.width = width;
    this.height = width; // Violates expected behavior!
  }
  setHeight(height: number): void {
    this.width = height;
    this.height = height; // Violates expected behavior!
  }
}

// After: Composition over inheritance
interface Shape {
  area(): number;
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  area(): number { return this.width * this.height; }
}

class Square implements Shape {
  constructor(private side: number) {}
  area(): number { return this.side * this.side; }
}
```

### 4. Interface Segregation Principle (ISP) Violations

#### Smell: Fat Interface
**Symptoms**:
- Interface with many methods (>5)
- Implementations leaving methods empty or throwing "not implemented"
- Clients depend on methods they don't use

**Detection**:
- Multiple `throw new Error('Not implemented')`
- Empty method implementations
- High fan-out from interface

**Refactoring**:
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

// After: Segregated interfaces
interface SearchAdapter {
  search(query: string): Results;
}

interface WarmableAdapter {
  warmup(): Promise<void>;
}

interface StoppableAdapter {
  stop(): Promise<void>;
}

interface MonitorableAdapter {
  getStats(): Stats;
  healthCheck(): boolean;
}

interface ConfigurableAdapter {
  configure(config: Config): void;
}

// Implementations can pick what they need
class SimpleAdapter implements SearchAdapter {
  search(query: string): Results { /* ... */ }
}

class AdvancedAdapter implements
  SearchAdapter,
  WarmableAdapter,
  StoppableAdapter,
  MonitorableAdapter {
  // Implements only needed methods
}
```

### 5. Dependency Inversion Principle (DIP) Violations

#### Smell: High-level Depends on Low-level
**Symptoms**:
- High-level modules import concrete implementations
- Direct instantiation of dependencies
- Hard to test due to concrete dependencies

**Detection**:
- Import count of concrete types > 4
- Direct `new` calls in business logic
- Difficulty mocking in tests

**Refactoring - Dependency Injection**:
```typescript
// Before: Direct dependency on concrete class
class EvaluationRunner {
  private adapter = new KiriSearchAdapter(); // Concrete dependency

  async run(queries: Query[]): Promise<Results> {
    return this.adapter.search(queries);
  }
}

// After: Dependency injection with interface
interface SearchAdapter {
  search(queries: Query[]): Promise<Results>;
}

class EvaluationRunner {
  constructor(private adapter: SearchAdapter) {} // Injected dependency

  async run(queries: Query[]): Promise<Results> {
    return this.adapter.search(queries);
  }
}

// Usage
const adapter = new KiriSearchAdapter();
const runner = new EvaluationRunner(adapter);
```

## Common Code Smells

### Long Method
**Threshold**: >40 lines (>60 for initialization)

**Refactoring**: Extract Method
```typescript
// Before
function processOrder(order: Order): void {
  // Validation (10 lines)
  // Price calculation (15 lines)
  // Inventory update (10 lines)
  // Notification (10 lines)
}

// After
function processOrder(order: Order): void {
  validateOrder(order);
  const price = calculatePrice(order);
  updateInventory(order);
  sendNotification(order, price);
}
```

### Long Parameter List
**Threshold**: >4 parameters

**Refactoring**: Parameter Object
```typescript
// Before
function createUser(
  name: string,
  email: string,
  age: number,
  address: string,
  phone: string
): User { /* ... */ }

// After
interface UserData {
  name: string;
  email: string;
  age: number;
  address: string;
  phone: string;
}

function createUser(userData: UserData): User { /* ... */ }
```

### Feature Envy
**Smell**: Method uses more data from another class than its own

**Refactoring**: Move Method
```typescript
// Before
class Report {
  generate(metrics: Metrics): string {
    const precision = metrics.getTruePositives() /
      (metrics.getTruePositives() + metrics.getFalsePositives());
    const recall = metrics.getTruePositives() /
      (metrics.getTruePositives() + metrics.getFalseNegatives());
    return `Precision: ${precision}, Recall: ${recall}`;
  }
}

// After
class Metrics {
  getPrecision(): number {
    return this.truePositives / (this.truePositives + this.falsePositives);
  }

  getRecall(): number {
    return this.truePositives / (this.truePositives + this.falseNegatives);
  }
}

class Report {
  generate(metrics: Metrics): string {
    return `Precision: ${metrics.getPrecision()}, Recall: ${metrics.getRecall()}`;
  }
}
```

### Primitive Obsession
**Smell**: Using primitives instead of small objects

**Refactoring**: Introduce Value Object
```typescript
// Before
function sendEmail(email: string): void {
  if (!email.includes('@')) throw new Error('Invalid email');
  // ...
}

// After
class Email {
  private constructor(private readonly value: string) {
    if (!value.includes('@')) throw new Error('Invalid email');
  }

  static from(value: string): Email {
    return new Email(value);
  }

  toString(): string {
    return this.value;
  }
}

function sendEmail(email: Email): void {
  // Email is already validated
}
```

## Refactoring Process

### 1. Identify the Smell
Use metrics and code review to identify violations:
- Complexity metrics (CC, LCOM4)
- Coupling metrics (imports, fan-out)
- LOC thresholds

### 2. Write Tests First
Before refactoring:
- Ensure existing tests pass
- Add tests for edge cases
- Consider property-based tests

### 3. Refactor Incrementally
- Small, safe steps
- Run tests after each change
- Commit frequently

### 4. Verify Improvement
After refactoring:
- Re-run metrics
- Confirm thresholds are met
- Verify tests still pass
- Check performance hasn't degraded

## TypeScript-Specific Patterns

### Use Type Guards
```typescript
function isSearchAdapter(obj: unknown): obj is SearchAdapter {
  return typeof obj === 'object' && obj !== null && 'search' in obj;
}
```

### Leverage Discriminated Unions
```typescript
type Result =
  | { success: true; data: Data }
  | { success: false; error: Error };

function handleResult(result: Result): void {
  if (result.success) {
    // TypeScript knows result.data exists
  } else {
    // TypeScript knows result.error exists
  }
}
```

### Use Readonly for Immutability
```typescript
interface Config {
  readonly timeout: number;
  readonly retries: number;
}
```

## References

- Martin Fowler - "Refactoring: Improving the Design of Existing Code"
- Robert C. Martin - "Clean Code" and "Clean Architecture"
- SOLID Principles applied to TypeScript
