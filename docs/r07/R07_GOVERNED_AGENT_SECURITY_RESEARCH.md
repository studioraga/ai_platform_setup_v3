# R07 Governed-Agent Security Research

Status: RESEARCH ONLY

## Objective

Demonstrate deterministic application-controlled execution
of approved tools for an agentic embedded-device system.

## Architecture

AI proposal
  -> Typed ToolCall
  -> Trusted principal and device registry
  -> Capability and tenant authorization
  -> Scoped approval and argument-digest verification
  -> Audit admission
  -> Controlled synthetic executor
  -> Result and audit outcome

## Preserved historical implementation

- labs/r07/governed_tool.py
- tests/r07/test_governed_tool.py

## Extended implementation

- labs/r07/governed_runtime.py
- tests/r07/test_governed_runtime.py
- labs/r07/diagnostic_demo.py

## Supported research controls

- Separate principal and proposed tool action
- Trusted application-owned device tenancy
- Strict allowlisted tools and arguments
- Capability authorization
- Independently scoped synthetic approval records
- Canonical argument-digest binding
- Expiration and request identity matching
- Cross-tenant refusal
- Pre-execution audit admission
- Executor failure reporting
- In-memory replay refusal for state changes
- Deterministic unauthorized-agent negative tests

## Approval digest

Tool arguments are serialized with deterministic JSON
key ordering and SHA-256.

The digest ensures equality of approved and executed
arguments; it is not proof of approval authenticity.

## Demonstration

Synthetic missing measurement -> authorized diagnostic
-> simulated I2C bus timeout -> audit evidence.

No physical hardware result is claimed.

## Known limitations

- R11 authenticated principal verification missing
- Authenticated approval-service integration missing
- R10 durable idempotency and fencing missing
- Hard executor timeout missing
- Device firmware safety validation missing
- Durable tamper-resistant audit storage missing
- Independent security acceptance missing

## Acceptance policy

Synthetic tests may pass while the requirement remains
unapproved.

R07 requirement status: PARTIAL_RESEARCH
Formal acceptance: PENDING
Production authorization: NOT GRANTED
