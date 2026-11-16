# R05.35 Owner-review workflow (draft)

Status: NOT APPROVED. This runbook does not assign API-owner or independent-reviewer decisions.

The output of `prepare_r05_owner_review.py` is a reproducible technical review queue. It does not confer API support or release authority. The generated `r05_owner_review.csv` is under ignored reports and contains 103 prioritized candidates with evidence and suggested review category but `proposed_decision=UNREVIEWED` for all entries. The remainder of the 1,602 implicit candidate keys is outside this bounded review only if a maintainer approves this scope boundary.

The kernel star import is `from .types import *`. Its SDK-defined dataclasses are `Principal`, `AgentRequest`, `ProposedAction`, `AgentResult`, and `PolicyDecision`. Other kernel bindings imported from `dataclasses`, `typing`, or `__future__` are incidental; process-address reprs in `dataclasses.field` signatures are not SDK version incompatibilities. The `TERMINAL_STATES` constant is additionally module-owned. The 12 runtime names include package submodule `types`.

Procedure: verify wheel SHA-256, generate technical dossier from the existing candidate JSON and kernel binding JSON, validate the review CSV, read `REVIEW_SUMMARY.md`, then submit the scope and each candidate decision to the authorized SDK owner. Record documented import/contract references and rationale. An independent reviewer must approve the final manifest and tests. No script may change an unreviewed decision to supported or set `qualified=true`. Maintain R05 requirement-level status as pending.
