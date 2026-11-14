# November 13 source audit: corrections and non-goals

## Source-backed findings

- `reports/section1-closure/accepted_files.txt` on Node1 selected **45** entries, while `evidence.sha256` still hashed only **35**. A `sha256sum -c` PASS on those 35 does not establish selection coverage. Regenerate with `scripts/qualification/verify_evidence_selection.py --write` and compare without `--write` after reviewing reports for secrets.
- The live `reports/r05-sdk-compatibility/compatibility_review.md` still said `PENDING NODE1 VERIFICATION`, although the uploaded test report has v0.29.0 **7 passed** and v0.30.0 **7 passed**. Use `reconcile_r05_evidence.py`; it does not certify full API compatibility.
- The prior `.gitignore` excluded `labs/` altogether, making a fresh clone incomplete. The new ignore permits source while excluding virtual environments, `.terraform`, `node_modules`, dist and state.
- The prior Python script rewrote tracked demo source on each run, hid version drift in broad dependency ranges, and assumed pip was installed in the uv venv. The new runner tests tracked source and uses `uv pip check`.
- The old README was labeled v2 and did not describe the actual Node1 v3/Phase F/R05 scope.
- Two original project repositories are **not** bundled, and their uncommitted work is preserved separately.

## Evidence-backed status

A–F local smoke/validation passed in prior Node1 logs. Form 8825 compatibility snapshot had 32 passing tests, while the current active source had five deleted tracked modules; Governance M29 baseline 290 tests and M30 six tests passed. v0.29.0 historical and corrected v0.30.0 wheel consumer shared contracts each passed seven cases. Static API inventory (228 → 234 Python files) saw six added M30 modules and no detected top-level signature removals; it does not prove all class methods or behavioral compatibility. R01–R16 are not accepted. M30 release remains blocked by independent approvals and production evidence.

## Remaining risks

- No host was actually freshly provisioned by this archive; fresh-machine provisioning requires running scripts on authorized infrastructure.
- `requirements/python-node1-resolved-20261113.txt` is a plain resolved version list, not a hash-locked cross-platform package set.
- Docker image references use version tags, not pinned SHA digests.
- Host-installed cloud CLIs are not automatically provisioned by this baseline; see `docs/deployment.md`.
- Historical logs are excluded from Git on purpose, so reproducibility claims depend on rerunning tests.
- No Git push performed by generation; the original source tar has no `.git` directory or remote.

## November 14 final logged correction

The later Node1 run corrected the earlier 35/45 hash mismatch: **45 selected / 45 SHA-256 manifest entries passed**. Docker daemon and existing practice containers were restored, service smoke passed, and Terraform/Helm validation passed. Source and ShellCheck passed. `git init -b main` succeeded, but only `git add -n` was executed; therefore **no commit** existed. Initial staging candidates included downloaded `kubectl`, Helm executables, vendor keyrings and `verify_python.sh.pre-sc1091` backup. `.gitignore` and a new staged-index audit exclude them.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
