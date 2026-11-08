# Core contracts and independent reference cases

## Outcome and users

Define a small domain-neutral boundary that can represent workforce resource use, genomic workflows and MCHS weighted activity without making their meanings interchangeable.

This is a planned work specification. Repository setup does not establish the capabilities below.

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

## Open implementation decisions

Choose supported units, exact-number limits, first valuation methods and schema-versioning details from the three concrete examples. Do not widen the first release to every future method.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
