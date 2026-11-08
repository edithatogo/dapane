# Research and validation programme

Status: planned evaluations, 8 November 2026. This document defines acceptance
evidence and research questions; it reports no Dapane runtime, performance or
clinical validation result. The repository setup establishes project context.

## Evidence is specific to the claim

Keep four assessments separate: reporting completeness, methodological appraisal,
computational verification and empirical validation. Schema or SHACL conformance
cannot establish that a source is true, a method appropriate or a programme
effective. A successful build cannot establish economic validity.

Each future qualification record should identify the exact source commit and
installed artifact, input/source digests, platform, method and capability, commands,
expected result origin, observed result, tolerances and unresolved limitations.
Use concise machine-readable results plus an explanation where needed. Reuse
existing checks when the relevant inputs have not changed; repeat broad tests
only for a concrete risk or a release gate. No additional approval board is
introduced by this programme.

The [requirements](./requirements.md), [track registry](./tracks.md) and
[workflow](./workflow.md) define execution. Claim scope follows the independently
qualified capability, not completion of every optional roadmap branch.

## Reference cases and expected-result independence

Use exact hand-derived cases, independently implemented calculation sheets or
scripts, and source-qualified official examples where redistribution is permitted.
Document derivations before comparing with the implementation. Reuse official
inputs under their actual terms and record any transcription/transformation.
Existing Python or workbook outputs are useful regression comparators, but cannot
be the sole oracle when they share the formula or suspected defect being tested.

| Case family | Required observations | Owning track |
| --- | --- | --- |
| Exact arithmetic | Nonterminating hour fractions, sub-cent amounts, negative corrections, bounded precision/overflow and explicit rounding at line/pool/aggregate level | [Rust kernel](./tracks/rust_kernel_20261108/index.md) |
| Units and quotes | Unit mismatch, absent quote versus explicit zero quote, resource versus activity quotation, incompatible classification edition and overlapping/ambiguous applicability | [Core contracts](./tracks/core_contracts_20261108/index.md) |
| Time and provenance | Usage spanning a rate boundary, half-open validity intervals, historical-as-known versus corrected data, withdrawn/corrected sources and immutable prior results | [Core contracts](./tracks/core_contracts_20261108/index.md) |
| Allocation and ledgers | Shared pools, alternative allocation drivers, residuals, duplicate resource IDs, loaded-rate component overlap, and exclusion of allocation views from source-ledger totals | [Rust kernel](./tracks/rust_kernel_20261108/index.md) |
| Economic interpretation | Acquisition, depreciation and annualisation treated as alternative policies; funding distinguished from resource cost; unused capacity distinguished from an observed cash saving | [MCHS/source adapters](./tracks/mchs_source_adapters_20261108/index.md) |
| Independent consumers | One workforce calculation used in one genomics recipe, with independently checked labour and batch components and historical API compatibility | [Python/two consumers](./tracks/python_two_consumers_20261108/index.md) |
| Installed language surfaces | Clean installed artifacts reproduce shared valid/invalid fixtures, preserve exact values and stable errors, and release memory correctly | [Python/two consumers](./tracks/python_two_consumers_20261108/index.md), [R/Julia](./tracks/polyglot_bindings_20261108/index.md) |
| Storage and scale | Encoding round trips, bounded memory, deterministic CPU results, chunk/reduction invariance, cancellation and incomplete-output diagnostics where applicable | [Release qualification](./tracks/release_consolidation_20261108/index.md) |

For stochastic methods, define distributions, correlations, indexed draws and
separate parameter draws from simulation replications. Exact arithmetic paths can
require exact equality; sampled or approximate methods need method-specific
numerical/statistical criteria. A seed alone is insufficient provenance across
different random generators, event ordering or backend versions.

## Existing semantic fixtures to reproduce numerically

These are reviewed UOGTO fixtures, not a delivered Dapane engine. Their sources are
pinned to
[`7e9075b8fd77543fc8853fab20319415cb86597d`](https://github.com/edithatogo/UOGTO/tree/7e9075b8fd77543fc8853fab20319415cb86597d).
All values are invented, and do not represent clinical prices, actual patients or
official hospital funding rates.

### Newborn screening: one shared batch

The [source fixture](https://github.com/edithatogo/UOGTO/blob/7e9075b8fd77543fc8853fab20319415cb86597d/examples/newborn-screening-costing.ttl)
has two infants, two specimens, one shared batch and a separate confirmation
episode. The runtime reference calculation must reproduce:

| Component | Infant A | Infant B | Source ledger |
| --- | ---: | ---: | ---: |
| Collection | 10 | 10 | 20 |
| One shared batch | 50 | 50 | 100 |
| Confirmation for B | 0 | 30 | 30 |
| Total in fictional AUD | 60 | 90 | 150 |

The allocated infant view sums to 150. It is not added again to the source ledger.
Mutation cases must detect assigning the entire batch to each infant, counting a
repeat specimen as another infant, omitting confirmation and adding both a loaded
staff rate and the same staff components separately.

The [newborn track](./tracks/newborn_screening_20261108/index.md) extends this with
repeat collection, failed/indeterminate assays, reflex tests, partially occupied
batches, a capacity step and a named observation window. Keep eligible births,
participating infants, valid screens, completed pathways and confirmed diagnoses
as distinct denominators. Compare programme totals, an additional condition/panel
and capacity expansion without assuming that average and marginal cost coincide.

### Weighted activity: direct funding valuation

The [activity-funding fixture](https://github.com/edithatogo/UOGTO/blob/7e9075b8fd77543fc8853fab20319415cb86597d/examples/activity-funding-valuation.ttl)
uses 2.50 fictional weighted units at 17.00 fictional AUD per unit, giving 42.50.
Its semantic graph has no `Resource` or `ResourceUse` instances after inference.
The runtime contract must allow a matching activity-kind quotation directly,
reject unqualified unit/kind substitutions, and retain `funding-valuation` as the
valuation basis. This checks an economic distinction as well as multiplication.

## Real programme and source validation

A real newborn-screening evaluation needs a defined programme/jurisdiction,
period, setting, perspective and comparison. Acquire source-qualified pathway,
staff time, consumable, equipment, transport, throughput, repeat and confirmation
inputs. Document sampling and missingness; preserve whether each value is observed,
assumed, transferred from another setting or inferred by a model.

Use permitted public or synthetic inputs in public fixtures. Keep patient-level
or restricted source records in their authorised environment and publish only
permitted reproducibility artifacts. De-identification alone does not establish
redistribution rights. Clinical eligibility and lifetime benefit assumptions are
owned by the linked programme/health-economic model, not inferred by costing.

External validation should compare independently observed quantities and costs,
check discrepancies by component and denominator, and test transfer to another
time period or site. Agreement with the data used to calibrate a model is not
external validation. Report uncertainty and the boundary within which a transfer
claim is supported. Australian programme material is a source-discovery entry
point for [screening and subsequent diagnostic testing](https://www.health.gov.au/our-work/newborn-bloodspot-screening/about),
not a universal pathway specification.

## Reporting-source qualification

The [reviewed standards_check catalogue](https://github.com/edithatogo/standards_check/tree/d1f1137edfa5375e0225ca2216903ce5583a44f0/reconciliations/costing)
contains 26 source records: 20 instrument versions and six contextual protocols or
reviews. It maps 31 domains and 106 verified original item/principle identifiers:
CHEERS 2022 (28), GHCC (17), AGREEDT (44), CHEERS-VOI supplements (6) and iDSI (11).
The [UOGTO snapshot](https://github.com/edithatogo/UOGTO/blob/7e9075b8fd77543fc8853fab20319415cb86597d/ontologies/reporting/costing-profiles.ttl)
contains 125 topic-mapping edges and 12 project-defined profiles.

These are bounded editorial research mappings requiring independent review.
GHCC coverage is at principle level, not every detailed checklist subrow;
CHEERS-VOI covers S1-S6, not every inherited/elaborated item. Other identified
instruments can have source/domain coverage without verified item extraction.
The catalogue adds zero full checklist transcriptions and is not an endorsed
universal standard or an exhaustive international systematic review.

The [reporting track](./tracks/reporting_profiles_20261108/index.md) should:

- Verify original tables and identifiers for remaining TDABC, CHEERS-AI, COI,
  BIA, immunisation, UNAIDS and jurisdictional profiles before claiming item
  completeness; preserve the actual source edition and extraction location.
- Independently review semantic mappings, record disagreements and retain
  source-specific requirements. `covers_topic` does not mean logical equivalence.
- Keep reporting, method appraisal, computational checks and empirical evidence
  as different assessments. Do not turn CHEERS completion into a quality score.
- Require evidence for reported requirements and a rationale for non-applicability;
  preserve partial, missing, unclear and unassessed states.
- Verify source permissions before any full checklist, template or spreadsheet
  redistribution. Dapane's future licence cannot relicense those sources.
- Recheck successors and unresolved protocols. No final universal microcosting
  or newborn-screening checklist, formal CHEERS-DCEA extension or final CHEERS
  ClimatE checklist was verified in the originating bounded review.

Compose CHEERS/GHCC with AGREEDT for screening, then add relevant method,
jurisdiction, budget-impact or VOI profiles. Select study-design adjuncts separately.
The primary anchors are [CHEERS 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8749494/),
[GHCC](https://ghcosting.org/pages/standards/appendices/principles_and_methods_reporting_checklist.php),
[AGREEDT](https://doi.org/10.1177/0272989X18797590),
[TDABC](https://doi.org/10.1186/s12913-020-05869-0) and
[AdViSHE](https://doi.org/10.1007/s40273-015-0327-2).

## Process and decision-integration evaluations

For the [process track](./tracks/process_models_20261108/index.md), compare executed
activity/resource records with independently enumerated tiny models before large
workloads. Include exclusive/parallel paths, loops/rework, shared staff, batch setup,
waiting versus active work, cancellation, censoring, transfers versus consumption
and model-version changes. Keep infant/specimen/batch links in object-centric logs.

Qualify a named Petri-net/PNML and BPMN subset with explicit resource and timing
semantics. Unsupported gateways/events must be rejected or separately reported;
silent flattening cannot count as conformance. Compare observed logs, bounded
manual traces and a qualified provider; provider agreement alone is insufficient
when both implementations share a conversion assumption.

For [decision integrations](./tracks/decision_integrations_20261108/index.md),
preserve strategy, scenario, draw, replication, perspective and subgroup identity.
Costs and outcomes must be joined through declared keys, with duplicate and missing
pairs rejected or explicitly handled. Test correlated uncertainty and distinguish
population heterogeneity from uncertainty in its parameters. Delegate supported
VOI/VOP/VOH operations to Voiage and strategic games to Paignia. Avoid summing
monetary transfers across perspectives as if they were new resource consumption.

A price-only change must preserve execution records. Where adoption or utilisation
responds to price, an explicit application scenario coordinates Innovate, process
execution and Dapane, with the feedback assumptions recorded.

## Frontier hypotheses and comparative evaluation

The [frontier track](./tracks/frontier_benchmarks_20261108/index.md) owns these
experiments. No novelty, superiority or performance result is asserted here.

| Hypothesis | Comparator and design | Primary evidence |
| --- | --- | --- |
| An evidence-linked ledger improves error detection | Controlled missing-cost, duplicate-cost, unit, denominator and provenance mutations against a conventional spreadsheet/script workflow | Detection sensitivity and false positives, explanation correctness, time to identify/fix, reproducibility |
| Object-centric costing better preserves shared resources | Identical infant/specimen/batch cases represented object-centrically and as flattened single-case traces, with independent allocation totals | Conservation violations, denominator errors, bias by throughput/rework and modelling effort |
| Incremental revaluation saves work without changing answers | Change one rate, policy or model fragment; compare each result with full recomputation using the same versioned inputs | Exact agreement on exact paths, justified tolerance otherwise, latency, memory and invalidation completeness |
| VOI-directed measurement improves costing decisions | Use a qualified Voiage method to compare time-motion, utilisation, wastage or price-data collection with fixed measurement plans | Expected/realised decision loss in controlled models, research costs and calibration; distinguish method validity from application assumptions |
| Capacity/adoption feedback changes implementation choices | Explicit Innovate trajectories and capacity thresholds compared with static average-cost assumptions | Incremental, opportunity and cash-cost differences, threshold recovery and sensitivity to behavioural assumptions |
| Multiple perspectives expose cost incidence and trade-offs | Paired perspective/subgroup outputs with known transfers and heterogeneity; qualified VOP/VOH and optional Paignia consumers | Correct incidence, no transfer double counting, interpretable decision changes and sensitivity to normative choices |
| Multi-site calibration can preserve useful information | A later aggregate/federated design compared with permitted central or local reference analyses | Disclosure risk, utility loss, site transportability and operational effort; no universal shared patient-data store |

Before experiments, register the question, input-generation/data protocol,
comparator versions, primary outcomes, tolerances and analysis plan. Include
representative batch, workforce, activity and programme cases rather than only
large synthetic arrays. Record CPU/OS, thread counts, memory, build flags and
cold/warm conditions for performance results. Benchmark scalar CPU first, then
justify each parallel/GPU/distributed path by workload-specific benefit.

Use controlled synthetic cases for known truth and failure injection; use external
programme data for transportability. Re-run a dated literature/software comparator
review before any frontier claim. Agent-produced outputs are not evidence of
independent human adoption or usability. A study should report limitations and
negative results alongside successful cases.

## Research outputs and release connection

Potential outputs are a reproducible software/methods paper after the first
qualified two-domain release, a newborn-screening application after real programme
validation, and separate methodological evaluations of shared-resource costing,
incremental revaluation or measurement design. Select venues after the relevant
claim and evidence are established; this setup makes no submission or publication
commitment.

The [release/consolidation track](./tracks/release_consolidation_20261108/index.md)
should package claim-specific fixtures, result manifests, source references and
capability limits with each release. Freeze historical study artifacts separately
from evolving defaults. An archive recommendation needs a working successor and
preserved unique research; successful benchmarks alone do not justify archiving a
domain or source-owner repository.
