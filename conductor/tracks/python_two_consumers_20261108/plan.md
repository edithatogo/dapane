# Implementation plan: Python delivery with workforce and genomics consumers

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Wrapper boundary

- [x] P1.1 Implement thin Python construction, batch calls, diagnostics and exact numeric conversion around the qualified Rust API.
- [x] P1.2 Keep Polars/Arrow adapters optional and retain Rust as the only owner of valuation/allocation formulas.
- [x] P1.3 Build and install the candidate wheel into a clean environment outside the checkout; verify public imports and native calls.

## Phase 2 — Independent domain consumers

- [ ] P2.1 Coordinate the workforce adapter with its source/rule owner; repair its generic import namespace in that provider repository through its own bounded change.
- [~] P2.2 Map one genomic workflow, batching and repeat/failure assumptions into resource recipes; label historical demonstration analyses.
- [ ] P2.3 Compose the genomic recipe with a dated workforce release and preserve component inclusion and source identities.
- [~] P2.4 Verify both consumers against independent reference cases and show that all shared arithmetic enters the Rust kernel.

## Phase 3 — Compatibility and migration

- [x] P3.1 Record actual interpreter/ABI/OS/architecture support, dependency locks and native build constraints.
- [ ] P3.2 Provide explicit old-entry-point adapters and a consumer rollback procedure; do not silently change historical results.
- [~] P3.3 Run installed-wheel parity, negative input/error tests and the two complete consumer examples; record evidence for the first release candidate.

## Evidence record

The 14 November bounded P2.2/P2.4 increment adds synthetic genomics capacity
comparisons under core-contract tasks C4.1/C4.2. Keep device useful life distinct
from maintenance contract duration, and one-time implementation costs distinct
from recurrent period costs. Candidate preparation assumptions are not validated
economic methods. This work does not migrate a real provider or edit CareOps.

The Python package delegates valuation/allocation to Rust and adds exact Decimal/Fraction transport. [Runtime verification](../../../docs/runtime-verification.md) records the installed-wheel matrix. Synthetic workforce/genomics consumers exercise the shared kernel; they do not complete P2.1/P2.3 provider migration, workforce namespace repair, dated real release composition, or P3.2 historical entry-point parity. P2.2/P2.4/P3.3 remain partial until those real consumers are qualified.

Full scope and observed commands/results are recorded in [runtime verification](../../../docs/runtime-verification.md). This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
