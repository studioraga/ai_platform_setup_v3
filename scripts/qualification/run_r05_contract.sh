#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TEST="$ROOT/tests/r05/test_shared_contract.py"
[[ -f "$TEST" ]] || { echo 'Missing tracked contract suite' >&2; exit 2; }
[[ $# -eq 3 ]] || { echo 'Usage: run_r05_contract.sh <consumer-python-0.29> <consumer-python-0.30> <evidence-dir>' >&2; exit 2; }
OLD="$1";NEW="$2";OUT="$3";mkdir -p "$OUT"
(cd /tmp; env -u PYTHONPATH GOV_EXPECTED_VERSION=0.29.0 "$OLD" -m pytest "$TEST" -q --import-mode=importlib -p no:cacheprovider) > "$OUT/v029_shared_contract.txt" 2>&1
(cd /tmp; env -u PYTHONPATH GOV_EXPECTED_VERSION=0.30.0 "$NEW" -m pytest "$TEST" -q --import-mode=importlib -p no:cacheprovider) > "$OUT/v030_shared_contract.txt" 2>&1
cat "$OUT/v029_shared_contract.txt" "$OUT/v030_shared_contract.txt"
echo 'PASS: both wheel consumers passed tracked R05 contract (limited tested scope)'
