# R05-B/C — candidate triage and isolated runtime probe

**State:** Engineering instruments proposed for review; no public API acceptance. Base: `590468d` on `feature/r05-extended-sdk-compatibility` (2026-11-14).

## Observed inputs

The Node1 v0.29.0 and v0.30.0 wheel candidate inventories contain **1,879** and **1,929** records respectively. These are implementation-level candidates, not approved exports. Historical seven shared tests passed in each consumer, but official public designation, JSON semantics, exceptions, and pre-1.0 policy remain unreviewed.

## R05-B workflow

1. Verify wheel hashes and the two candidate JSONs against the source wheels; rerun exporter if provenance changes.
2. `classify_r05_public_candidates.py` creates ignored `reports/r05-extended/r05b_triage.json` and CSV based on shared-test import paths and static candidates.
3. Prioritize `SHARED_TEST_IMPORT_SEED`, `DECLARED_ALL_CANDIDATE`, `UNRESOLVED_STAR_IMPORT`, missing/changed symbols, and newly introduced v0.30 enterprise-freeze modules.
4. Review both wheel package `__init__.py` files, documented consumer examples, maintainer-supported exports and class methods. Fill `public_decision`, `documented_reference`, and `owner` in a **separate reviewed approval manifest**, not in the auto-generated CSV.
5. An empty `__all__`, absent `__all__`, or an import in an existing test is not proof of public support. Resolve aliases/star imports and runtime `__getattr__` where relevant.

## R05-C first runtime probe

Use **explicitly separate** wheel-installed v0.29 and v0.30 virtual environments. The probe verifies installed distribution metadata and package import origin under `site-packages`, then imports only symbols from existing tracked shared tests and records `inspect.signature` results. It does **not** instantiate classes, invoke methods, test serialization or prove compatibility. Do not use it for release authorization.

Execute all runtime tests from a neutral working directory, with `PYTHONPATH` unset and working artifacts outside Git. Compare JSON reports manually and record exact potential deltas; normalize path-dependent fields rather than requiring identical import origins.

## R05-D to R05-E acceptance gates

- **D:** Approved common contract vectors for serialization, exception identity/code, default deny, tenant isolation, tampered signatures, expiry, nonce replay and corrupt-cache fail-closed behavior; separate v0.30-only tests.
- **E:** Maintainer-approved supported-surface manifest and pre-1.0 change/version policy, plus explicit disposition of historical v0.29 metadata discrepancy.
- **Independent review:** Reviewer identity, wheel digests, Git commit, test commands, negative test results, and signed decision. Keep R05 `NOT_RUN/PENDING` until then. R03 only follows R05 disposition.

No Governance/Form8825 source mutation. No wheel bytes, token values, runtime evidence or secrets inside Git.
