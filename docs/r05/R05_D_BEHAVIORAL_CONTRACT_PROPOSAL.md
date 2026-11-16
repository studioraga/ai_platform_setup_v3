# R05-D Governance SDK Behavioral Compatibility Proposal

Status: PROPOSED — NOT APPROVED

## Scope

Historical Governance SDK v0.29.0 compared with
corrected v0.30.0.

This document distinguishes observed implementation
behavior from normative supported-public-API guarantees.

## 1. Authorization

Observed:
- Explicit rule matching
- Deny precedence
- Attribute-based decisions
- Default refusal for unmatched operations

Not established:
- Automatic database tenant isolation
- Cross-service authorization enforcement

## 2. Budgets

Observed:
- Step and tool-call consumption
- BudgetExceeded behavior
- Counter state after over-limit rejection

Owner decision required:
Whether counter mutation before rejection is contractual.

## 3. Workflow state

Observed:
- Legal state transition behavior
- Illegal transition rejection
- Resulting state preservation

Owner decision required:
Complete supported transition matrix.

## 4. Request signing

Observed:
- Valid HMAC request verification
- Selected method/path/body/key/timestamp negative cases

Owner decision required:
Stable canonicalization and supported key lifecycle.

## 5. Replay protection

Observed:
- Persistent nonce state
- Duplicate nonce refusal
- Selected malformed-state and TTL cases

Not established:
- Distributed atomicity
- Multi-process concurrent guarantees
- Cross-host replay consistency

## 6. Serialization

Observed:
- Dataclass construction
- AgentResult.as_dict()
- Python tuple/list behavior
- JSON normalization through standard Python encoding

Not established:
- Versioned stable JSON wire schema
- Forward/backward payload migration rules

## 7. Exceptions

Observed:
- Selected exception types and parent classes

Not established:
- Complete stable exception taxonomy
- Stable error codes unless explicitly documented

## Acceptance

Technical test inventory: captured separately
SDK owner decision: PENDING
Independent reviewer: PENDING
R05-D status: OBSERVATIONAL_ONLY
