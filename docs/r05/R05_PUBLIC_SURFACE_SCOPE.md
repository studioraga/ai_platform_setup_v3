# R05 Supported Public Surface — Scope Decision

Status: PROPOSED — OWNER APPROVAL REQUIRED

## Included review scope

1. All 103 prioritized static candidates.
2. Twelve existing shared-consumer import seeds.
3. Statically declared __all__ exports.
4. Reviewed aliases and kernel star re-exports.
5. Version-specific v0.30 additions.
6. Any additional symbols explicitly documented as supported.

## Excluded from automatic compatibility guarantees

- Undocumented implementation symbols
- Private/underscore-prefixed members
- Incidental module globals
- Dynamic bindings not reviewed
- Unapproved implicit candidate records

The 1,602 implicit candidates are not individually certified by the
current bounded R05 assessment.

This is a scope limitation, not evidence that those symbols are
unimportable or incompatible.

## Contract classification

SUPPORTED_COMMON
SUPPORTED_V030_ONLY
INTERNAL
UNCERTAIN
BREAKING_REVIEW

## Requirements for an approved supported contract

- Exact documented import path
- Declared version availability
- Owner-approved method and schema scope
- Documented exceptions and negative behavior as applicable
- Test IDs and reproducible evidence
- Independent review

## Approval

SDK owner: PENDING
Independent reviewer: PENDING
Decision date: PENDING
Status: NOT APPROVED
