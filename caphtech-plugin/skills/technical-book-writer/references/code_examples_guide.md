# Code Examples Guide

Standards and best practices for writing, testing, and maintaining code examples in technical books.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Example Structure](#example-structure)
3. [Naming Conventions](#naming-conventions)
4. [Comments and Documentation](#comments-and-documentation)
5. [Testing and Validation](#testing-and-validation)
6. [Integration with Text](#integration-with-text)
7. [Language-Specific Guidelines](#language-specific-guidelines)

## Core Principles

### 1. Examples Must Run

**Every code example must be:**
- Syntactically correct
- Runnable without errors
- Tested in the actual environment
- Updated when dependencies change

**Never include:**
- Pseudo-code presented as real code
- Incomplete code without clear indication
- Examples that "should work" but haven't been tested

### 2. Examples Should Be Minimal

Include only what's necessary to demonstrate the concept:

**❌ Too much code:**
```python
# 50 lines of boilerplate
# Obscures the actual concept
# Readers get lost in details
```

**✅ Minimal example:**
```python
# 5-10 lines showing the core concept
# Clear and focused
# Easy to understand
```

### 3. Examples Should Be Realistic

**Avoid toy examples:**
```python
def add(a, b):
    return a + b  # Too trivial
```

**Use realistic scenarios:**
```python
def calculate_discount(price, discount_percentage, member_tier):
    """Calculate final price with tier-based discounts."""
    base_discount = price * (discount_percentage / 100)
    tier_bonus = TIER_BONUSES.get(member_tier, 0)
    return price - base_discount - tier_bonus
```

### 4. Examples Should Be Progressive

Build from simple to complex:

1. **First example**: Minimal, shows basic usage
2. **Second example**: Adds real-world context
3. **Third example**: Handles edge cases or advanced scenarios

## Example Structure

### Complete Examples

When showing a complete example, include all necessary parts:

```python
# 1. Imports
import requests
from typing import Dict, Optional

# 2. Constants or configuration
API_BASE_URL = "https://api.example.com"
TIMEOUT = 30

# 3. Main code
def fetch_user_data(user_id: int) -> Optional[Dict]:
    """Fetch user data from the API.

    Args:
        user_id: The user's unique identifier

    Returns:
        User data dictionary or None if not found
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/{user_id}",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching user {user_id}: {e}")
        return None

# 4. Usage example (if helpful)
if __name__ == "__main__":
    user = fetch_user_data(123)
    print(user)
```

### Partial Examples (Snippets)

When showing only part of the code, make it clear:

```python
# Inside the UserService class:

def authenticate(self, username: str, password: str) -> bool:
    """Authenticate user credentials."""
    # ... (implementation details omitted for brevity)
    return is_valid
```

Use comments like:
- `# ... (rest of the code)`
- `# ... (implementation details omitted)`
- `# Earlier in the file:`
- `# This goes inside the __init__ method:`

## Naming Conventions

### Variables and Functions

Use meaningful, descriptive names:

**❌ Poor names:**
```python
def proc(d):
    x = d * 0.1
    return d - x
```

**✅ Good names:**
```python
def apply_discount(price):
    discount_amount = price * 0.1
    final_price = price - discount_amount
    return final_price
```

### Consistency Across Examples

Use consistent naming throughout the book:
- If you use `user_id` in chapter 1, don't switch to `userId` in chapter 3
- If you use `fetch_data()`, don't switch to `getData()` later
- Maintain consistent variable names for similar concepts

### Example Data

Use realistic but generic example data:

**✅ Good:**
```python
user = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "age": 28
}
```

**❌ Avoid:**
```python
user = {
    "name": "John Doe",  # Overused
    "email": "test@test.com",  # Not realistic
    "age": 999  # Not realistic
}
```

## Comments and Documentation

### When to Comment

**DO comment:**
- Non-obvious logic
- Important design decisions
- Edge cases and gotchas
- Parameters and return values (docstrings)
- Why code is written a certain way

**DON'T comment:**
- Obvious code (`i += 1  # increment i`)
- What the code does (code should be self-explanatory)
- Redundant explanations

### Comment Style

**Inline comments** - Explain specific lines:
```python
# Calculate hash using SHA-256 for security compliance
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

**Block comments** - Explain sections:
```python
# Validate user input before processing
# This prevents SQL injection and ensures data integrity
if not validate_input(user_input):
    raise ValueError("Invalid input")
```

**Docstrings** - Document functions/classes:
```python
def calculate_total(items: List[Item], tax_rate: float) -> float:
    """Calculate total price including tax.

    Args:
        items: List of items to calculate total for
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If tax_rate is negative
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax
```

## Testing and Validation

### Making Examples Testable

Structure code to be easily testable:

**❌ Hard to test:**
```python
# Tightly coupled, uses global state
def process():
    data = GLOBAL_DATA
    result = complex_operation(data)
    GLOBAL_STATE = result
    print(result)  # Side effect
```

**✅ Easy to test:**
```python
# Pure function, testable
def process(data: List[int]) -> List[int]:
    """Process data and return result."""
    return [x * 2 for x in data if x > 0]

# Can be tested:
assert process([1, -2, 3]) == [2, 6]
```

### Validation Workflow

1. **Write code** - Create the example
2. **Extract** - Use `extract_code_blocks.py` to extract code
3. **Test** - Run the extracted code
4. **Validate** - Use `validate_code_examples.py` for syntax checking
5. **Update** - Fix any issues
6. **Re-test** - Verify fixes work

### Test Markers

If examples require specific setup, mark them:

```python
# Requires: API_KEY environment variable
# Requires: Docker running
# Requires: test_data.csv in same directory

def example_function():
    # ...
```

## Integration with Text

### Before Code

Introduce the example:
- What problem does it solve?
- What concept does it demonstrate?
- What should readers pay attention to?

**Example:**
> The following example shows how to implement retry logic with exponential backoff. Notice how we use the `time.sleep()` function with increasing delays:

### After Code

Explain the code:
- Walk through key parts
- Highlight important patterns
- Discuss alternatives or trade-offs

**Example:**
> In this implementation, we start with a 1-second delay and double it after each retry, up to a maximum of 5 attempts. This prevents overwhelming the server while still retrying transient failures.

### Inline Highlights

Reference specific lines in your explanation:

> On line 3, we initialize the `retry_count` variable to track how many attempts we've made...

Or use comments in code:

```python
retry_count = 0  # Track number of retry attempts
max_retries = 5  # Limit retries to prevent infinite loops
```

## Language-Specific Guidelines

### Python

- Follow PEP 8 style guide
- Use type hints for function signatures
- Include docstrings for functions/classes
- Use meaningful variable names (snake_case)
- Prefer list comprehensions when clear

### JavaScript/TypeScript

- Use `const` and `let`, not `var`
- Use arrow functions for callbacks
- Include JSDoc comments for TypeScript
- Use async/await instead of raw promises
- Follow consistent naming (camelCase)

### Go

- Follow Go conventions (gofmt)
- Include error handling in examples
- Use descriptive variable names
- Show defer usage where appropriate
- Include package and imports

### Java

- Follow Java naming conventions
- Include access modifiers
- Show proper exception handling
- Use generics where appropriate
- Include package declarations

### General Guidelines

For all languages:
1. Follow the language's official style guide
2. Use the most modern, idiomatic syntax
3. Show error handling appropriately
4. Include necessary imports/dependencies
5. Make code runnable (or clearly mark if not)

## Common Pitfalls

### 1. Hardcoded Paths

**❌ Avoid:**
```python
with open("/Users/alice/data.csv") as f:  # Won't work for others
```

**✅ Better:**
```python
from pathlib import Path

data_path = Path(__file__).parent / "data.csv"
with open(data_path) as f:
```

### 2. Missing Error Handling

Show error handling in realistic examples:

```python
try:
    result = risky_operation()
except SpecificError as e:
    # Handle gracefully
    logging.error(f"Operation failed: {e}")
    return None
```

### 3. Unclear Dependencies

Always specify:
- Library versions
- Required packages
- Environment variables
- External services needed

### 4. Copy-Paste Errors

Common issues:
- Old function names not updated
- Variable names inconsistent
- Missing imports
- Outdated API calls

**Prevention:** Extract and test all code examples regularly.

## Summary

Good code examples are:
- **Correct** - Syntactically valid and tested
- **Clear** - Easy to read and understand
- **Concise** - Minimal but complete
- **Realistic** - Represent real-world usage
- **Consistent** - Follow same patterns throughout
- **Documented** - Include necessary comments
- **Testable** - Can be extracted and run
