# Requirements

Status: product acceptance baseline, 8 November 2026. The first runtime implements
a bounded subset recorded in the [0.1 contract](../docs/contract-v0.1.md) and
[verification evidence](../docs/runtime-verification.md). The requirements below
remain broader than that candidate; synthetic numerical and package checks do
not complete provider, domain, deployment or research qualification.

The [product](product.md) defines scope; the [design](design.md) explains the
implementation boundary; [decisions](decisions.md) records the chosen direction.
The [track registry](tracks.md) owns execution status. Requirement identifiers
remain stable when descriptions or implementation plans change.

## RQ-01 — Domain-neutral types and contracts

Owners: [core contracts](tracks/core_contracts_20261108/index.md) and
[Rust kernel](tracks/rust_kernel_20261108/index.md).

Represent physical resource use, classified/weighted activity, unit quotations,
rate releases, valuation policies, component ledgers and reproducible run bundles
as distinct versioned contracts. Domain concepts belong in optional packages.

Acceptance:

- One static resource-cost calculation and one direct activity-funding calculation
  use the same core without forcing activity to become physical resource use.
- The minimal core runs without a domain plugin, table engine, simulator,
  ontology reasoner, game solver, network service or Power Platform tenant.
- Public serialization versions, units, identities and error categories are
  explicit; unsupported versions fail clearly and historical runs remain
  reproducible through versioned implementations or documented migrations.

## RQ-02 — Exact numerical, unit and date semantics

Owners: [core contracts](tracks/core_contracts_20261108/index.md) and
[Rust kernel](tracks/rust_kernel_20261108/index.md).

Preserve decimal source values and rational quantities. Define precision, scale,
overflow, conversion and rounding before crossing JSON, Arrow or language
boundaries. Separate a quotation's effective interval from publication,
retrieval and knowledge dates. Pricing edition and economic price year differ.

Acceptance:

- Independent fixtures cover nonterminating fractional hours, sub-cent values,
  overflow, incompatible units and rate changes during a usage interval.
- Decimal/rational values round-trip without silent binary-float coercion;
  invalid denominators and unsupported precision produce structured errors.
- Line, pool and aggregate rounding are explicit; rate selection is reproducible
  under a specified knowledge cutoff and never silently chooses a newer release.
- Missing, excluded, unsupported and genuine zero values remain distinguishable.

## RQ-03 — Ledger, allocation and economic distinctions

Owners: [core contracts](tracks/core_contracts_20261108/index.md) and
[Rust kernel](tracks/rust_kernel_20261108/index.md).

Keep economic opportunity cost, accounting expense, acquisition expenditure,
cash flow, tariff/funding valuation and observed payment distinct. A resource can
be valued under several policies, but is counted once within each declared view.
Every shared pool retains its source lines, allocation method and residual.

Acceptance:

- Allocated values plus explicit residuals reconcile exactly to each pool under
  the selected rounding policy; allocation views are not added back to source
  expenditure when producing a programme total.
- Duplicate-use and overlapping-component fixtures detect accidental double
  counting, including a loaded staff rate combined with its included on-costs.
- Alternative asset treatments are not silently added together; transfers across
  perspectives and unused capacity are not automatically reported as social
  resource cost or cash savings.
- Results retain valuation basis, perspective, currency, denominator, observation
  window and component lineage through aggregation.

## RQ-04 — Python delivery and two independent domain consumers

Owner: [Python and two consumers](tracks/python_two_consumers_20261108/index.md).

Deliver thin PyO3/maturin bindings and qualify workforce and genomics as independent
consumers of the same Rust calculation. Domain owners retain employment rules,
assay recipes, historical source interpretation and public compatibility adapters.

Acceptance:

- A dated workforce quotation is used in a genomic workflow without reimplementing
  core arithmetic or duplicating loaded labour or shared batch components.
- Native Rust and clean installed Python wheels reproduce independently calculated
  reference cases, invalid-input behaviour and declared numeric transport.
- The advertised interpreter/platform matrix is exercised, optional imports stay
  isolated and consumer installation does not rely on a source checkout.
- Demonstration PSA/VOI outputs are separated from scientific reference cases;
  needed workforce namespace repairs are coordinated with its repository owner.

## RQ-05 — MCHS and quotation/source adapters

Owner: [MCHS and source adapters](tracks/mchs_source_adapters_20261108/index.md).

Consume MCHS classification-specific activity and funding rules, and reuse
reimbursement-atlas source releases and parsers. Preserve source qualification,
access rights, applicability, classification edition and valuation meaning.

Acceptance:

- Typed activity can use an applicable activity quotation directly; mismatched
  kinds or units require an explicit transformation and cannot imply resource use.
- Parallel resource-cost, tariff/funding and payment views remain distinguishable.
- Replaying a pinned source release reproduces the valuation; corrections create
  traceable releases rather than silently replacing historical inputs.
- Synthetic, observed, official and unverified sources retain their status;
  possession of a file or a licence does not establish methodological validity.

## RQ-06 — Newborn-screening pathway composition

Owner: [newborn screening](tracks/newborn_screening_20261108/index.md).

Compose programme-specific pathways from workforce quotations and laboratory
recipes. Distinguish infant, screening episode, specimen/card, collection attempt,
assay, batch, result, recall, confirmation and follow-up identities. Clinical scope,
branch probabilities and timing belong to versioned programme inputs.

Acceptance:

- The synthetic two-infant example conserves its invented total of 150: collection
  10 each, one batch of 100 allocated 50 each, and confirmation of 30 for one
  infant. Resulting infant views are 60 and 90, not additional source costs.
- Cases cover repeats, inadequate specimens, failed assays, shared transport,
  partially occupied batches and a capacity step without multiplying shared costs.
- Eligible births, participating infants, valid screens, completed pathways and
  diagnoses retain separate denominators; average and incremental analyses name
  their comparator and horizon.
- A real programme pack requires sourced workflow/rates and independent reference
  calculations. Synthetic arithmetic proves neither clinical validity nor benefit.

## RQ-07 — Ontology, reporting and evidence

Owner: [reporting profiles](tracks/reporting_profiles_20261108/index.md).

Use UOGTO for costing semantics and profile reconciliation, and standards_check for
source-instrument ownership. Keep original instruments, versions, item identities,
extraction scope and conditional applicability. Treat protocols and reviews as
evidence artefacts rather than endorsed operational checklists.

Acceptance:

- A version-pinned profile produces a report linked to run evidence and original
  source requirements; the catalogue need not be reasoned over in the hot path.
- Reported, partially reported, missing, unassessed and not-applicable information
  are distinct. Reported claims link to evidence; not-applicable claims state why.
- Reporting completeness, methodological appraisal, computational verification
  and empirical validation are separate outcomes without an invented overall
  quality score or claims of global checklist completeness.
- Catalogue bytes, provenance and mapping scope are verified; topic mappings do
  not become equivalence assertions or undisclosed full-text reproductions.

## RQ-08 — Optional Power Platform delivery

Owner: [Power Platform](tracks/power_platform_20261108/index.md).

Provide a standard-connector baseline using Canvas/SharePoint inputs, job metadata
and summaries, with immutable request/result files and manual CLI operation first.
Keep an authorised asynchronous worker, premium API and local PCF/WASM experiment
as separate optional delivery routes. Power Fx does not duplicate valuation rules.

Acceptance:

- The baseline round-trips the same versioned bundle and result as the CLI without
  a hidden custom connector, premium HTTP action, Dataverse or Copilot dependency.
- Actual app, flow and environment entitlements are assessed for the chosen
  deployment. A queue or worker does not remove licensing obligations behind it.
- Worker/service routes separately demonstrate scoped access, idempotent claiming,
  retries, cancellation and handling of incomplete output; large results remain
  files rather than list-row payloads.
- PCF/WASM stays experimental until target-host, CSP, memory, packaging and parity
  checks pass. Deployment status is recorded separately from a working prototype.

## RQ-09 — R and Julia bindings

Owner: [polyglot bindings](tracks/polyglot_bindings_20261108/index.md).

R may call the shared Rust core directly through extendr. Julia uses a qualified,
versioned C ABI and native artifacts. Neither requires Python, and R delivery need
not wait for the C ABI. Wrappers translate inputs/results without duplicating maths.

Acceptance:

- Independently installed R and Julia packages reproduce the shared fixtures and
  preserve exact values, missingness, units, errors and version identities.
- Host lifetime/GC and threading rules are exercised. The C ABI has explicit
  lengths, ownership, allocation/free symmetry, version negotiation and panic
  containment; Rust layouts or unwinding never cross it.
- Supported operating systems/architectures and native artifact availability are
  demonstrated before package publication or compatibility claims.

## RQ-10 — Process models and Kairos

Owner: [process models](tracks/process_models_20261108/index.md).

Accept observed or simulated activity/resource events, then qualify XES, OCEL 2.0,
a bounded Petri-net/PNML profile and a named BPMN 2.0 subset. Reuse process tooling
and Kairos execution contracts; keep both Kairos and Dapane independently usable.
Represent event, process and object context over one source ledger. Associations
must not implicitly allocate or multiply costs; explicit attribution/allocation
determines object views. The initial runtime preserves context but does not
execute processes or infer usage from event duration.

Acceptance:

- Infant/specimen/batch relationships, activity identity and observation/simulation
  basis survive imports. Resource recipes attach to activity instances, with
  valuation applied separately.
- Independent cases exercise exclusive/parallel paths, contention, rework, cancelled
  and censored activity, transfer versus consumption and shared resources.
- Unsupported gateways, events, loops or timing semantics produce explicit
  diagnostics. Importing a diagram is not treated as proof of executable semantics.
- Repricing unchanged usage does not rerun execution; behaviour feedback is an
  explicit application scenario. Adapter licences and exact revisions are recorded.

## RQ-11 — Decision-model integrations

Owner: [decision integrations](tracks/decision_integrations_20261108/index.md).

Provide paired outputs to qualified Voiage methods, workload/adoption interfaces to
Innovate, and explicit valuation-to-payoff transformations for Paignia. Dapane owns
cost/valuation mechanics, not clinical outcomes, diffusion models or game solvers.

Acceptance:

- Strategy, scenario, parameter draw, replication, perspective and subgroup keys
  remain aligned across cost and outcome records; correlations are preserved.
- Epistemic uncertainty, population heterogeneity and methodological alternatives
  are separately identifiable; actual models are evaluated without random stand-ins.
- VOI, value-of-perspective and value-of-heterogeneity work uses provider-qualified
  capabilities, with unsupported methods and limitations visible to consumers.
- Adoption/capacity and strategic-pricing cases specify their feedback and payoff
  assumptions and do not add transfers across perspectives as new resource cost.

## RQ-12 — Qualification, performance, frontier research and consolidation

Owners: [release and consolidation](tracks/release_consolidation_20261108/index.md)
and [frontier benchmarks](tracks/frontier_benchmarks_20261108/index.md).

Qualify each published capability against independent cases and installed artifacts.
Evaluate evidence-linked costing, object-centric allocation, incremental revaluation,
measurement planning and adoption/capacity hypotheses against dated comparators.
Consolidation preserves unique research, source rights and functioning successors.

Acceptance:

- One tested compatibility matrix records engine/provider versions, Rust MSRV,
  language ABI, platforms and feature sets. Preview jobs do not silently expand
  supported releases; source checks and installed-artifact checks remain distinct.
- Acceleration demonstrates agreed numerical equivalence and chunk-boundary
  invariance before throughput claims. Incremental results match full recomputation.
- Research reports include independent oracles, comparator scope, controlled
  errors, modelling effort and limitations; multi-site evidence is needed before
  transportability claims. Planned hypotheses are never labelled achieved novelty.
- Release provenance, dependency/licence checks, source-data rights and capability
  maturity are recorded. No project licence or registry publication is inferred
  from this setup. Each archive has a unique-asset review and a working successor.

## Traceability and change control

Each implementation track declares its requirement IDs and acceptance evidence.
Runtime criteria stay pending until demonstrated. A documentation-only task can be
complete without completing a runtime requirement. Record changes to a shared
contract or economic meaning in [decisions](decisions.md), update affected consumers
and keep ordinary implementation decisions within the authorised task scope.
