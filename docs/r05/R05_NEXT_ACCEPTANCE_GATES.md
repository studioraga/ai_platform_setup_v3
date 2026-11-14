# R05-C/D/E continuation — evidence requirements

**Status:** engineering preparation only. The R05-B/C probe commit `0dd2913` is evidence of tools, not approved public API or R05 acceptance.

## Observed Node1 evidence

- v0.29 and v0.30 wheel hashes are captured outside Git.
- Candidate inventories: 1,879 and 1,929; triage: 1,705 combined symbol keys.
- 12 seed imports in both installed wheel consumers, zero observed top-level signature/type deltas.
- Eight synthetic discovery tests passed; the historical seven shared tests per version previously passed.

## Review gates

1. **B classification:** Resolve package public imports and `__all__`, the kernel star import, documentation, and aliases. Maintainer signs supported/common versus private versus v0.30-only declarations. No automatic approval.
2. **C common method contracts:** For every *approved* common symbol, enumerate constructors, inherited methods, positional/keyword boundaries, async behavior, exceptions, and re-export identity. Run identical tests in both wheel consumer environments. Document unsupported or dynamic signatures.
3. **D behavioral tests:** Explicit serialization schema/JSON normalization, stable exception categories, invalid input, deny precedence, tenant constraints if actually enforced, HMAC failure, expiry, nonce duplication and replay corruption. Do not infer tenant isolation from a resource prefix test.
4. **E version policy:** Maintainer-approved pre-1.0 contract and disposition of distribution metadata versus historical `__version__` mismatch; breaking-change migration plan.
5. **Independent gate:** Evidence SHA, wheel provenance, test logs, reproducible commands, public-surface approval and reviewer identity. R05 remains NOT_RUN / PENDING pending all these decisions. M30 production release remains unrelated.

Generated JSON, CSV, security reports, wheel bytes, and runtime credentials stay in ignored `reports/` or the original preparation environment; never in Git.
