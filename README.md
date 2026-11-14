# Principal AI Platform Practice — portable v3 baseline

**Status:** Source-only baseline prepared from the Node1 November 13, 2026 snapshot. This is a **reusable local/offline engineering training environment**, **not** a production Azure/AKS deployment, and does not approve M30 release or Section 1 competency sign-off.

## Fresh-clone quick start (Ubuntu 24.04, x86-64)

```bash
./scripts/fresh_machine_preflight.sh
./scripts/validate_baseline.sh
# Review proposed packages, then run if needed:
./install_base_ubuntu2404.sh
# Install official Docker Engine + Compose v2, uv, Node 22 LTS, and optional cloud CLIs (see docs/deployment.md)
./scripts/verify_python.sh
./scripts/verify_react.sh
./scripts/install_playwright_e2e.sh
./create_env.sh && ./validate_env.sh
./scripts/guard_before_compose.sh  # deliberately blocks occupied ports, including existing practice services
# If clean and approved: docker compose pull && docker compose up -d --wait
./smoke.sh
./scripts/verify_cloud_tools.sh
```

The repository includes actual source under `labs/`, React `package-lock.json`, Terraform HCL, Helm chart templates and the shared R05 SDK contract under `tests/r05/`. Do not commit `.env`, `secrets/`, `reports/`, virtualenvs, `node_modules`, downloaded CLI installers, private code snapshots or built wheels.

## Baseline scope and evidence

On Node1 the user-provided logs show A–F local/offline checks, 290 Governance baseline tests, 6 M30 tests, Form 8825 reconstructed-snapshot 32 tests, historical Governance v0.29.0 and corrected snapshot v0.30.0 wheel validation, and shared consumer contracts 7/7 on each wheel. **These historical results are not automatically reproduced on a fresh machine.** The original Form 8825 working tree had five deleted tracked modules. Governance v0.30.0 changes were uncommitted. R01–R16 remain open. Do not deploy or release based on smoke evidence.

## Documentation

- [Instructions and setup stages](docs/instruction.md)
- [Architecture and trust boundaries](docs/architecture.md)
- [Fresh-machine deployment](docs/deployment.md)
- [Validation and acceptance](docs/validation.md)
- [Verification script index](docs/verrification_scripts.md) (original requested spelling)
- [Dependency inventory](docs/dependencies.md)
- [R05 compatibility and next milestones](docs/roadmap.md)
- [Git review and promotion](docs/git_release.md)

Legacy patch notes and runbooks remain historical records; this README and docs are authoritative for the portable baseline.

## Baseline reconciliation, 2026-11-14 (supersedes older pending statements)

Node1 source validation and ShellCheck, Python (5 tests), React build/lint (3 component tests), Playwright (1 E2E), PostgreSQL/Redis/Qdrant practice smoke, Terraform offline validation/plan, Helm lint/render, and the 45/45 local evidence manifest passed in the supplied logs. Docker Engine 29.5.1 was recovered by starting the existing system daemon; the three named practice containers and their named volumes were **reused, not recreated**.

**Historical note:** the original preparation checkout initially had no Git commit after `git add -n`. This was corrected during migration. On 2026-11-14, PR #1 merged source-only baseline commit `66ac5b19a7a1f74f64f1e9668739abae0d6375f7` into `main` at `3f429aacb889f55521671cb013a73ed5550d90be` (as confirmed by the repository owner). Subsequent engineering work must use a new feature branch; see [Git runbook](docs/git_release.md).

R05: both Governance v0.29.0 and corrected v0.30.0 wheel consumers previously passed 7 shared tests; full public API, class-method, schema, exception and pre-1.0 SemVer review remains open. Requirements R01–R16 are **16 NOT_RUN**. No M30 production freeze is approved.

## Verified baseline reference

[Baseline qualification checkpoint](docs/baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.

## Repository provenance

[Repository migration](docs/repository_migration.md) describes the migration into the existing Studio Raga GitHub repository and its acceptance boundaries.

## R05 post-baseline engineering increment

[R05 extended SDK compatibility engineering specification](docs/r05/R05_EXTENDED_COMPATIBILITY_SPEC.md) defines phase-by-phase static API inventory, public-export review, dual-wheel runtime contracts, serialization/exception/denial tests and a **proposed** pre-1.0 policy requiring owner approval. Do not treat R05-A discovery results as final compatibility or production authorization.

## R05-B public API review checkpoint

The R05 discovery branch includes the pushed `590468d` candidate-export increment; two inventories contain 1,879 (v0.29) and 1,929 (v0.30) **unapproved** static candidates. Follow [R05-B/C review plan](docs/r05/R05_BC_REVIEW_PLAN.md) for triage, documented export classification and isolated wheel runtime probes. No `main` merge or R05 sign-off is implied.
