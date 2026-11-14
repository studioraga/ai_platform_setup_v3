# Principal AI Platform v3.1 — source-audited sequential runbook

## Important baseline
Phase A Docker API PASS, historical CCTV Qdrant restart issue open and isolated. Phase B package installation PASS. Phase C five API tests PASS; Ruff/Black/dependency check PASS. Revalidate the v3.1 source scripts using the strict gate. No D/E/F project tests are claimed to have run.

## Step 4.2 — source acceptance
From root: `./scripts/validate_source.sh`. This uses `set -Eeuo pipefail` so a ShellCheck finding stops the gate. It handles `/etc/os-release` and generated `.env`/venv activation as targeted exceptions; never turn off ShellCheck globally. `shellcheck --severity=style ./*.sh ./scripts/*.sh` can also be run directly.

## Step 4.4 — immutable-ish evidence, before changing packages
In root: `source labs/python-api/.venv/bin/activate`, then `python -m pip freeze > reports/python_requirements_resolved.txt`, `python -m pip check | tee reports/python_dependency_check.txt`, `python -m pytest -v labs/python-api/tests | tee reports/python_tests.txt` (run tests from labs/python-api so module resolves), `ruff check labs/python-api/platform_demo.py labs/python-api/tests`, `black --check ...`; `deactivate`. Keep resolved list; for a true reproducible baseline commit pyproject and uv.lock, use `uv sync --locked` in the lab project. Do not confuse freeze with a lockfile.

## Phase D — React
Check Node Vite engine requirement with `npm view vite@latest engines --json`, then select a supported nvm Node version; preserve system install. Run `./scripts/verify_react.sh` with `set -o pipefail` and tee output. Confirm npm lockfile, `npm run build`, `npx vitest run --environment jsdom src/App.test.tsx`. For E2E: `./scripts/install_playwright_e2e.sh`; if browser dependencies missing follow Playwright diagnosis. Record separate execution output and do not claim E2E from browser install alone.

## Phase E — containers
Keep CCTV Qdrant separate; old project is `docker`, new project `principal-ai-platform-practice`. Ensure no stack already owns ports 15432/16379/16333. `./create_env.sh && ./validate_env.sh && ./scripts/guard_before_compose.sh` then `docker compose config --quiet && docker compose pull && docker compose up -d --wait && docker compose ps && ./smoke.sh`. The guard intentionally blocks a second run when mapped ports are in use; inspect `docker compose ps -a` first. Use `docker compose stop`, never `down -v` for routine stopping. Verify postgres persistence and Redis/Qdrant persistence separately; log images/digests. Passwords in Compose env can be inspected by Docker administrators; loopback exposure only, not production security.

## Phase F — cloud and delivery tooling
`./scripts/verify_cloud_tools.sh`; vendor installations for az, azd, Terraform, kubectl, Helm, VS Code. Record CLI versions. Offline Terraform `fmt -check`, `init -backend=false`, `validate`, `plan` for provider-free config. Helm lint/template static chart. These don't demonstrate cloud deployment. No apply/provision without budget and permissions.

## Section 4 — original projects
Extract and inspect archives independently under source-verification, preserving commits/README/pins and avoiding production DB side effects. Use `./scripts/verify_original_project.sh form8825 <path>` and `... governance <path>`. Confirm manifest and DB target before running test/migration scripts. For Form8825 verify extraction correctness, FastAPI, migrations, OpenAPI, frontend. For governance verify policy security, agent approval checks, package build, clean consumer installation, public imports. Record exact commands/exit codes/results; no claims from filenames alone.

## Section 5 — R01-R16
Update each CSV row only with existing evidence files and explicit acceptance results; run `python3 section1_audit.py`. Its checks are structural only, not proof of actual principal skill. Keep historical evidence, current host evidence and cloud-production demonstration distinct.

## Section 6 — gap exercises
API+SDK contract, SQL RLS and concurrency, Redis idempotency/DLQ, Qdrant tenant filtering, JWT/OIDC negative tests, OTel tracing, Copilot measurement, Terraform/Helm ADRs. Each requires runnable tests and explanation.

## Section 7 — acceptance
Create acceptance MD from template, run source gate, phase validation, original repo test gates, matrix audit. Generate `./scripts/evidence_manifest.sh` only on approved non-secret logs. `sha256sum -c reports/evidence.sha256`. Have a manual correctness, operability and communication review before marking Section 1 complete.
