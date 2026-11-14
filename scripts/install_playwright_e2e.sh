#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/labs/react-ui"
[[ -f "$APP/package.json" ]] || { echo 'ERROR: run React scaffold first' >&2; exit 2; }
cd "$APP"
npx playwright install chromium
npx playwright test --config=playwright.config.ts --reporter=line
