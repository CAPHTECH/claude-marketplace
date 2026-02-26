#!/usr/bin/env python3
import json
import sys

REQUIRED_TOP_KEYS = ["decision", "items", "tasks"]
REQUIRED_ITEM_KEYS = ["id", "category", "question", "hypothesis", "impact", "evidence", "urgency", "effort"]
REQUIRED_TASK_KEYS = ["id", "uncertainty_id", "hypothesis", "method", "timebox", "decision_rule", "evidence_artifact"]

def die(msg: str) -> None:
    print(f"[INVALID] {msg}")
    sys.exit(1)

def in_range(x, lo=1, hi=5) -> bool:
    return isinstance(x, int) and lo <= x <= hi

def main(path: str) -> None:
    try:
        data = json.load(open(path, "r", encoding="utf-8"))
    except Exception as e:
        die(f"Failed to parse JSON: {e}")

    for k in REQUIRED_TOP_KEYS:
        if k not in data:
            die(f"Missing top-level key: {k}")

    if not isinstance(data["items"], list) or len(data["items"]) == 0:
        die("items must be a non-empty list")

    ids = set()
    for it in data["items"]:
        for k in REQUIRED_ITEM_KEYS:
            if k not in it:
                die(f"Item missing key {k}: {it}")
        if it["id"] in ids:
            die(f"Duplicate item id: {it['id']}")
        ids.add(it["id"])
        for score_key in ["impact", "evidence", "urgency", "effort"]:
            if not in_range(it[score_key]):
                die(f"{it['id']} invalid {score_key} (1-5 int): {it[score_key]}")

    if not isinstance(data["tasks"], list):
        die("tasks must be a list")

    item_ids = {it["id"] for it in data["items"]}
    task_ids = set()
    for t in data["tasks"]:
        for k in REQUIRED_TASK_KEYS:
            if k not in t:
                die(f"Task missing key {k}: {t}")
        if t["id"] in task_ids:
            die(f"Duplicate task id: {t['id']}")
        task_ids.add(t["id"])
        if t["uncertainty_id"] not in item_ids:
            die(f"Task {t['id']} references unknown uncertainty_id: {t['uncertainty_id']}")

    print("[OK] uncertainty_plan.json looks valid.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_uncertainty_plan.py uncertainty_plan.json")
        sys.exit(2)
    main(sys.argv[1])
