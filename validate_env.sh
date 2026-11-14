#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
for name in POSTGRES_PASSWORD QDRANT_API_KEY; do
 val="$(grep -E "^${name}=" .env 2>/dev/null | cut -d= -f2- || true)"
 [[ ${#val} -ge 24 ]] || { echo "FAIL: ${name} missing/too short"; exit 1; }
done
for file in .env secrets/redis.acl secrets/redis_password; do
 [[ -s "$file" ]] || { echo "FAIL: missing $file"; exit 1; }
 perm="$(stat -c %a "$file")"; [[ "$perm" == '600' ]] || { echo "FAIL: $file permissions $perm (expected 600)"; exit 1; }
done
 echo 'PASS: credentials files present with expected permissions'
