#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/reports/baseline-qualification"
OUT="$ROOT/reports/baseline-qualification/dependency_inventory.txt"
{
  date -Is
  # shellcheck source=/dev/null
  . /etc/os-release
  printf 'OS=%s VERSION=%s ARCH=%s\n' "$ID" "$VERSION_ID" "$(dpkg --print-architecture)"
  for t in python3 uv node npm docker terraform helm kubectl az azd gh code shellcheck git; do
    if command -v "$t" >/dev/null 2>&1; then
      printf '%s path=%s\n' "$t" "$(command -v "$t")"
    else
      printf '%s MISSING\n' "$t"
    fi
  done
  python3 --version 2>&1 || true
  node --version 2>&1 || true
  npm --version 2>&1 || true
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker version --format 'DockerServer={{.Server.Version}}'
    docker compose version
    for image in postgres:17.6 redis:7.4.5-alpine qdrant/qdrant:v1.15.4; do
      printf 'Image=%s ' "$image"
      docker image inspect "$image" --format '{{json .RepoDigests}}' 2>/dev/null || echo 'NOT_PRESENT'
    done
  fi
} > "$OUT"
echo "Wrote ignored dependency inventory: $OUT"
