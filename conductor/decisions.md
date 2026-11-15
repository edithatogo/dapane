# Architecture decisions

Recorded 8 November 2026 from the user's requested framework direction and the
[MCHS precursor design](https://github.com/edithatogo/mchs/blob/d7935044821d072a194d80e9cd4f5b9174fa9652/docs/roadmaps/dapane-framework.md).
Dapane now owns the shared framework plan. The precursor remains historical
context; provider repositories retain their domain responsibilities.

**Accepted design direction** means that implementation should follow the decision.
It does not mean that code, compatibility or deployment has been demonstrated.
Change a decision with a dated rationale and affected requirements; retain the
history rather than silently rewriting the architectural basis.

## ADR-001 — Independent Rust core

Status: accepted design direction. Requirements: RQ-01, RQ-04, RQ-12.

Dapane owns a small Rust valuation/allocation core and its thin interfaces.
Workforce, genomics and MCHS remain specialist products. Static costing must work
without a simulator, ontology reasoner, game solver, table engine or cloud tenant.
Prove the boundary with workforce and genomics before expanding capabilities.

Consequence: source and domain-rule ownership stay outside the generic kernel;
existing APIs need explicit migration adapters rather than wholesale rewrites.

## ADR-002 — Resource use and activity remain different

Status: accepted design direction. Requirements: RQ-01, RQ-03, RQ-05.

Physical ResourceUse and classified ActivityMeasure are separate inputs. A typed
quotation can apply directly to its corresponding resource or activity kind.
Funding, tariffs, cash payments, accounting expense and economic cost retain
their valuation basis. Activity-to-resource conversion requires an explicit recipe.

Consequence: MCHS can participate without implying that weighted activity measures
physical consumption. Pricing applications can compare views without conflating them.

## ADR-003 — Exact values and conserving ledgers

Status: accepted design direction. Requirements: RQ-02, RQ-03.

Support decimal and rational inputs with explicit precision, conversion and
rounding policies. Allocations plus residuals reconcile to source pools. Count
resource use once within each valuation view; preserve separate views over the
same inputs and disclose loaded-rate components.

Consequence: wrappers and IO adapters must preserve numeric meaning. Faster
backends need equivalence evidence before promotion. Numerical crate selection
and bounds are still decisions for implementation.

## ADR-004 — Explicit optional plugins and immutable releases

Status: accepted design direction. Requirements: RQ-01, RQ-04, RQ-05, RQ-07.

Start with typed packages and versioned file adapters registered explicitly.
Plugins describe capabilities, compatible contracts, source releases and evidence.
Do not begin with an unstable native dynamic ABI or unrestricted formula language.
Rate and data corrections create new traceable releases.

Consequence: clean installation and replay need versioned artifacts. A data pack
does not grant permission to execute code or establish source/scientific validity.

## ADR-005 — Python first, independent R and Julia routes

Status: accepted design direction. Requirements: RQ-04, RQ-09.

Use PyO3/maturin for Python. R may call Rust directly through extendr. Julia uses
a versioned C ABI and qualified native artifacts. R need not wait for the C ABI;
neither later binding depends on Python. All wrappers share numerical rules.

Consequence: each interface needs ownership, lifetime, error and exact-value tests
using installed packages. Wrapper/toolchain versions are not selected by this ADR.

## ADR-006 — Standard Power Platform baseline, optional richer delivery

Status: accepted design direction. Requirements: RQ-08.

Start with standard SharePoint/Canvas exchange and manual CLI execution. Add an
authorised worker, premium service or PCF/WASM route independently when useful.
Keep the calculation in the shared Rust implementation.

Consequence: an otherwise standard connector does not establish all user, flow or
environment entitlements. Worker operation and WASM feasibility need separate
evidence. No tenant, service or deployment is established here.

## ADR-007 — Reuse ontology and reporting ownership

Status: accepted design direction. Requirements: RQ-07, RQ-11.

UOGTO owns costing semantics and profile reconciliation; standards_check owns
instrument provenance. Dapane consumes pinned versions and emits evidence-linked
reporting. It keeps reporting, appraisal, verification and empirical validation
separate and uses explicit payoff transformations at decision-model boundaries.

Consequence: the costing engine does not fork the source catalogue or require a
reasoner for ordinary execution. A mapping's scope and review status stay visible.

## ADR-008 — Process models produce usage; valuation consumes it

Status: accepted design direction. Requirements: RQ-06, RQ-10, RQ-11.

Use object-aware event contracts and optional process adapters. Qualify a bounded
Petri-net/PNML profile and a named BPMN subset. Kairos stays independent of Dapane.
Rate changes revalue unchanged usage; feedback affecting execution is coordinated
explicitly by the application.

Consequence: a parser or diagram cannot silently supply timing, resource or
economic semantics. Supported subsets, provider revisions and licences are recorded.

## ADR-009 — Qualification precedes widening claims

Status: accepted design direction. Requirements: RQ-12.

Begin with independent reference cases and deterministic CPU execution. Measure
installed-artifact behaviour, modelling effort and comparative results before
claiming compatibility, acceleration or novelty. Distinguish synthetic evidence
from external validation and keep optional research features maturity-labelled.

Consequence: no fixed calendar promise or completed roadmap marker can substitute
for capability evidence. Archive candidates require a working successor and review
of unique research and source assets.

## ADR-010 — Implement a bounded exact profile before provider migration

Status: implemented direction, 8 November 2026. Requirements: RQ-01, RQ-02,
RQ-03, RQ-04, RQ-06, RQ-10.

The first candidate uses `num-rational`/`num-bigint` for nonnegative exact values,
strict decimal strings/rational pairs for transport, explicit point service dates
and selected quote IDs. It rounds each source line half-even, then allocates the
rounded pool by largest remainder with object-ID tie breaking. Source, policy,
method and engine identities are retained in deterministic request/report bundles.
Numeric and record bounds are part of [contract 0.1](../docs/contract-v0.1.md).

Event, process and object context coexist. Object associations never assign
money; direct attribution or an explicit allocation creates conserving views.
Equivalent inherited and explicit process/activity context must be treated as
the same context when pricing disjoint components of one underlying use.

The core and CLI are default workspace members. Python is a separate thin PyO3
crate with interpreter-specific wheels; Arrow/Parquet and every simulator remain
optional. The qualified first inputs are independent synthetic cases, not a
claim that legacy packages have been migrated. The
[provider review](../docs/provider-boundaries.md) found Kairos's public usage
export still pending; Dapane remains independently usable.

Consequence: reject unknown methods/fields and unsupported intervals, retractions,
FX, tax, escalation, discounting or capital annualization. Source validation flags
remain caller declarations. Component inclusion tags prevent duplicate charges
but do not invent a monetary decomposition of loaded rates. Full provider, process,
reporting and release tracks stay open. [Compatibility](../docs/compatibility.md)
defines versioning, namespacing and rollback for the first profile.

## ADR-011 — Version partial capacity separately from full-pool recovery

Status: implemented bounded direction, 14 November 2026. Requirements: RQ-01,
RQ-02, RQ-03, RQ-04. Existing core-contract and Python-consumer tracks own it.

Retain 0.1 normalised weighting and zero residual. Add an explicit 0.2 capacity
array with an independently supplied known/unknown instrument-hour denominator,
known/unknown use records and incomplete coverage. Assigned shares plus a named
unallocated bucket conserve each rounded pool; the bucket is already included
in unattributed ledger totals. Its rounding tie priority precedes object IDs.
Unknown shares are nullable and never represented as observed zero. Reject
unsupported units, coverage modes, fields and silent version downgrades.

Device useful life, maintenance contract duration and cost recurrence remain
separate preparation assumptions in the synthetic scenario manifest. The core
consumes the resulting explicit quotes; no new economic annualisation method or
utilisation estimator is claimed. Source qualification, full observation coverage
and real provider integration remain open. CareOps consumes qualified versioned
bundles and does not duplicate valuation. Its files are outside this work.

Consequence: [contract 0.2](../docs/contract-v0.2.md) and the
[independent genomics cases](../fixtures/genomics-capacity/README.md) define the
small delivered scope. No dependency, runtime package version, provider owner or
release status changes. Typed Rust struct literals require the new empty vector;
0.1 JSON/CLI/Python inputs and the five original fixture digests remain compatible.

## ADR-012 — Version immutable candidate evidence separately from valuation

Status: implemented bounded direction, **15 November 2026**. Requirements:
RQ-01, RQ-02, RQ-03. The core-contracts track owns definition and reference
acceptance; its [verification record](tracks/core_contracts_20261108/verification.md)
identifies the reviewed revision, executed checks and qualification limits.

Run-bundle profile 0.1 wraps unchanged request/report profiles 0.1 and 0.2.
It binds full snapshots, predecessor digests, a declared source revision,
observation windows, rate releases, exclusions and alternative asset treatments.
Corrections replace the full snapshot; withdrawal creates a nonfinancial
tombstone. Historical selection verifies the complete chain against a separately
retained head checkpoint and never sums versions.

Retain the complete quote snapshot when source ID, source version and quote ID
are unchanged. Each source release retains one publication date and consistent
non-null declared content digests across all seen revisions. Different quote
subsets, quote ordering and retrieval dates are allowed. Quote correction requires
a new source version; intermediate omission does not erase identity history.
Provider owners retain source truth, eligibility, rights and qualification of
actual corrected releases.

Repository conformance tooling checks structure, dates, lineage and declared
economic-view consistency, then replays every full valuation snapshot through
an installed Rust wheel. All financial arithmetic remains in Rust. The interval
reference uses explicitly prepared dated segments; capital references use
alternative prepared quotations with declared assumptions.

Consequence: [bundle 0.1](../docs/run-bundle-v0.1.md) has its own schema and
digest namespace. Retain numerical method identities, original expectations
and prior schema implementations. Candidate integrity/replay does not establish
signed provenance, binary-to-source attestation, economic validity or production
publication. Interval integration is separately versioned in ADR-013; new capital methods, real provider
adapters and release qualification remain with their existing owners. The
registry and verification evidence determine completion and archival status.

## ADR-013 — Version declared calendar-day interval exposure separately

Status: implemented bounded direction, **15 November 2026**. Requirements:
RQ-01, RQ-02, RQ-03, RQ-12. The Rust-kernel track owns this increment and its
[qualification and review](tracks/rust_kernel_20261108/verification.md).

Retain point/capacity profiles 0.1/0.2 and their historical digests. Add interval
schema `0.1` and method `dapane-intervals-v0.1.0` as an explicit Rust/CLI envelope.
The caller supplies the total exact quantity, half-open calendar dates, pinned
quote IDs and `uniform_calendar_day` exposure. Each segment receives total quantity
times its calendar-day fraction; no working calendar, clock or utilisation is inferred.

Validate original parent-use identity, source/context and disjoint components before
expansion. Selected quotations must exactly cover the interval and preserve the
component set. Use domain-separated parent/date tuple hashes for generated identities,
reject collisions, and expand parent allocation references to their children. Bound
encoded output-request bytes before copying large source/context records.

The scalar engine remains the single valuation/allocation implementation. It rounds
each generated line half-even before summing; artificial extra rate boundaries can
therefore change rounded totals. Preserve original request/interval snapshots, exact
segments, the expanded scalar request and separate envelope digests for audit/replay.

Consequence: [the interval contract](../docs/interval-contract-v0.1.md) is an additive
native/CLI capability; the Python wrapper's public API is unchanged. Richer exposure,
timestamp/timezone semantics and economic methods need separate scoped increments.
The locked dependency boundary is qualified on Rust 1.99.1; project-licence selection,
distribution notices and registry publication retain their release/consolidation owner.

## ADR-014 — Apache-2.0 for Dapane project code

Status: accepted and applied, **15 November 2026**. Requirements: RQ-12, RQ-04.
The project owner explicitly selected Apache 2.0 for this release integration.
The canonical Apache-2.0 text is retained in the root LICENSE, with project
attribution in NOTICE. All three Rust crates inherit the workspace SPDX licence;
citation metadata declares the same project licence. Nested crate sources,
Python wheel/source distributions and candidate CLI bundles include the licence,
notice and full third-party notice bundle. Python's optional aggregate distribution
licence expression is omitted under the documented
[metadata boundary](../docs/release-controls.md); it is not inferred from Cargo's
project licence or from a conservative dependency notice inventory.

This decision applies to Dapane project material. Third-party dependencies and
separately obtained provider data retain their own terms. No external provider
assets are added by this decision. Dependency licence checks include unpublished
workspace packages; the former private-package exemption is removed.

Consequence: project-licence selection is resolved. The
[provider subset](../docs/python-provider-verification.md) is qualified with its
own bounded evidence. Registry/channel choices, exact-source release qualification,
broader migration and external asset inclusion retain their existing requirements.
Package publication stays disabled pending the applicable evidence.

## Decisions intentionally left to their implementation tracks

| Decision | Owner and constraint |
| --- | --- |
| Wider schemas and compatibility windows | Request profiles 0.1/0.2, bundle 0.1 and interval 0.1 define the current boundary. Further profiles need explicit versioning, reference cases and migration in a new scoped contract increment coordinated with the owning kernel/provider track. |
| Wider numeric methods and platform matrix | First Rust/CPython versions and precision bounds are recorded in the technology stack and runtime evidence; other methods/platforms remain unqualified. |
| Package registry identities | Release/consolidation track; Apache-2.0 is selected in ADR-014, while registry ownership and publication remain unqualified. |
| First real newborn programme and data access | Newborn-screening track; separate synthetic arithmetic from sourced programme validity. |
| Power Platform tenant and optional worker/API/WASM route | Power Platform track; retain the standard file baseline and record actual entitlements and host evidence. |
| Exact process subset, adapter revisions and advanced backends | Process/frontier tracks; use bounded semantic and comparative tests. |

Routine choices within an authorised track should be resolved and recorded by the
implementer. This decision log creates no additional approval committee. Changes
that alter the agreed product scope or economic meaning must be made explicit in
the requirements, design and affected consumer plans.
