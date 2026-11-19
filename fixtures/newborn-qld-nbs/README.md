# Bounded Queensland / Australian Newborn Bloodspot Screening Labour Pack (`0.1.0`)

This pack implements a bounded Phase 3 (`N3.1`–`N3.2` and `N3.3` labour-slice
comparison) composition for `newborn_screening_20261108` under the **health-service
provider perspective**. It pairs Dapane's two already-qualified pinned provider
inputs with public Queensland / Australian Newborn Bloodspot Screening (NBS)
governance references while preserving all unquoted programme stages, clinical
rates, and downstream costs as explicit source gaps.

> [!IMPORTANT]
> **Bounded non-clinical scope:** Only **manual DNA extraction labour** (`30`
> minutes laboratory work + `5` minutes administration per physical batch at the
> published Queensland Health HP3 pay point 1 base hourly reference `AUD 46.0658`)
> is priced here. This pack contains no patient records, no real Queensland
> perinatal epidemiology, no clinical benefit claim, no empirical validation,
> and no complete-programme NBS costing.

## Programme governance & pinned provider inputs

Public governance scope (recorded in [programme.json](programme.json)):

- **Queensland Clinical Guidelines (`MN25.53`):** Newborn bloodspot screening
  clinical guideline governing consent, universal heel-prick DBS collection at
  48–72 hours of age, early-discharge pathways, and repeat-specimen indications
  ([QCG](https://www.health.qld.gov.au/qcg)).
- **Queensland Government / Pathology Queensland:** Public NBS programme overview
  covering 25–30+ rare serious conditions including CF, CH, PKU/amino acid
  disorders, CAH, galactosaemia, fatty acid oxidation disorders, SMA, and SCID
  ([qld.gov.au NBS](https://www.qld.gov.au/health/children/babies/newborn-bloodspot-screening)).
- **Australian Government Department of Health and Aged Care:** National NBS
  framework and expansion scope ([health.gov.au NBS](https://www.health.gov.au/our-work/newborn-bloodspot-screening)).

Pinned provider inputs matching [provider-consumers.lock.json](../../docs/provider-consumers.lock.json)
and [python-provider-verification.md](../../docs/python-provider-verification.md):

| Input | Pinned repository & commit | Pinned source / artifact identity | Scope & explicit mapping note |
| --- | --- | --- | --- |
| QLD HP3.1 base salary quotation | `edithatogo/microcosting_healthworkforce` (`c351a7c6420a356c4c13d2da3010bc7e7d0341f9`, Python `3.15.2`) | Release `qld-health-hp3p1-reference-20261115`, quote `qld-hp3p1-minute-20260901` (`46.0658 / 60` AUD/min, `base_salary` only, `financial_cost`); source SHA-256 `6948663378e34af05b8dbf91d8799ad1dc14ee831136dc57165d3241d1af17ff`; exported artifact SHA-256 `9cd5e8bb48b29186b7fd4ea911f914c0e0dbf4f3fc188a1f6728cbe65947ec60` | Direct published reference base pay only; no superannuation, leave loading, penalty rates, or productive-hours adjustment. |
| Manual DNA extraction labour recipe | `edithatogo/microcosting_genomics` (`be2451f34a389f90e618cf37a5e8e1fcbb148dea`, Python `3.15.1`) | Recipe `manual-dna-extraction-v1`, sheet `Labour - Usage - VCGS`, cells `D22` (`30` min `labwork`) + `D23` (`5` min `admin`), nominal max 6 specimens/batch; workbook SHA-256 `2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4` | Analyst scenario maps `laboratory-scientist` HP3.1 base rate to historical manual DNA extraction batch minutes; no Pathology Queensland timing equivalence is claimed. |

## Explicit source gaps, exclusions & pending reporting

11 explicit records are declared in `programme.json#source_gaps`:

| Gap / exclusion ID | Stage | Status | Explanation |
| --- | --- | --- | --- |
| `collection_workforce_and_consumables` | `collection` | `unqualified_source_gap` | Collection events (`48`–`72`h) are context-only; midwifery/nursing minutes, lancets, and Guthrie cards are unquoted. |
| `specimen_transport` | `transport` | `unqualified_source_gap` | Statewide courier/postal transit rates to Pathology Queensland central laboratories are unavailable. |
| `accession_and_qc` | `accession_qc` | `unqualified_source_gap` | Specimen receipt, punching, demographic entry, and bloodspot adequacy QC are unquoted. |
| `biochemical_msms_and_immunoassay` | `assay` | `unqualified_source_gap` | TMS, fluoroimmunoassay, and galactosaemia enzyme assay labour/reagent inputs are excluded. |
| `molecular_reagents_and_instruments` | `assay` | `unqualified_source_gap` | DNA extraction kits, PCR/sequencing reagents, equipment depreciation, and capacity denominators are excluded. |
| `workforce_oncosts_and_loadings` | `manual_dna_extraction` | `unqualified_source_gap` | Only `base_salary` is quoted; on-costs, leave loading, penalties, and productive-hours factors are absent. |
| `reporting_recall_and_clinical_confirmation` | `confirmation` | `unqualified_source_gap` | Reporting, positive-screen recall, sweat tests, confirmatory testing, and follow-up are context-only (`0.00`). |
| `programme_overhead` | `programme_overhead` | `unqualified_source_gap` | LIMS administration, programme coordination, and registry governance overheads are unquoted. |
| `epidemiological_probabilities_and_timing` | `programme` | `unqualified_source_gap` | Birth cohorts (`4` and `8` births inside `[2026-11-01, 2026-11-16)`), inadequate-card counts, and confirmation flags are illustrative structures only. |
| `family_time_and_downstream_care` | `family_time` | `excluded_by_perspective` | Excluded under the selected `provider` perspective (`N3.2`). |
| `uogto_reporting_profiles` | `reporting_export` | `pending_optional_track` | CHEERS/GHCC/AGREEDT UOGTO exports remain pending qualification of `reporting_profiles_20261108` (PR #27); core valuation executes independently. |

## Independent exact & rounded comparison (5 cases)

Per physical batch (`30` min `labwork` + `5` min `admin` at `46.0658 / 60` AUD/min):

- `labwork`: exact `230329/10000` (`23.0329`), half-even rounded `23.03`
- `admin`: exact `230329/60000` (`3.838816...`), half-even rounded `3.84`
- Single batch total: exact `1612303/60000`, rounded `26.87` (matches the provider qualification oracle in [python-provider-verification.md](../../docs/python-provider-verification.md))
- Two-batch total: exact `1612303/30000`, rounded `53.74`

| Case | Batches | Exact total (AUD) | Rounded total (AUD) | Infant totals (AUD) | Denominators (`elig / part / valid / comp / diag`) |
| --- | ---: | --- | ---: | --- | --- |
| `qld-nbs-full-batch-6` | 1 (6 infants) | `1612303/60000` | `26.87` | `01..05: 4.48`, `06: 4.47` (`07, 08, 09-end: 0.00`) | `8 / 6 / 6 / 6 / 1` |
| `qld-nbs-partial-batch-3` | 1 (3 infants) | `1612303/60000` | `26.87` | `01: 8.96`, `02: 8.96`, `03: 8.95` (`04, 05-end: 0.00`) | `4 / 3 / 3 / 3 / 1` |
| `qld-nbs-failed-batch-repeat-3` | 2 (failed + repeat, 3 infants each) | `1612303/30000` | `53.74` | `01: 17.92`, `02: 17.92`, `03: 17.90` | `4 / 3 / 3 / 3 / 1` |
| `qld-nbs-inadequate-card-recollection-3` | 2 (`02,03` in `batch-1`; `01` repeat in `batch-2`) | `1612303/30000` | `53.74` | `01: 26.87`, `02: 13.44`, `03: 13.43` | `4 / 3 / 3 / 3 / 1` |
| `qld-nbs-unresolved-failed-screen-3` | 1 (3 infants; `01` assay failed) | `1612303/60000` | `26.87` | `01: 8.96`, `02: 8.96`, `03: 8.95` | `4 / 3 / 2 / 2 / 0` (`diag: null`) |

Independent denominator cost ratios in [expected.json](expected.json) record
both rounded-ledger (`26.87 / denom` or `53.74 / denom`) and exact-ledger
(`exact_total / denom`) expectations. Zero denominators map to `null` (never `0`).

## Reproduction & versioned rollback

Run all five prepared requests through an installed native CLI or installed wheel
from outside the checkout:

```sh
for c in qld-nbs-full-batch-6 qld-nbs-partial-batch-3 qld-nbs-failed-batch-repeat-3 qld-nbs-inadequate-card-recollection-3 qld-nbs-unresolved-failed-screen-3; do
  /path/to/dapane evaluate "/path/to/dapane/fixtures/newborn-qld-nbs/${c}.json"
done

cd /tmp
/path/to/consumer/bin/python -m pytest -p no:cacheprovider --import-mode=importlib \
  /path/to/dapane/tests/python/test_newborn_qld_nbs.py -q
```

**Rollback:** This pack is strictly additive (`fixtures/newborn-qld-nbs/` and
`tests/python/test_newborn_qld_nbs.py`). To roll back to the synthetic-only
baseline (`profile 0.1.0`), deselect or revert this directory and its dedicated
test file; [newborn-synthetic](../newborn-synthetic/README.md),
[newborn-screening.json](../newborn-screening.json), [expected.json](../expected.json),
the Rust kernel, and [provider-consumers.lock.json](../../docs/provider-consumers.lock.json)
remain completely unchanged.
