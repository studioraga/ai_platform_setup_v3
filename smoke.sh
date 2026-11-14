#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
./validate_env.sh
docker info >/dev/null
# Read-only checks target the configured principal-ai-platform-practice Compose project.
docker compose config --quiet
for service in postgres redis qdrant; do
 cid="$(docker compose ps -q "$service")"
 [[ -n "$cid" ]] || { echo "ERROR $service is not running"; exit 2; }
done
for service in postgres redis; do
 cid="$(docker compose ps -q "$service")"
 good=0
 for ((attempt=1; attempt<=24; attempt++)); do
   echo "Waiting for $service health: attempt $attempt/24"
   [[ "$(docker inspect -f '{{.State.Health.Status}}' "$cid" 2>/dev/null || true)" == healthy ]] && { good=1; break; }
   sleep 2
 done
 [[ "$good" == 1 ]] || { echo "ERROR $service not healthy"; exit 2; }
done
docker compose exec -T postgres psql -U interview -d interview -v ON_ERROR_STOP=1 -Atc 'SELECT current_database(), 2+2;'
docker compose exec -T postgres psql -U interview -d interview -v ON_ERROR_STOP=1 -Atc 'BEGIN; CREATE TEMP TABLE platform_smoke(id int); INSERT INTO platform_smoke VALUES (42); SELECT COUNT(*) FROM platform_smoke; ROLLBACK;'
docker compose exec -T redis sh -c 'REDISCLI_AUTH="$(cat /run/secrets/redis_password)" redis-cli ping' | grep -qx PONG
# Use environment without printing secret or command to log.
set -a
# shellcheck source=/dev/null
source .env
set +a
curl -fsS --retry 8 --retry-delay 2 --max-time 10 -H "api-key: $QDRANT_API_KEY" http://127.0.0.1:16333/collections | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "ok"'
unauth="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:16333/collections)"
[[ "$unauth" == 401 || "$unauth" == 403 ]] || { echo "ERROR Qdrant no-auth returned $unauth"; exit 2; }
echo 'PASS: isolated local PostgreSQL, Redis and Qdrant basic checks'
