# Track registry

This is the authoritative local track list. Dapane coordinates the shared framework;
provider repositories retain their domain rules, source catalogues and runtime responsibilities.
See the [roadmap](roadmap.md) for delivery gates and the [workflow](workflow.md) for execution.

## Status vocabulary

Markers: `[ ]` pending/new, `[~]` in progress, `[x]` completed, `[!]` blocked, `[-]` cancelled or archived.
`status` in each metadata file uses `new`, `in_progress`, `blocked`, `completed`, `cancelled` or `archived`.
A completed planning task does not change a runtime capability from planned to qualified.

| Marker | Track | Status | Requirements |
| --- | --- | --- | --- |
| [-] | [Conductor setup and source-of-truth handoff](./tracks/conductor_setup_20261108/index.md) | archived | RQ-01, RQ-12 |
| [-] | [Core contracts and independent reference cases](./tracks/core_contracts_20261108/index.md) | archived | RQ-01, RQ-02, RQ-03 |
| [-] | [Minimal Rust valuation kernel and CLI](./tracks/rust_kernel_20261108/index.md) | archived | RQ-01, RQ-02, RQ-03, RQ-12 |
| [-] | [Python delivery with workforce and genomics consumers](./tracks/python_two_consumers_20261108/index.md) | archived | RQ-04, RQ-02, RQ-03 |
| [x] | [MCHS activity and quotation-source adapters](./tracks/mchs_source_adapters_20261108/index.md) | completed | RQ-05, RQ-01, RQ-03 |
| [x] | [Reporting profiles and evidence exports](./tracks/reporting_profiles_20261108/index.md) | completed | RQ-07, RQ-01 |
| [x] | [Newborn screening pathway composition](./tracks/newborn_screening_20261108/index.md) | completed | RQ-06, RQ-03, RQ-07 |
| [-] | [Optional Power Platform delivery](./tracks/power_platform_20261108/index.md) | archived | RQ-08, RQ-03 |
| [!] | [R and Julia bindings](./tracks/polyglot_bindings_20261108/index.md) | blocked | RQ-09, RQ-02 |
| [-] | [Observed events, Petri nets and BPMN adapters](./tracks/process_models_20261108/index.md) | archived | RQ-10, RQ-01, RQ-03 |
| [x] | [Uncertainty and decision-library integration](./tracks/decision_integrations_20261108/index.md) | completed | RQ-11, RQ-02, RQ-03 |
| [!] | [Release assurance and conditional consolidation](./tracks/release_consolidation_20261108/index.md) | blocked | RQ-12, RQ-04 |
| [~] | [Frontier research and comparative benchmarks](./tracks/frontier_benchmarks_20261108/index.md) | in_progress | RQ-12, RQ-06, RQ-10, RQ-11 |
| [x] | [Regulatory public-finance and health-system valuation handoff for tobac](./tracks/tobac_regulatory_fiscal_valuation_20261110/index.md) | completed | RQ-01, RQ-02, RQ-07, RQ-11 |
| [x] | [Serde and canonicalization equivalence qualification](./tracks/serde_canonicalization_qualification_20261118/index.md) | completed | RQ-01, RQ-02, RQ-03 |

## Next executable work

Twelve of the fifteen tracks have met their recorded scope. Six are archived and six are completed. One is in progress and two are blocked. The [ownership map](parallel-ownership.md) records the integrator and lane assignments.

The [installed core and two-provider qualification](../docs/python-provider-verification.md), [fiscal handoff](tracks/tobac_regulatory_fiscal_valuation_20261110/plan.md), [decision-provider runs](tracks/decision_integrations_20261108/plan.md) and [canonicalization qualification](tracks/serde_canonicalization_qualification_20261118/plan.md) record the delivered numerical and integration scopes. The latest fiscal comparisons cover New Zealand and Australian synthetic policy cases. The decision runs include an installed adoption model.

| Open track | Implemented | What remains |
| --- | --- | --- |
| [Frontier benchmarks](tracks/frontier_benchmarks_20261108/plan.md) | Independent static cases, six native pathway comparisons and installed decision-provider experiments | Assess transportability with authorised external or multisite data. Publication requires the appropriate evidence and authority. |
| [R and Julia](tracks/polyglot_bindings_20261108/plan.md) | Installed R and Julia candidates, C ABI review and instrumented native parity | Select and qualify the intended distribution surfaces. |
| [Release assurance](tracks/release_consolidation_20261108/plan.md) | Repeatable candidate builds, installed consumers, provenance and dependency checks | Confirm publication channel and account, and obtain a completed central offline-security run for the candidate source. |

The [first release handoff](../docs/release-handoff-2026-11-15.md) and [trusted-main qualification](../docs/release-qualification-2026-11-19.md) retain the source and artifact identities for earlier candidates.

The [archived Power Platform baseline](tracks/power_platform_20261108/review.md) covers the synthetic manual exchange and versioned SharePoint setup contract. The owner deferred the live pilot.

## Synchronisation

Keep task markers, each track index, metadata and this table consistent. Put only local
track IDs in `dependencies`; record source/provider readiness in `external_dependencies`.
Re-check provider versions before implementing a consumer. Retain the original design
source in MCHS as provenance; this registry is the current framework delivery owner.
