#!/usr/bin/env python3
"""Assess R05 evidence without granting formal approval."""

import argparse
import csv
import json
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--simulation", required=True)
    p.add_argument("--coverage", required=True)
    p.add_argument("--behavior-gaps", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--formal-review", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    sim = read_json(args.simulation)
    coverage = read_json(args.coverage)
    behavior = read_json(args.behavior_gaps)
    policy = read_json(args.policy)

    with open(args.formal_review, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 103:
        raise SystemExit("FAIL: Formal candidate count mismatch")

    if sim.get("status") != "SIMULATED_SCOPE_ONLY":
        raise SystemExit("FAIL: Invalid simulation input")

    if sim.get("r05_requirement_approved") is not False:
        raise SystemExit("FAIL: Simulation claims real approval")

    if coverage.get("candidate_count") != 12:
        raise SystemExit("FAIL: Unexpected common coverage")

    if coverage.get("unresolved_import_paths"):
        raise SystemExit("FAIL: Unresolved runtime import paths")

    if behavior.get("approved") is not False:
        raise SystemExit("FAIL: Unsupported behavioral approval")

    if policy.get("owner_approved") is not False:
        raise SystemExit("FAIL: Unsupported version-policy approval")

    pending = sum(
        r.get("proposed_decision") in ("", "UNREVIEWED")
        for r in rows
    )

    blockers = [
        {
            "id": "R05-B",
            "reason": f"{pending} unreviewed formal API decisions",
        },
        {
            "id": "R05-C",
            "reason": "Normative method contracts not approved",
        },
        {
            "id": "R05-D",
            "reason": "Behavioral schemas and exceptions not approved",
        },
        {
            "id": "R05-E",
            "reason": "Version transition policy not approved",
        },
        {
            "id": "R05-G",
            "reason": "Independent acceptance not recorded",
        },
    ]

    report = {
        "schema_version": 1,
        "status": "ENGINEERING_PREFLIGHT_COMPLETE",
        "engineering_simulation_accepted": True,
        "formal_r05_status": "BLOCKED",
        "requirement_pass": False,
        "governance_release_authorized": False,
        "candidate_count": len(rows),
        "pending_formal_decisions": pending,
        "common_candidate_count": 12,
        "blockers": blockers,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
