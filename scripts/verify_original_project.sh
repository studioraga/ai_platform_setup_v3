#!/usr/bin/env bash
set -Eeuo pipefail
[[ $# -eq 2 ]] || { echo 'Usage: scripts/verify_original_project.sh <form8825|governance> <source-dir>'; exit 2; }
kind="$1"; src="$(realpath "$2")"
[[ "$kind" == form8825 || "$kind" == governance ]] || exit 2
[[ -d "$src" ]] || exit 2
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/reports/original-projects/$kind"; mkdir -p "$out"
{
  echo "Source directory: $src"; date -Is
  (cd "$src" && git rev-parse HEAD 2>/dev/null || echo 'Archive without Git metadata')
  if git -C "$src" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$src" status --short
  else
    echo 'Git working-tree status unavailable (archive or non-Git directory)'
  fi
  find "$src" -maxdepth 3 -type f \( -name pyproject.toml -o -name 'requirements*.txt' -o -name uv.lock -o -name package-lock.json -o -name alembic.ini -o -name pytest.ini \) -print
} | tee "$out/source-inventory.txt"
echo 'No original project code modified or tests assumed passed. Follow documented source-specific test commands.'
