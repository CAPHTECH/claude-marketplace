# Refactoring Executor Scripts

## Overview

This directory contains utility scripts for automated refactoring execution.

## Scripts

### parse-report.ts
Parses refactoring discovery reports and extracts actionable issues.

**Usage**:
```bash
pnpm tsx scripts/parse-report.ts <report-file.md>
```

**Output**: JSON with prioritized issues

### ts-morph-refactors.ts
AST-based refactoring helpers using ts-morph.

**Functions**:
- `extractMethod()` - Extract code block to new method
- `extractClass()` - Extract class responsibilities
- `moveMethod()` - Move method to different class
- `renameSymbol()` - Rename symbol across project

**Usage**:
```typescript
import { extractMethod } from './ts-morph-refactors';

extractMethod('src/user/service.ts', 15, 25, 'validateUser');
```

### verify-step.sh
Automated verification script for each refactoring step.

**Usage**:
```bash
./scripts/verify-step.sh "step-1-extract-validator"
```

**Checks**:
- Tests pass
- Type check passes
- Lint passes
- Build succeeds

**Auto-rollback**: If any check fails

## Installation

```bash
pnpm add -D ts-morph ts-node
```

## Examples

See `references/tooling-playbook.md` for detailed usage examples.
