#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports/docker-diagnosis
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="reports/docker-diagnosis/${stamp}"
mkdir -p "$out"
docker info --format 'Docker Server={{.ServerVersion}}' | tee "$out/engine.txt"
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | tee "$out/containers.txt"
docker compose ls | tee "$out/compose-projects.txt"
if ! docker container inspect docker-qdrant-1 >/dev/null 2>&1; then
  echo 'No docker-qdrant-1 found; no historical Qdrant container diagnosed.'; exit 0
fi
# Inspect may include secrets, mounts and env; private permissions and no auto-publication.
umask 077
docker inspect docker-qdrant-1 > "$out/qdrant-inspect.PRIVATE.json"
docker logs --timestamps --tail 250 docker-qdrant-1 > "$out/qdrant-log.PRIVATE.txt" 2>&1 || true
docker inspect docker-qdrant-1 --format 'Name={{.Name}} Status={{.State.Status}} Exit={{.State.ExitCode}} RestartCount={{.RestartCount}} Policy={{.HostConfig.RestartPolicy.Name}} Image={{.Config.Image}}' | tee "$out/qdrant-status.txt"
docker inspect docker-qdrant-1 --format 'ComposeProject={{index .Config.Labels "com.docker.compose.project"}} ComposeService={{index .Config.Labels "com.docker.compose.service"}}' | tee "$out/qdrant-ownership.txt"
printf '%s\n' "PRIVATE files: $out. Do not share without redaction; no containers modified."
