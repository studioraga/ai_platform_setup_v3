# Principal AI Platform v3 — Baseline Qualification Checkpoint

Date: 2026-11-14
Reference host: Node1, Ubuntu 24.04 amd64

## Purpose

Establish a reusable source-only engineering environment
for incremental Principal AI Platform development.

This is not a production deployment, enterprise security
certification, or final Section 1 acceptance.

## Verified Node1 scope

| Gate | Observed result |
|---|---|
| Source and ShellCheck | PASS |
| Python/FastAPI | 5 tests PASS |
| React/Vitest | Build/lint PASS, 3 tests PASS |
| Playwright | 1 E2E PASS |
| PostgreSQL | 17.6, local smoke PASS |
| Redis | 7.4.5-alpine, local smoke PASS |
| Qdrant | v1.15.4, local smoke PASS |
| Terraform | Offline fmt/init/validate/plan PASS |
| Helm | Lint/render PASS |
| Evidence integrity | 45 selected / 45 hashed PASS |
| Governance v0.29.0 | 7 shared consumer tests PASS |
| Governance v0.30.0 | 7 shared consumer tests PASS |
| R01-R16 | 16 NOT_RUN |

## Runtime reference

- Python 3.12.3
- Node.js 22.23.3
- npm 10.9.9
- Docker Engine 29.5.1
- Docker Compose 5.1.3

Actual image digests and other host tool paths are recorded
in the ignored Node1 dependency-inventory report.

## Dependency authorities

- requirements/python-direct.txt
- requirements/python-node1-resolved-20261113.txt
- labs/react-ui/package.json
- labs/react-ui/package-lock.json
- compose.yaml
- labs/terraform-offline/main.tf
- labs/helm/principal-platform/
- docs/dependencies.md

The historical Python snapshot is not a hash-locked
cross-platform installation lock.

Container image tags alone are not immutable image identities.
Fresh hosts must independently qualify their runtime images.

## Security and repository boundaries

Git contains source code, tests, documentation and declared
dependencies only.

Do not commit runtime secrets, databases, Docker volumes,
downloaded executables, build artifacts, historical wheels,
local project snapshots or evidence reports.

The staged-index audit must pass, followed by independent
secret scanning and manual diff inspection.

## Known limitations

- One Starlette/httpx deprecation warning in Python tests.
- R05 covers seven shared consumer contracts, not the complete
  historical SDK public surface.
- R01-R16 requirement-level acceptance is incomplete.
- Form 8825 active source is independently qualified elsewhere.
- Governance M30 production-release approval is not granted.
- Cloud infrastructure deployment is not qualified.
- Fresh-machine end-to-end reproduction remains to be executed.

## Next independent engineering increments

1. R05: class and instance methods, documented exports and
   re-exports, serialization, exceptions, and pre-1.0 SemVer policy.
2. R03: FastAPI/OpenAPI consumer compatibility.
3. R09: PostgreSQL RLS, tenant isolation and concurrency.
4. R10: Redis idempotency/replay and Qdrant tenant filtering.
5. R06/R07: RAG evaluation and policy-governed agents.
6. R11-R16: identity, observability, CI/CD, reliability,
   architecture and principal-level engineering evidence.

Each increment requires source review, negative tests,
reproducible evidence, and independent acceptance.

## Git acceptance

Baseline Git commit: NOT YET RECORDED
Remote push: NOT YET VERIFIED
Fresh-clone acceptance: PENDING
