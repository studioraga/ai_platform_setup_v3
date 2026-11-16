#!/usr/bin/env python3
"""Generate simulated R05 review decisions. Never authorizes an SDK API."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposal", required=True)
    ap.add_argument("--decision", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args()

    proposal = Path(a.proposal)
    decision_file = Path(a.decision)
    out = Path(a.output)
    manifest_path = Path(a.manifest)

    marker = decision_file.read_text(encoding="utf-8")

    if "Decision: SIMULATED_ACCEPTANCE" not in marker:
        raise SystemExit("FAIL: Simulation decision marker missing")

    if "Formal SDK owner approval: NOT GRANTED" not in marker:
        raise SystemExit("FAIL: Formal approval boundary missing")

    if out.exists() or manifest_path.exists():
        raise SystemExit("FAIL: Refusing to overwrite existing evidence")

    with proposal.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = list(reader.fieldnames or [])

    required = {
        "candidate_id", "import_path", "suggested_review",
        "recommended_decision", "proposed_decision",
        "decision_rationale", "documentation_reference",
        "owner_name",
    }

    if not required.issubset(columns):
        raise SystemExit(f"FAIL: Missing columns: {required-set(columns)}")

    if len(rows) != 103:
        raise SystemExit(f"FAIL: Expected 103, got {len(rows)}")

    ids = [r["candidate_id"] for r in rows]
    if len(set(ids)) != 103:
        raise SystemExit("FAIL: Duplicate candidate IDs")

    for column in ("simulation_status", "simulation_reason"):
        if column not in columns:
            columns.append(column)

    common, deferred = [], []

    for row in rows:
        recommendation = row["recommended_decision"]

        if row["proposed_decision"] not in ("", "UNREVIEWED"):
            raise SystemExit("FAIL: Proposal contains existing formal decisions")

        if recommendation == "SUPPORTED_COMMON":
            if row["suggested_review"] != "TESTED_IMPORT_CANDIDATE":
                raise SystemExit("FAIL: Non-tested symbol promoted")
            if not row["import_path"]:
                raise SystemExit("FAIL: Missing common import path")
            common.append(row["import_path"])

        elif recommendation == "DEFERRED_OUT_OF_SCOPE":
            deferred.append(row["candidate_id"])

        else:
            raise SystemExit(f"FAIL: Unsupported recommendation: {recommendation}")

        row["proposed_decision"] = recommendation
        row["decision_rationale"] = (
            "SIMULATION ONLY: " + row["recommendation_basis"]
        )
        row["owner_name"] = "ENGINEERING_SIMULATION"
        row["simulation_status"] = "NOT_FORMALLY_APPROVED"
        row["simulation_reason"] = (
            "Real owner approval pending; workflow validation only"
        )

        # No fabricated SDK documentation or approval reference.
        row["documentation_reference"] = ""

    if len(common) != 12 or len(deferred) != 91:
        raise SystemExit("FAIL: Unexpected scope counts")

    if len(set(common)) != len(common):
        raise SystemExit("FAIL: Duplicate import path")

    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema_version": 1,
        "simulation_id": "R05-B-SIM-001",
        "status": "SIMULATED_SCOPE_ONLY",
        "public_api_approved": False,
        "owner_approved": False,
        "independent_review_approved": False,
        "r05_requirement_approved": False,
        "input_sha256": digest(proposal),
        "decision_record_sha256": digest(decision_file),
        "supported_common_candidates": sorted(common),
        "deferred_priority_candidate_ids": sorted(deferred),
        "qualification_status": "SIMULATION_PENDING_RUNTIME",
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "SIMULATED_SCOPE_ONLY",
        "common": len(common),
        "deferred": len(deferred),
        "approved": False,
    }))

if __name__ == "__main__":
    main()
