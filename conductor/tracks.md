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
| [ ] | [Optional Power Platform delivery](./tracks/power_platform_20261108/index.md) | new | RQ-08, RQ-03 |
| [!] | [R and Julia bindings](./tracks/polyglot_bindings_20261108/index.md) | blocked | RQ-09, RQ-02 |
| [~] | [Observed events, Petri nets and BPMN adapters](./tracks/process_models_20261108/index.md) | in_progress | RQ-10, RQ-01, RQ-03 |
| [x] | [Uncertainty and decision-library integration](./tracks/decision_integrations_20261108/index.md) | completed | RQ-11, RQ-02, RQ-03 |
| [!] | [Release assurance and conditional consolidation](./tracks/release_consolidation_20261108/index.md) | blocked | RQ-12, RQ-04 |
| [~] | [Frontier research and comparative benchmarks](./tracks/frontier_benchmarks_20261108/index.md) | in_progress | RQ-12, RQ-06, RQ-10, RQ-11 |
| [x] | [Regulatory public-finance and health-system valuation handoff for tobac](./tracks/tobac_regulatory_fiscal_valuation_20261110/index.md) | completed | RQ-01, RQ-02, RQ-07, RQ-11 |
| [x] | [Serde and canonicalization equivalence qualification](./tracks/serde_canonicalization_qualification_20261118/index.md) | completed | RQ-01, RQ-02, RQ-03 |

## Next executable work

The [parallel ownership map](parallel-ownership.md) records Dylan's seven bounded
roadmap lanes and the sole integration/release owner. Lane assignments do not
change the lifecycle states above. Workers update their own tracks and request
matching registry/shared-file changes through the integrator. Publication remains
disabled and Power Platform is deferred.

The setup track is complete and archived in place. The core-contract/reference track is completed and
archived in place after PR #9 integration; its
[acceptance evidence](tracks/core_contracts_20261108/verification.md) and
[archive entry](archive/README.md) retain the exact qualified scope.
The Rust kernel is archived in place after
[bounded acceptance and independent review](tracks/rust_kernel_20261108/verification.md),
including declared calendar-day interval splitting and the minimal dependency
boundary.

A bounded exact Rust/CLI kernel, Python binding and five synthetic consumers have
[runtime evidence](../docs/runtime-verification.md). The
[capacity increment](../docs/genomics-capacity-verification.md) adds five synthetic
genomics comparisons and explicit 0.2 semantics while retaining 0.1 compatibility.
The Python/two-consumer track is completed and archived in place after
[installed workforce and manual-extraction qualification](../docs/python-provider-verification.md)
and [review with fixes](tracks/python_two_consumers_20261108/review.md).
Its selected provider scope retains exact source identities, independent reference
cases and historical entry points. Across the 15 registered tracks (4 archived, 7
`in_progress`, 2 `blocked`, 2 `new`), all seven standalone roadmap lanes
(`bindings`, `decisions`, `mchs`, `newborn`, `observed`, `reporting`, `static`) are
now integrated on `main` alongside X2 PNML/BPMN adapters (`adapters/process_models/`),
bounded D2/D3 preparation contracts (`adapters/decision_provider_d2/`), and the new
`serde_canonicalization_qualification_20261118` specification track. On `main`,
the process-model track incorporates X1 independent contracts
([`adapters/observed_events/`](../adapters/observed_events/README.md)) and bounded
X2 PNML/BPMN adapters ([`adapters/process_models/`](../adapters/process_models/README.md)),
while X1.2 raw XES/OCEL decoding (`edithatogo/mailweft#4`) and X3 Kairos integration
remain open. Likewise, `polyglot_bindings_20261108` (`[!]` `blocked`) awaits C ABI/Julia
B3 and installed R/C host qualification, `release_consolidation_20261108` (`[!]` `blocked`)
retains upstream advisory (`RUSTSEC-2026-0543`) and offline-security gates, and D2/D3
installed provider execution (`D2.1`–`D3.3`) remains open. Next work addresses their
acceptance criteria, broader provider and quantity/correction semantics, and release
prerequisites. The first release follows contracts → Rust kernel → installed Python
and two real provider consumers → release assurance. Power Platform, R/Julia, process
models and decision integrations are independently qualified optional branches.

The [release handoff](../docs/release-handoff-2026-11-15.md) consumes all four
incorporated archives and the existing provider qualification, and
[post-merge `main` qualification](../docs/release-qualification-2026-11-19.md)
records the `0658d94` matrix, exact-artifact provider check and signed
trusted-main provenance. Release work completes distribution notices and verifies
the exact candidate artifacts. Publication remains disabled pending
channel/account choices; final qualification also retains the separate centrally
managed offline-security execution gate (`43769725442` auto-cancelled after
24h queue timeout with no runner).

## Synchronisation

Keep task markers, each track index, metadata and this table consistent. Put only local
track IDs in `dependencies`; record source/provider readiness in `external_dependencies`.
Re-check provider versions before implementing a consumer. Retain the original design
source in MCHS as provenance; this registry is the current framework delivery owner.
