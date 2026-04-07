#!/usr/bin/env python3
"""Lint requirement YAML files used by requirements-plugin."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FIELDS = [
    "id",
    "title",
    "status",
    "priority",
    "context",
    "trigger",
    "guarantee",
    "forbid",
    "observable",
    "positive_examples",
    "negative_examples",
    "links",
]

ALLOWED_STATUS = {"draft", "reviewed", "active", "deprecated", "superseded"}
ALLOWED_PRIORITY = {"p0", "p1", "p2", "p3"}
REQ_ID_PATTERN = re.compile(r"^REQ-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}$")


@dataclass
class Issue:
    severity: str
    path: str
    req_id: str
    message: str


def load_yaml(path: Path) -> Any:
    """Load YAML with PyYAML when available, otherwise Ruby YAML."""
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except ModuleNotFoundError:
        return load_yaml_with_ruby(path)


def load_yaml_with_ruby(path: Path) -> Any:
    script = r"""
require "json"
require "yaml"

path = ARGV[0]
text = File.read(path, encoding: "UTF-8")
data = YAML.safe_load(text, aliases: true)
puts JSON.generate(data)
"""
    try:
        completed = subprocess.run(
            ["ruby", "-e", script, str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "YAML parser is unavailable. Install PyYAML or Ruby."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or exc.stdout.strip()
        raise RuntimeError(f"Ruby YAML parse failed: {stderr}") from exc

    payload = completed.stdout.strip()
    if not payload:
        return None
    return json.loads(payload)


def iter_yaml_files(inputs: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {raw}")
        if path.is_file():
            if path.suffix.lower() in {".yaml", ".yml"}:
                files.append(path)
            continue
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() in {".yaml", ".yml"}:
                files.append(candidate)
    # Keep order stable and unique.
    resolved = sorted({file.resolve() for file in files})
    if not resolved:
        raise FileNotFoundError("No YAML files were found in the provided paths.")
    return resolved


def extract_requirements(doc: Any) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []

    if isinstance(doc, dict) and "id" in doc:
        return [doc], warnings

    if isinstance(doc, list):
        requirements = [item for item in doc if isinstance(item, dict) and "id" in item]
        if not requirements:
            warnings.append("No requirement entries found in list document.")
        return requirements, warnings

    if isinstance(doc, dict) and isinstance(doc.get("requirements"), list):
        requirements = [
            item for item in doc["requirements"] if isinstance(item, dict) and "id" in item
        ]
        if requirements:
            warnings.append(
                "Catalog-like document detected. Only per-entry keys are linted."
            )
        else:
            warnings.append("No requirement entries found under top-level requirements.")
        return requirements, warnings

    warnings.append("Document is not a requirement record or requirements list.")
    return [], warnings


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def observable_is_empty(value: Any) -> bool:
    if isinstance(value, dict):
        return all(is_empty(item) for item in value.values())
    return is_empty(value)


def append_issue(
    issues: list[Issue], severity: str, path: Path, req_id: str, message: str
) -> None:
    issues.append(Issue(severity=severity, path=str(path), req_id=req_id, message=message))


def lint_requirement(path: Path, requirement: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    req_id = str(requirement.get("id", "<missing-id>"))

    for field in REQUIRED_FIELDS:
        if field not in requirement:
            append_issue(issues, "high", path, req_id, f"Missing required field: {field}")

    if "id" in requirement and not REQ_ID_PATTERN.match(req_id):
        append_issue(
            issues,
            "medium",
            path,
            req_id,
            "Requirement id should match REQ-domain-001 style.",
        )

    if is_empty(requirement.get("title")):
        append_issue(issues, "high", path, req_id, "title must not be empty.")

    status = requirement.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        append_issue(
            issues,
            "high",
            path,
            req_id,
            f"status must be one of {sorted(ALLOWED_STATUS)}.",
        )

    priority = requirement.get("priority")
    if priority is not None and priority not in ALLOWED_PRIORITY:
        append_issue(
            issues,
            "medium",
            path,
            req_id,
            f"priority must be one of {sorted(ALLOWED_PRIORITY)}.",
        )

    context = requirement.get("context")
    if "context" in requirement and not isinstance(context, dict):
        append_issue(issues, "high", path, req_id, "context must be a mapping.")
    elif isinstance(context, dict) and is_empty(context):
        append_issue(issues, "medium", path, req_id, "context must not be empty.")

    for list_field in ["guarantee", "forbid", "positive_examples", "negative_examples"]:
        value = requirement.get(list_field)
        if list_field in requirement and not isinstance(value, list):
            append_issue(issues, "high", path, req_id, f"{list_field} must be a list.")
        elif isinstance(value, list) and len(value) == 0:
            append_issue(issues, "high", path, req_id, f"{list_field} must not be empty.")

    if "observable" in requirement and observable_is_empty(requirement.get("observable")):
        append_issue(issues, "high", path, req_id, "observable must not be empty.")

    links = requirement.get("links")
    if "links" in requirement and not isinstance(links, dict):
        append_issue(issues, "high", path, req_id, "links must be a mapping.")

    guarantee_items = {
        str(item).strip()
        for item in requirement.get("guarantee", [])
        if isinstance(item, str) and item.strip()
    }
    forbid_items = {
        str(item).strip()
        for item in requirement.get("forbid", [])
        if isinstance(item, str) and item.strip()
    }
    duplicated_statements = sorted(guarantee_items & forbid_items)
    for statement in duplicated_statements:
        append_issue(
            issues,
            "high",
            path,
            req_id,
            f"Same statement appears in both guarantee and forbid: {statement}",
        )

    unknowns = requirement.get("unknowns", [])
    if status == "active" and isinstance(unknowns, list) and len(unknowns) > 0:
        append_issue(
            issues,
            "medium",
            path,
            req_id,
            "active requirement still has unresolved unknowns.",
        )

    return issues


def build_report(files: list[Path]) -> dict[str, Any]:
    all_issues: list[Issue] = []
    file_warnings: list[dict[str, str]] = []
    id_registry: dict[str, list[str]] = {}
    requirements_scanned = 0

    for path in files:
        doc = load_yaml(path)
        requirements, warnings = extract_requirements(doc)

        for warning in warnings:
            file_warnings.append({"path": str(path), "message": warning})

        for requirement in requirements:
            requirements_scanned += 1
            req_id = str(requirement.get("id", "<missing-id>"))
            id_registry.setdefault(req_id, []).append(str(path))
            all_issues.extend(lint_requirement(path, requirement))

    for req_id, locations in sorted(id_registry.items()):
        if req_id == "<missing-id>":
            continue
        if len(locations) > 1:
            joined = ", ".join(locations)
            all_issues.append(
                Issue(
                    severity="high",
                    path="(multiple)",
                    req_id=req_id,
                    message=f"Duplicate requirement id found across files: {joined}",
                )
            )

    issue_dicts = [asdict(issue) for issue in all_issues]
    return {
        "ok": len(all_issues) == 0,
        "files_scanned": len(files),
        "requirements_scanned": requirements_scanned,
        "issues": issue_dicts,
        "warnings": file_warnings,
    }


def print_human_report(report: dict[str, Any]) -> None:
    if report["warnings"]:
        print("[WARNINGS]")
        for warning in report["warnings"]:
            print(f"- {warning['path']}: {warning['message']}")
        print("")

    if report["ok"]:
        print(
            f"[OK] Scanned {report['files_scanned']} files and "
            f"{report['requirements_scanned']} requirement entries."
        )
        return

    print(
        f"[ISSUES] Found {len(report['issues'])} issues in "
        f"{report['requirements_scanned']} requirement entries."
    )
    print("")
    for issue in report["issues"]:
        print(
            f"- [{issue['severity']}] {issue['req_id']} @ {issue['path']}: "
            f"{issue['message']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint requirement YAML files for missing fields and basic contradictions."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Requirement YAML file or directory. Directories are scanned recursively.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print report as JSON.",
    )
    args = parser.parse_args()

    try:
        files = iter_yaml_files(args.paths)
        report = build_report(files)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_report(report)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
