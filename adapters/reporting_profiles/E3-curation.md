# E3 — Reporting consumer curation (pending upstream qualification)

This document records E3.1–E3.3 for the reporting track. E1–E2 are complete;
E3 curation is bounded synthetic documentation and verification only. No
production SDK, shared schema registration, or interval-to-bundle export is
claimed.

## E3.1 — Profile composition

Twelve project-defined reporting profiles are pinned, each referencing
original instrument/version/item identifiers from the upstream catalogue.
No profile is a full-checklist transcription, and none claims external
endorsement or methodological completeness.

| Profile | IRI suffix | Primary standards | Costing context | Notes |
|---|---|---|---|---|
| `ai-intervention` | `/profile/ai-intervention` | CHEERS-AI 2024 | diagnostic costing (AI intervention) | Source: `cheers_ai_2024` |
| `australian-hospital-costing` | `/profile/australian-hospital-costing` | AHPCS 4.2 | hospital activity costing | Source: `ahpcs_4_2` |
| `budget-impact` | `/profile/budget-impact` | ISPOR BIA 2014 | budget-impact analysis | Domain-only instrument; verified mapping count 0; extraction gap declared |
| `cost-of-illness-appraisal` | `/profile/cost-of-illness-appraisal` | COI appraisal 2023 | appraisal instrument | `purpose` is `appraisal`, not `reporting`; rejected by this reporting-only candidate |
| `diagnostic-strategy` | `/profile/diagnostic-strategy` | CHEERS 2022 | diagnostic costing | Source: `cheers_2022` |
| `economic-methods-appraisal` | `/profile/economic-methods-appraisal` | appraisal guideline | appraisal | `purpose` is `appraisal`, not `reporting`; rejected by this reporting-only candidate |
| `england-patient-costing` | `/profile/england-patient-costing` | NHS ACG 2026 | jurisdictional (England patient costing) | Source: `nhs_acg_2026` |
| `general-costing` | `/profile/general-costing` | GHCC 2017 / Second Panel 2016 | general costing | Source: `ghcc_2017` |
| `newborn-screening` | `/profile/newborn-screening` | synthetic declaration | newborn screening | Project-defined synthetic profile; no external endorsement |
| `time-driven-costing` | `/profile/time-driven-costing` | TDABC 2020 | conditional TDABC | Source: `tdabc_2020` |
| `validation-reporting` | `/profile/validation-reporting` | synthetic declaration | validation reporting | Project-defined synthetic profile; no external endorsement |
| `value-of-information` | `/profile/value-of-information` | CHEERS-VOI 2023 | value-of-information | Source: `cheers_voi_2023` |

CHEERS/GHCC/AGREEDT composition across profiles:
- **CHEERS 2022** (27 original items): referenced by `diagnostic-strategy` profile for diagnostic costing scope.
- **CHEERS-AI 2024**: referenced by `ai-intervention` profile for AI-intervention costing scope.
- **CHEERS-VOI 2023** (6 items): referenced by `value-of-information` profile for VOI scope.
- **GHCC 2017** (17 items): referenced by `general-costing` profile for general costing scope.
- **AGREEDT 2018** (45 items): identity-mapped across profiles; extraction qualifications retained upstream; editorial mapping review required.
- **TDABC 2020**: referenced by `time-driven-costing` profile for conditional time-driven activity-based costing scope.
- **ISPOR BIA 2014**: referenced by `budget-impact` profile for budget-impact scope; domain-only instrument with no verified full-checklist transcription.
- **NHS ACG 2026**: referenced by `england-patient-costing` profile for jurisdictional (England) scope.

Two appraisal-purpose profiles (`cost-of-illness-appraisal`, `economic-methods-appraisal`) are present in the pinned catalogue but are not accepted by this reporting-only candidate: their `purpose` is `appraisal`, not `reporting`. Protocols and reviews remain evidence artefacts, not operational reporting checklists.

## E3.2 — Routing to upstream owners; local status retention

Missing item extraction, independent mapping review and new semantic terms are
not resolved locally. They are declared here and routed to their upstream owners:

### Extraction gaps (domain-only instruments, zero verified mappings)

| Instrument | Version | Profile(s) | Gap | Routed to |
|---|---|---|---|---|
| `ispor_bia_2014` | ISPOR BIA 2014 | `budget-impact` | `verified_mapping_count`: 0; no full-checklist transcription | standards_check owner (item-level extraction qualification) |
| `cheers_climate_protocol_2025` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |
| `genomic_microcosting_protocol_2023` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |
| `genomic_microcosting_review_2023` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |
| `genomic_oncology_review_2026` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |
| `microcosting_protocol_2016` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |
| `microcosting_review_2021` | synthetic source | — | contextual publication, not an instrument | UOGTO owner (new semantic term) |

### Items requiring independent editorial mapping review

All 106 original instrument/version/item identifiers carry
`mapping_review_status: editorial_mapping_review_required`. This status is
retained locally and is not relabelled as independently reviewed. UOGTO and
standards_check owners retain editorial review authority.

### New semantic terms

New terms not present in the pinned upstream ontology (CHEERS-AI 2024,
CHEERS-VOI 2023, cost-of-illness appraisal 2023, NHS ACG 2026) are routed to
the UOGTO owner for ontology registration. No new term is declared locally as
an upstream standard.

### Local retention

All declarations above are retained locally as synthetic, unvalidated evidence
artefacts. They do not change the native run-bundle schema, the shared Cargo
dependency graph, or any provider-owned source.

## E3.3 — Verification against pinned upstream pack; static valuation without reporting

### SHACL conformance against pinned upstream pack

The export graph is validated against the actual pinned UOGTO ontology, costing
profiles graph and costing-valuation SHACL shapes with:
- Network retrieval disabled
- OWL imports disabled
- Inference disabled
- Advanced rules disabled
- JavaScript disabled
- Only the fixed inline prefix JSON-LD 1.1 context accepted
- Only upstream OWL object/datatype properties accepted as predicates
- Only upstream export node classes accepted
- No nested contexts or upstream redefinitions

All 41 reporting acceptance tests pass, including two negative graph mutations
that require nonconformance from the actual upstream SHACL (removed evidence
from a partial assertion; removed rationale from a not-applicable assertion).

### Static valuation without reporting dependencies

An isolated `python -I -S` subprocess loads only the installed native Dapane
module (rdflib, pyshacl and `adapters.reporting_profiles` are absent) and
executes the static newborn-screening baseline (`fixtures/newborn-screening.json`),
producing `150.00` exactly. This demonstrates that static native valuation
remains available with reporting dependencies disabled.

### Verification commands executed

```sh
DAPANE_REPORTING_SOURCES=/path/to/exact-snapshots \
  python -m unittest discover -s adapters/reporting_profiles/tests -v
python scripts/validate_intervals.py --cli /path/to/exact/dapane
ruff check adapters/reporting_profiles
ruff format --check adapters/reporting_profiles
python scripts/validate_conductor.py
python -m unittest discover -s tests -p test_conductor_validation.py -v
```

41 reporting tests passed on CPython 3.12.14 with the exact release-owner wheel.
Native interval validation, Ruff lint/format and 12 Conductor lifecycle tests
also passed. The single Conductor registry marker mismatch (REP-IR-01) remains
open and is owned by the sole integrator; it is not waived.

## Limitations

- Source hashes identify repository files; they do not verify publisher source truth or independent content review.
- The UOGTO pack is an open PR head (`7e9075b8...`), not a released semantic product.
- SHACL success is graph conformance only; it is not methodological correctness or empirical validity.
- Reporting coverage is caller-declared with explicit unassessed defaults; no compliance score is produced.
- Installed SDK extra, shared schema registration and interval-to-bundle export remain separate integrator decisions.
