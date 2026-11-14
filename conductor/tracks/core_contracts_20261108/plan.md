# Implementation plan: Core contracts and independent reference cases

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Inventory and reference cases

- [x] C1.1 Inspect the first workforce, genomics and MCHS capabilities; freeze one bounded example from each and label demonstration-only analyses.
- [x] C1.2 Derive expected exact quantities, rates, costs and allocation totals independently; retain any official/reference-source restrictions.
- [x] C1.3 Verify fixture provenance and reconcile discrepancies before adopting a baseline.

## Phase 2 — Contract definition

- [x] C2.1 Specify record fields, identities, units, activity kinds, valuation bases, component inclusion and structured errors.
- [x] C2.2 Specify decimal coefficient/scale or string encoding, numerator/denominator encoding, precision/overflow bounds and explicit conversion/rounding.
- [~] C2.3 Specify effective/knowledge dates, correction/retraction handling, schema versions and reproducible bundle manifests.
- [x] C2.4 Validate schemas against positive and negative reference fixtures; reject unsupported semantics rather than coercing them.

## Phase 3 — Consumer mapping

- [x] C3.1 Map one workforce, genomic and weighted-activity record to the contract; document intentional information loss or unsupported fields.
- [x] C3.2 Record extension namespacing, backward compatibility and deprecation behaviour without designing a native dynamic plugin ABI.
- [~] C3.3 Run the contract-fixture checks, document the accepted first kernel scope and update requirement/decision records.

## Bounded synthetic genomics increment — 14 November 2026

- [x] C4.1 Preserve the 0.1 full-pool contract and define a separate 0.2 instrument-capacity allocation with explicit unknown quantities and conserved unallocated value.
- [x] C4.2 Verify independent time/sample comparisons, missing use/capacity, rounding, strict rejection and installed Python parity using synthetic repository fixtures only.

The single Dapane integration coordinator owns this increment with P2.2/P2.4 in
the existing Python consumer track. PR #2 was integrated at
`056e8e3f78f6843bcd55e5d3816e7a23b167305f` after all seven checks passed on
`2e67d74329f664f0f2e4861869774425c82e176a`. Conditional security PR #5 is a
separate owner and is untouched. CareOps consumes qualified bundles; its files
and valuation implementation are outside this increment.

## Evidence record

The implemented profile is [contract 0.1](../../../docs/contract-v0.1.md), with [schemas](../../../schemas/README.md), [compatibility](../../../docs/compatibility.md) and [provider mappings](../../../docs/provider-boundaries.md). C2.3/C3.3 remain active for the broader correction/interval/capital scope and its acceptance cases. Unsupported fields are rejected in 0.1; this does not silently complete those profiles.

Full scope and observed commands/results are recorded in [runtime verification](../../../docs/runtime-verification.md). This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.

C4.1/C4.2 evidence: [capacity contract](../../../docs/contract-v0.2.md), [candidate cases](../../../fixtures/genomics-capacity/README.md), and [increment verification](../../../docs/genomics-capacity-verification.md). These complete the bounded synthetic tasks only.
