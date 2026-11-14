# Node1 v3 — Steps D–F and Sections 4–7

## Corrected findings from November 10 logs
- **Phase A: Docker is functional.** Existing `docker-qdrant-1` (CCTV project) restarted repeatedly (exit 1); mounts point to `cctv-ip-or-lan-usb-camera-ingest-ai-inference/data/qdrant*`. Its application logs were not included in the shared pasted text, so cause remains unproven. Do not alter its container or volumes.
- **Phase B: PASS**: apt completed, gcc/g++/make/pkg-config/Redis CLI/PostgreSQL client/ShellCheck/jq checked; Python 3.12 virtualenv/pip checked.
- **Phase C: functional tests PASS (4), lint FAIL (3 errors)** in v2. v3 fixes unused `HTTPException` import, import sorting, formatting and adds explicit async fixture loop scope. Starlette's httpx TestClient deprecation is an upstream compatibility warning and is **not** silently suppressed. v3 adds fifth upper-bound test and enforces lint + formatting + tests in the script.

## Install v3 in parallel with v2 (never overwrite your existing v2 repo)
```bash
cd ~/dev/pub/ai-platform-principal-prep
unzip ~/Downloads/CV/28_USContract/Principal_AI_Platform_Setup_v3_Corrected.zip
cd principal_ai_platform_setup_v3
for f in ./*.sh ./scripts/*.sh; do bash -n "$f" || exit 1; done
python3 section1_audit.py
```

## Phase A / B retention and Phase C corrective check
No need to re-run apt. Copy v2 Phase A/B log evidence into v3 only after verifying it does not contain private data. Do not mark the old Qdrant service as healthy.
```bash
set -o pipefail
./preflight.sh | tee reports/preflight_v3.log
./diagnose_docker.sh | tee reports/docker_v3.log
./scripts/verify_python.sh 2>&1 | tee reports/python_setup.txt
cd labs/python-api && source .venv/bin/activate
ruff check platform_demo.py tests
black --check platform_demo.py tests
python -m pytest -q tests
python -m pip check
cd ../.. && deactivate
```
Expected: at least five passing scratch API tests, no lint violations; upstream deprecations can remain documented. Use `pip` installed in the uv environment or `uv pip check` if pip executable isn't present.

## Phase D React
```bash
./scripts/verify_react.sh 2>&1 | tee reports/react_setup.txt
cd labs/react-ui
npx playwright install chromium
npm run build
npx vitest run --environment jsdom src/App.test.tsx
cd ../..
```
Vite template version is not pinned. Record `node --version`, `npm --version`, and the generated package-lock. Install browser shared libraries only if Playwright says they are missing. A browser **installation** is not an E2E test: add Playwright `webServer` and a browser navigation assertion before claiming E2E PASS.

## Phase E Isolated PostgreSQL, Redis, Qdrant
```bash
./create_env.sh && ./validate_env.sh
./scripts/guard_before_compose.sh
# Only when the guard passes:
docker compose config --quiet
docker compose pull
docker compose up -d --wait
docker compose ps
./smoke.sh 2>&1 | tee reports/local_services_smoke.txt
```
If port guard finds the **same** practice stack already using ports, inspect `docker compose ps -a` and use `docker compose up -d --wait` only if the running services belong to the expected `principal-ai-platform-practice` project. Never stop/delete the historical `docker` project. Local HTTP Qdrant credentials are suitable only for localhost experiments; do not expose to LAN or Internet. The Compose Qdrant key is visible to Docker administrators. Follow up with persistence tests after restart, tenant isolation / ACL / RLS drills, and record image digests.

## Phase F Cloud and delivery
```bash
./scripts/verify_cloud_tools.sh
```
Install missing CLI tools using vendor docs: Azure CLI, azd, Terraform, kubectl, Helm, VS Code. Re-run inventory. Do not perform `terraform apply` or Azure provisioning without permission and budget. Verify offline `terraform fmt -check`/`terraform validate`, Helm `lint`/`template`, SDK wheel build, and local pipeline quality gates.

## Section 4 Original projects
For each project: extract historical archive to distinct `source-verification` directory; **do not** run tests against production DB or mutate an existing branch. Inventory with:
```bash
./scripts/verify_original_project.sh form8825 /path/to/form8825
./scripts/verify_original_project.sh governance /path/to/portable-agentic-ai-governance
```
For Form8825: inspect source README/requirements/pyproject, database URL, Alembic scripts, OpenAPI snapshot, test isolation and frontend package scripts first. Only then create project-specific virtualenv, install declared dependencies, run `pytest`, migration checks, API contract tests, `npm ci`, frontend build and Playwright tests. Record exact commands, exit codes, test counts, migrations, DB isolation and baseline commit.
For governance: inspect pyproject and tests, install declared extras, run the documented test subsets and security/gate verifiers, build wheel using `python -m build`, run `twine check`, install wheel into a clean venv, discover package metadata/public import path, and execute consumer smoke tests. Do not claim a PyPI release just because wheel builds.

## Section 5 Requirements → evidence → gaps
Update each R01–R16 CSV row only after real evidence exists. Three distinct claims: historical source evidence, practice host runtime readiness, and production qualification. For `PASS`, attach real relative artifact path and acceptance_result, and ensure the evidence file exists. Run `python3 section1_audit.py`. Do not mark Azure deployment, OIDC, SDK published release, production RAG, or Copilot performance as PASS without demonstration.

## Section 6 Gap drills
Build (1) versioned API+SDK+contract regression, (2) PostgreSQL RLS/keyset/optimistic concurrency, (3) Redis idempotency/outbox and poison-message DLQ, (4) Qdrant tenant-filtered RAG with evaluation, (5) OIDC JWKS/expiry/tenant tests, (6) OpenTelemetry failed-request tracing, (7) Copilot vs manual matched task quality analysis, (8) Terraform/Helm validated minimal cloud architecture. Each produces a runnable repository, tests, ADR, logs, and security review.

## Section 7 Evidence + acceptance
```bash
cp reports/section1_acceptance.template.md reports/section1_acceptance.md
./scripts/section1_checklist.sh
python3 section1_audit.py
./scripts/evidence_manifest.sh
sha256sum -c reports/evidence.sha256
```
Review correctness, operability, and communication independently; preserve exact tested artifact hashes. The manifest hashes only allowlisted reports and does NOT sanitize their contents. Before sharing, redact source URLs containing tokens, credentials, environment variables and sensitive logs.

## Status as of supplied logs
A Docker API PASS; historical CCTV Qdrant BLOCKED separate; B system dependencies PASS; C API tests PASS, v2 lint FAIL, v3 correction **locally source-reviewed but not yet executed on Node1**; D/E/F NOT_RUN; original Form8825/Governance NOT_RUN; R01-R16 NOT_RUN and signoff PENDING.
