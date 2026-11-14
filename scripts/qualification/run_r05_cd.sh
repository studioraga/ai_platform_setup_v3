#!/usr/bin/env bash
# R05-C/D experimental qualification runner. Never changes Governance source or tags.
set -Eeuo pipefail
if (( $# != 5 )); then
  echo "Usage: $0 <v029-python> <v030-python> <v029-wheel> <v030-wheel> <evidence-dir>" >&2
  exit 2
fi
PY29="$1"; PY30="$2"; W29="$3"; W30="$4"; OUT="$5"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
[[ -x "$PY29" && -x "$PY30" && -f "$W29" && -f "$W30" ]] || { echo 'Missing interpreter/wheel' >&2; exit 2; }
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
EXPECTED29=34883c2c14284e85b39531a677636b7b290178942a471e745da57b3b27be2279
EXPECTED30=9672f1b3350411080fd75bc08caaff335de684ae75a9fcf69b462f9f67e79be5
printf '%s  %s\n%s  %s\n' "$EXPECTED29" "$W29" "$EXPECTED30" "$W30" | sha256sum -c | tee "$OUT/wheel_hash_check.txt"
for version in 0.29.0 0.30.0; do
  if [[ "$version" == '0.29.0' ]]; then PY="$PY29"; ID=v029; else PY="$PY30"; ID=v030; fi
  # Run in neutral cwd; each package is imported only from its installed consumer.
  ( cd /tmp
    env -u PYTHONPATH -u PYTHONHOME GOV_EXPECTED_VERSION="$version" "$PY" -m pytest -q \
      "$ROOT/tests/r05/test_shared_contract.py" \
      "$ROOT/tests/r05/test_r05_extended_behavior.py" \
      --import-mode=importlib -p no:cacheprovider
  ) | tee "$OUT/${ID}_behavior_tests.txt"
  ( cd /tmp
    env -u PYTHONPATH -u PYTHONHOME "$PY" \
      "$ROOT/scripts/qualification/inventory_r05_method_contracts.py" \
      --expected-version "$version" --output "$OUT/${ID}_method_inventory.json"
  ) | tee "$OUT/${ID}_method_inventory.log"
done
python3 "$ROOT/scripts/qualification/compare_r05_method_contracts.py" \
  --old "$OUT/v029_method_inventory.json" --new "$OUT/v030_method_inventory.json" \
  --output "$OUT/method_delta.json" | tee "$OUT/method_delta.log"
sha256sum "$OUT"/*.json "$OUT"/*.txt "$OUT"/*.log > "$OUT/evidence.sha256"
echo 'PASS: bounded R05-C/D observational tests and method comparison; public API approval remains PENDING'
