# Implementation plan: Newborn screening pathway composition

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Domain recipe

- [x] N1.1 Define the newborn object relationships and supported stage/branch vocabulary using the shared contracts.
- [x] N1.2 Compose workforce and laboratory recipes with explicit resource/component inclusion and allocation policies.
- [x] N1.3 Verify that multiple assays per specimen and multiple infants per batch retain correct identities and cost boundaries.

## Phase 2 — Synthetic execution cases

- [x] N2.1 Implement the independent 150-total, 60/90-allocation case with invented quantities and rates clearly labelled synthetic.
- [x] N2.2 Add repeat collection, inadequate specimens, failed/reflex assays, partial batches and an extra-capacity threshold case.
- [x] N2.3 Verify pool conservation, marginal versus average results, denominator/window definitions and family-time inclusion by perspective.

## Phase 3 — Programme and reporting qualification

- [ ] N3.1 Select a real programme scope and acquire authorised, source-qualified workflow/quantity/rate inputs; record gaps explicitly.
- [ ] N3.2 Produce costing outputs through the shared core. If reporting/profile support is selected, first qualify reporting_profiles_20261108 and then its UOGTO exports; otherwise retain that capability as pending. Neither this adapter nor real-programme source acquisition blocks Phases 1–2 synthetic costing. Keep outcomes/eligibility assumptions in the programme or health-economic model.
- [ ] N3.3 Compare the programme calculations with independent examples, record unresolved source limitations and document reproduction/rollback before advertising real-programme support.

## Evidence record

The [synthetic request](../../../fixtures/newborn-screening.json) and [independent expectations](../../../fixtures/expected.json) implement N2.1, with explicit infant/specimen/batch/confirmation objects, four events, a process and relations. The authorised N1 synthetic recipe, vocabulary and component composition are implemented in fixtures/newborn-synthetic. This does not claim real provider or programme execution. The bounded repeat/failure/capacity and denominator references are now implemented. Source-qualified programmes, real providers and production reporting remain pending.

Full scope and observed commands/results are recorded in [runtime verification](../../../docs/runtime-verification.md). This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.

## Authorised lane and N1 evidence, 2026-11-15

This lane owns this track, `fixtures/newborn-synthetic/` and
`tests/python/test_newborn_synthetic.py`, as explicitly authorised by Dylan.
Initial main is `e34f87c9df39a2132fecee142431cdeefb732471`; the sole open PR
was release PR #17 at `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`.
The integrator owns shared crates, schemas, manifests, CI, registry and root docs.
No other worker was created; no external repository was changed.

Four N1 installed-wheel checks passed before proceeding to N2. A workspace restart
cleared the initial temporary checkout after an earlier 196-test run. Recovered
files are tested afresh; that earlier run is not claimed as proof of recovered bytes.
The initial local N1 commit `429d3320c4199042882c111546a3aba5c356d817` was never pushed
and is not the submission SHA. N3 remains pending.

## N2 executed scope and review

Thirteen prepared cases pass 63 dedicated installed-wheel checks. The recovered
full installed Python suite passes 196 tests. Existing point/interval validators,
twelve Conductor regressions and Ruff lint/format also pass. Record-order invariance,
eleven native rejection cases, distinct-infant denominators, zero denominators,
family inclusion and unknown capacity retain their explicit meanings.

Self-review narrowed the compatibility freeze to the newborn entry inside the
shared expectations file, so unrelated additions remain possible. It also added
result-to-assay-to-specimen-to-infant checks before a final result can qualify an
episode. Neither review is labelled independent third-party review. N3 remains
pending and the track stays in progress.

The later integrator ownership PR #20 reserves `adapters/newborn_screening/` by
default. Dylan explicitly authorised this lane's fixture/test paths. Request the
central map be reconciled to those paths; this lane does not edit that map, the
registry, shared schemas, crates, manifests, CI or root docs.

The [exact-source handoff](handoff.md) and [verification receipt](verification.json)
retain the published implementation SHA/tree, artifact identities, CLI digests,
rounding control and executed-versus-unexecuted qualification.
