# R07 M1 — Authenticated Approval Research

Status: RESEARCH_ONLY
Formal R07 approval: PENDING

## Parent checkpoint

R07 research commit: 24e7d1f

## Objective

Ensure that the application does not trust an arbitrary
approval object supplied alongside an AI-generated tool call.

## New files

- labs/r07/approval_authority.py
- tests/r07/test_approval_authority.py

## Trust model

The issuing service owns the approval signing key.

The application receives a signed approval through
an authorized application-side lookup.

The LLM can propose a tool call but cannot mint approvals
or select verification keys.

## Approval binding

The signed payload includes:

- Approval ID
- Approver identity
- Requesting principal identity
- Tenant identity
- Tool name
- Device ID
- Request ID
- Approval expiration
- SHA-256 digest of approved tool arguments
- Signing key ID

## Research cryptography

HMAC-SHA-256 protects the integrity of the canonical
approval record when the secret key is not accessible
to an unauthorized issuer.

This research does not qualify:
- Production signing-key storage
- Organizational approver authorization
- OIDC identity verification
- Key rotation/revocation
- Single-use approval consumption
- Distributed concurrency
- Durable audit or replay protection

## Evidence requirements

Positive:
- Correctly signed approval accepted
- Valid read-only operation without approval accepted

Negative:
- Missing signed approval
- Unknown signing key
- Unauthorized approver
- Modified signed payload
- Wrong signature
- Forged signing key
- Modified approved arguments
- Expired approval
- Cross-tenant device
- Unsigned direct approval object
- Insufficient signing-key length

## Qualification

Engineering regression: PENDING EXECUTION
Formal R07 acceptance: NOT GRANTED
Production release: NOT AUTHORIZED
