#!/usr/bin/env python3
"""Generate an unapproved R05 scope proposal without modifying input evidence."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

RECOMMENDATIONS = {
    "TESTED_IMPORT_CANDIDATE": (
        "SUPPORTED_COMMON",
        "Both historical consumer suites exercise this import. "
        "Proposed common contract; documentation and owner approval required."
    ),
    "DECLARED_EXPORT_CANDIDATE": (
        "DEFERRED_OUT_OF_SCOPE",
        "Declared export candidate outside the initial bounded kernel contract. "
        "Requires separate export and documented-support review."
    ),
    "NEW_ONLY_REVIEW": (
        "DEFERRED_OUT_OF_SCOPE",
        "Candidate introduced in v0.30. Separate version-specific "
        "qualification is required."
    ),
    "STAR_IMPORT_REVIEW": (
        "DEFERRED_OUT_OF_SCOPE",
        "Star-import declaration is not itself a callable public symbol. "
        "Its actual SDK-defined re-exports require individual review."
    ),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])

    required = {
        "candidate_id",
        "import_path",
        "suggested_review",
        "proposed_decision",
        "decision_rationale",
    }
    if not required.issubset(fields):
        raise SystemExit(f"Missing columns: {sorted(required - set(fields))}")

    if len(rows) != 103:
        raise SystemExit(f"Expected 103 candidates; found {len(rows)}")

    identifiers = [r["candidate_id"] for r in rows]
    if len(identifiers) != len(set(identifiers)):
        raise SystemExit("Duplicate candidate IDs")

    for field in ("recommended_decision", "recommendation_basis"):
        if field not in fields:
            fields.append(field)

    for row in rows:
        group = row["suggested_review"]
        if group not in RECOMMENDATIONS:
            raise SystemExit(f"Unknown review category: {group}")

        recommendation, basis = RECOMMENDATIONS[group]
        row["recommended_decision"] = recommendation
        row["recommendation_basis"] = basis

        # Keep actual decisions untouched.
        if row["proposed_decision"] not in ("", "UNREVIEWED"):
            raise SystemExit(
                "Input contains existing decisions. Preserve and review them."
            )

    dest = Path(args.output)
    if dest.exists():
        raise SystemExit(f"Refusing to overwrite: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["recommended_decision"] for r in rows)

    summary = {
        "status": "PROPOSAL_ONLY",
        "owner_approved": False,
        "independent_review_approved": False,
        "rows": len(rows),
        "recommendations": dict(counts),
        "warning": "Recommendations are not public API approvals."
    }

    Path(args.summary).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
