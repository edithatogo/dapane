# Product definition

## Purpose

Dapane will provide a reusable Rust microcosting and valuation framework. It will
apply explicit valuation policies to resource-use and activity records, preserve
their provenance, reconcile shared costs and return reproducible result bundles.
Its specialist consumers initially cover health workforce, genomic testing,
hospital activity/funding and newborn screening.

## Users and decisions

- Researchers need reproducible component costs, assumptions, sensitivity inputs
  and reporting evidence for economic studies.
- Service and programme analysts need costs by activity, pathway, patient group,
  throughput and capacity scenario, with meaningful denominators.
- Domain-library maintainers need one qualified implementation of common
  arithmetic while retaining their own specialist rules and source releases.
- Operational users need forms, comparisons and explanations in CareOps or Power
  Apps without creating another financial calculation implementation.
- Decision-model developers need aligned scenario/draw/perspective/subgroup
  outputs that can be combined with health outcomes and behavioural models.

## Product outcomes

1. Reproduce a valuation from immutable inputs, versions and declared policies.
2. Explain which quantities, prices, allocations or assumptions produced a result.
3. Revalue unchanged use under another quotation release or perspective.
4. Detect missing quotes, incompatible units, duplicate source costs and
   unreconciled allocations before presenting a result as complete.
5. Compose specialist packages without a mandatory simulator, cloud tenant,
   database, table engine or ontology reasoner.
6. Publish language and platform support only for qualified installed artefacts.

## First delivery boundary

The first implementation target is a small Rust kernel, a CLI/file contract and
Python binding used by one workforce calculation and one genomic workflow. It
must cover exact values, source applicability, a component ledger and a shared
allocation case. Preserve existing domain APIs through adapters.

Newborn screening is the next new domain. It must distinguish infants, specimens,
assays, batches, repeats, confirmation and output denominators. The Power Platform
baseline is standard-connector/file exchange; worker, premium API and browser
delivery remain separately qualified options.

## Boundaries

Dapane owns common contracts, valuation/allocation mechanics, provenance and
binding behaviour. It does not own employment awards, assay definitions, official
hospital classifications, tariff-source collection, clinical eligibility,
simulation clocks, game solvers or VOI estimators. Those stay with their providers.

The framework supports resource and activity valuations with explicit economic,
accounting, cash, tariff and funding bases. Strategic price setting and
cost-effectiveness remain composed decision applications. A quantity-times-price
calculation alone does not demonstrate an appropriate opportunity-cost estimate,
clinical benefit or actual payment.

## Non-functional priorities

Numerical correctness and source traceability come first. APIs should be usable
from small studies and batch workloads; IO and acceleration remain optional.
Determinism, clear failures, bounded memory and installable packages are release
criteria. Exact execution and stochastic model evaluation have separately stated
reproducibility contracts.

## Current maturity

Only project context and its documentation validator exist at initialisation.
Runtime code, provider adapters, distributions, deployments and scientific
benchmarks are planned. The [requirements](requirements.md), [roadmap](roadmap.md)
and [tracks](tracks.md) define their acceptance evidence.
