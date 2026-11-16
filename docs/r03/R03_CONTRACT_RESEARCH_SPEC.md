# R03 — OpenAPI compatibility research baseline

Status: **RESEARCH_ONLY / NOT_RUN as a requirement**. R05 acceptance remains pending. This independent R03 research may be committed but not marked as qualification or deployed.

## Actual baseline

- `labs/python-api/platform_demo.py`: FastAPI `Principal Platform Practice` version 0.1.0.
- GET `/health` -> `{"status":"ok"}`.
- POST `/v1/double` accepts an integer `value` in [0, 1000], returns doubled integer; invalid requests return 422.
- `labs/python-api/openapi.generated.json` is an existing OpenAPI 3.1.0 snapshot, not a frozen reviewed contract.

## Scope of comparison tool

`compare_r03_openapi.py` detects removed operations/paths, newly required input fields, narrowed scalar constraints, changed input primitive types, some removed response codes and security metadata changes. It is deliberately incomplete for full JSON Schema composition, transitive `$ref`, response compatibility, clients, auth flow and migration acceptance.

**No false acceptance:** reports always contain `qualified: false`, even with no detected differences. A breaking or review-required finding results in exit code 2.

## Gates before R03 is implemented/accepted

1. Record independent R05 acceptance or an approved decision explicitly authorizing preparatory R03 research (this document does not provide approval).
2. Review/freeze `openapi.generated.json` by digest and server source commit; run existing FastAPI tests.
3. Add documented compatible and intentionally breaking server versions in isolated fixtures; confirm comparator behavior.
4. Generate two pinned clients from those versions, run cross-version consumer tests and check 401/403/422/429/5xx behavior where implemented. Current demo does NOT implement authentication or these errors beyond 422. Never fabricate their behavior.
5. Implement complete schema diff or use a reviewed OpenAPI-diff dependency for complex constructs; independently review classifier findings.
6. Capture test commands, versions, signed human disposition, evidence hash; update only R03 requirement after acceptance.

## Follow-on dependencies

- R09 PostgreSQL: disposable database and RLS with deny tests, connection pool tenant-context reset, transaction isolation, EXPLAIN plans.
- R10 Redis/Qdrant: pinned containers, idempotency/replay and recovery; Qdrant tenant payload filtering and unauthorized retrieval denials.
- R06/R07: retrieval evaluation with fixed dataset/metrics; governed agent tools and prompt injection negative cases.
- R11–R13: identity, OTel SLI/SLO and provenance controls.
- R01/R02/R04/R14–R16: architecture ADRs, measured implementation tradeoffs, review evidence.

Keep each requirement on its own branch and evidence matrix. Never infer a PASS from installed tools or the R05 simulation.
