# Implementation plan: Reporting profiles and evidence exports

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Source and semantic alignment

- [ ] E1.1 Inspect and pin the UOGTO costing pack and standards_check catalogue; record PR/release status and content identities without assuming a pending PR is released.
- [ ] E1.2 Map each Dapane record and evidence state to the relevant ontology term or document an explicit unmapped field.
- [ ] E1.3 Verify source identities, original item IDs, mapping scope and the distinction between instruments and contextual publications.

## Phase 2 — Optional evidence export

- [ ] E2.1 Implement versioned evidence/JSON-LD exports and conditional profile selection outside the scalar numerical core.
- [ ] E2.2 Emit requirement-level evidence locations, applicability rationale and explicit coverage states from contract fixtures.
- [ ] E2.3 Run positive/negative schema and SHACL fixtures, including missing evidence, invalid not-applicable assertions and source-version mismatch.

## Phase 3 — Consumer use and curation

- [ ] E3.1 Document CHEERS/GHCC/AGREEDT composition for diagnostic costing and conditional TDABC, budget-impact and jurisdictional profiles.
- [ ] E3.2 Route missing item extraction, independent mapping review and new semantic terms to their upstream owners; retain their status locally.
- [ ] E3.3 Verify the export against the pinned upstream pack and demonstrate that disabling reporting leaves static valuation available.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
