# Implementation plan: Reporting profiles and evidence exports

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Source and semantic alignment

- [x] E1.1 Inspect and pin the UOGTO costing pack and standards_check catalogue; record PR/release status and content identities without assuming a pending PR is released.
- [x] E1.2 Map each Dapane record and evidence state to the relevant ontology term or document an explicit unmapped field.
- [x] E1.3 Verify source identities, original item IDs, mapping scope and the distinction between instruments and contextual publications.

## Phase 2 — Optional evidence export

- [x] E2.1 Implement versioned evidence/JSON-LD exports and conditional profile selection outside the scalar numerical core.
- [x] E2.2 Emit requirement-level evidence locations, applicability rationale and explicit coverage states from contract fixtures.
- [~] E2.3 Run positive/negative schema and SHACL fixtures, including missing evidence, invalid not-applicable assertions and source-version mismatch.

## Phase 3 — Consumer use and curation

- [ ] E3.1 Document CHEERS/GHCC/AGREEDT composition for diagnostic costing and conditional TDABC, budget-impact and jurisdictional profiles.
- [ ] E3.2 Route missing item extraction, independent mapping review and new semantic terms to their upstream owners; retain their status locally.
- [ ] E3.3 Verify the export against the pinned upstream pack and demonstrate that disabling reporting leaves static valuation available.

## Evidence record

The restored optional adapter passed 35 synthetic acceptance tests on CPython 3.12.14 with the exact release-owner wheel. Final review, source-bound evidence and integration requests are being completed.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.

## Bounded lane ownership

This lane owns E1–E2, this track and `adapters/reporting_profiles/`, including its tests, dependency lock and documentation. This follows the integrator ownership map in PR #20. Shared schemas, crates, scripts, CI and registry remain integrator-owned; registry synchronisation is requested in the handoff. E3 remains pending and outside this increment.
