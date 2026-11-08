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

## Decisions intentionally left to their implementation tracks

| Decision | Owner and constraint |
| --- | --- |
| Public schemas, names and compatibility windows | Core-contracts track; preserve the semantic boundaries above and qualify consumers. |
| Numeric crates, precision bounds, Rust MSRV and language/platform matrix | Core/kernel and release tracks; select from tested providers, not inferred compatibility. |
| Project licence and package registry identities | Release/consolidation track; the empty repository supplied no licence or published package identity. |
| First real newborn programme and data access | Newborn-screening track; separate synthetic arithmetic from sourced programme validity. |
| Power Platform tenant and optional worker/API/WASM route | Power Platform track; retain the standard file baseline and record actual entitlements and host evidence. |
| Exact process subset, adapter revisions and advanced backends | Process/frontier tracks; use bounded semantic and comparative tests. |

Routine choices within an authorised track should be resolved and recorded by the
implementer. This decision log creates no additional approval committee. Changes
that alter the agreed product scope or economic meaning must be made explicit in
the requirements, design and affected consumer plans.
