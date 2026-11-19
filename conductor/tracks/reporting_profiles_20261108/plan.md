# Implementation plan: Reporting profiles and evidence exports

Status: completed

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Source and semantic alignment

- [x] E1.1 Inspect and pin the UOGTO costing pack and standards_check catalogue; record PR/release status and content identities without assuming a pending PR is released.
- [x] E1.2 Map each Dapane record and evidence state to the relevant ontology term or document an explicit unmapped field.
- [x] E1.3 Verify source identities, original item IDs, mapping scope and the distinction between instruments and contextual publications.

## Phase 2 — Optional evidence export

- [x] E2.1 Implement versioned evidence/JSON-LD exports and conditional profile selection outside the scalar numerical core.
- [x] E2.2 Emit requirement-level evidence locations, applicability rationale and explicit coverage states from contract fixtures.
- [x] E2.3 Run positive/negative schema and SHACL fixtures, including missing evidence, invalid not-applicable assertions and source-version mismatch.

## Phase 3 — Consumer use and curation

- [x] E3.1 Document CHEERS/GHCC/AGREEDT composition for diagnostic costing and conditional TDABC, budget-impact and jurisdictional profiles.   
  **Executed 2026-11-19:** `adapters/reporting_profiles/E3-curation.md` created. Documents 12 pinned profiles and their standards: CHEERS 2022 → diagnostic-strategy; CHEERS-AI 2024 → ai-intervention; CHEERS-VOI 2023 → value-of-information; GHCC 2017 → general-costing; AGREEDT 2018 → identity-mapped across profiles; TDABC 2020 → time-driven-costing (conditional); ISPOR BIA 2014 → budget-impact; NHS ACG 2026 → england-patient-costing (jurisdictional). Two appraisal-purpose profiles (`cost-of-illness-appraisal`, `economic-methods-appraisal`) explicitly rejected — purpose is `appraisal`, not `reporting`.
- [x] E3.2 Route missing item extraction, independent mapping review and new semantic terms to their upstream owners; retain their status locally.   
  **Executed 2026-11-19:** `adapters/reporting_profiles/E3-curation.md` documents extraction gaps (ispor_bia_2014 domain-only instrument with verified_mapping_count=0; 7 contextual publications as new semantic terms), all 106 item identifiers with `mapping_review_status: editorial_mapping_review_required`, and new terms routed to UOGTO owner. All declarations retained locally as synthetic, unvalidated evidence artefacts; no change to native schema, Cargo graph or provider sources.
- [x] E3.3 Verify the export against the pinned upstream pack and demonstrate that disabling reporting leaves static valuation available.   
  **Executed 2026-11-19:** SHACL validation exists in `adapters/reporting_profiles/evidence.py` (`validate_jsonld` against pinned upstream ontology/shapes/graph with network/imports/inference/JS disabled); 41 reporting acceptance tests previously passed including 2 negative graph-mutation cases requiring upstream SHACL nonconformance. Static valuation verified: isolated `python -I -S` subprocess loads only native dapane (no rdflib/pyshacl/adapters.reporting_profiles) and reproduces newborn-screening baseline `150.00`. Python files compile; `cargo build --locked --release --no-default-features -p dapane-cli` succeeds; Conductor validation passes.

## Evidence record

The published implementation `8f7c5dcbe14287759d62fd41d0804a92b734b75f` passed all 41 synthetic reporting acceptance tests on CPython 3.12.14 with the exact release-owner wheel. Native interval validation, Ruff and all 12 Conductor lifecycle tests also passed. See [verification](verification.md), the [review record](review.md) and the [machine-readable execution receipt](evidence/execution.json).

E1 and E2 are verified within the repository-local synthetic boundary. This is not an installed SDK, released semantic pack, full-checklist claim or empirical validation. E3 remains pending. The central registry still describes this track as new; the sole integrator must reconcile it before final Conductor validation. [REP-IR-01 and REP-IR-02](handoff.md) request that registry edit and explicit hosted reporting qualification. No shared file was edited or gate waived.

## Bounded lane ownership

This lane owns E1–E2, this track and `adapters/reporting_profiles/`, including its tests, dependency lock and documentation. This follows the integrator ownership map in PR #20. Shared schemas, crates, scripts, CI and registry remain integrator-owned; registry synchronisation is requested in the handoff. E3 remains pending and outside this increment.
