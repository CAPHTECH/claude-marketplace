#!/usr/bin/env python3
"""Validate pce-memory claims against current file state using hash comparison."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def compute_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"
    except FileNotFoundError:
        return "MISSING"
    except Exception as e:
        return f"ERROR:{e}"


def extract_file_references(claim_text: str) -> List[str]:
    """Extract file path references from claim text."""
    patterns = [
        r'[\w/.-]+\.(?:json|md|py|ts|js|toml|yaml|yml)',
        r'[\w/.-]+/[\w.-]+',
    ]

    files = []
    for pattern in patterns:
        matches = re.findall(pattern, claim_text)
        files.extend(matches)

    return list(set(files))


def validate_claim(claim: Dict, project_root: Path) -> Tuple[str, str]:
    """
    Validate a single claim.

    Returns:
        Tuple of (status, reason)
        status: VALID | OUTDATED | MISSING | UNVERIFIABLE
    """
    text = claim.get("text", "")
    provenance = claim.get("provenance", {})

    # Check if provenance contains file hash
    stored_hash = provenance.get("file_hash")
    source_file = provenance.get("source_file")

    if stored_hash and source_file:
        file_path = project_root / source_file
        current_hash = compute_hash(file_path)

        if current_hash == "MISSING":
            return "MISSING", f"File not found: {source_file}"
        elif current_hash.startswith("ERROR"):
            return "UNVERIFIABLE", current_hash
        elif current_hash == stored_hash:
            return "VALID", "Hash matches"
        else:
            return "OUTDATED", f"Hash mismatch: stored={stored_hash[:20]}... current={current_hash[:20]}..."

    # Try to extract file references from claim text
    file_refs = extract_file_references(text)
    if not file_refs:
        return "UNVERIFIABLE", "No file references found in claim"

    # Check if any referenced files exist and have changed
    for ref in file_refs:
        file_path = project_root / ref
        if file_path.exists():
            # File exists but we don't have stored hash to compare
            return "UNVERIFIABLE", f"File exists ({ref}) but no stored hash for comparison"

    return "UNVERIFIABLE", "Cannot verify claim without stored file hash"


def main():
    parser = argparse.ArgumentParser(description="Validate pce-memory claims")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument("--claims", help="JSON file with claims to validate")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    project_root = Path(args.project_path).resolve()

    # Read claims from file or stdin
    if args.claims:
        with open(args.claims) as f:
            claims = json.load(f)
    else:
        print("Reading claims from stdin (paste JSON, then Ctrl+D)...")
        claims = json.load(sys.stdin)

    # Handle both list and dict with claims key
    if isinstance(claims, dict) and "claims" in claims:
        claims = claims["claims"]

    results = {
        "VALID": [],
        "OUTDATED": [],
        "MISSING": [],
        "UNVERIFIABLE": [],
    }

    for claim in claims:
        claim_data = claim.get("claim", claim)
        claim_id = claim_data.get("id", "unknown")
        status, reason = validate_claim(claim_data, project_root)

        results[status].append({
            "claim_id": claim_id,
            "text": claim_data.get("text", "")[:100] + "...",
            "reason": reason,
        })

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Validation Results for {project_root}\n")
        print("=" * 60)

        for status, items in results.items():
            if items:
                print(f"\n{status} ({len(items)}):")
                for item in items:
                    print(f"  [{item['claim_id']}] {item['reason']}")

        print("\n" + "=" * 60)
        total = sum(len(v) for v in results.values())
        valid = len(results["VALID"])
        print(f"Summary: {valid}/{total} claims validated")

        # Suggest feedback
        if results["OUTDATED"]:
            print("\nSuggested feedback for OUTDATED claims:")
            for item in results["OUTDATED"]:
                print(f'  feedback(claim_id="{item["claim_id"]}", signal="outdated", score=-0.5)')


if __name__ == "__main__":
    main()
