#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
./section1_audit.py
printf '\nReports collected:\n'
find reports -maxdepth 3 -type f ! -iname '*private*' -printf '%p\n' | sort
printf '\nSection 1 requires manual correctness/operability/communication review; this is not a PASS certification.\n'
