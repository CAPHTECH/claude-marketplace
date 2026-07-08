#!/usr/bin/env python3
"""Generate a lightweight Markdown report from Relational Design hook events."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".relational-design")
    args = p.parse_args()

    root = Path(args.root)
    log = root / "events" / "hook-events.jsonl"
    if not log.exists():
        print("# Relational Design Event Report\n\nNo hook event log found.")
        return 0

    events = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except Exception:
            continue

    by_phase = Counter(e.get("phase", "unknown") for e in events)
    design_edits = [e for e in events if e.get("phase") == "post-tool-use" and e.get("is_design_file")]
    files = Counter(e.get("file_path", "") for e in design_edits if e.get("file_path"))

    print("# Relational Design Event Report\n")
    print(f"Total events: {len(events)}\n")
    print("## By phase")
    for phase, n in by_phase.most_common():
        print(f"- {phase}: {n}")
    print("\n## Design-related edited files")
    if files:
        for path, n in files.most_common():
            print(f"- `{path}`: {n}")
    else:
        print("No design-related edits detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
