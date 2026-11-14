#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/labs/react-ui"
[[ -f "$APP/package.json" && -f "$APP/package-lock.json" ]] || { echo 'ERROR: React project or lockfile missing' >&2; exit 2; }
cd "$APP"
node --version
npm --version
if [[ ! -d node_modules ]]; then
  npm ci --no-audit
fi
for dep in vitest @testing-library/react jsdom @playwright/test oxlint; do
  node -e "require.resolve('$dep/package.json')" >/dev/null 2>&1 || {
    echo "ERROR: missing $dep; review package-lock.json and run npm ci" >&2
    exit 3
  }
done
# Oxlint 1.93.0 on this Node1 snapshot does not expand 'src' as a directory.
# Explicit file names are required; NEVER accept a zero-file lint pass.
files=(src/App.tsx src/App.test.tsx src/main.tsx)
for required in "${files[@]}"; do
  [[ -f "$required" ]] || { echo "ERROR: missing $required" >&2; exit 4; }
done
lint_files="$(./node_modules/.bin/oxlint --no-ignore --debug=files "${files[@]}")"
for required in "${files[@]}"; do
  grep -Fxq "$required" <<<"$lint_files" || {
    echo "ERROR: Oxlint does not discover $required" >&2
    exit 5
  }
done
printf 'PASS: Oxlint discovers %s source files\n' "${#files[@]}"
npm run build
npm run lint
./node_modules/.bin/vitest run --environment jsdom src/App.test.tsx
printf 'PASS: React build, nonempty lint, and isolated component tests. Playwright remains separate.\n'
