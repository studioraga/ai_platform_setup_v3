#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
./validate_env.sh
docker info --format 'Docker Server={{.ServerVersion}}' >/dev/null
project="$(docker compose config --format json | python3 -c 'import json,sys;print(json.load(sys.stdin)["name"])')"
[[ "$project" == 'principal-ai-platform-practice' ]] || { echo "ERROR unexpected project name: $project"; exit 1; }
# Distinguish existing practice project from unrelated containers and never modify other projects.
echo 'Existing practice stack:'
docker compose ps -a
for port in 15432 16379 16333; do
  if ss -H -ltn "sport = :$port" | grep -q .; then
    echo "Port $port already occupied; inspect listener and owning Docker container before running compose up."
    ss -ltnp "sport = :$port" || true
    # Running existing *practice* services may own these ports; user must approve after inspecting.
    exit 2
  fi
done
echo 'PASS: practice project name confirmed and mapped host ports unoccupied'
