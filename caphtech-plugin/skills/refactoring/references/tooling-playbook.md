# Tooling Playbook for Refactoring Execution

## Overview

This playbook provides concrete examples of using TypeScript tooling for safe refactoring execution. Each tool section includes installation, usage examples, failure diagnostics, and integration patterns.

---

## Tool 1: TypeScript Compiler (tsc)

### Purpose
- Type checking before and after refactoring
- Verify no type errors introduced
- Catch breaking changes early

### Installation
```bash
# Usually already installed with TypeScript project
pnpm add -D typescript
```

### Usage Examples

#### Example 1: Full Type Check
```bash
# Check entire project
pnpm tsc --noEmit

# With pretty output
pnpm tsc --noEmit --pretty

# Check specific files only
pnpm tsc --noEmit src/specific/file.ts
```

**Success Output**:
```
# No output = success (exit code 0)
```

**Failure Output**:
```
src/user/service.ts:15:3 - error TS2322: Type 'string' is not assignable to type 'number'.

15   age: "30",
     ~~~

Found 1 error.
```

#### Example 2: Incremental Type Checking
```bash
# Use incremental mode for faster checks
pnpm tsc --noEmit --incremental
```

**Benefits**:
- Faster subsequent checks (uses `.tsbuildinfo` cache)
- Ideal for iterative refactoring

#### Example 3: Watch Mode During Refactoring
```bash
# Continuous type checking
pnpm tsc --noEmit --watch
```

**Usage**:
- Leave running in separate terminal
- Instant feedback on type errors

### Failure Diagnostics

#### Failure 1: Type Error After Refactoring
```
error TS2345: Argument of type 'string[]' is not assignable to parameter of type 'number[]'.
```

**Diagnosis**:
1. Check function signature change
2. Verify caller expectations
3. Identify if signature change was intentional

**Fix**:
```typescript
// Before refactoring
function process(data: string[]): void { /* ... */ }

// After refactoring (broken)
function process(data: number[]): void { /* ... */ }

// Fix: Either revert signature or update callers
process(['1', '2', '3']); // ❌ Type error
process([1, 2, 3]); // ✅ Fixed
```

#### Failure 2: Missing Type Definitions
```
error TS2339: Property 'newMethod' does not exist on type 'UserService'.
```

**Diagnosis**:
1. Check if extracted method needs export
2. Verify import statements updated
3. Check interface definitions

**Fix**:
```typescript
// Before: Method was private
class UserService {
  private validateUser() { /* ... */ }
}

// After: Method extracted to separate module, needs export
export class UserValidator {
  public validate() { /* ... */ } // ✅ Public export
}
```

### Integration with Refactoring Workflow

```bash
# Pre-refactoring checkpoint
pnpm tsc --noEmit && echo "✅ Baseline type check passed"

# After each refactoring step
pnpm tsc --noEmit && git add . && git commit -m "refactor: ..." || git reset --hard

# Automated in verify-step.sh
#!/bin/bash
pnpm tsc --noEmit
if [ $? -ne 0 ]; then
  echo "❌ Type check failed - rolling back"
  git reset --hard HEAD
  exit 1
fi
```

---

## Tool 2: Vitest / Jest

### Purpose
- Verify behavior preservation
- Catch regressions immediately
- Measure test execution time

### Installation
```bash
# Vitest (recommended for modern projects)
pnpm add -D vitest @vitest/ui

# Jest (alternative)
pnpm add -D jest ts-jest @types/jest
```

### Usage Examples

#### Example 1: Run All Tests
```bash
# Vitest
pnpm vitest run

# Jest
pnpm jest
```

**Success Output**:
```
✓ src/user/validator.test.ts (3 tests) 245ms
✓ src/user/service.test.ts (5 tests) 312ms

Test Files  2 passed (2)
Tests  8 passed (8)
Duration  1.23s
```

**Failure Output**:
```
❌ src/user/service.test.ts > UserService > should save user
AssertionError: expected 'saved' to equal 'created'

 ❯ src/user/service.test.ts:15:22
     13|   it('should save user', () => {
     14|     const result = service.save(user);
     15|     expect(result).toBe('created');
           ^
```

#### Example 2: Run Specific Tests
```bash
# Run tests matching pattern
pnpm vitest run user

# Run single test file
pnpm vitest run src/user/validator.test.ts

# Run tests in changed files only
pnpm vitest run --changed
```

#### Example 3: Watch Mode
```bash
# Continuous testing during refactoring
pnpm vitest

# With UI
pnpm vitest --ui
```

#### Example 4: Coverage Report
```bash
# Generate coverage
pnpm vitest run --coverage

# With JSON output for parsing
pnpm vitest run --coverage --reporter=json > coverage.json
```

**Coverage Output**:
```
-------------------------|---------|----------|---------|---------|
File                     | % Stmts | % Branch | % Funcs | % Lines |
-------------------------|---------|----------|---------|---------|
All files                |   85.23 |    78.45 |   91.67 |   84.12 |
 src/user/validator.ts   |   95.00 |    90.00 |  100.00 |   94.44 |
 src/user/service.ts     |   78.50 |    70.00 |   85.71 |   77.00 |
-------------------------|---------|----------|---------|---------|
```

### Failure Diagnostics

#### Failure 1: Test Expects Old Behavior
```javascript
❌ Expected: 'User validated'
   Received: 'Validation complete'
```

**Diagnosis**:
1. Check if behavior intentionally changed
2. If yes: Update test expectation (rare - be cautious)
3. If no: Revert refactoring

**Decision Tree**:
```
Test failure detected
├─ Was behavior change intentional?
│  ├─ Yes: Update test (document why)
│  └─ No: Revert refactoring ← MOST COMMON
```

#### Failure 2: Test Flakiness
```javascript
❌ TypeError: Cannot read property 'id' of undefined
   (passes on second run)
```

**Diagnosis**:
1. Check for timing issues (async/await)
2. Check for global state mutation
3. Check for test order dependency

**Fix**:
```javascript
// Before: Flaky test (race condition)
it('should load user', () => {
  service.loadUser(1);
  expect(service.currentUser).toBeDefined(); // ❌ Async not awaited
});

// After: Fixed
it('should load user', async () => {
  await service.loadUser(1);
  expect(service.currentUser).toBeDefined(); // ✅ Properly awaited
});
```

### Integration with Refactoring Workflow

```bash
# Pre-refactoring: Capture baseline
pnpm vitest run --reporter=json > baseline-tests.json

# After each step: Quick validation
pnpm vitest run --reporter=json --bail > step-tests.json
if [ $? -ne 0 ]; then
  echo "❌ Tests failed - rolling back"
  git reset --hard HEAD
  exit 1
fi

# Compare test count
BASELINE_COUNT=$(cat baseline-tests.json | jq '.numTotalTests')
STEP_COUNT=$(cat step-tests.json | jq '.numTotalTests')
if [ "$BASELINE_COUNT" -ne "$STEP_COUNT" ]; then
  echo "⚠️ Test count changed: $BASELINE_COUNT → $STEP_COUNT"
fi
```

---

## Tool 3: ESLint

### Purpose
- Code style and quality checks
- Catch common mistakes
- Auto-fix formatting issues

### Installation
```bash
pnpm add -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### Usage Examples

#### Example 1: Lint Entire Project
```bash
# Lint all files
pnpm eslint src/

# With auto-fix
pnpm eslint src/ --fix

# Specific file
pnpm eslint src/user/service.ts
```

**Success Output**:
```
# No output = no issues (exit code 0)
```

**Failure Output**:
```
src/user/service.ts
  15:3  error    'userName' is assigned a value but never used    @typescript-eslint/no-unused-vars
  22:10 warning  Unexpected console statement                      no-console

✖ 2 problems (1 error, 1 warning)
```

#### Example 2: JSON Output for Parsing
```bash
pnpm eslint src/ --format=json > lint-results.json
```

**JSON Output**:
```json
[
  {
    "filePath": "src/user/service.ts",
    "messages": [
      {
        "ruleId": "@typescript-eslint/no-unused-vars",
        "severity": 2,
        "message": "'userName' is assigned a value but never used",
        "line": 15,
        "column": 3
      }
    ],
    "errorCount": 1,
    "warningCount": 0
  }
]
```

#### Example 3: Dry-Run (Preview Fixes)
```bash
# See what would be fixed without applying changes
pnpm eslint src/ --fix-dry-run --format=json
```

### Failure Diagnostics

#### Failure 1: Unused Variable After Refactoring
```
error 'oldFunction' is defined but never used @typescript-eslint/no-unused-vars
```

**Diagnosis**:
1. Check if function was replaced by refactoring
2. Verify no remaining callers
3. Delete if truly unused

**Fix**:
```typescript
// Before: Both old and new function exist
function oldFunction() { /* ... */ } // ❌ Unused
function newFunction() { /* ... */ } // ✅ Replacement

// After: Remove old function
function newFunction() { /* ... */ } // ✅ Only new function
```

#### Failure 2: Complexity Warning
```
warning Function 'processOrder' has a complexity of 15. Maximum allowed is 10 complexity
```

**Diagnosis**:
1. Check if refactoring actually reduced complexity
2. If yes: Lint rule might need update
3. If no: Continue refactoring

**Fix**:
- Continue with Extract Method pattern to reduce complexity
- Don't adjust lint rule just to pass

### Integration with Refactoring Workflow

```bash
# Pre-refactoring: Capture baseline
pnpm eslint src/ --format=json > baseline-lint.json
BASELINE_ERRORS=$(cat baseline-lint.json | jq '[.[].errorCount] | add')
BASELINE_WARNINGS=$(cat baseline-lint.json | jq '[.[].warningCount] | add')

# After each step: Validate
pnpm eslint src/ --format=json > step-lint.json
STEP_ERRORS=$(cat step-lint.json | jq '[.[].errorCount] | add')
STEP_WARNINGS=$(cat step-lint.json | jq '[.[].warningCount] | add')

if [ "$STEP_ERRORS" -gt "$BASELINE_ERRORS" ]; then
  echo "❌ Lint errors increased: $BASELINE_ERRORS → $STEP_ERRORS"
  git reset --hard HEAD
  exit 1
fi

if [ "$STEP_WARNINGS" -gt "$BASELINE_WARNINGS" ]; then
  echo "⚠️ Lint warnings increased: $BASELINE_WARNINGS → $STEP_WARNINGS"
fi
```

---

## Tool 4: ts-morph (AST-Based Refactoring)

### Purpose
- Automated code transformations
- Safe AST-level refactoring
- Extract/Move/Rename operations

### Installation
```bash
pnpm add -D ts-morph
```

### Usage Examples

#### Example 1: Extract Method Automatically
```typescript
import { Project } from 'ts-morph';

function extractMethod(
  filePath: string,
  startLine: number,
  endLine: number,
  newMethodName: string
): void {
  const project = new Project({
    tsConfigFilePath: 'tsconfig.json'
  });

  const sourceFile = project.getSourceFileOrThrow(filePath);
  const statements = sourceFile.getStatements();

  // Find statements in range
  const statementsToExtract = statements.filter(stmt => {
    const line = stmt.getStartLineNumber();
    return line >= startLine && line <= endLine;
  });

  // Extract to new function
  const functionDeclaration = sourceFile.addFunction({
    name: newMethodName,
    statements: statementsToExtract.map(s => s.getText())
  });

  // Replace original code with function call
  statementsToExtract[0].replaceWithText(`${newMethodName}();`);
  for (let i = 1; i < statementsToExtract.length; i++) {
    statementsToExtract[i].remove();
  }

  // Save changes
  sourceFile.saveSync();
}

// Usage
extractMethod('src/user/service.ts', 15, 25, 'validateUser');
```

#### Example 2: Rename Symbol Everywhere
```typescript
import { Project } from 'ts-morph';

function renameSymbol(
  symbolName: string,
  newName: string
): void {
  const project = new Project({ tsConfigFilePath: 'tsconfig.json' });

  // Find all source files
  const sourceFiles = project.getSourceFiles();

  sourceFiles.forEach(sourceFile => {
    // Rename in this file
    const identifiers = sourceFile.getDescendantsOfKind(SyntaxKind.Identifier);

    identifiers
      .filter(id => id.getText() === symbolName)
      .forEach(id => id.rename(newName));
  });

  // Save all changes
  project.saveSync();
}

// Usage
renameSymbol('oldFunctionName', 'newFunctionName');
```

#### Example 3: Move Method to Another Class
```typescript
import { Project } from 'ts-morph';

function moveMethod(
  sourceClass: string,
  methodName: string,
  targetClass: string
): void {
  const project = new Project({ tsConfigFilePath: 'tsconfig.json' });

  // Find source class
  const sourceFile = project.getSourceFiles().find(sf =>
    sf.getClass(sourceClass) !== undefined
  );

  const sourceClassDecl = sourceFile!.getClass(sourceClass)!;
  const method = sourceClassDecl.getMethod(methodName)!;

  // Find target class
  const targetFile = project.getSourceFiles().find(sf =>
    sf.getClass(targetClass) !== undefined
  );

  const targetClassDecl = targetFile!.getClass(targetClass)!;

  // Copy method to target
  targetClassDecl.addMethod({
    name: method.getName(),
    parameters: method.getParameters().map(p => ({
      name: p.getName(),
      type: p.getType().getText()
    })),
    returnType: method.getReturnType().getText(),
    statements: method.getBodyText()
  });

  // Remove from source
  method.remove();

  // Save changes
  project.saveSync();
}
```

### Integration with Refactoring Workflow

See `scripts/ts-morph-refactors.ts` for complete implementations.

---

## Tool 5: Git

### Purpose
- Track changes incrementally
- Enable rollback
- Create reviewable commits

### Usage Examples

#### Example 1: Incremental Commits
```bash
# Stage specific refactoring
git add src/user/validator.ts

# Commit with descriptive message
git commit -m "refactor: extract validation to UserValidator

- Extract validation logic from UserService
- Add UserValidator interface
- Add tests for UserValidator

Tests: ✅ All pass
Types: ✅ No errors
"

# Repeat for each refactoring step
```

#### Example 2: Rollback Last Change
```bash
# Uncommitted changes
git reset --hard HEAD

# Last commit
git reset --hard HEAD~1

# Specific commit
git revert <commit-hash>
```

#### Example 3: Create Refactoring Branch
```bash
# Create branch for refactoring
git checkout -b refactor/extract-user-validator

# Work in isolation
# ... make changes ...

# Push to remote
git push -u origin refactor/extract-user-validator
```

---

## Combined Verification Script

### `scripts/verify-step.sh`

```bash
#!/bin/bash
set -e

STEP_NAME=$1
OUTPUT_DIR="logs/refactoring"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Verifying refactoring step: $STEP_NAME"

# Test
echo "✅ Running tests..."
pnpm vitest run --reporter=json > "$OUTPUT_DIR/$STEP_NAME-tests.json"
TEST_RESULT=$?

# Type check
echo "✅ Type checking..."
pnpm tsc --noEmit 2> "$OUTPUT_DIR/$STEP_NAME-types.txt"
TYPE_RESULT=$?

# Lint
echo "✅ Linting..."
pnpm eslint src/ --format=json > "$OUTPUT_DIR/$STEP_NAME-lint.json"
LINT_RESULT=$?

# Build (optional)
if [ -f "package.json" ] && grep -q "\"build\"" package.json; then
  echo "✅ Building..."
  pnpm build > "$OUTPUT_DIR/$STEP_NAME-build.log" 2>&1
  BUILD_RESULT=$?
else
  BUILD_RESULT=0
fi

# Summary
echo ""
echo "📊 Verification Summary:"
echo "  Tests: $([ $TEST_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Types: $([ $TYPE_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Lint:  $([ $LINT_RESULT -eq 0 ] && echo '✅ PASS' || echo '⚠️  WARN')"
echo "  Build: $([ $BUILD_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo ""

# Exit with failure if critical checks failed
if [ $TEST_RESULT -ne 0 ] || [ $TYPE_RESULT -ne 0 ] || [ $BUILD_RESULT -ne 0 ]; then
  echo "❌ Verification failed - rolling back"
  git reset --hard HEAD
  exit 1
fi

echo "🎉 All verifications passed!"
exit 0
```

**Usage**:
```bash
# After each refactoring step
./scripts/verify-step.sh "step-1-extract-validator"

# If verification passes, commit
git add .
git commit -m "refactor: extract validator"

# If verification fails, automatic rollback occurs
```

---

## Tooling Checklist

### Pre-Refactoring Setup
- [ ] TypeScript configured (`tsconfig.json`)
- [ ] Test framework configured (`vitest.config.ts` or `jest.config.js`)
- [ ] ESLint configured (`.eslintrc.js`)
- [ ] Git repository initialized
- [ ] Verification script created (`scripts/verify-step.sh`)

### Per-Step Validation
- [ ] Run `pnpm tsc --noEmit` (type check)
- [ ] Run `pnpm vitest run` (tests)
- [ ] Run `pnpm eslint src/` (lint)
- [ ] Run `pnpm build` (build check)
- [ ] Commit if all pass, rollback if any fail

### Post-Refactoring Verification
- [ ] Full test suite passes
- [ ] Type check passes
- [ ] Lint passes with no new warnings
- [ ] Build succeeds
- [ ] Metrics improved (LOC, CC, cohesion)

---

## References

- TypeScript Handbook: https://www.typescriptlang.org/docs/handbook/
- Vitest Documentation: https://vitest.dev/
- ESLint User Guide: https://eslint.org/docs/user-guide/
- ts-morph Documentation: https://ts-morph.com/
