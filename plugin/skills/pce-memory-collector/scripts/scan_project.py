#!/usr/bin/env python3
"""Scan project structure and output key files for pce-memory collection."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List

# Key files to look for (prioritized)
KEY_FILES = [
    # Project metadata
    "package.json", "Cargo.toml", "pyproject.toml", "go.mod",
    "pom.xml", "build.gradle", "composer.json", "Gemfile",
    # Config
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "tsconfig.json", "webpack.config.js", "vite.config.ts",
    # Documentation
    "README.md", "CLAUDE.md", "CONTRIBUTING.md",
    # Skills
    "SKILL.md",
]

# Directories to scan for specific patterns
SCAN_PATTERNS = {
    "skills": ["**/SKILL.md"],
    "config": ["**/*.config.js", "**/*.config.ts", "**/config/**"],
    "api": ["**/api/**", "**/routes/**", "**/endpoints/**"],
}

# Ignore patterns
IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
               "dist", "build", ".next", "target", ".kiri"}


def compute_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"
    except Exception:
        return ""


def scan_project(project_path: str) -> Dict:
    """Scan project and return structured information."""
    root = Path(project_path).resolve()

    result = {
        "project_root": str(root),
        "key_files": [],
        "structure": {},
        "categories": {
            "project-info": [],
            "architecture": [],
            "dependencies": [],
            "config": [],
            "documentation": [],
        }
    }

    # Find key files
    for key_file in KEY_FILES:
        file_path = root / key_file
        if file_path.exists():
            info = {
                "path": str(file_path.relative_to(root)),
                "hash": compute_hash(file_path),
                "size": file_path.stat().st_size,
            }
            result["key_files"].append(info)

            # Categorize
            if "package.json" in key_file or "Cargo.toml" in key_file:
                result["categories"]["project-info"].append(info["path"])
                result["categories"]["dependencies"].append(info["path"])
            elif "config" in key_file.lower():
                result["categories"]["config"].append(info["path"])
            elif ".md" in key_file:
                result["categories"]["documentation"].append(info["path"])

    # Scan directory structure (top 2 levels)
    for item in sorted(root.iterdir()):
        if item.name in IGNORE_DIRS or item.name.startswith("."):
            continue

        if item.is_dir():
            subdir_files = []
            try:
                for subitem in sorted(item.iterdir())[:10]:  # Limit
                    if subitem.name not in IGNORE_DIRS:
                        subdir_files.append(subitem.name)
            except PermissionError:
                pass
            result["structure"][item.name] = subdir_files
        else:
            result["structure"][item.name] = "file"

    return result


def main():
    parser = argparse.ArgumentParser(description="Scan project for pce-memory collection")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = scan_project(args.project_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Project: {result['project_root']}\n")

        print("Key Files:")
        for f in result["key_files"]:
            print(f"  - {f['path']} ({f['size']} bytes)")

        print("\nStructure:")
        for name, contents in result["structure"].items():
            if contents == "file":
                print(f"  {name}")
            else:
                print(f"  {name}/")
                for item in contents[:5]:
                    print(f"    - {item}")

        print("\nCategories:")
        for cat, files in result["categories"].items():
            if files:
                print(f"  {cat}: {', '.join(files)}")


if __name__ == "__main__":
    main()
