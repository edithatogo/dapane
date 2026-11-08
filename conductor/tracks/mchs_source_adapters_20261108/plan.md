# Implementation plan: MCHS activity and quotation-source adapters

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Provider contract mapping

- [ ] M1.1 Inspect the current MCHS and reimbursement-atlas contracts and select exact provider revisions and supported capabilities.
- [ ] M1.2 Map classification/edition, activity kind, quote applicability and source/licence fields without duplicating provider equations or parsers.
- [ ] M1.3 Verify the mapping using activity-only, incompatible-quote and edition-boundary cases.

## Phase 2 — Adapters and parallel views

- [ ] M2.1 Implement the bounded MCHS activity adapter and atlas quotation-pack adapter behind optional dependencies.
- [ ] M2.2 Produce explicitly labelled cost/funding/tariff/payment views only when the required evidence exists; payments require observations or a labelled model.
- [ ] M2.3 Verify exact results, provenance, missing-rate handling and separation of valuation views.

## Phase 3 — Consumer migration

- [ ] M3.1 Coordinate repository-local MCHS/atlas integration changes and preserve existing public interfaces during qualification.
- [ ] M3.2 Document provider pins, supported editions, source restrictions and rollback to prior qualified adapters.
- [ ] M3.3 Run installed consumer fixtures and reject any conversion of weighted activity into fictitious resources; record exact qualification evidence.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
