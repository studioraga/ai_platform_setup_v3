# R05-D Security and Exception Acceptance Matrix

Status: REVIEW REQUIRED

| Gate | Existing evidence | Additional acceptance |
|---|---|---|
| Default-deny authorization | Shared/extended tests | Approved policy semantics |
| Deny precedence | Extended behavior tests | Approved conflicting-rule behavior |
| Attribute authorization | Extended behavior tests | Approved missing/malformed attribute rules |
| HMAC verification | Shared/extended tests | Canonicalization and signing contract |
| Tamper rejection | Extended behavior tests | Approved negative matrix |
| Nonce replay refusal | Shared/extended tests | Approved persistence and replay boundaries |
| Malformed nonce state | Extended behavior tests | Approved fail-closed contract |
| Budget exception | Extended behavior tests | Approved exception/state semantics |
| Workflow rejection | Extended behavior tests | Approved transition matrix |
| Tenant isolation | Not established by R05 | Separate R09 PostgreSQL RLS |
| Distributed replay atomicity | Not established by R05 | Separate R10 reliability qualification |

## Review requirements

For each supported contract:
- Identify exact test function and source line
- Record positive and negative expected behavior
- Record version applicability
- Record accepted exception category
- Record evidence file and SHA-256
- Record owner and independent reviewer decision

## Qualification

R05-D observed test execution: VERIFIED HISTORICALLY
R05-D normative approval: PENDING
R09 tenant isolation: NOT QUALIFIED HERE
R10 distributed replay: NOT QUALIFIED HERE
