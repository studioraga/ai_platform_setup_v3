# Dependency inventory and reproducibility policy

| Layer | Node1 observed/required | Source or provisioning | Fresh-machine evidence |
|---|---|---|---|
| OS | Ubuntu 24.04 amd64 (Node1) | `lsb_release`, `dpkg` | preflight |
| Python | 3.12.3 | Ubuntu 24.04 Python | `python3 --version` |
| Python env manager | `uv` (version depends on approved installation) | official Astral installer/managed package | `uv --version` |
| Python direct libraries | FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic, psycopg, Redis, Qdrant, pytest, Ruff, Black, mypy, OTel, build, Twine, PyYAML etc. | `requirements/python-direct.txt` | verify_python |
| Historical resolved Python dependencies | 2026-11-13 Node1 freeze, **not cross-platform lock** | `requirements/python-node1-resolved-20261113.txt` | optional review |
| Node | Node 22 LTS (Node1 previously v22.23.3) | approved Node installation | `node --version` |
| NPM | Match installed Node, use committed `package-lock.json` | `npm ci` | React build/tests |
| Browser | Chromium via Playwright | `npx playwright install chromium` | Playwright tests |
| Docker | Engine 29.5.1 observed; Compose v2 | official signed Docker Ubuntu repo | `docker info; docker compose version` |
| Datastore images | postgres:17.6, redis:7.4.5-alpine, qdrant/qdrant:v1.15.4 | `compose.yaml` | smoke/persistence |
| Cloud tools | az 2.92.0, azd 1.37.3, Terraform 1.17.2, kubectl 1.37.2, Helm 4.3.1, gh 2.45.0, VS Code 1.146.0 | official vendor repos/checksummed binaries | inventory + offline exercises |
| Host build packages | build-essential, pkg-config, libssl-dev, libffi-dev, libpq-dev, python3-venv, postgresql-client, redis-tools, shellcheck, git-lfs, jq and more | `install_base_ubuntu2404.sh` | apt version manifest |
| Original repos | Form 8825 and Governance are **optional external** projects | use explicit paths; never copied | independent qualification |

**Important:** Docker image tags are not content-addressed. Before compliance release record exact `RepoDigests` from a reviewed pull and inspect image architecture/vulnerabilities. Node1 resolved pip file lacks hashes and may include platform-specific wheels. npm lock is committed; neither the full host nor pip ecosystem is fully deterministic on arbitrary machines. Prefer an approved `uv.lock` and SHA-pinned image digests for a later frozen production revision.

Official reference sites: https://docs.docker.com/engine/install/ubuntu/ ; https://docs.astral.sh/uv/ ; https://nodejs.org/ ; https://kubernetes.io/docs/tasks/tools/ ; https://helm.sh/docs/ ; https://developer.hashicorp.com/terraform/install ; https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux ; https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd ; https://code.visualstudio.com/docs/setup/linux ; https://playwright.dev/docs/browsers .

## Verified dependency update from the latest logs

- Docker Engine **29.5.1**, Compose **5.1.3**, context `default`, `/var/lib/docker`. Starting the daemon did not enable it permanently.
- PostgreSQL image `postgres:17.6`, Redis `redis:7.4.5-alpine`, Qdrant `qdrant/qdrant:v1.15.4`; existing named volumes reused; images are **tag-pinned, not digest-locked**.
- Python scratch lab 5 tests passed; Node **22.23.3**, npm **10.9.9**, React/Vite build, Vitest 3, Chromium E2E 1 passed.
- Earlier verified tooling: Terraform 1.17.2, Helm 4.3.1, Azure CLI 2.92.0, azd 1.37.3, kubectl 1.37.2, gh 2.45.0, VS Code 1.146.0. Fresh host must independently install/verify them.
- Preserve the React `package-lock.json` in Git. Python direct requirement ranges and historical freeze are not a hash-locked cross-platform lock. Record actual fresh-host versions with `scripts/record_dependency_inventory.sh`.
- Exclude downloaded tools/keyrings and checksums in `labs/cloud-tool-install/` from the source-only baseline; use reviewed vendor sources on each machine.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
