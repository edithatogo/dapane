# MCHS activity and quotation-source adapters

## Outcome and users

Connect classified hospital activity and versioned quotation sources without conflating tariffs, funding, resource cost and actual payment.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-05, RQ-01, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Map MCHS classifications, editions and supported funding rules to ActivityMeasure and activity-kind quotations.
- Consume reimbursement-atlas source packs through a versioned adapter rather than duplicate collectors/parsers.
- Preserve public APIs and produce parallel, clearly labelled valuation views when the underlying evidence supports them.

## Deliverables

- MCHS adapter contract and cross-repository consumer fixtures.
- Quotation-source manifest adapter carrying source, access, effective/knowledge dates and exact values.
- Comparison report for supported activity/funding and resource-cost views.

## Prerequisites and interfaces

Local track dependencies:

- [python_two_consumers_20261108](../python_two_consumers_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/mchs: classification-specific equations, activity editions and existing Rust/wrapper qualification.
- edithatogo/reimbursement-atlas: authoritative quotation source registry, parsers, source licences and releases.

## Acceptance criteria

1. The activity-only funding fixture produces the correct result with zero inferred or manufactured ResourceUse records.
2. Pricing/classification edition is retained separately from economic price year and quote knowledge date.
3. Unqualified synthetic/local fixtures are not presented as official rate releases.
4. Incompatible resource/activity quotations, stale applicability and missing source rights/status produce explicit diagnostics.
5. Resource cost, funding entitlement, tariff and observed payment remain separately queryable and are not summed by default.

## Risks and constraints

A common money representation can hide different economic meanings. An accessible source is not necessarily redistributable or scientifically qualified.

## Migration and rollback

Pin provider releases and preserve previous adapters. A source correction changes the release/method identity; it does not overwrite historical-as-known runs.

## Open implementation decisions

Select the first classification edition and quotation providers from available qualified releases. The adapter does not establish new domain equation validity.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
