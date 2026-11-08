# Implementation plan: Newborn screening pathway composition

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Domain recipe

- [ ] N1.1 Define the newborn object relationships and supported stage/branch vocabulary using the shared contracts.
- [ ] N1.2 Compose workforce and laboratory recipes with explicit resource/component inclusion and allocation policies.
- [ ] N1.3 Verify that multiple assays per specimen and multiple infants per batch retain correct identities and cost boundaries.

## Phase 2 — Synthetic execution cases

- [ ] N2.1 Implement the independent 150-total, 60/90-allocation case with invented quantities and rates clearly labelled synthetic.
- [ ] N2.2 Add repeat collection, inadequate specimens, failed/reflex assays, partial batches and an extra-capacity threshold case.
- [ ] N2.3 Verify pool conservation, marginal versus average results, denominator/window definitions and family-time inclusion by perspective.

## Phase 3 — Programme and reporting qualification

- [ ] N3.1 Select a real programme scope and acquire authorised, source-qualified workflow/quantity/rate inputs; record gaps explicitly.
- [ ] N3.2 Produce costing outputs through the shared core. If reporting/profile support is selected, first qualify reporting_profiles_20261108 and then its UOGTO exports; otherwise retain that capability as pending. Neither this adapter nor real-programme source acquisition blocks Phases 1–2 synthetic costing. Keep outcomes/eligibility assumptions in the programme or health-economic model.
- [ ] N3.3 Compare the programme calculations with independent examples, record unresolved source limitations and document reproduction/rollback before advertising real-programme support.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
