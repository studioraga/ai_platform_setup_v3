# Instructions — developer workflow

1. Confirm Ubuntu 24.04 amd64 with `scripts/fresh_machine_preflight.sh`; verify Docker isolation and free ports before any mutations.
2. Run source-only `scripts/validate_baseline.sh`; it never contacts cloud or modifies outside the checkout.
3. Review and install apt dependencies with `install_base_ubuntu2404.sh` (requires sudo and changes host packages).
4. Install Docker Engine/Compose v2 from the official signed vendor source; never remove or prune other projects. Install `uv` and Node 22 LTS with approved vendor/source and verify their versions.
5. Run `scripts/verify_python.sh` (creates an isolated venv and tests existing source); use `--frozen-snapshot` only after reviewing Node1's historical resolved package versions. Direct requirement ranges are **not a lock**.
6. Run `scripts/verify_react.sh` and `scripts/install_playwright_e2e.sh`; `npm ci` uses committed package-lock. Ensure Chromium dependencies are installed only after review.
7. Run `create_env.sh` once; credentials remain local, `0600`, and never belong in Git. Run `validate_env.sh`.
8. Run `scripts/guard_before_compose.sh` and inspect any occupied ports. Only then, if safe, `docker compose pull` and `docker compose up -d --wait`; `smoke.sh` verifies this named stack. Never `down -v` or global `docker prune`.
9. Check cloud CLIs with `scripts/verify_cloud_tools.sh`; it is informational and **not fail-closed**. For strict checks, use the prerequisite inventory and explicit tool-path/versions. Terraform and Helm are offline exercises; Kubernetes/Azure deployment are not tested.
10. If original Governance/Form 8825 repos are available, point `scripts/verify_original_project.sh` at their actual directories; it inventories only. Tests require separate repository approval and disposable dependencies. For R05, install the exact old/new verified wheels into separate consumers and use `scripts/qualification/run_r05_contract.sh`.
11. Preserve validation reports locally; use `scripts/qualification/verify_evidence_selection.py` to check manifest coverage. Evidence integrity does not mean sign-off.
12. Make source changes in a feature branch, inspect diffs, run checks, and obtain explicit review before pushing. Historical M29 Git tag and M30 uncommitted work are never modified by this repository.

## Engineering gates

A host and Docker isolation; B Ubuntu toolchain; C Python FastAPI; D React/Playwright; E PostgreSQL/Redis/Qdrant persistence; F cloud CLI/IaC local exercises; R05 SDK compatibility; then R03 and R06–R16 requirement drills. No automatic Section 1 closure or M30 freeze.

## Latest pre-commit correction

The initial Git repo was created on Node1, but `git add -n` **did not stage** files; the subsequent commit failed. Execute the real reviewed `git add` and then `./scripts/check_git_baseline.sh`. The Git dry-run showed unwanted `labs/cloud-tool-install/kubectl`, `labs/cloud-tool-install/linux-amd64/helm`, downloaded keyrings and `scripts/verify_python.sh.pre-sc1091`; the new ignore rules exclude those. Source baseline must include actual `labs/` apps, Helm/TF, React lockfile, tests, scripts and docs. Do not use `git add .`, `git clean` or `git reset --hard`.

The latest local service smoke, Terraform and Helm commands passed. Do not re-run `docker compose up` over already running project containers. See `docs/deployment.md` and `docs/git_release.md`.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
