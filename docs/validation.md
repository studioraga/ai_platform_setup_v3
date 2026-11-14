# Validation and acceptance matrix

| Gate | Exact check | Required result | Limitations |
|---|---|---|---|
| Source | `scripts/validate_baseline.sh` | 0, required files present | Not an application test |
| A | `preflight.sh`, Docker/port inventory | scoped Docker and host fit | Does not authorize system changes |
| B | `install_base_ubuntu2404.sh` then apt review | prerequisites available | Host mutation requires review |
| C | `scripts/verify_python.sh` | API tests, Ruff, Black, OpenAPI | Scratch app only |
| D | `scripts/verify_react.sh`, `scripts/install_playwright_e2e.sh` | non-empty lint, build, unit, E2E | Browser availability varies |
| E | `validate_env.sh`, Compose guard, `smoke.sh` | health, auth negative, SQL/Redis/Qdrant | Loopback demo; persistence checked separately |
| F | CLI inventory, isolated Terraform plan, Helm lint/template | offline proof | No Azure or K8s runtime |
| R05 | shared R05 contract for two reviewed wheels | 7 cases per wheel, exit 0 | limited public API, SemVer review required |
| Matrix | `python3 section1_audit.py` | exactly 16 valid rows | all `NOT_RUN` until specific drills |
| Evidence | `verify_evidence_selection.py` | selection and manifest match | hashes do not certify correctness |
| Signoff | manual reviewer with evidence | explicit recorded disposition | M30 production freeze always separate |

## Node1 historical checkpoint (2026-11-13)

Provided logs show installed cloud tools and offline IaC gates pass; reconstructed Form 8825 tests 32 pass but active package modules deleted; Governance baseline 290, M30 6, and R05 shared consumer tests 7/7 each. The uploaded latest log has 45 selected R05 evidence files but only 35 manifest entries; `sha256sum -c` over those 35 is **not** coverage of 45. The R05 compatibility review also still contains `PENDING NODE1 VERIFICATION` although the shared-contract tests passed. Correct those before any baseline acceptance using `scripts/qualification/reconcile_r05_evidence.py --root .` and `scripts/qualification/verify_evidence_selection.py --write`; then verify without `--write`. Full R05 and R01–R16 sign-off remain pending.

## Expected hard blockers

- Fresh host lacks secrets: create with `create_env.sh`; the source baseline has no credentials.
- Existing port occupied: guard blocks; do not bypass without ownership verification.
- Original source repositories unavailable: skip external project suites as `NOT_RUN` with explanation.
- Historical Governance v0.29.0 wheel missing: use authoritative tag and a reproducible build; never invent.
- Any R05 consumer contract fails: retain failure and do not mark compatibility PASS.
- Missing evidence file: fail manifest closure and preserve negative report.

## Updated actual Node1 checkpoint: 2026-11-14

| Gate | Logged outcome |
|---|---|
| ShellCheck / source validation | PASS |
| Python/FastAPI | 5 passed, 1 Starlette/httpx deprecation warning |
| React | build/lint PASS, 3 Vitest passed |
| Playwright | 1 E2E passed |
| Docker practice stack | existing containers reused, `smoke.sh` exit 0 |
| Terraform offline | fmt/init/validate/plan exit 0 |
| Helm | lint and render exit 0 |
| Evidence | 45 selected and 45 hashed, verification exit 0 |
| R05 | 7 shared tests pass against each verified wheel (prior logs) |
| R01–R16 | 16 NOT_RUN; NOT ACCEPTED |
| Git | initialized only; `git add -n` does not stage; commit failed |

**Correction:** Any earlier paragraph claiming the evidence manifest still had 35 of 45 files is historical and superseded by this section. Evidence integrity does not equal functional acceptance.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
