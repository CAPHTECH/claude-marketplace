#!/usr/bin/env bash
# Skill Initializer - Creates a new skill directory with template SKILL.md
#
# Usage:
#   init_skill.sh <skill-name> <output-directory> [--references] [--scripts] [--assets]
#
# Examples:
#   init_skill.sh my-skill ./skills
#   init_skill.sh my-skill ./skills --references --scripts

set -euo pipefail

MAX_NAME_LENGTH=64

usage() {
  echo "Usage: $0 <skill-name> <output-directory> [--references] [--scripts] [--assets]"
  echo ""
  echo "Arguments:"
  echo "  skill-name        Skill name (lowercase, digits, hyphens only)"
  echo "  output-directory   Directory where the skill folder will be created"
  echo ""
  echo "Options:"
  echo "  --references      Create references/ directory"
  echo "  --scripts         Create scripts/ directory"
  echo "  --assets          Create assets/ directory"
  exit 1
}

normalize_name() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//'
}

title_case() {
  echo "$1" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1'
}

# Parse arguments
if [ $# -lt 2 ]; then
  usage
fi

RAW_NAME="$1"
OUTPUT_DIR="$2"
shift 2

CREATE_REFERENCES=false
CREATE_SCRIPTS=false
CREATE_ASSETS=false

while [ $# -gt 0 ]; do
  case "$1" in
    --references) CREATE_REFERENCES=true ;;
    --scripts)    CREATE_SCRIPTS=true ;;
    --assets)     CREATE_ASSETS=true ;;
    *) echo "[ERROR] Unknown option: $1"; usage ;;
  esac
  shift
done

# Normalize name
SKILL_NAME=$(normalize_name "$RAW_NAME")

if [ -z "$SKILL_NAME" ]; then
  echo "[ERROR] Skill name must include at least one letter or digit."
  exit 1
fi

if [ ${#SKILL_NAME} -gt $MAX_NAME_LENGTH ]; then
  echo "[ERROR] Skill name '$SKILL_NAME' is too long (${#SKILL_NAME} chars). Max: $MAX_NAME_LENGTH."
  exit 1
fi

if [ "$SKILL_NAME" != "$RAW_NAME" ]; then
  echo "Note: Normalized skill name from '$RAW_NAME' to '$SKILL_NAME'."
fi

SKILL_DIR="$OUTPUT_DIR/$SKILL_NAME"
SKILL_TITLE=$(title_case "$SKILL_NAME")

# Check existing
if [ -d "$SKILL_DIR" ]; then
  echo "[ERROR] Directory already exists: $SKILL_DIR"
  exit 1
fi

# Create directory
mkdir -p "$SKILL_DIR"
echo "[OK] Created directory: $SKILL_DIR"

# Create SKILL.md
cat > "$SKILL_DIR/SKILL.md" << TEMPLATE
---
name: ${SKILL_NAME}
description: TODO - What this skill does and when to use it. Include trigger phrases.
---

# ${SKILL_TITLE}

## Overview

TODO: 1-2 sentences explaining what this skill enables.

## Workflow

TODO: Choose structure (Workflow/Task/Reference/Capability) and implement.

See skill-creator's references/progressive-disclosure.md for patterns.
TEMPLATE
echo "[OK] Created SKILL.md"

# Create resource directories
if $CREATE_REFERENCES; then
  mkdir -p "$SKILL_DIR/references"
  echo "[OK] Created references/"
fi

if $CREATE_SCRIPTS; then
  mkdir -p "$SKILL_DIR/scripts"
  echo "[OK] Created scripts/"
fi

if $CREATE_ASSETS; then
  mkdir -p "$SKILL_DIR/assets"
  echo "[OK] Created assets/"
fi

echo ""
echo "[OK] Skill '$SKILL_NAME' initialized at $SKILL_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit SKILL.md: complete description and body"
echo "  2. Add resources to references/, scripts/, assets/ as needed"
echo "  3. Run validate_skill.py to check structure"
