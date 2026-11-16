# R05-E Pre-1.0 Governance SDK Compatibility Policy

Status: PROPOSED — NOT APPROVED
Applies to: Governance 0.29.0 and corrected 0.30.0

## 1. Purpose

Define measurable compatibility commitments for approved
public SDK interfaces and version-specific additions.

## 2. Supported surface

Only paths explicitly accepted in a reviewed public API
manifest receive contractual compatibility guarantees.

Importability, static declarations, examples and tests are
evidence of implementation behavior, not automatic approval.

## 3. Common contracts

For owner-approved common interfaces, the following require
compatibility review:

- Import paths and aliases
- Constructor parameters and defaults
- Public methods and binding types
- Return values and data schemas
- Documented exception types and failure behavior
- Security refusal behavior

## 4. v0.30-only features

A feature introduced in v0.30 is not automatically a
regression merely because it is missing from v0.29.

Its support status must be approved independently.

## 5. Breaking changes

Changes to an approved contract require:

- Explicit classification
- Consumer impact analysis
- Migration procedure
- Reviewed version transition
- Owner approval
- Independent acceptance where required

No compatibility guarantee is assigned automatically
to unreviewed internal implementation symbols.

## 6. Serialization

Python dataclass representation and JSON wire-format
compatibility must be considered separately.

Stable wire schemas require versioned contracts and tests.

## 7. Exceptions

Only documented and owner-approved exception types,
categories and failure-state behaviors are contractual.

Human-readable exception text is not necessarily stable.

## 8. Security

A version transition must not silently weaken
owner-approved authorization and refusal guarantees.

This policy does not assert:

- Automatic PostgreSQL tenant isolation
- Distributed nonce atomicity
- Production identity-provider integration

Those capabilities require separate platform validation.

## 9. Historical version discrepancy

Governance v0.29.0 distribution metadata reports 0.29.0,
while historical package-level __version__ was reported
as 0.21.1.

This inconsistency must be recorded as a historical
provenance finding.

Do not modify the immutable historical wheel or Git tag
to conceal it.

For these qualification tests, installed distribution
metadata is used as the version identity.

## 10. Deprecation and migration

Proposed requirement:
Breaking changes to approved contracts require explicit
deprecation or migration guidance.

The actual deprecation duration and compatibility window
require owner approval.

## 11. Acceptance

SDK owner: PENDING
Policy decision: PENDING
Independent reviewer: PENDING
R05-E acceptance: PENDING
Governance M30 release: NOT AUTHORIZED
