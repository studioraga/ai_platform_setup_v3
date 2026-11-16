#!/usr/bin/env python3
"""Verify exact expected formal R05-B rejection.

Simulation validation is permitted, but formal approval
must remain blocked while the actual owner review is pending.
"""

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validator", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-pending", type=int, default=103)
    args = parser.parse_args()

    validator = Path(args.validator).resolve()
    worksheet = Path(args.csv).resolve()
    output = Path(args.output).resolve()

    if not validator.is_file():
        raise SystemExit("FAIL: Formal validator missing")

    if not worksheet.is_file():
        raise SystemExit("FAIL: Formal worksheet missing")

    if args.expected_pending < 1:
        raise SystemExit("FAIL: Expected pending must be positive")

    with worksheet.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 103:
        raise SystemExit(
            f"FAIL: Unexpected candidate count: {len(rows)}"
        )

    ids = [row["candidate_id"] for row in rows]

    if len(set(ids)) != 103 or any(not value for value in ids):
        raise SystemExit("FAIL: Duplicate or empty candidate ID")

    counts = Counter(
        row["proposed_decision"] for row in rows
    )

    if counts.get("UNREVIEWED", 0) != args.expected_pending:
        raise SystemExit(
            "FAIL: Formal worksheet state differs from expected"
        )

    command = [
        sys.executable,
        str(validator),
        "--csv",
        str(worksheet),
        "--require-complete",
    ]

    result = subprocess.run(
        command,
        cwd="/tmp",
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    expected_message = (
        f"{args.expected_pending} unresolved review decisions"
    )

    # A nonzero exit alone does NOT constitute a successful test.
    if result.returncode == 0:
        raise SystemExit(
            "FAIL: Formal validator unexpectedly approved pending review"
        )

    if expected_message not in result.stderr:
        raise SystemExit(
            "FAIL: Validator failed for an unexpected reason:\n"
            + result.stderr[-2000:]
        )

    if "Traceback" not in result.stderr:
        raise SystemExit(
            "FAIL: Expected validator exception was not observed"
        )

    report = {
        "schema_version": 1,
        "gate": "R05_B_FORMAL_APPROVAL",
        "expected_result": "BLOCKED",
        "observed_result": "BLOCKED",
        "blocker_code": "OWNER_SCOPE_APPROVAL_PENDING",
        "total_candidates": len(rows),
        "unreviewed_candidates": args.expected_pending,
        "formal_approval": False,
        "simulation_pass_does_not_authorize_release": True,
        "negative_test_passed": True,
        "validator_exit_code": result.returncode,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps(report, indent=2))
    print("PASS: Formal R05-B approval blocked for expected reason")


if __name__ == "__main__":
    main()
