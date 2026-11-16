#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

DECISIONS = {
    "UNREVIEWED",
    "SUPPORTED_COMMON",
    "SUPPORTED_V030_ONLY",
    "INTERNAL",
    "UNCERTAIN",
    "BREAKING_REVIEW",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--priority-csv", required=True)
    parser.add_argument("--old-inventory", required=True)
    parser.add_argument("--new-inventory", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    priority = Path(args.priority_csv)
    old_path = Path(args.old_inventory)
    new_path = Path(args.new_inventory)
    output = Path(args.output)

    old = json.loads(old_path.read_text())
    new = json.loads(new_path.read_text())

    expected = {
        "old": "34883c2c14284e85b39531a677636b7b290178942a471e745da57b3b27be2279",
        "new": "9672f1b3350411080fd75bc08caaff335de684ae75a9fcf69b462f9f67e79be5",
    }

    if old.get("wheel_sha256") != expected["old"]:
        raise SystemExit("FAIL: v0.29 wheel provenance mismatch")

    if new.get("wheel_sha256") != expected["new"]:
        raise SystemExit("FAIL: v0.30 wheel provenance mismatch")

    with priority.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 103:
        raise SystemExit(
            f"FAIL: Expected reviewed queue of 103, found {len(rows)}"
        )

    records = []
    seen = set()

    for row in rows:
        module = row["module"].strip()
        symbol = row["symbol"].strip()
        key = (module, symbol)

        if not module or not symbol:
            raise SystemExit("FAIL: Empty module or symbol")

        if key in seen:
            raise SystemExit(f"FAIL: Duplicate candidate {key}")

        seen.add(key)

        decision = row.get("public_decision", "").strip()
        if decision not in DECISIONS:
            decision = "UNREVIEWED"

        import_module = module.removesuffix(".py").replace("/", ".")

        records.append({
            "candidate_id": hashlib.sha256(
                f"{module}:{symbol}".encode()
            ).hexdigest()[:16],
            "module": module,
            "symbol": symbol,
            "import_module": import_module,
            "import_path": (
                f"{import_module}.{symbol}"
                if symbol != "*" else None
            ),
            "triage": row["triage"],
            "observed_v029_kind": row.get("v029_kind", ""),
            "observed_v030_kind": row.get("v030_kind", ""),
            "classification": decision,
            "documentation_reference":
                row.get("documented_reference", "").strip() or None,
            "owner": row.get("owner", "").strip() or None,
            "owner_decision_date": None,
            "methods_in_scope": [],
            "serialization_contract": None,
            "exception_contract": None,
            "version_disposition": None,
            "exclusion_reason": None,
            "review_notes": None,
            "independent_reviewer": None,
            "review_status": "PENDING",
        })

    records.sort(key=lambda x: (x["module"], x["symbol"]))

    manifest = {
        "schema_version": 1,
        "manifest_type": "R05_PUBLIC_API_REVIEW",
        "generated_date": str(date.today()),
        "status": "PROPOSED",
        "qualified": False,
        "owner_approved": False,
        "independent_review_approved": False,
        "versions": ["0.29.0", "0.30.0"],
        "inputs": {
            "priority_csv_sha256": sha256(priority),
            "old_inventory_sha256": sha256(old_path),
            "new_inventory_sha256": sha256(new_path),
            "old_wheel_sha256": expected["old"],
            "new_wheel_sha256": expected["new"],
        },
        "candidate_count": len(records),
        "out_of_scope_candidates": {
            "status": "PENDING_SCOPE_DISPOSITION",
            "description":
                "Remaining implicit candidates require an approved "
                "scope/exclusion rule; they are not automatically public."
        },
        "candidates": records,
        "review": {
            "sdk_owner": None,
            "independent_reviewer": None,
            "approval_date": None,
            "decision": "PENDING",
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps({
        "output": str(output),
        "candidates": len(records),
        "classifications": dict(Counter(
            r["classification"] for r in records
        )),
        "qualified": False,
    }))

if __name__ == "__main__":
    main()
