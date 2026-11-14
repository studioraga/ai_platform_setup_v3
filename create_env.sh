#!/usr/bin/env bash
# Initialize local-only practice credentials once. Never rotate or overwrite partial credentials.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
umask 077
files=("$ROOT/.env" "$ROOT/secrets/redis.acl" "$ROOT/secrets/redis_password")
existing=0
for f in "${files[@]}"; do
  if [[ -e "$f" || -L "$f" ]]; then
    ((existing+=1))
  fi
done
if (( existing == ${#files[@]} )); then
  for f in "${files[@]}"; do
    if [[ -L "$f" || ! -f "$f" ]]; then
      echo "FAIL: Unsafe credential path: $f" >&2
      exit 2
    fi
  done

  echo 'Existing credential set detected; not modifying it. Run ./validate_env.sh.'
  exit 0
fi
if (( existing != 0 )); then
  echo "FAIL: incomplete credential set ($existing/${#files[@]} present); refusing changes to avoid inconsistent secrets" >&2
  printf 'Check these paths (do not paste contents):\n' >&2
  printf '  %s\n' "${files[@]}" >&2
  exit 2
fi
mkdir -p "$ROOT/secrets"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import secrets,sys
root=Path(sys.argv[1]); redis=secrets.token_hex(24)
(root/'.env').write_text('POSTGRES_PASSWORD='+secrets.token_hex(24)+'\nQDRANT_API_KEY='+secrets.token_hex(24)+'\n')
(root/'secrets'/'redis.acl').write_text('user default on >'+redis+' ~* &* +@all\n')
(root/'secrets'/'redis_password').write_text(redis+'\n')
for path in (root/'.env',root/'secrets'/'redis.acl',root/'secrets'/'redis_password'):
    path.chmod(0o600)
print('Generated new local credentials with 0600 permissions. Do not commit or share them.')
PY
