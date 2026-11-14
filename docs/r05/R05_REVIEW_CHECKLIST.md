# R05 Review Worksheet — pending manual decisions

| Item | Version 0.29 evidence | Version 0.30 evidence | Decision | Reviewer |
|---|---|---|---|---|
| Wheel fingerprint capture / provenance approval | SHA-256 recorded | SHA-256 recorded | Capture PASS; provenance approval PENDING | — |
| Public API declaration and re-export paths | 1,879 candidate records; unclassified | 1,929 candidate records; unclassified | Discovery PASS; supported-surface review PENDING | — |
| Class/instance methods and signatures | AST candidate inventory | AST candidate inventory | PENDING | — |
| Dataclass fields / serialization and JSON | Seven-test seed only | Seven-test seed only | PENDING | — |
| Exceptions and negative auth / replay | Seven-test seed only | Seven-test seed only | PENDING | — |
| Pre-1.0 SemVer policy, compatibility guarantee | Not authorized | Not authorized | PENDING | — |
| Dual-wheel expanded runtime test suite | Not run | Not run | PENDING | — |
| Independent API/security acceptance | Not run | Not run | BLOCKED | — |

For every alleged breaking change, record exact source symbol, old/new signature/schema/response, supporting test and migration recommendation. Document intentionally new v0.30-only APIs separately. Refuse a PASS disposition without reviewer identity and evidence hashes.
