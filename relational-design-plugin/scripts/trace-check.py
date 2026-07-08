#!/usr/bin/env python3
"""Lightweight Relational Design trace checker."""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

ID_RE = re.compile(r"RD-(?:O|A|C|R|H|DD|AR|CR|RV|RT|BF)-\d+", re.I)
ID_DEF_RE = re.compile(r"^\s*-?\s*id:\s*(RD-(?:O|A|C|R|H|DD|AR|CR|RV|RT|BF)-\d+)\s*$", re.I | re.M)
REQUIRED_SECTIONS = [
    "observations",
    "assumptions",
    "constraints",
    "relations",
    "hypotheses",
    "decisions",
    "artifacts",
    "critiques",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".relational-design")
    p.add_argument("--session", default="current-session.yaml")
    args = p.parse_args()

    root = Path(args.root)
    session = root / args.session
    if not session.exists():
        print(f"missing: {session}")
        return 1

    text = session.read_text(encoding="utf-8")
    all_ids = ID_RE.findall(text)
    definitions = ID_DEF_RE.findall(text)
    defined_ids = set(definitions)
    missing_sections = [s for s in REQUIRED_SECTIONS if f"{s}:" not in text]
    duplicate_ids = sorted({id_ for id_, count in Counter(definitions).items() if count > 1})
    dangling_refs = sorted(set(all_ids) - defined_ids)

    print(f"trace session: {session}")
    print(f"trace ids: {len(all_ids)} occurrences, {len(defined_ids)} defined nodes")
    if missing_sections:
        print("missing sections:")
        for s in missing_sections:
            print(f"  - {s}")
    else:
        print("sections: ok")

    if duplicate_ids:
        print("duplicate id definitions:")
        for i in duplicate_ids:
            print(f"  - {i}")
    else:
        print("id uniqueness: ok")

    if dangling_refs:
        print("dangling references (referenced but never defined as a node id):")
        for i in dangling_refs:
            print(f"  - {i}")
    else:
        print("reference resolution: ok")

    if "confidence:" not in text:
        print("warning: no confidence markers found")
    if "depends_on:" not in text:
        print("warning: no dependency markers found")
    if "status:" not in text:
        print("warning: no status markers found")

    ok = not missing_sections and not duplicate_ids and not dangling_refs
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
