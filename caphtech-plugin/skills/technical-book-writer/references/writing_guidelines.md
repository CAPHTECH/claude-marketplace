# Technical Writing Guidelines

Comprehensive best practices for writing high-quality technical books that are clear, accurate, and reader-focused.

## Table of Contents

1. [Chapter Structure](#chapter-structure)
2. [Content Depth](#content-depth)
3. [Reader Focus](#reader-focus)
4. [Technical Accuracy](#technical-accuracy)
5. [Clarity and Readability](#clarity-and-readability)
6. [Examples and Illustrations](#examples-and-illustrations)
7. [Review Checklist](#review-checklist)

## Chapter Structure

### Essential Components

Every chapter should include:

1. **Introduction**
   - Chapter objectives - What will readers learn?
   - Prerequisites - What should readers know beforehand?
   - Context - How does this chapter fit into the bigger picture?

2. **Main Content**
   - Conceptual explanations before code
   - Progressive disclosure - simple to complex
   - Clear section headings that guide the reader
   - Transitions between sections

3. **Code Examples**
   - Relevant, realistic examples
   - Incremental complexity
   - Explanations before and after code
   - Clear connection to concepts

4. **Summary**
   - Key takeaways (3-5 bullet points)
   - What readers should now be able to do
   - Preview of next chapter (optional)

5. **Additional Resources** (optional)
   - Further reading
   - Exercises or challenges
   - Common pitfalls to avoid

### Section Hierarchy

Use heading levels consistently:
- `#` - Chapter title
- `##` - Major sections
- `###` - Subsections
- `####` - Rarely needed, use sparingly

Avoid going deeper than `####` - if needed, consider restructuring.

## Content Depth

### Calibrating Depth

**Too shallow:**
- "Call this function to get the result"
- No explanation of *why* or *when*
- Missing context or trade-offs

**Appropriate depth:**
- Explain the concept first
- Show how to use it with code
- Discuss when to use it and alternatives
- Mention common pitfalls or edge cases

**Too deep:**
- Implementation details not relevant to readers
- Tangential topics that distract from main point
- Over-explanation of obvious concepts

### The 80/20 Rule

Focus on the 20% of features/concepts that readers will use 80% of the time. Cover edge cases and advanced topics only when necessary for completeness.

### Progressive Disclosure

Start with the simplest version, then build up:

1. **Minimal example** - Shows core concept
2. **Practical example** - Realistic use case
3. **Advanced example** - Edge cases, optimizations (if relevant)

## Reader Focus

### Know Your Audience

Define your target reader:
- What's their experience level?
- What are they trying to achieve?
- What background knowledge can you assume?

### Reader-Centered Language

**Instead of:**
- "This library provides..."
- "The system works by..."
- "Feature X does Y..."

**Use:**
- "You can use this library to..."
- "You'll learn how to..."
- "This will help you..."

### Learning Objectives

Each chapter should answer:
- What can I build after reading this?
- What problems can I solve?
- How does this relate to my goals?

## Technical Accuracy

### Verification Checklist

Before publishing, verify:

1. **Code examples**
   - All code runs without errors
   - Versions are specified (libraries, languages, tools)
   - Dependencies are listed
   - Environment setup is documented

2. **Technical explanations**
   - Concepts are explained correctly
   - No oversimplification that leads to misconceptions
   - Terminology is used consistently and correctly
   - References to APIs/docs are current

3. **Claims and statements**
   - Performance claims are backed by evidence
   - "Best practices" are actually best practices
   - Comparisons with alternatives are fair

### Avoiding Common Errors

- **Version drift** - Update examples when libraries change
- **Platform assumptions** - Specify OS/environment requirements
- **Copy-paste errors** - Test every code snippet
- **Outdated screenshots** - Update UI images when interfaces change

## Clarity and Readability

### Writing Style

**Be concise:**
- Remove unnecessary words
- Use active voice ("You can call the function" not "The function can be called")
- Short sentences are better than long ones

**Be specific:**
- "The request takes 200ms" not "The request is fast"
- "Supports 10,000 concurrent users" not "Handles lots of users"
- "Uses SHA-256" not "Uses secure hashing"

**Be consistent:**
- Use the same terms throughout (e.g., "function" vs "method")
- Follow the same code style in all examples
- Maintain consistent formatting

### Paragraph Structure

- One main idea per paragraph
- First sentence states the main point
- 3-5 sentences is ideal
- Use bullet points for lists

### Transitions

Guide readers between topics:
- "Now that we've covered X, let's look at Y..."
- "Before we dive into implementation, let's understand..."
- "This approach works well for simple cases, but for complex scenarios..."

## Examples and Illustrations

### Code Examples

**Characteristics of good examples:**
- **Minimal** - Only includes what's necessary to illustrate the concept
- **Complete** - Can be run without missing pieces
- **Realistic** - Resembles real-world usage, not toy examples
- **Clear** - Well-formatted, commented appropriately
- **Incremental** - Builds on previous examples

**Example structure:**
1. **Context** - Explain what the example demonstrates
2. **Code** - Show the implementation
3. **Explanation** - Walk through key parts
4. **Output** - Show expected results (if applicable)
5. **Variations** - Discuss alternatives or common modifications

### Diagrams and Visuals

Use visuals when:
- Architecture needs illustration
- Concepts have spatial relationships
- Process flows need clarification
- Comparisons benefit from side-by-side views

Types of visuals:
- **Architecture diagrams** - System components and relationships
- **Sequence diagrams** - Interaction flows over time
- **Flowcharts** - Decision trees and process flows
- **Data flow diagrams** - How data moves through the system
- **Screenshots** - UI elements, tool interfaces

### Analogies and Metaphors

Use analogies to explain complex concepts:
- Make sure the analogy is simpler than the concept
- Acknowledge where the analogy breaks down
- Don't overextend analogies

## Review Checklist

Before finalizing a chapter:

### Content Review
- [ ] Chapter objectives are clear and met
- [ ] Prerequisites are listed
- [ ] Concepts are explained before code
- [ ] Examples are complete and tested
- [ ] Summary captures key takeaways
- [ ] Terminology is consistent
- [ ] Cross-references are valid

### Code Review
- [ ] All code examples run without errors
- [ ] Dependencies and versions are specified
- [ ] Code follows consistent style
- [ ] Comments explain non-obvious parts
- [ ] Variable names are meaningful
- [ ] Error handling is shown where appropriate

### Readability Review
- [ ] Sentences are clear and concise
- [ ] Paragraphs have single focus
- [ ] Headings guide the reader
- [ ] Transitions connect sections
- [ ] Active voice is used
- [ ] Technical jargon is explained

### Accuracy Review
- [ ] Technical explanations are correct
- [ ] API references are current
- [ ] Performance claims are verified
- [ ] Best practices are sound
- [ ] No broken links
- [ ] Screenshots are up-to-date

### Reader Focus Review
- [ ] Learning objectives are clear
- [ ] Content matches reader's level
- [ ] Practical value is evident
- [ ] Examples are realistic
- [ ] Common pitfalls are addressed
- [ ] Next steps are suggested
