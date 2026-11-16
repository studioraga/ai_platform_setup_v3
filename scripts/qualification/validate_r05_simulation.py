#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

p = argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--manifest", required=True)
p.add_argument("--proposal", required=True)
args = p.parse_args()

with open(args.csv, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

m = json.loads(Path(args.manifest).read_text())

assert len(rows) == 103
assert len({r["candidate_id"] for r in rows}) == 103

assert m["status"] == "SIMULATED_SCOPE_ONLY"
assert m["owner_approved"] is False
assert m["public_api_approved"] is False
assert m["independent_review_approved"] is False
assert m["r05_requirement_approved"] is False
assert m["input_sha256"] == sha(Path(args.proposal))

common = [
    r for r in rows
    if r["proposed_decision"] == "SUPPORTED_COMMON"
]
deferred = [
    r for r in rows
    if r["proposed_decision"] == "DEFERRED_OUT_OF_SCOPE"
]

assert len(common) == 12
assert len(deferred) == 91

assert set(m["supported_common_candidates"]) == {
    r["import_path"] for r in common
}

for row in rows:
    assert row["owner_name"] == "ENGINEERING_SIMULATION"
    assert row["simulation_status"] == "NOT_FORMALLY_APPROVED"
    assert row["decision_rationale"].startswith("SIMULATION ONLY:")

print("PASS: Simulated decisions are internally consistent")
print("Formal R05 approval: NOT GRANTED")
