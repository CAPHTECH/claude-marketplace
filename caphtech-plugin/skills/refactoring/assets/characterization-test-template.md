# Characterization Test Template

## Purpose

Characterization tests lock down existing behavior before refactoring. They capture "what the code currently does" rather than "what it should do" (that's for specification tests).

---

## Test Template

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('{{MODULE_NAME}} - Characterization Tests', () => {
  // Setup: Recreate the exact conditions under which behavior was observed
  beforeEach(() => {
    // {{SETUP_DESCRIPTION}}
  });

  afterEach(() => {
    // {{TEARDOWN_DESCRIPTION}}
  });

  describe('{{BEHAVIOR_CATEGORY_1}}', () => {
    it('{{BEHAVIOR_DESCRIPTION_1}}', () => {
      // Given: {{GIVEN_CONDITION}}
      const input = {{INPUT_VALUE}};
      const context = {{CONTEXT_VALUE}};

      // When: {{ACTION_TAKEN}}
      const result = {{FUNCTION_UNDER_TEST}}(input, context);

      // Then: {{EXPECTED_BEHAVIOR}}
      expect(result).toEqual({{EXPECTED_OUTPUT}});
    });

    it('handles edge case: {{EDGE_CASE_1}}', () => {
      // Given: {{EDGE_CASE_CONDITION}}
      const input = {{EDGE_INPUT}};

      // When: {{ACTION}}
      const result = {{FUNCTION}}(input);

      // Then: {{EDGE_EXPECTED_BEHAVIOR}}
      expect(result).toEqual({{EDGE_OUTPUT}});
    });
  });

  describe('{{BEHAVIOR_CATEGORY_2}}', () => {
    it('{{BEHAVIOR_DESCRIPTION_2}}', () => {
      // Given: {{GIVEN}}
      // When: {{WHEN}}
      // Then: {{THEN}}
    });
  });

  describe('Error conditions', () => {
    it('throws {{ERROR_TYPE}} when {{ERROR_CONDITION}}', () => {
      // Given: Invalid input
      const invalidInput = {{INVALID_INPUT}};

      // When/Then: Expect error
      expect(() => {{FUNCTION}}(invalidInput))
        .toThrow({{ERROR_MESSAGE}});
    });
  });

  describe('Side effects', () => {
    it('{{SIDE_EFFECT_DESCRIPTION}}', () => {
      // Given: Initial state
      const initialState = {{INITIAL_STATE}};

      // When: Action with side effect
      {{FUNCTION_WITH_SIDE_EFFECT}}({{INPUT}});

      // Then: State changed
      expect({{STATE_CHECK}}).toBe({{EXPECTED_STATE}});
    });
  });
});
```

---

## Example: User Validation

```typescript
import { describe, it, expect } from 'vitest';
import { validateUser } from './user-service';

describe('validateUser - Characterization Tests', () => {
  describe('Valid user scenarios', () => {
    it('returns true for user with all required fields', () => {
      // Given: Complete user object
      const user = {
        id: '123',
        name: 'John Doe',
        email: 'john@example.com',
        age: 30
      };

      // When: Validation is called
      const result = validateUser(user);

      // Then: Validation passes
      expect(result).toBe(true);
    });

    it('returns true for user with minimum age (18)', () => {
      // Given: User exactly at minimum age
      const user = {
        id: '456',
        name: 'Jane',
        email: 'jane@example.com',
        age: 18
      };

      // When: Validated
      const result = validateUser(user);

      // Then: Passes
      expect(result).toBe(true);
    });
  });

  describe('Invalid user scenarios', () => {
    it('returns false for user without email', () => {
      // Given: User missing email
      const user = {
        id: '789',
        name: 'Bob',
        age: 25
      };

      // When: Validated
      const result = validateUser(user);

      // Then: Fails
      expect(result).toBe(false);
    });

    it('returns false for user under minimum age', () => {
      // Given: User age 17
      const user = {
        id: '999',
        name: 'Alice',
        email: 'alice@example.com',
        age: 17
      };

      // When: Validated
      const result = validateUser(user);

      // Then: Fails
      expect(result).toBe(false);
    });
  });

  describe('Edge cases', () => {
    it('handles null input by returning false', () => {
      // Given: Null input
      const user = null;

      // When: Validated
      const result = validateUser(user);

      // Then: Fails gracefully
      expect(result).toBe(false);
    });

    it('handles undefined email as invalid', () => {
      // Given: User with undefined email
      const user = {
        id: '111',
        name: 'Charlie',
        email: undefined,
        age: 30
      };

      // When: Validated
      const result = validateUser(user);

      // Then: Fails
      expect(result).toBe(false);
    });

    it('accepts email without @ symbol (observing current behavior)', () => {
      // Given: Email without @
      const user = {
        id: '222',
        name: 'Dave',
        email: 'notanemail',
        age: 25
      };

      // When: Validated
      const result = validateUser(user);

      // Then: Currently passes (may be a bug, but characterizing actual behavior)
      expect(result).toBe(true);
      // TODO: After refactoring, consider adding proper email validation
    });
  });
});
```

---

## Guidelines for Writing Characterization Tests

### DO:
- ✅ Capture actual current behavior (even if it seems wrong)
- ✅ Test happy paths and edge cases
- ✅ Test error conditions
- ✅ Use descriptive test names
- ✅ Document surprising behavior with comments
- ✅ Use Given/When/Then structure

### DON'T:
- ❌ Change behavior while writing tests
- ❌ Skip edge cases
- ❌ Assume behavior without verifying
- ❌ Write tests that describe desired behavior (save that for specification tests)

### When in Doubt:
1. Run the code with various inputs
2. Observe what actually happens
3. Write test that captures that behavior
4. If behavior seems wrong, add a TODO comment

---

## Observation Worksheet

Use this to systematically capture behavior:

### Function Under Test: `{{FUNCTION_NAME}}`

**Input 1**: {{INPUT_1}}
**Output 1**: {{OUTPUT_1}}
**Notes**: {{NOTES_1}}

**Input 2**: {{INPUT_2}}
**Output 2**: {{OUTPUT_2}}
**Notes**: {{NOTES_2}}

**Input 3** (Edge Case): {{INPUT_3}}
**Output 3**: {{OUTPUT_3}}
**Notes**: {{NOTES_3}}

**Input 4** (Error Case): {{INPUT_4}}
**Output 4**: {{OUTPUT_4}}
**Notes**: {{NOTES_4}}

**Side Effects Observed**:
- {{SIDE_EFFECT_1}}
- {{SIDE_EFFECT_2}}

---

## Snapshot Testing for Complex Outputs

For complex objects or large outputs:

```typescript
it('generates expected report structure', () => {
  // Given: Sample data
  const data = getSampleData();

  // When: Report generated
  const report = generateReport(data);

  // Then: Matches snapshot
  expect(report).toMatchSnapshot();
});
```

**When to use snapshots**:
- Complex object structures
- HTML/UI output
- Large text outputs
- Configuration objects

**When NOT to use snapshots**:
- Simple boolean/number results
- When specific values matter (use explicit expects)
- Timestamps or random data (mock these first)

---

## Checklist for Characterization Test Completeness

- [ ] Happy path covered
- [ ] Edge cases identified and tested
- [ ] Error conditions tested
- [ ] Side effects captured
- [ ] Null/undefined handling tested
- [ ] Boundary values tested
- [ ] All test names are descriptive
- [ ] Given/When/Then structure used
- [ ] All tests pass with current implementation
- [ ] Surprising behavior documented with TODOs

---

## Integration with Refactoring

1. **Before refactoring**:
   - Write characterization tests
   - Ensure all tests pass (green)
   - Commit tests separately

2. **During refactoring**:
   - Keep tests unchanged
   - If test fails, behavior changed (usually unintended)
   - Tests act as safety net

3. **After refactoring**:
   - All characterization tests should still pass
   - May add new specification tests for improved behavior
   - May mark surprising behaviors as fixed (with TODO resolved)

---

## Example Commit Messages

```
test: add characterization tests for UserService validation

- Capture current validation behavior before refactoring
- Cover happy paths, edge cases, and error conditions
- Note: Email validation currently allows invalid formats (TODO)

Tests: 15 new tests, all pass ✅
```

---

## References

- Michael Feathers - "Working Effectively with Legacy Code" (Chapter 13)
- Martin Fowler - "Refactoring" (Chapter 4: Building Tests)
