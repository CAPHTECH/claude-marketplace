#!/usr/bin/env python3
"""Collect design artifacts for consistency checking.

Scans a project directory and outputs a JSON manifest of:
- Design documents (docs/*.md)
- Schema files (schemas/**/*.json, migrations/*.sql)
- WIT/IDL interface files (wit/*.wit)
- Source files with invariant markers (LAW-*, TERM-*)
- Test files

Usage:
    python3 collect_artifacts.py <project_root> [--output manifest.json]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def find_files(root: Path, patterns: list[str], exclude_dirs: list[str] = None) -> list[str]:
    exclude = set(exclude_dirs or ["target", "node_modules", ".git", "vendor"])
    results = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if any(ex in path.parts for ex in exclude):
                continue
            results.append(str(path.relative_to(root)))
    return sorted(set(results))


def extract_invariants(root: Path, source_files: list[str]) -> list[dict]:
    """Extract LAW-*, TERM-*, invariant markers from source and doc files."""
    invariants = []
    pattern = re.compile(r"(LAW-[A-Z]+-\d+|TERM-[A-Z]+-\w+)")
    for fpath in source_files:
        full = root / fpath
        if not full.is_file():
            continue
        try:
            text = full.read_text(errors="replace")
        except Exception:
            continue
        for m in pattern.finditer(text):
            invariants.append({
                "id": m.group(1),
                "file": fpath,
                "offset": m.start(),
            })
    return invariants


def extract_schema_entities(root: Path, schema_files: list[str]) -> list[dict]:
    """Extract entity names from JSON Schema files."""
    entities = []
    for fpath in schema_files:
        full = root / fpath
        if not full.is_file() or not fpath.endswith(".json"):
            continue
        try:
            data = json.loads(full.read_text())
        except Exception:
            continue
        props = data.get("properties", {})
        required = data.get("required", [])
        entities.append({
            "file": fpath,
            "fields": list(props.keys()),
            "required": required,
        })
    return entities


def extract_sql_tables(root: Path, migration_files: list[str]) -> list[dict]:
    """Extract table names and columns from SQL migrations."""
    tables = []
    create_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^;]+)\)",
        re.IGNORECASE | re.DOTALL,
    )
    col_pattern = re.compile(r"^\s*(\w+)\s+(TEXT|BIGINT|JSONB|TIMESTAMPTZ|INTEGER|BOOLEAN|REAL)", re.IGNORECASE)
    for fpath in migration_files:
        full = root / fpath
        if not full.is_file():
            continue
        text = full.read_text(errors="replace")
        for m in create_pattern.finditer(text):
            table_name = m.group(1)
            body = m.group(2)
            columns = []
            for line in body.split("\n"):
                cm = col_pattern.match(line)
                if cm:
                    columns.append({"name": cm.group(1), "type": cm.group(2).upper()})
            tables.append({"file": fpath, "table": table_name, "columns": columns})
    return tables


def extract_wit_functions(root: Path, wit_files: list[str]) -> list[dict]:
    """Extract function signatures from WIT files."""
    functions = []
    func_pattern = re.compile(r"(\w[\w-]*):\s*func\(([^)]*)\)(?:\s*->\s*(\S+))?")
    for fpath in wit_files:
        full = root / fpath
        if not full.is_file():
            continue
        text = full.read_text(errors="replace")
        for m in func_pattern.finditer(text):
            functions.append({
                "file": fpath,
                "name": m.group(1),
                "params": m.group(2).strip(),
                "return_type": m.group(3) or "void",
            })
    return functions


def main():
    parser = argparse.ArgumentParser(description="Collect design artifacts")
    parser.add_argument("project_root", help="Path to project root")
    parser.add_argument("--output", "-o", default=None, help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    design_docs = find_files(root, ["docs/*.md", "docs/**/*.md"])
    schema_files = find_files(root, ["schemas/**/*.json", "schemas/*.json"])
    migration_files = find_files(root, ["migrations/*.sql"])
    wit_files = find_files(root, ["wit/*.wit"])
    test_files = find_files(root, ["**/tests/**/*.rs", "**/*_test.rs", "**/test_*.rs", "**/*_tests.rs", "scripts/test-*.sh"])
    source_files = find_files(root, ["**/*.rs", "**/*.py", "**/*.ts"])
    manifest_files = find_files(root, ["**/manifest.json"])
    config_files = find_files(root, ["CLAUDE.md", "config/*.yml", "config/*.yaml", ".env.example"])

    all_text_files = design_docs + source_files + test_files
    invariants = extract_invariants(root, all_text_files)
    schema_entities = extract_schema_entities(root, schema_files)
    sql_tables = extract_sql_tables(root, migration_files)
    wit_functions = extract_wit_functions(root, wit_files)

    manifest = {
        "project_root": str(root),
        "artifacts": {
            "design_docs": design_docs,
            "schema_files": schema_files,
            "migration_files": migration_files,
            "wit_files": wit_files,
            "test_files": test_files,
            "source_files": source_files,
            "manifest_files": manifest_files,
            "config_files": config_files,
        },
        "extracted": {
            "invariants": invariants,
            "schema_entities": schema_entities,
            "sql_tables": sql_tables,
            "wit_functions": wit_functions,
        },
        "summary": {
            "design_doc_count": len(design_docs),
            "schema_count": len(schema_files),
            "migration_count": len(migration_files),
            "test_file_count": len(test_files),
            "source_file_count": len(source_files),
            "invariant_count": len(invariants),
            "unique_invariant_ids": len(set(i["id"] for i in invariants)),
            "wit_function_count": len(wit_functions),
            "sql_table_count": len(sql_tables),
        },
    }

    output = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Manifest written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
