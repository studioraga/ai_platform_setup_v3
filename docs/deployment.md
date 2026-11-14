# Deployment — reproducible new Ubuntu 24.04 machine

> This deploys a **loopback-only practice stack**, not production Azure/AKS. Obtain permission before installing host packages, adding Docker access or changing startup configuration.

## 0. Clone and inspect

```bash
git clone <AUTHORIZED_REPOSITORY_URL> principal_ai_platform_setup_v3
cd principal_ai_platform_setup_v3
./scripts/fresh_machine_preflight.sh
./scripts/validate_baseline.sh
```

Do not paste a placeholder clone URL unchanged. Inspect scripts before execution.

## 1. Host prerequisites

```bash
./install_base_ubuntu2404.sh
python3 --version; git --version
```

Install Docker Engine + Compose v2 from the official signed Ubuntu repository. Docker's post-install group membership is root-equivalent; use `sudo docker` unless you explicitly accept that access. Install `uv` using an approved vendor mechanism. Install Node 22 LTS from an approved signed distribution; `npm --version`, `node --version` must succeed. Do not replace the system Python. Optional cloud tooling: az/azd/Terraform/kubectl/Helm/GitHub CLI/VS Code from their signed official repos or validated checksummed binary releases. `scripts/verify_cloud_tools.sh` reports missing but returns success; it is inventory only.

## 2. Isolated application tests

```bash
./scripts/verify_python.sh
./scripts/verify_react.sh
./scripts/install_playwright_e2e.sh
```

Python direct versions are constrained ranges, not strict lock; inspect `requirements/python-node1-resolved-20261113.txt` for the historical reference snapshot. Fresh machine may download browser system dependencies; inspect Playwright warnings and install approved libraries before rerun.

## 3. Databases and networking

```bash
./create_env.sh
./validate_env.sh
./scripts/guard_before_compose.sh
# On PASS and authorized clean ports only:
docker compose config --quiet
docker compose pull
docker compose up -d --wait
./smoke.sh
docker compose ps
```

Expected host listeners: `127.0.0.1:15432` PostgreSQL, `127.0.0.1:16379` Redis, `127.0.0.1:16333` Qdrant. If port guard fails because services already run from this project, inspect `docker compose ps` and run `./smoke.sh` instead of starting duplicate containers. No `down -v`, no global prune, never touch unrelated CCTV/AI workloads.

## 4. Offline IaC

```bash
(cd labs/terraform-offline && terraform init -backend=false -input=false && terraform fmt -check && terraform validate && terraform plan -input=false)
helm lint labs/helm/principal-platform
helm template principal-platform labs/helm/principal-platform > reports/rendered_kubernetes.yaml
```

Terraform output-only planning does not create real infrastructure; Helm placeholder image has not been built, and `/health` runtime behavior is not Kubernetes-qualified. For static security assertions use a small YAML verifier or follow `docs/validation.md`.

## 5. Optional source repos and R05

Do not assume that an external Governance repository or its historical Git tag is available on a fresh host. `scripts/verify_original_project.sh governance /ABSOLUTE/PATH` is inventory only. To run R05 obtain the authenticated historic v0.29.0 wheel and the reviewed corrected v0.30.0 wheel, verify digests, install them into **two different consumer venvs**, install pytest in each, then:

```bash
./scripts/qualification/run_r05_contract.sh /PATH/old-venv/bin/python /PATH/new-venv/bin/python reports/r05-sdk-compatibility
```

Never re-label a wheel to fabricate a previous version. The old `__version__` discrepancy and the M30 release gate remain documented.

## 6. Cleanup and evidence

All reports remain ignored and local. Use `scripts/qualification/verify_evidence_selection.py --write` **only after manually reviewing** the selected reports for secrets; then run without `--write` to confirm complete 1:1 manifest coverage. For containers, `docker compose stop` is safe relative to volumes; do not prune or remove storage.

## Existing Node1 recovered Docker state (2026-11-14)

The local Docker daemon initially had no socket and was inactive/disabled. Inspect the system service, daemon context/data root, and existing other projects; after operator review, `sudo systemctl start docker.service` restored Engine 29.5.1. The three already-created practice containers were stopped (`Exited 255`). Existing labels and the `pgdata`, `redisdata`, `qdrantdata` mounts were checked; ports were clear. `docker compose start postgres redis qdrant` restored the *same* containers; PostgreSQL and Redis reported healthy, Qdrant responded through `./smoke.sh`, and smoke exited 0. Do not convert this recovery into automatic destructive `compose up`, `down -v`, prune or credential rotation.

Fresh machines should first run a read-only preflight and install an approved Docker Engine, `uv`, Node 22 and optional cloud tooling. These CLIs are not bundled as binary downloads in the Git repo. `scripts/record_dependency_inventory.sh` collects actual versions and image digests.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.

## R05 tool deployment note

R05-A needs Python 3.12 standard library, Pytest for local comparator unit tests, and externally supplied wheel ZIPs; it requires no Docker, Azure or cloud credentials. Run inside the `ai_platform_setup_v3` source checkout, emit reports only under ignored `reports/`, and never install either wheel into the base Python environment. [R05 specification](r05/R05_EXTENDED_COMPATIBILITY_SPEC.md).
