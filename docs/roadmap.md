# Next incremental engineering milestones

Baseline freeze criteria: source files tracked (including labs), fresh clone sanity pass, reviewed instructions/dependencies, no secrets or machine-state in Git, evidence manifest coverage repaired on Node1, correct R05 report and explicit limited-scope qualification.

1. **R05 extended SDK compatibility:** expand static inventory to methods/re-exports/types, shared serialization and exception contracts, SemVer policy, negative authorization; do not approve M30 production freeze.
2. **R03 API/OpenAPI consumer:** versioned contract and generated client; compatible and intentional breaking change demonstrations.
3. **R09 PostgreSQL:** disposable tenant identities, row-level security with negative cross-tenant access, concurrency and explain plans.
4. **R10 Redis/Qdrant:** idempotency, replay, checkpoint/restart, tenant-filtered vector read/deny and migration.
5. **R06/R07:** retrieval evaluation and bounded policy-governed agents, approval/denial/audit.
6. **R11/R12/R13:** OIDC/JWT/JWKS negatives, OpenTelemetry/SLI/SLO incident exercise, repeatable CI/signing/provenance.
7. **R01/R02/R04/R14–R16:** ADRs, Python/React performance and edge cases, measured AI coding, executive architecture and role evidence.

Every stage needs code, negative tests, artifacts, reviewer decision and a separate commit; do not infer PASS from installed software.

## Next work after the reviewed Git baseline

1. **R05 extended:** inventory shared class methods, public re-exports, argument/default/return contracts, stable serialization formats, exception and denial semantics, and explicit pre-1.0 breaking-change policy. Run the same expanded consumer suite on v0.29 and v0.30; preserve M30 approval separation.
2. **R03:** versioned OpenAPI clients, compatible and intentional breaking changes.
3. **R09:** disposable PostgreSQL multi-tenant schema, RLS and cross-tenant denials, concurrency and EXPLAIN.
4. **R10:** Redis idempotency, retries/replay and Qdrant tenant-filtered retrieval/migration.
5. **R06/R07:** retrieval quality, prompt-injection negatives and governance-controlled tool approvals.
6. **R11–R13:** OIDC/JWKS negative checks, OpenTelemetry and evidence-backed CI/CD.
7. **R01/R02/R04/R14–R16:** architecture ADRs, code reliability and measured principal delivery artifacts.

Every stage requires code, reproducible tests, negative cases, evidence and a separate manually reviewed acceptance decision.

## Verified baseline reference

[Baseline qualification checkpoint](baseline_qualification_checkpoint.md) records the dated Node1 evidence, dependency boundaries, outstanding engineering gates and fresh-machine acceptance limitations.
