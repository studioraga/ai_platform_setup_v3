# Verification scripts — canonical index

*Filename intentionally matches the requested `verrification_scripts.md` spelling.*

| Script | Inputs | Behavior | Mutates? |
|---|---|---|---|
| `scripts/fresh_machine_preflight.sh` | none | inspect OS/tools/Compose | writes local report only |
| `scripts/validate_baseline.sh` | none | verify source inventory, Python/Bash syntax, requirement matrix | pycache generated (ignored) |
| `preflight.sh` | optional report dir | host/service audit | local reports only |
| `install_base_ubuntu2404.sh` | normal user with sudo | apt package provisioning | **host packages** |
| `scripts/verify_python.sh` | optional `--frozen-snapshot` | isolated deps, Ruff/Black/pytest/OpenAPI | **local venv/generated OpenAPI** |
| `scripts/verify_react.sh` | Node + lockfile | npm ci when needed, build/lint/Vitest | **local modules/dist** |
| `scripts/install_playwright_e2e.sh` | npm dependencies | install Chromium, run E2E | local browser cache |
| `create_env.sh`, `validate_env.sh` | none | create only if absent / validate credentials | **private .env/secrets** |
| `scripts/guard_before_compose.sh` | Docker config, ports | stop if occupied/unowned | none |
| `smoke.sh` | running named stack | SQL rollback, Redis PONG, Qdrant auth check | temp SQL transaction only |
| `scripts/verify_cloud_tools.sh` | none | CLI version inventory; returns 0 even when tools missing | local report |
| `scripts/verify_original_project.sh` | kind + source path | repository identity/inventory, not tests | local report |
| `scripts/qualification/run_r05_contract.sh` | two interpreters, output path | same seven tests against both installed wheel consumers | local reports/tmp |
| `scripts/qualification/verify_evidence_selection.py` | `--root`, optional `--write` | verify complete file selection/hashes | `--write` updates manifest |
| `scripts/section1_checklist.sh` | existing local reports | structural matrix and report listing | none |
| `scripts/evidence_manifest.sh` | legacy known reports | historical partial allowlist only | writes legacy hash file |
| `scripts/validate_source.sh` | shellcheck installed | static checks | pycache only |

All executable verification scripts are intended to run from a normal non-root user shell; run `set -e` only in scripts/subshells, never blindly in interactive terminal. Test exit 0 is not evidence of production readiness. Avoid printing credentials, real customer documents or original project configs into shareable logs.

## New baseline verification tools

- `scripts/check_git_baseline.sh`: examines **staged Git index contents**, refuses absent staging, source-external paths, downloaded CLI tools, large/binary files, and common literal secrets. Additional manual secret review remains mandatory.
- `scripts/record_dependency_inventory.sh`: records OS, Python/Node/CLI versions, Docker Server/Compose and image RepoDigests (when available) in **ignored local reports**, without dumping credentials.
- `scripts/validate_source.sh`: updated to include `scripts/qualification/*.sh` in Bash syntax/style lint.

Check stages separately. Do not treat `git add -n` output as proof of staging or the Git index audit as proof of a clean fresh-machine deployment.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.

## R05 extended audit scripts

`scripts/qualification/audit_r05_public_api.py`: static AST inventory for public-candidate methods, fields and re-export syntax; emits JSON under ignored `reports/r05-extended/`. `tests/r05/test_public_api_inventory.py`: self-tests with synthetic wheels (no third-party package required beyond pytest). See [R05 specification](r05/R05_EXTENDED_COMPATIBILITY_SPEC.md).
