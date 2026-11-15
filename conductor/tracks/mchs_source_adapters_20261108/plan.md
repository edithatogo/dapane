# Implementation plan: MCHS activity and quotation-source adapters

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Provider contract mapping

- [x] M1.1 Inspect the current MCHS and reimbursement-atlas contracts and select exact provider revisions and supported capabilities.
- [x] M1.2 Map classification/edition, activity kind, quote applicability and source/licence fields without duplicating provider equations or parsers.
- [~] M1.3 Verify the mapping using activity-only, incompatible-quote and edition-boundary cases.

## Phase 2 — Adapters and parallel views

- [~] M2.1 Implement the bounded MCHS activity adapter and atlas quotation-pack adapter behind optional dependencies.
- [~] M2.2 Produce explicitly labelled cost/funding/tariff/payment views only when the required evidence exists; payments require observations or a labelled model.
- [!] M2.3 Verify exact results, provenance, missing-rate handling and separation of valuation views.

## Phase 3 — Consumer migration

- [ ] M3.1 Coordinate repository-local MCHS/atlas integration changes and preserve existing public interfaces during qualification.
- [ ] M3.2 Document provider pins, supported editions, source restrictions and rollback to prior qualified adapters.
- [ ] M3.3 Run installed consumer fixtures and reject any conversion of weighted activity into fictitious resources; record exact qualification evidence.

## Evidence record

M1.1/M1.2 are supported by [exact upstream inspection and mapping](contracts.md).
The M1/M2 source candidate, synthetic fixtures and 34 authored tests are in
`adapters/mchs_sources/`. [Review](review.md) records source fixes. An earlier
working version passed 24 tests using the existing native CLI; those results do
not qualify the recovered final source after the execution environment outage.

**M1.3 and M2 remain open.** The exact-head suite, formatting and installed package
checks have not executed. M2.3 is blocked on an available existing execution
runtime and the integrator-owned qualification invocation. See
[verification](verification.md), [handoff](handoff.md), and
[shared-change requests](shared-change-requests.md). M3 remains outside this lane.

Owner: Dapane — MCHS and atlas adapters. Baseline:
`e34f87c9df39a2132fecee142431cdeefb732471`. Upstream repositories are read-only.
The sole integrator owns the root registry; its matching in_progress row is
requested, not edited or waived. Publication remains disabled.
