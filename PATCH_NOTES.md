# v2 → v3 source corrections
1. `scripts/verify_python.sh`: remove unused import, normalize imports, formatted tests, `ruff check`, `black --check`, five tests (including value upper bound), explicit `pytest.ini` async scopes, and make fail-on-lint mandatory.
2. `scripts/verify_react.sh`: add deterministic Vitest component test and execute it, not just check Vitest's version. Playwright E2E remains an explicitly separate gate.
3. `scripts/evidence_manifest.sh`: restrict to allowlisted reports rather than recursively hashing arbitrary possibly-private files; hashing is not redaction.
4. `scripts/verify_cloud_tools.sh`: repeatable best-effort inventory that distinguishes absent tools.
5. Runbook sets actual statuses: Phase A Docker PASS / historical CCTV Qdrant failure separate, Phase B PASS, Phase C v2 tests PASS but lint FAIL, D–F pending.
6. Retained v2 Compose images / credentials and source project inventories, not asserted validated on Node1. Docker Compose may need additional adjustment after actual runtime logs.
