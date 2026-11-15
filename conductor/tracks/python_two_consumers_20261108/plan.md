# Implementation plan: Python delivery with workforce and genomics consumers

Status: archived

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Wrapper boundary

- [x] P1.1 Implement thin Python construction, batch calls, diagnostics and exact numeric conversion around the qualified Rust API.
- [x] P1.2 Keep Polars/Arrow adapters optional and retain Rust as the only owner of valuation/allocation formulas.
- [x] P1.3 Build and install the candidate wheel into a clean environment outside the checkout; verify public imports and native calls.

## Phase 2 — Independent domain consumers

- [x] P2.1 Coordinate the workforce adapter with its source/rule owner; repair its generic import namespace in that provider repository through its own bounded change.
- [x] P2.2 Map one genomic workflow, batching and repeat/failure assumptions into resource recipes; label historical demonstration analyses.
- [x] P2.3 Compose the genomic recipe with a dated workforce release and preserve component inclusion and source identities.
- [x] P2.4 Verify both consumers against independent reference cases and show that all shared arithmetic enters the Rust kernel.

## Phase 3 — Compatibility and migration

- [x] P3.1 Record actual interpreter/ABI/OS/architecture support, dependency locks and native build constraints.
- [x] P3.2 Provide explicit old-entry-point adapters and a consumer rollback procedure; do not silently change historical results.
- [x] P3.3 Run installed-wheel parity, negative input/error tests and the two complete consumer examples; record evidence for the first release candidate.

## Evidence record

Completed and archived in place on 15 November 2026 after implementation,
independent review, fixes and the required qualification checks. The
[provider qualification record](../../../docs/python-provider-verification.md)
identifies immutable revisions, the exact source/artifact hashes, actual commands,
results and scope limits. The [review](review.md) retains findings and closure.

The final increment supplies the previously missing provider work: workforce
namespace/resource compatibility, a dated quotation export, the manual extraction
recipe and explicit failures/retries, exact file composition, installed native
parity and the actual historical calculator route. All shared valuation and
allocation stay in Rust; no provider dependency pin was widened.

The coordinating branch incorporates the completed core-contract and Rust-kernel
work. Both installed consumers and the 133-test Python suite were requalified
against the integrated Rust source. Provider-owned gates verify the full owning
packages, including workforce's LibreOffice-dependent tests and genomic wheel
packaging. Only the selected labour scope is qualified; whole-assay and
scientific validation are not inferred.

### Retained earlier checkpoints

The 14 November bounded P2.2/P2.4 increment added synthetic genomics capacity
comparisons under core-contract tasks C4.1/C4.2. It kept device useful life distinct
from maintenance contract duration, and one-time implementation costs distinct
from recurrent period costs. Those candidate assumptions are not validated
economic methods.

The earlier [runtime record](../../../docs/runtime-verification.md) qualified
the native binding and synthetic consumers while the real provider work remained
open. This completion increment supplies that missing evidence without rewriting
the earlier observations. Interrupted setup and failed intermediate attempts are
not counted as passes.

The specification, completed plan, metadata, review and evidence retain their
original paths. The archive concerns this track; provider ownership and the
separate release/consolidation gates remain intact.
