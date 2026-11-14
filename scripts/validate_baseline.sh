#!/usr/bin/env bash
# Source and working-copy checks. Does not assume existing runtime secrets are absent.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
from pathlib import Path
required = [
    'README.md', 'compose.yaml', 'create_env.sh', 'validate_env.sh',
    'labs/python-api/platform_demo.py', 'labs/python-api/tests/test_platform_demo.py',
    'labs/react-ui/package.json', 'labs/react-ui/package-lock.json',
    'labs/react-ui/src/App.test.tsx', 'labs/react-ui/e2e/starter.spec.ts',
    'labs/terraform-offline/main.tf', 'labs/helm/principal-platform/Chart.yaml',
    'tests/r05/test_shared_contract.py', 'requirements/python-direct.txt',
    'docs/instruction.md', 'docs/architecture.md', 'docs/validation.md',
    'docs/verrification_scripts.md', 'docs/deployment.md',
    'scripts/check_git_baseline.sh','scripts/record_dependency_inventory.sh',
]
missing = [p for p in required if not Path(p).is_file()]
if missing:
    raise SystemExit('FAIL: missing source baseline files: ' + ', '.join(missing))
print(f'PASS: {len(required)} required source files present')
PY
# Git checks only when Git has been initialized. This is not a command to initialize Git.
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  repo_root="$(git rev-parse --show-toplevel)"
  if [[ "$repo_root" != "$ROOT" ]]; then
    echo "FAIL: unexpected enclosing Git repository: $repo_root" >&2
    exit 2
  fi
  for path in .env secrets/redis.acl secrets/redis_password reports/section1-closure/evidence.sha256; do
    if git ls-files --error-unmatch -- "$path" >/dev/null 2>&1; then
      echo "FAIL: private/runtime file tracked by Git: $path" >&2
      exit 2
    fi
    if ! git check-ignore -q -- "$path"; then
      echo "FAIL: private/runtime file not ignored: $path" >&2
      exit 2
    fi
  done
  for path in labs/python-api/platform_demo.py labs/react-ui/package-lock.json labs/terraform-offline/main.tf labs/helm/principal-platform/Chart.yaml tests/r05/test_shared_contract.py; do
    if git check-ignore -q -- "$path"; then
      echo "FAIL: required source incorrectly ignored: $path" >&2
      exit 2
    fi
  done
  echo 'PASS: local credentials/evidence excluded from Git; labs source eligible for tracking'
else
  echo 'INFO: Git is not initialized here; Git tracking checks deferred until repository initialization'
fi
python3 - <<'PY'
from pathlib import Path
import stat
for name in ('.env', 'secrets/redis.acl', 'secrets/redis_password'):
    p = Path(name)
    if p.exists():
        if not p.is_file() or p.is_symlink():
            raise SystemExit(f'FAIL: unexpected credential file type: {name}')
        mode = stat.S_IMODE(p.stat().st_mode)
        if mode & 0o077:
            raise SystemExit(f'FAIL: credential file accessible to group/others: {name} (mode={mode:o})')
        print(f'PASS: local credential permission {name}: {mode:o}')
print('PASS: source checks do not disclose credential values')
PY
for p in ./*.sh ./scripts/*.sh ./scripts/qualification/*.sh; do
  [[ -f "$p" ]] || continue
  bash -n "$p"
done
python3 -m compileall -q section1_audit.py scripts/qualification tests/r05 labs/python-api
python3 section1_audit.py
if command -v shellcheck >/dev/null 2>&1; then
  # Run ShellCheck on applicable scripts; report tool absence as SKIP, not PASS.
  mapfile -t shell_scripts < <(find . -maxdepth 1 -type f -name '*.sh'; find scripts -type f -name '*.sh')
  shellcheck --severity=warning "${shell_scripts[@]}"
else
  echo 'SKIP: shellcheck not installed'
fi
printf '%s\n' 'PASS: portable baseline source/permission checks; runtime and R01-R16 remain separate gates'
