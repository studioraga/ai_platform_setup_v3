#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
command -v shellcheck >/dev/null || { echo 'ERROR: shellcheck missing'; exit 2; }
for script in ./*.sh ./scripts/*.sh ./scripts/qualification/*.sh; do
  [[ -f "$script" ]] || continue
  bash -n "$script"
done
printf '%s\n' 'PASS: Bash syntax'
python3 -m compileall -q section1_audit.py scripts/qualification tests/r05 labs/python-api
printf '%s\n' 'PASS: Python compilation'
shellcheck --severity=style ./*.sh ./scripts/*.sh ./scripts/qualification/*.sh
printf '%s\n' 'PASS: ShellCheck all scripts'
python3 section1_audit.py
printf '%s\n' 'PASS: requirements matrix structure'
