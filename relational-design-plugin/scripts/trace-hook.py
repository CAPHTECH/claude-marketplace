#!/usr/bin/env python3
"""
Relational Design hook helper.

This script is intentionally conservative:
- It logs metadata only, not file content.
- It is advisory-only: it never denies or blocks a tool call.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

DESIGN_EXTENSIONS = {
    ".tsx", ".jsx", ".vue", ".svelte", ".astro",
    ".css", ".scss", ".sass", ".less",
    ".html", ".mdx",
}
DESIGN_PATH_PATTERNS = [
    r"/(design-system|tokens|theme|styles)/",
    r"/(stories|storybook)/",
]
TRACE_ID_RE = re.compile(r"RD-(O|A|C|R|H|DD|AR|CR|RV|RT|BF)-\d+", re.I)


def read_input() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw_stdin_unparsed": raw[:1000]}


def emit(obj: Dict[str, Any]) -> None:
    if obj:
        print(json.dumps(obj, ensure_ascii=False))


def trace_root(cwd: Path) -> Path:
    return cwd / ".relational-design"


def active_session_exists(root: Path) -> bool:
    return (root / "current-session.yaml").exists()


def get_file_path(event: Dict[str, Any]) -> str:
    tool_input = event.get("tool_input") or {}
    return str(tool_input.get("file_path") or tool_input.get("path") or "")


def is_design_file(path: str) -> bool:
    if not path:
        return False
    normalized = path.replace("\\", "/")
    suffix = Path(normalized).suffix.lower()
    if suffix in DESIGN_EXTENSIONS:
        return True
    return any(re.search(pattern, normalized) for pattern in DESIGN_PATH_PATTERNS)


def contains_trace_id(event: Dict[str, Any]) -> bool:
    tool_input = event.get("tool_input") or {}
    for key in ("content", "new_string", "old_string"):
        value = tool_input.get(key)
        if isinstance(value, str) and TRACE_ID_RE.search(value):
            return True
    return False


def safe_event_record(event: Dict[str, Any], phase: str) -> Dict[str, Any]:
    tool_input = event.get("tool_input") or {}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "hook_event_name": event.get("hook_event_name"),
        "session_id": event.get("session_id"),
        "cwd": event.get("cwd"),
        "tool_name": event.get("tool_name"),
        "tool_use_id": event.get("tool_use_id"),
        "file_path": get_file_path(event),
        "is_design_file": is_design_file(get_file_path(event)),
        "has_inline_trace_id": contains_trace_id(event),
        "agent_type": event.get("agent_type"),
    }


def append_log(root: Path, event: Dict[str, Any], phase: str) -> None:
    try:
        events = root / "events"
        events.mkdir(parents=True, exist_ok=True)
        with (events / "hook-events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(safe_event_record(event, phase), ensure_ascii=False) + "\n")
    except Exception:
        # Hooks should not fail the user's work because logging failed.
        pass


def advisory_context(path: str, active: bool) -> str:
    if active:
        return (
            f"Relational Design: You are editing a design-related file ({path}). "
            "Keep non-trivial visual, layout, copy, or interaction choices linked to the active trace session."
        )
    return (
        f"Relational Design: You are editing a design-related file ({path}) without an active trace session. "
        "Before finalizing, create .relational-design/current-session.yaml or ask trace-archivist to record observations, relations, hypotheses, decisions, and critiques."
    )


def handle_pre_tool_use(event: Dict[str, Any]) -> None:
    cwd = Path(event.get("cwd") or os.getcwd())
    root = trace_root(cwd)
    append_log(root, event, "pre-tool-use")

    path = get_file_path(event)
    if not is_design_file(path):
        return

    active = active_session_exists(root)

    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": advisory_context(path, active)
        }
    })


def handle_post_tool_use(event: Dict[str, Any]) -> None:
    cwd = Path(event.get("cwd") or os.getcwd())
    root = trace_root(cwd)
    append_log(root, event, "post-tool-use")


def handle_subagent_stop(event: Dict[str, Any]) -> None:
    cwd = Path(event.get("cwd") or os.getcwd())
    root = trace_root(cwd)
    append_log(root, event, "subagent-stop")
    agent = event.get("agent_type", "Relational Design agent")
    emit({
        "systemMessage": (
            f"Relational Design role boundary check for {agent}: confirm observed facts, assumptions, "
            "relations, hypotheses, decisions, artifacts, critiques, and retractions were kept as separate "
            "node types, and that this agent did not exceed its role."
        )
    })


def handle_session_start(event: Dict[str, Any]) -> None:
    cwd = Path(event.get("cwd") or os.getcwd())
    root = trace_root(cwd)
    append_log(root, event, "session-start")
    # Keep SessionStart quiet unless a trace session already exists.
    if active_session_exists(root):
        emit({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Relational Design active session found at {root / 'current-session.yaml'}. Continue preserving design trace dependencies."
            }
        })


def count_design_edits(root: Path) -> int:
    log = root / "events" / "hook-events.jsonl"
    if not log.exists():
        return 0
    count = 0
    try:
        for line in log.read_text(encoding="utf-8").splitlines()[-200:]:
            try:
                item = json.loads(line)
            except Exception:
                continue
            if item.get("phase") == "post-tool-use" and item.get("is_design_file"):
                count += 1
    except Exception:
        pass
    return count


def handle_stop(event: Dict[str, Any]) -> None:
    cwd = Path(event.get("cwd") or os.getcwd())
    root = trace_root(cwd)
    append_log(root, event, "stop")
    edits = count_design_edits(root)
    active = active_session_exists(root)

    if edits and not active:
        message = (
            f"Relational Design detected {edits} recent design-related edit(s), but no active trace session exists at "
            f"{root / 'current-session.yaml'}. Create or update the trace record before treating the design as finalized."
        )
        emit({"systemMessage": message})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["session-start", "pre-tool-use", "post-tool-use", "subagent-stop", "stop"])
    args = parser.parse_args()
    event = read_input()

    if args.phase == "session-start":
        handle_session_start(event)
    elif args.phase == "pre-tool-use":
        handle_pre_tool_use(event)
    elif args.phase == "post-tool-use":
        handle_post_tool_use(event)
    elif args.phase == "subagent-stop":
        handle_subagent_stop(event)
    elif args.phase == "stop":
        handle_stop(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
