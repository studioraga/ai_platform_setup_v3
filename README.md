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

The preparation directory was initialized with `git init -b main`, but **no commit or push happened**: `git add -n` was a dry run, followed immediately by a failed `git commit` with no staged files. Before the real initial commit, exclude downloaded tool binaries and local backup scripts, run a staged-index audit, inspect and scan the diff, and push only to an authorized remote. See [Git runbook](docs/git_release.md).

R05: both Governance v0.29.0 and corrected v0.30.0 wheel consumers previously passed 7 shared tests; full public API, class-method, schema, exception and pre-1.0 SemVer review remains open. Requirements R01–R16 are **16 NOT_RUN**. No M30 production freeze is approved.

## Verified baseline reference

[Baseline qualification checkpoint](docs/baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.

## Repository provenance

[Repository migration](docs/repository_migration.md) describes the migration into the existing Studio Raga GitHub repository and its acceptance boundaries.
