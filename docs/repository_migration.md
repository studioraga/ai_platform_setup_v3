# Principal AI Platform v3 — Repository Migration

## Repository

Target: https://github.com/studioraga/ai_platform_setup_v3

Original destination baseline:
8e434dabf5f53198031d380b12ed836e28c98a22

Source:
principal_ai_platform_setup_v3

Migration method:
Reviewed export of the source Git index into the existing
destination repository, preserving destination Git history.

## Engineering scope

Portable Ubuntu 24.04 amd64 engineering environment:

- Python 3.12 / FastAPI
- Node.js 22 / React / Vite / Vitest / Playwright
- PostgreSQL 17.6
- Redis 7.4.5-alpine
- Qdrant v1.15.4
- Terraform offline experiments
- Helm chart linting and rendering
- Governance SDK shared-consumer verification

## Recorded Node1 qualification

- Source validation and ShellCheck: PASS
- Python: 5 tests PASS
- React/Vitest: 3 tests PASS
- Playwright: 1 E2E PASS
- PostgreSQL/Redis/Qdrant smoke: PASS
- Terraform offline validation/plan: PASS
- Helm lint/render: PASS
- Historical evidence integrity: 45/45 PASS
- Governance v0.29.0 shared contracts: 7 PASS
- Governance v0.30.0 shared contracts: 7 PASS

These are recorded Node1 results, not fresh-machine results.

## Dependency references

- requirements/python-direct.txt
- requirements/python-node1-resolved-20261113.txt
- labs/react-ui/package.json
- labs/react-ui/package-lock.json
- compose.yaml
- labs/terraform-offline/main.tf
- labs/helm/principal-platform/
- docs/dependencies.md

Python resolved versions are a historical environment snapshot,
not a complete hash-locked cross-platform installation lock.

## Security and release boundaries

Do not include Node1 runtime secrets, reports, virtual
environments, Docker volumes, downloaded executables,
historical SDK wheels, or unrelated project repositories.

R01-R16 are not independently accepted.

The seven shared R05 tests do not prove full public API
or pre-1.0 semantic-version compatibility.

Governance M30 production release is not approved.
Live cloud deployment is not qualified.

## Planned follow-on engineering

1. R05 extended SDK compatibility
2. R03 OpenAPI version compatibility
3. R09 PostgreSQL tenant isolation and RLS
4. R10 Redis/Qdrant reliability and tenant isolation
5. R06/R07 governed RAG and agent execution
6. R11-R16 identity, telemetry, CI/CD and architecture
