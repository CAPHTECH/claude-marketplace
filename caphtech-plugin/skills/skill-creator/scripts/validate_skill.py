#!/usr/bin/env python3
"""
Skill Validator for Claude Code skills.

Validates SKILL.md structure, frontmatter fields, and common issues.

Usage:
    python3 validate_skill.py <skill-directory>
"""

import re
import sys
from pathlib import Path

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES = 500

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "context",
    "agent",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "model",
    "argument-hint",
    "hooks",
}


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter without external dependencies."""
    if not content.startswith("---"):
        return None, "No YAML frontmatter found (must start with ---)"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format (missing closing ---)"

    frontmatter_text = match.group(1)
    result = {}

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        result[key] = value

    return result, ""


def validate_skill(skill_path: str) -> list[str]:
    """Validate a skill directory. Returns list of issues (empty = valid)."""
    issues = []
    skill_dir = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"]

    content = skill_md.read_text()

    # Parse frontmatter
    frontmatter, error = parse_frontmatter(content)
    if frontmatter is None:
        return [f"Frontmatter error: {error}"]

    # Check required fields
    if "name" not in frontmatter:
        issues.append("Missing required field: name")
    if "description" not in frontmatter:
        issues.append("Missing required field: description")

    # Validate name
    name = frontmatter.get("name", "")
    if name:
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", name):
            issues.append(
                f"Name '{name}' must be kebab-case "
                "(lowercase letters, digits, hyphens; no leading/trailing hyphens)"
            )
        if "--" in name:
            issues.append(f"Name '{name}' contains consecutive hyphens")
        if len(name) > MAX_NAME_LENGTH:
            issues.append(
                f"Name is too long ({len(name)} chars, max {MAX_NAME_LENGTH})"
            )
        if name != skill_dir.name:
            issues.append(
                f"Name '{name}' does not match directory name '{skill_dir.name}'"
            )

    # Validate description
    description = frontmatter.get("description", "")
    if description:
        if "<" in description or ">" in description:
            issues.append("Description contains XML tags (< or >)")
        if len(description) > MAX_DESCRIPTION_LENGTH:
            issues.append(
                f"Description too long ({len(description)} chars, max {MAX_DESCRIPTION_LENGTH})"
            )
        if description.startswith("|") or description.startswith(">"):
            issues.append(
                "Description appears to use YAML multiline (| or >). Use single line."
            )
        if "TODO" in description:
            issues.append("Description contains TODO placeholder")

    # Check for unexpected frontmatter keys
    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        issues.append(
            f"Unexpected frontmatter keys: {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    # Validate context field
    context = frontmatter.get("context", "")
    if context and context != "fork":
        issues.append(f"Invalid context value '{context}'. Only 'fork' is supported.")

    # Validate agent without context: fork
    if "agent" in frontmatter and frontmatter.get("context") != "fork":
        issues.append("'agent' requires 'context: fork'")

    # Check body line count
    body_start = content.find("---", 3)
    if body_start != -1:
        body = content[body_start + 3 :].strip()
        body_lines = body.count("\n") + 1
        if body_lines > MAX_BODY_LINES:
            issues.append(
                f"SKILL.md body is {body_lines} lines (recommended max: {MAX_BODY_LINES}). "
                "Consider moving content to references/."
            )

    # Check references/ links
    references_dir = skill_dir / "references"
    if references_dir.exists():
        ref_files = set(f.name for f in references_dir.iterdir() if f.is_file())
        linked_refs = set(re.findall(r"references/([^\s)\]]+)", content))
        unlinked = ref_files - linked_refs
        if unlinked:
            issues.append(
                f"Reference files not linked from SKILL.md: {', '.join(sorted(unlinked))}"
            )

    # Check for common anti-patterns
    unwanted_files = ["README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"]
    for f in unwanted_files:
        if (skill_dir / f).exists():
            issues.append(f"Unnecessary file found: {f}")

    return issues


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_skill.py <skill-directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    if not Path(skill_path).is_dir():
        print(f"[ERROR] Not a directory: {skill_path}")
        sys.exit(1)

    issues = validate_skill(skill_path)

    if not issues:
        print("[OK] Skill is valid!")
        sys.exit(0)
    else:
        print(f"[ISSUES] Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
