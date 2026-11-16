# R07 M2–M5 corrected engineering research

Status: PARTIAL_RESEARCH; formal R07 acceptance NOT GRANTED.

## M2 correction
The signed-approval adapter validates approval before the governed runtime checks
capability. For the missing-capability scenario, provide a signed valid approval,
then verify that the runtime denies `CAPABILITY_MISSING`. The additional test
demonstrates `SIGNED_APPROVAL_REQUIRED` if both approval and capability are
missing. Neither check is bypassed.

## M3
`ReplayStore` models a single-node SQLite claim lifecycle. It records first
claims, rejects duplicate processing/fingerprint collisions, persists completion,
rejects stale/expired completion and preserves `OUTCOME_UNCERTAIN` on expiration.
There is no automatic recovery or cross-service exactly-once guarantee.

## M4
A bounded Python subprocess runs only synthetic diagnostic commands. One test
forces a deadline expiry. The direct child is terminated by subprocess.run,
but hardware cancellation and process-tree/resource isolation are unqualified.

## M5
A firmware simulator refuses unsafe-state reset, unknown commands and wrong
device identities. A SQLite audit prototype persists events locally. Neither
represents physical firmware, trusted transport, or tamper-resistant audit.

## Gates
- R11 live OIDC/JWKS lifecycle and key rotation: BLOCKED_DEPENDENCY
- M1 production approver and signing-key custody: BLOCKED_DEPENDENCY
- R10 distributed fencing and reconciliation: PARTIAL_RESEARCH
- M4 process-tree isolation and physical cancellation: NOT_RUN
- M5 hardware firmware tests and immutable audit: NOT_RUN
- Independent R07 acceptance: PENDING

Keep the feature branch separate from protected main.
