# R05 Public API Manifest Specification

Status: PROPOSED
Requirement acceptance: PENDING

## Purpose

Convert reviewed SDK discovery candidates into an explicit
supported-public-API contract for v0.29.0 and corrected v0.30.0.

## Sources

- Fingerprinted historical and corrected wheel artifacts
- R05-A AST comparison
- R05-B candidate inventories
- R05-B priority review
- R05-C runtime import and method observations
- Documented package consumer examples
- Maintainer-reviewed export declarations

## Candidate classifications

UNREVIEWED
SUPPORTED_COMMON
SUPPORTED_V030_ONLY
INTERNAL
UNCERTAIN
BREAKING_REVIEW

Importability alone is never sufficient for SUPPORTED_COMMON.

## Approval requirements

Every supported symbol must have:
- Exact import path
- Version availability
- Explicit documentation reference
- Contract scope and methods
- Serialization/exception reference where applicable
- Owner classification
- Independent review

Internal or deferred candidates must have an exclusion rationale.

## Version-specific behavior

The manifest distinguishes common contracts from capabilities
introduced in corrected v0.30.0. New symbols are not automatically
classified as breaking changes in v0.29.0.

## Evidence boundaries

The working manifest remains under ignored reports/.
Only approved sanitized contract definitions may be committed.

## Approval

SDK owner: PENDING
Independent reviewer: PENDING
Qualification status: NOT APPROVED
