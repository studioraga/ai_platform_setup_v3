# R10 Redis and Qdrant Reliability Research

Status: RESEARCH ONLY

## Redis

Implemented experiments:
- Atomic first claim with SET NX PX
- Duplicate claim rejection
- Token-checked completion

Not qualified:
- Exactly-once external side effects
- Durable completion across failure
- Worker fencing generations
- Lease renewal and recovery
- Redis restart durability
- Concurrent worker behavior

## Qdrant

Implemented experiments:
- Two-tenant synthetic vector collection
- Server-side tenant filter construction
- Tenant A/B filtered retrieval
- Cross-tenant request rejection
- Provider-response tenant verification
- Intentionally unfiltered security demonstration

Not qualified:
- Production authentication
- Direct database access restrictions
- Real tenant-identity binding
- Snapshot and restore
- Concurrent tenant operations

## Governance

No R10 requirement-level PASS is authorized.
All test outcomes require real logs and checksum evidence.
