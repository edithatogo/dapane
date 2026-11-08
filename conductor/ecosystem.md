# Ecosystem ownership and migration

Status: framework design and integration plan, 8 November 2026. Dapane is the
canonical home of the shared framework's requirements, design, roadmap and tracks.
This setup does not implement or release a costing engine or any domain adapter.

## Source of truth

The [MCHS architecture at the reviewed commit](https://github.com/edithatogo/mchs/blob/d7935044821d072a194d80e9cd4f5b9174fa9652/docs/roadmaps/dapane-framework.md)
is the originating proposal. Its cross-repository coordination role now transfers
to this repository. MCHS continues to own its calculator and adapter work. Future
shared-framework decisions belong in [Dapane's design](./design.md),
[decision record](./decisions.md) and [track registry](./tracks.md); sibling
repositories should link those records rather than maintain competing copies.

Ownership describes the intended boundary. It does not assert that a provider
has already delivered the interface or passed Dapane's consumer qualification.

| Owner | Retained responsibility | Dapane boundary and local owner |
| --- | --- | --- |
| Dapane | Generic quantities, quotations, valuation policies, allocation, ledgers, reproducibility and thin language surfaces | [Core contracts](./tracks/core_contracts_20261108/index.md), [Rust kernel](./tracks/rust_kernel_20261108/index.md) |
| [microcosting_healthworkforce](https://github.com/edithatogo/microcosting_healthworkforce) | Employment conditions, classifications, eligibility, dated source rules and labour quotations | Emit typed quantities/quotes; retain rule interpretation and repair the generic import namespace in the provider. [Python and two consumers](./tracks/python_two_consumers_20261108/index.md) |
| [microcosting_genomics](https://github.com/edithatogo/microcosting_genomics) | Assay recipes, laboratory workflows, batching, repeats and historical workbook interpretation | Emit resource-use recipes and consume dated workforce quotes; separate demonstration analyses from qualified computations. [Python and two consumers](./tracks/python_two_consumers_20261108/index.md) |
| [mchs](https://github.com/edithatogo/mchs) | Classifications, weighted activity and edition-specific funding/tariff equations | Preserve activity units and editions; an activity quotation need not imply resource consumption. [MCHS and source adapters](./tracks/mchs_source_adapters_20261108/index.md) |
| [reimbursement-atlas](https://github.com/edithatogo/reimbursement-atlas) | Schedule discovery, parsers, editions, source licensing and cross-jurisdiction evidence | Consume versioned source packs; avoid a second schedule registry or parser collection. [MCHS and source adapters](./tracks/mchs_source_adapters_20261108/index.md) |
| [CareOps](https://github.com/edithatogo/careops), `modules/careops-costing` | Assumption capture, operational workflows, review, presentation and reporting | Consume versioned input/result bundles; Power Fx and report expressions do not duplicate valuation maths. [Power Platform](./tracks/power_platform_20261108/index.md) |
| [Kairos](https://github.com/edithatogo/kairos) | Neutral simulation execution, clocks, resource use and random-stream identity | Supply usage events when its provider contract is qualified; Kairos has no dependency on Dapane. [Process models](./tracks/process_models_20261108/index.md) |
| [CareOps-Sim](https://github.com/edithatogo/careops-sim) | Healthcare process and operational models | Attach healthcare resource recipes to neutral execution; costing remains a separate consumer. [Process models](./tracks/process_models_20261108/index.md) |
| [Innovate](https://github.com/edithatogo/innovate) | Adoption, utilisation, substitution and competition trajectories | Supply scenario trajectories; the application coordinates feedback between behaviour, capacity and valuation. [Decision integrations](./tracks/decision_integrations_20261108/index.md) |
| [Voiage](https://github.com/edithatogo/voiage) | Qualified VOI, value-of-perspective and value-of-heterogeneity methods | Consume correctly paired strategy/draw/replication/perspective/subgroup outcomes; Dapane does not add a local VOI estimator. [Decision integrations](./tracks/decision_integrations_20261108/index.md) |
| [Paignia](https://github.com/edithatogo/paignia) | Supported games, strategic interaction and solution methods | Consume explicitly transformed domain payoffs; costs, funding and monetary transfers are not automatically utilities. [Decision integrations](./tracks/decision_integrations_20261108/index.md) |
| [UOGTO](https://github.com/edithatogo/UOGTO) | Economic/semantic definitions, reporting profiles and explicit HTA/game bridges | Use a pinned semantic profile without a mandatory runtime reasoner. [Reporting profiles](./tracks/reporting_profiles_20261108/index.md) |
| [standards_check](https://github.com/edithatogo/standards_check) | Original reporting-instrument provenance, versions and source catalogue | Retain original item identifiers and source rights; semantic reconciliation belongs in UOGTO. [Reporting profiles](./tracks/reporting_profiles_20261108/index.md) |
| [rust4pm](https://github.com/edithatogo/rust4pm) | Process-mining and interoperability work | Qualify a specific provider revision and bounded XES/OCEL/PNML capability; do not infer general BPMN execution support. [Process models](./tracks/process_models_20261108/index.md) |

The newborn-screening package is the first new domain planned here. It composes
workforce quotations, laboratory recipes and a versioned programme pathway. Its
implementation location can be selected during the
[newborn-screening track](./tracks/newborn_screening_20261108/index.md); no package
name or separate repository is reserved by this setup.

## Reviewed cross-repository snapshots

All three PRs below were **open and unmerged** when checked on 8 November 2026.
Their branch contents are usable review evidence, not proof of a released provider
capability. Recheck merge/release state at the relevant integration milestone.

| Record | Immutable reviewed head | What it establishes |
| --- | --- | --- |
| [MCHS PR 411](https://github.com/edithatogo/mchs/pull/411) | [`d7935044821d072a194d80e9cd4f5b9174fa9652`](https://github.com/edithatogo/mchs/commit/d7935044821d072a194d80e9cd4f5b9174fa9652) | Originating architecture and coordination plan; no Dapane runtime |
| [UOGTO PR 128](https://github.com/edithatogo/UOGTO/pull/128) | [`7e9075b8fd77543fc8853fab20319415cb86597d`](https://github.com/edithatogo/UOGTO/commit/7e9075b8fd77543fc8853fab20319415cb86597d) | Applied costing ontology, reporting reconciliation and semantic fixtures |
| [standards_check PR 65](https://github.com/edithatogo/standards_check/pull/65) | [`155f4f645ca673328548cfdd7901234c1fa82a1a`](https://github.com/edithatogo/standards_check/commit/155f4f645ca673328548cfdd7901234c1fa82a1a) | Source catalogue and its validation/CI integration |

The UOGTO reporting snapshot deliberately pins the earlier catalogue commit
[`d1f1137edfa5375e0225ca2216903ce5583a44f0`](https://github.com/edithatogo/standards_check/tree/d1f1137edfa5375e0225ca2216903ce5583a44f0/reconciliations/costing).
The later standards_check head includes workflow integration. Preserve the exact
input commit and content digests in the
[UOGTO import manifest](https://github.com/edithatogo/UOGTO/blob/7e9075b8fd77543fc8853fab20319415cb86597d/validation/costing-reporting-import.json)
instead of silently rewriting provenance to the newest branch head.

Other provider tracks mentioned by the originating plan include Kairos Track 114,
Voiage's simulation-outcome/perspective/heterogeneity work and Paignia T17. These
are discovery pointers. Inspect their current specifications and delivered
contracts before scheduling a dependent implementation; a roadmap entry is not
an installed interface.

## Dependency direction and delivery rules

- Domain adapters depend on Dapane contracts; the minimal core does not import
  workforce, genomics, MCHS, simulators, table engines or a cloud tenant.
- Quote providers retain collection, interpretation and licence ownership.
  Dapane validates their declared contract and applicability rather than treating
  all quotations as equivalent evidence.
- Python, R, Julia, CLI and optional WASM surfaces share the Rust implementation.
  R can use extendr directly; Julia's C ABI is not a prerequisite for R.
- Optional modules have explicit installation/features and capability metadata.
  Missing optional components produce a bounded unsupported-capability result.
  They do not prevent a basic static valuation.
- Exact tested versions, schemas and consumer fixtures define compatibility.
  Do not move sibling pins together merely to make their version strings match.
- Large tabular IO belongs behind optional Arrow/Parquet adapters. Preserve
  decimal/rational semantics, identities and provenance across encodings.
- Standard SharePoint/file exchange is the initial Power Platform route.
  Worker, premium API and local PCF/WASM routes have independent qualification;
  none is required to release the core or newborn pathway package.

See [design](./design.md), [technology choices](./tech-stack.md) and the
[roadmap](./roadmap.md) for the proposed implementation boundaries.

## Migration sequence and rollback

1. Freeze independently checked input/output cases in the domain owner's
   repository. Record official, observed, assumed and synthetic source status.
   Identify unique methods, data and public APIs before extracting mechanics.
2. Define a small versioned adapter against Dapane's contracts. Keep the previous
   provider release and historical examples reproducible during comparison.
3. Run both implementations against independent expected results. A historical
   output is a regression comparator, not automatically a scientific oracle.
   Record intentional corrections separately from mechanical extraction.
4. Qualify a clean installed consumer and publish only the supported capability.
   Keep adapter and provider version compatibility explicit; do not depend on
   an unpublished local checkout for a release claim.
5. Change the domain package's selected implementation after parity and source
   checks. Retain its public API through a compatibility adapter where practical.
6. Preserve input bundles, source releases and prior executable artifacts. A
   rollback selects the prior adapter/provider release; it does not silently
   reinterpret an old ledger under a newer schema or rate pack. Schema migrations
   retain original inputs and distinguish migrated from original run identities.

The first proof is workforce plus one genomic workflow. MCHS's activity/tariff
adapter and newborn screening follow their own acceptance criteria. Simulators,
R/Julia and Power Platform can advance independently once their required core
contracts exist. Their completion is not a universal release gate.

## Consolidation and archive candidates

These recommendations carry forward the
[bounded originating inventory](https://github.com/edithatogo/mchs/blob/d7935044821d072a194d80e9cd4f5b9174fa9652/docs/roadmaps/dapane-framework.md#consolidation-and-archive-decisions).
No archive action is performed or scheduled automatically by this setup. The
[release and consolidation track](./tracks/release_consolidation_20261108/index.md)
owns successor checks and any separately authorised repository action.

| Repository or group | Recommendation | Required check before change |
| --- | --- | --- |
| `mchs`, `microcosting_healthworkforce`, `microcosting_genomics` | Retain specialist products and domain APIs | Extract shared mechanics while preserving unique rules, sources and historical reproducibility |
| `careops-costing`, `careops-costing-public` | The originating review found these already archived | Verify current state; continue with the CareOps module rather than restarting migration |
| `hwcc` | Conditional archive candidate | Preserve unique rules, workbooks and non-public evidence; establish a functioning maintained successor |
| `cobra-costing` | Conditional candidate; originating review inspected a minimal root | Review all branches/history and research intent before deciding that unique content is absent |
| `tutorial_microcosting_genomics` | Preserve scholarly identity; consolidate duplicate execution where useful | Preserve citations, manuscript assets, history and reproducible published results |
| `checklist_microcosting` | Preserve methods research; move reusable software only where appropriate | Retain protocol/synthetic status and unique research; link the standards_check/UOGTO successors |
| `voi_sequencing_costs` | Keep as a research consumer | Replace duplication through qualified adapters while preserving study artifacts |
| `standards_check`, `UOGTO`, `reimbursement-atlas`, `rust4pm` | Keep their separate ownership | Avoid duplicate ontologies, source registries, schedule parsers and process infrastructure |

## Source and deployment boundaries

Public repository availability does not establish rights to redistribute every
embedded source. Preserve publisher, data, software and quotation permissions
separately. Neither Dapane nor a wrapper changes the licence of an upstream
instrument, workbook or dataset. Runtime licence selection is a release decision,
not inferred from an adjacent repository.

Power Platform design must be checked against the target environment and current
[app licence designation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/license-designation),
[Managed Environment licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing)
and [PCF documentation](https://learn.microsoft.com/en-us/power-apps/developer/component-framework/overview).
Standard connector classification alone does not establish each user's rights;
worker/file transport does not remove obligations for services behind it. These
references inform the design and do not attest to a deployed tenant.

For process adapters, qualify the selected
[process_mining capabilities and version](https://docs.rs/process_mining/) and
[BPMN specification subset](https://www.omg.org/spec/BPMN/2.0.2/).
[PM4Py](https://github.com/process-intelligence-solutions/pm4py) is an optional
interoperability/comparison candidate with its own licence terms. Process
diagrams and reporting-checklist Petri nets do not establish executable clinical
or resource semantics.
