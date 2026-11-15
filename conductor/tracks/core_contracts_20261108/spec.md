# Core contracts and independent reference cases

## Outcome and users

Define a small domain-neutral boundary that can represent workforce resource use, genomic workflows and MCHS weighted activity without making their meanings interchangeable.

This is the retained full acceptance specification. All six criteria below are
satisfied for the versioned synthetic contract/reference scope, as mapped in
[closeout verification](verification.md). The criteria have not been removed or
weakened. Archival does not complete broader kernel methods, real provider/source
qualification, process execution or release acceptance.

## Scope and requirements

Owning requirements: **RQ-01, RQ-02, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Specify ResourceUse, ActivityMeasure, UnitQuote, RateRelease, ValuationPolicy, ValuationLine, ComponentLedger and RunBundle.
- Specify typed quantities, rational/decimal transport, dates, evidence states, errors and schema evolution before language bindings.
- Establish independent arithmetic and economic reference cases before translating legacy outputs.

## Deliverables

- Versioned machine-readable schemas and a contract document, with a supported-field/capability inventory.
- Independent positive, boundary and invalid fixtures under a dedicated reference-fixture directory.
- A compact compatibility and migration policy for schema, numeric and method versions.

## Prerequisites and interfaces

Local track dependencies:

- [conductor_setup_20261108](../conductor_setup_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/microcosting_healthworkforce: conditions/source contract and exact Fraction-like arithmetic cases.
- edithatogo/microcosting_genomics: one source-qualified assay/workflow and historical workbook evidence.
- edithatogo/mchs: classification edition and activity/funding contract.

The [provider mappings](../../../docs/provider-boundaries.md) retain the inspected
contracts and their limitations. Synthetic contract acceptance does not promote
these external providers to fully qualified integrations; their owners retain
those readiness obligations.

## Acceptance criteria

1. A resource quotation and an activity-kind quotation can be represented distinctly; incompatible kinds/units are rejected.
2. A nonterminating fractional duration and decimal quotation survive transport without a binary-float round trip.
3. Rate applicability uses explicit half-open intervals and separates effective dates, knowledge dates and economic price year.
4. Fixtures distinguish missing, zero, synthetic, observed and unsupported inputs, and preserve source/access/validation states separately.
5. Fixtures cover sub-cent allocation with residuals, loaded-rate component duplication, duplicate resource-use identity and alternative capital treatments.
6. Expected values are independently derived, with source and calculation notes; old package output alone is not the oracle.

## Risks and constraints

A universal unqualified cost field would erase economic meaning. An excessively permissive schema can accept unsupported combinations while appearing valid; enumerate supported semantics and preserve diagnostics.

## Migration and rollback

Retain fixture/schema versions. Corrections to economic meaning receive a new method/schema version and a migration note; do not rewrite historical expected results silently.

## Recorded decisions and extension boundary

The supported quantities, exact-number limits, first valuation methods and
schema versions are recorded in contracts 0.1/0.2 and bundle 0.1, with
[ADR-010–012](../../decisions.md). Do not widen their claims to every future
method. Later methods require a separately versioned increment with their owning
kernel/provider track and new acceptance evidence.

## Execution and verification

The [phased plan](plan.md) and [metadata](metadata.json) retain the completed work.
[Verification](verification.md) records actual commands, source identities,
review fixes, merge evidence and limits. The track is archived in place;
[repository workflow](../../workflow.md) continues to govern other work.
