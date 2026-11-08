# Implementation plan: Python delivery with workforce and genomics consumers

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Wrapper boundary

- [ ] P1.1 Implement thin Python construction, batch calls, diagnostics and exact numeric conversion around the qualified Rust API.
- [ ] P1.2 Keep Polars/Arrow adapters optional and retain Rust as the only owner of valuation/allocation formulas.
- [ ] P1.3 Build and install the candidate wheel into a clean environment outside the checkout; verify public imports and native calls.

## Phase 2 — Independent domain consumers

- [ ] P2.1 Coordinate the workforce adapter with its source/rule owner; repair its generic import namespace in that provider repository through its own bounded change.
- [ ] P2.2 Map one genomic workflow, batching and repeat/failure assumptions into resource recipes; label historical demonstration analyses.
- [ ] P2.3 Compose the genomic recipe with a dated workforce release and preserve component inclusion and source identities.
- [ ] P2.4 Verify both consumers against independent reference cases and show that all shared arithmetic enters the Rust kernel.

## Phase 3 — Compatibility and migration

- [ ] P3.1 Record actual interpreter/ABI/OS/architecture support, dependency locks and native build constraints.
- [ ] P3.2 Provide explicit old-entry-point adapters and a consumer rollback procedure; do not silently change historical results.
- [ ] P3.3 Run installed-wheel parity, negative input/error tests and the two complete consumer examples; record evidence for the first release candidate.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
