# Markdown Conventions

Markdown formatting guidelines for consistent, professional technical book content.

## Table of Contents

1. [Headings](#headings)
2. [Code Blocks](#code-blocks)
3. [Inline Code](#inline-code)
4. [Links](#links)
5. [Images](#images)
6. [Lists](#lists)
7. [Tables](#tables)
8. [Emphasis](#emphasis)
9. [Blockquotes](#blockquotes)
10. [Special Formatting](#special-formatting)

## Headings

### Hierarchy

Use ATX-style headings (`#` prefix):

```markdown
# Chapter Title (H1)
## Major Section (H2)
### Subsection (H3)
#### Minor Subsection (H4)
```

**Rules:**
- One H1 per file (chapter title)
- Don't skip levels (no H1 → H3)
- Keep headings concise (< 60 characters)
- Use sentence case, not title case
- No period at the end

**❌ Avoid:**
```markdown
# This Is A Very Long Chapter Title That Goes On And On
### Subsection (skipped H2)
## Section.
```

**✅ Correct:**
```markdown
# Introduction to async programming
## Understanding the event loop
### How callbacks work
```

### Heading IDs

Use explicit IDs for important sections:

```markdown
## Configuration {#config}
### Environment variables {#env-vars}
```

This allows stable cross-references even if heading text changes.

## Code Blocks

### Fenced Code Blocks

Always specify the language:

````markdown
```python
def hello():
    print("Hello, World!")
```
````

**Supported languages:**
- `python`, `javascript`, `typescript`, `java`, `go`, `rust`
- `html`, `css`, `json`, `yaml`, `xml`
- `bash`, `shell`, `sql`, `markdown`

### Code Block Formatting

**DO:**
- Specify language for syntax highlighting
- Keep examples under 30 lines when possible
- Include necessary imports
- Use proper indentation

**DON'T:**
- Use generic `code` or leave language blank
- Include line numbers (unless required by publisher)
- Mix tabs and spaces

### Highlighting Specific Lines

Some markdown processors support line highlighting:

````markdown
```python {3,5-7}
def process_data(data):
    # Validate input
    if not data:  # Line 3 highlighted
        return None
    # Process lines 5-7 highlighted
    result = transform(data)
    return result
```
````

### File Names and Context

Include file name or context above code block:

````markdown
**`src/utils.py`**
```python
def calculate_total(items):
    return sum(item.price for item in items)
```
````

Or as a comment:

````markdown
```python
# File: src/utils.py

def calculate_total(items):
    return sum(item.price for item in items)
```
````

## Inline Code

Use backticks for inline code:

```markdown
The `calculate_total()` function returns a `float` value.
Use the `--verbose` flag to enable debug output.
```

**When to use inline code:**
- Function names: `fetch_data()`
- Variable names: `user_id`
- Class names: `DatabaseConnection`
- File names: `config.yaml`
- Command-line flags: `--help`
- Short code snippets: `x = 10`
- API endpoints: `/api/users`

**When NOT to use:**
- Regular words that happen to be code-related
- Emphasis (use *italics* or **bold** instead)

## Links

### Internal Links

Link to other chapters or sections:

```markdown
See [Chapter 3](chapter3.md) for more details.
Refer to the [configuration section](#configuration).
```

### External Links

```markdown
Check the [official documentation](https://example.com/docs).
```

**Best practices:**
- Use descriptive link text (not "click here")
- Verify links before publishing
- Consider using reference-style links for readability

### Reference-Style Links

For better readability in long documents:

```markdown
The [official guide][guide] provides more examples.
See the [API reference][api] for details.

[guide]: https://example.com/guide
[api]: https://example.com/api
```

### Link Formatting

**✅ Good:**
```markdown
Read the [Python documentation](https://docs.python.org) for more info.
```

**❌ Avoid:**
```markdown
Click [here](https://docs.python.org).
For more info visit https://docs.python.org.
```

## Images

### Basic Syntax

```markdown
![Alt text](path/to/image.png)
![Architecture diagram](images/architecture.png)
```

### With Captions

```markdown
![User dashboard](images/dashboard.png)

*Figure 1: The main user dashboard showing recent activity*
```

### Image Organization

Organize images by chapter:

```
book/
├── chapter1/
│   ├── chapter1.md
│   └── images/
│       ├── diagram1.png
│       └── screenshot1.png
├── chapter2/
│   ├── chapter2.md
│   └── images/
│       └── flowchart.png
```

Reference with relative paths:

```markdown
![Data flow](images/flowchart.png)
```

### Image Best Practices

- Use descriptive alt text for accessibility
- Keep images under 1MB
- Use PNG for screenshots and diagrams
- Use JPG for photos
- Use SVG for vector graphics when possible
- Include captions for complex diagrams

## Lists

### Unordered Lists

Use `-` for consistency:

```markdown
- First item
- Second item
  - Nested item
  - Another nested item
- Third item
```

**Don't mix:**
```markdown
- Item
* Item  ❌ Don't mix - and *
+ Item  ❌ Don't mix - and +
```

### Ordered Lists

```markdown
1. First step
2. Second step
3. Third step
   1. Sub-step
   2. Another sub-step
4. Fourth step
```

**Tip:** Use `1.` for all items - markdown will auto-number:

```markdown
1. First
1. Second
1. Third
```

This makes reordering easier.

### Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

### List Formatting

**DO:**
- Use consistent bullet style (- preferred)
- Add blank lines between list items if they're long
- Indent nested items with 2 spaces
- Capitalize first word of each item
- Use periods if items are complete sentences

**Example:**
```markdown
- **Installation**: Download and install the package.
- **Configuration**: Edit the config file with your settings.
- **Testing**: Run the test suite to verify installation.
```

## Tables

### Basic Table

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

### Alignment

```markdown
| Left-aligned | Center-aligned | Right-aligned |
|:-------------|:--------------:|--------------:|
| Text         | Text           | 123           |
| More text    | More text      | 456           |
```

### Table Best Practices

- Keep tables simple (< 5 columns ideal)
- Use tables for tabular data, not layout
- Include header row
- Align columns for readability in source
- Consider alternatives for complex data

**When tables get too complex, consider:**
- Breaking into multiple tables
- Using a different format (code block, list)
- Creating a diagram

## Emphasis

### Italic

Use single asterisks or underscores:

```markdown
*emphasis* or _emphasis_
```

**When to use:**
- Introducing new terms
- Slight emphasis
- Book/article titles

### Bold

Use double asterisks:

```markdown
**strong emphasis**
```

**When to use:**
- Important points
- Warnings
- Key terms

### Bold + Italic

```markdown
***very strong emphasis***
```

Use sparingly - usually bold or italic alone is sufficient.

### Formatting Combinations

```markdown
**Important**: The `config.yaml` file *must* be in the root directory.
```

## Blockquotes

### Basic Blockquote

```markdown
> This is a quote or important note.
> It can span multiple lines.
```

### Nested Blockquotes

```markdown
> First level
>> Second level
>>> Third level
```

### Blockquote Usage

**Use for:**
- Important notes or warnings
- Quotes from other sources
- Callout boxes

**Styled callouts** (if supported):

```markdown
> **Note**: This is an informational note.

> **Warning**: This action cannot be undone.

> **Tip**: Use keyboard shortcuts to speed up your workflow.
```

## Special Formatting

### Horizontal Rules

Use three or more dashes:

```markdown
---
```

**When to use:**
- Separate major sections
- Before/after important content
- Between chapters (in multi-chapter files)

### Line Breaks

Two spaces at end of line, or use `<br>`:

```markdown
First line
Second line

Or:

First line<br>
Second line
```

### Escaping Characters

Use backslash to escape markdown characters:

```markdown
\*Not italic\*
\[Not a link\]
\`Not code\`
```

### HTML in Markdown

Use sparingly, only when markdown is insufficient:

```markdown
<details>
<summary>Click to expand</summary>

Hidden content here.

</details>
```

### Comments

```markdown
<!-- This is a comment, not visible in output -->
```

**Use for:**
- Notes to yourself or editors
- Temporarily hiding content
- Metadata

## Consistency Checklist

- [ ] Headings use ATX style (`#`)
- [ ] Code blocks specify language
- [ ] Lists use consistent bullet style (-)
- [ ] Links use descriptive text
- [ ] Images have alt text
- [ ] Emphasis uses asterisks, not underscores
- [ ] One blank line between paragraphs
- [ ] No trailing whitespace
- [ ] Files end with newline
- [ ] Consistent capitalization in headings

## Markdown Linting

Consider using a markdown linter:
- `markdownlint` - Checks formatting rules
- `remark-lint` - Configurable markdown linter
- `vale` - Prose linter for style and grammar

**Example `.markdownlint.json` config:**
```json
{
  "MD013": { "line_length": 100 },
  "MD033": false,
  "MD041": false
}
```

## Summary

Consistent markdown formatting:
- Improves readability in source files
- Ensures professional output
- Makes collaboration easier
- Enables automated validation
- Simplifies conversion to other formats
