# R05-C/D bounded method and behavioral test increment

**State: candidate discovery implementation, NOT APPROVED API or full compatibility.**

## Inputs

- Historical independently verified 0.29.0 and corrected-snapshot 0.30.0 wheels, installed in isolated consumers.
- Existing seven-case `test_shared_contract.py`, unchanged.
- `tests/r05/test_r05_extended_behavior.py` adds observed deterministic kernel behavior regression.
- `inventory_r05_method_contracts.py` reflects *eight explicitly selected class imports*, no method invocation; `compare_r05_method_contracts.py` compares those runtime reports.

## Evidence and stop conditions

1. Prove hashes of wheel files; record installation source and external venv path. Distribution version and site-packages do not independently prove exact wheel origin.
2. Execute reflection in each isolated consumer interpreter and compare generated files. A delta is REVIEW REQUIRED, not an automatic compatible change.
3. Execute the existing 7 tests and the new observed-behavior tests in both consumers, with pytest, isolated cwd, fixed deterministic fixtures and temporary replay files.
4. Preserve logs and generated reports under ignored `reports/r05-extended/phase-cd/`. Do not commit wheels, venvs, reports or secrets.
5. Mark public symbols `UNREVIEWED` unless maintainer documentation and independent owner approval provide the contractual commitment. The tests here characterize observed behavior, not promises of public support.

## Critical limitations

- `Principal.attributes['tenant']` is not intrinsically compared to a resource tenant path by the `AuthorizationEngine`; ABAC policy must explicitly require tenant conditions. **Do not claim R09 tenant isolation**.
- `RunBudget` increments its counters before throwing `BudgetExceeded` on overrun. This is an observed implementation behavior, not necessarily the desired interface policy.
- `AgentResult.as_dict()` preserves tuple fields in Python; JSON encoding converts tuples to lists. A frozen dataclass can still contain mutable nested dictionaries.
- `PersistentNonceCache` is filesystem state, not distributed exactly-once/replay protection; no production guarantees are inferred.
- Probes import reviewed modules (module initializers may execute); use isolated consumers and fixed hash-verified input artifacts.
- Reflection ignores inherited/dynamic descriptors and does not derive generated constructor behavior from documentation.
- This suite is bounded to selected kernel contracts and cannot approve the 1,705 unclassified triage records.

## Future R05 acceptance

R05-B: reviewed/signed public export manifest including re-export identity and unresolved star import. R05-C: approved common method behavior, inherited and generated signatures, version-specific changes. R05-D: normative serialization/exception/negative security contract plus field-level schemas. R05-E: maintainer-signed pre-1.0 version policy. Independent review and all negative evidence required before R05 requirement status changes from `NOT_RUN`.

## Node1 execution command (after source review)

```bash
./scripts/qualification/run_r05_cd.sh \
  "$V29" "$V30" "$R05_OLD_WHEEL" "$R05_NEW_WHEEL" \
  "$DST/reports/r05-extended/phase-cd"
```

Script hashes are fixed to the previously reviewed historical wheel inputs and fail on different bytes. Existing installed consumers are **not reinstalled**. To prove binary installation provenance, build new, uniquely named venvs from those verified wheels and run the same command against them. Existing venv package metadata alone cannot prove installation source.

The detached test run in the review environment reported **19 tests passed per wheel** and **8 common reviewed candidate classes, 0 declaration differences**. These results must be reproduced on Node1 and remain `qualified=false` because the scope is intentionally limited and no public API owner signed the manifest.
