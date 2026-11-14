#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/reports"
OUT="$ROOT/reports/fresh_machine_preflight.txt"
{
  echo 'Read-only fresh-machine prerequisite inventory'; date -Is
  # shellcheck disable=SC1091
  . /etc/os-release
  printf 'OS=%s VERSION_ID=%s ARCH=%s\n' "$ID" "$VERSION_ID" "$(dpkg --print-architecture)"
  printf 'Kernel=%s\n' "$(uname -r)"
  for t in sudo curl gpg git docker uv python3 node npm psql redis-cli az azd terraform kubectl helm gh code shellcheck; do
    if command -v "$t" >/dev/null 2>&1; then printf '%-12s %s\n' "$t" "$(command -v "$t")"; else printf '%-12s MISSING\n' "$t"; fi
  done
  echo 'Docker compose:'
  if command -v docker >/dev/null 2>&1; then docker compose version 2>&1 || :; fi
  echo 'No installation, authentication, deployment or service changes performed.'
} | tee "$OUT"
