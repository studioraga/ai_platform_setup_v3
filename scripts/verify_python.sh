#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/labs/python-api"
cd "$APP"
command -v uv >/dev/null || { echo 'ERROR: uv is required; see docs/deployment.md' >&2; exit 2; }
[[ -x .venv/bin/python ]] || uv venv --python 3.12 .venv
# The original complete Node1 freeze is a reference, not a cross-platform lock.
# Reproduce observed versions with --frozen-snapshot only after manual review.
if [[ "${1:-}" == '--frozen-snapshot' ]]; then
  uv pip install --python .venv/bin/python -r "$ROOT/requirements/python-node1-resolved-20261113.txt"
else
  uv pip install --python .venv/bin/python -r "$ROOT/requirements/python-direct.txt"
fi
uv pip check --python .venv/bin/python
.venv/bin/ruff check platform_demo.py tests
.venv/bin/black --check platform_demo.py tests
.venv/bin/python -m pytest -q tests
.venv/bin/python - <<'PYOPENAPI'
from platform_demo import app
import json
from pathlib import Path
Path('openapi.generated.json').write_text(json.dumps(app.openapi(), indent=2)+'\n')
print('PASS: source-backed Python API tests and OpenAPI generation')
PYOPENAPI
