# Implementation plan: Core contracts and independent reference cases

Status: archived

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Inventory and reference cases

- [x] C1.1 Inspect the first workforce, genomics and MCHS capabilities; freeze one bounded example from each and label demonstration-only analyses.
- [x] C1.2 Derive expected exact quantities, rates, costs and allocation totals independently; retain any official/reference-source restrictions.
- [x] C1.3 Verify fixture provenance and reconcile discrepancies before adopting a baseline.

## Phase 2 — Contract definition

- [x] C2.1 Specify record fields, identities, units, activity kinds, valuation bases, component inclusion and structured errors.
- [x] C2.2 Specify decimal coefficient/scale or string encoding, numerator/denominator encoding, precision/overflow bounds and explicit conversion/rounding.
- [x] C2.3 Specify effective/knowledge dates, correction/retraction handling, schema versions and reproducible bundle manifests.
- [x] C2.4 Validate schemas against positive and negative reference fixtures; reject unsupported semantics rather than coercing them.

## Phase 3 — Consumer mapping

- [x] C3.1 Map one workforce, genomic and weighted-activity record to the contract; document intentional information loss or unsupported fields.
- [x] C3.2 Record extension namespacing, backward compatibility and deprecation behaviour without designing a native dynamic plugin ABI.
- [x] C3.3 Run the contract-fixture checks, document the accepted first kernel scope and update requirement/decision records.

## Bounded synthetic genomics increment — 14 November 2026

- [x] C4.1 Preserve the 0.1 full-pool contract and define a separate 0.2 instrument-capacity allocation with explicit unknown quantities and conserved unallocated value.
- [x] C4.2 Verify independent time/sample comparisons, missing use/capacity, rounding, strict rejection and installed Python parity using synthetic repository fixtures only.

The single Dapane integration coordinator owns this increment with P2.2/P2.4 in
the existing Python consumer track. PR #2 was integrated at
`056e8e3f78f6843bcd55e5d3816e7a23b167305f` after all seven checks passed on
`2e67d74329f664f0f2e4861869774425c82e176a`. Conditional security PR #5 is a
separate owner and is untouched. CareOps consumes qualified bundles; its files
and valuation implementation are outside this increment.

## Independent review and closeout — 15 November 2026

- [x] C5.1 Verify immutable release identity across the complete history and the specific chronology guard through the installed-wheel regression cases.
- [x] C5.2 Reconcile context and review evidence, verify the final PR checks and archive the completed contract track in place.

## Evidence record

The implemented profiles are [contract 0.1](../../../docs/contract-v0.1.md),
[capacity contract 0.2](../../../docs/contract-v0.2.md) and the separate
[run-bundle 0.1 envelope](../../../docs/run-bundle-v0.1.md), with
[schemas](../../../schemas/README.md), [compatibility](../../../docs/compatibility.md)
and [provider mappings](../../../docs/provider-boundaries.md).
C2.3/C3.3/C5.1/C5.2 are complete against the unchanged six contract/reference
acceptance criteria. Explicitly segmented intervals and alternative prepared
capital quotations define this track's accepted boundary; automatic interval
integration and capital methods remain with the kernel/provider tracks.

Final reviewed head `ea2cbffae505475108bfa5fb67e290f44349fee0` passed all 11
configured checks before [PR #9](https://github.com/edithatogo/dapane/pull/9)
merged at `224cf91dbcf513feaa022b2cf5aa310a965472ce`. Archival follows that
merge, as requested. See [closeout verification](verification.md), the
[independent review](independent-review.md) and [archive catalogue](../../archive/README.md).
All 14 task records are retained; none was removed to obtain completion.

The earlier [runtime verification](../../../docs/runtime-verification.md) and
[capacity verification](../../../docs/genomics-capacity-verification.md) remain
dated observations. Synthetic candidate calculations are not empirical validation.
Metadata, track index and registry record the same in-place archival disposition.
