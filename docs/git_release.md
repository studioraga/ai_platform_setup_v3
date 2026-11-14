# Git baseline review and push checklist

A supplied tarball has no `.git` history or remote. Apply this source-only baseline to your local `principal_ai_platform_setup_v3` Git checkout after reviewing differences. Never initialize a new repository over an existing checkout by accident.

```bash
cd ~/dev/pub/ai-platform-principal-prep/principal_ai_platform_setup_v3
git status --short; git branch --show-current; git remote -v
# Back up existing source before copying the reviewed baseline package into the checkout.
# Verify .gitignore excludes runtime state but includes labs and tests.
git status --short
git add -n README.md .gitignore docs scripts requirements tests labs compose.yaml   create_env.sh validate_env.sh smoke.sh preflight.sh install_base_ubuntu2404.sh   requirements_evidence_gap_drills.csv section1_audit.py
# Inspect stage candidates before real add. Never use git add -A without reviewing ignored/previously tracked state.
git add README.md .gitignore docs scripts requirements tests labs compose.yaml   create_env.sh validate_env.sh smoke.sh preflight.sh install_base_ubuntu2404.sh   requirements_evidence_gap_drills.csv section1_audit.py
git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
# Check tracked files for secrets locally before commit.
git commit -m 'baseline: freeze portable principal AI practice stack and R05 contracts'   -m 'Track Python FastAPI and React/Playwright source, Terraform/Helm offline examples and pinned React dependency lockfile. Add fresh-machine prerequisite inventory, documented installation order, local-only Compose safety boundaries and explicit evidence integrity checks. Preserve original Governance and Form 8825 repositories and their in-progress changes. Record R05 cross-version seven-case shared consumer suite and limitations; keep R01-R16 and M30 production release unapproved.'
git push -u origin HEAD
```

Before push, check `git ls-files` for `.env`, private keys, reports, wheels, `node_modules`, venv and tar archives. GitHub repository existence/permissions and push success must be validated from Node1; the source archive cannot push itself. Suggested **baseline tag only after manual approval**, not automatic. If a forbidden file is already tracked, `.gitignore` does not untrack it; remove from index with reviewed `git rm --cached` and rotate any exposed credential.

## Correction to initial Git commit attempt

`git init -b main` was successful. `git add -n` only printed candidates and did not stage them, so `git commit` failed. Before retrying, review the new `labs/cloud-tool-install/` and `*.pre-*` exclusions. Run the **real** scoped `git add` after a dry run, followed by `./scripts/check_git_baseline.sh`, `git diff --cached --check`, manual staged diff/secret scan, then commit. Do not force-push to an unknown remote; check `git ls-remote origin refs/heads/main` and reconcile any existing history. Do not tag a production release.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
