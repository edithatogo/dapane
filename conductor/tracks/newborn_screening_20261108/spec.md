# Newborn screening pathway composition

## Outcome and users

Demonstrate the next new domain by composing workforce quotations and laboratory recipes into a versioned newborn-screening programme model, with conserved shared costs and explicit denominators.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-06, RQ-03, RQ-07** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Separate infant, screening episode, specimen/card, collection attempt, assay, batch, result, recall, confirmation and follow-up identities.
- Support configurable collection, transport, accession/QC, testing, repeat/reflex, reporting, recall, confirmation and programme-overhead stages.
- Distinguish programme averages, marginal added conditions/panels and capacity-step scenarios under declared perspectives.

## Deliverables

- A versioned newborn-screening recipe/profile and source manifest.
- Synthetic shared-batch, repeat/failure, denominator and capacity fixtures.
- A scoped real programme pack and independently checked reporting output when source evidence is available.

## Prerequisites and interfaces

Local track dependencies:

- [python_two_consumers_20261108](../python_two_consumers_20261108/index.md)

Recipe construction and synthetic costing qualification do not require the reporting adapter. Task N3.2 requires [reporting_profiles_20261108](../reporting_profiles_20261108/index.md) only for the selected reporting/profile capability; leave that capability pending until its own evidence exists.

External readiness, checked separately from the local dependency graph:

- edithatogo/microcosting_healthworkforce and edithatogo/microcosting_genomics: qualified quotation and laboratory-recipe providers.
- Jurisdiction/programme source owner: actual screening scope, clinical pathway, probabilities, timing, quantities and rates; no default clinical assumptions are supplied.
- edithatogo/UOGTO and edithatogo/standards_check: diagnostic and general costing reporting profiles.

## Acceptance criteria

1. The synthetic two-infant fixture conserves a 150 total: collections 10 each, one batch 100 allocated 50/50 and confirmation 30 for infant B; infant views are 60 and 90.
2. Collection, transport, setup, controls and batch resources are counted once; allocation views do not add another expense.
3. Repeat specimens/tests alter appropriate quantities without inflating the distinct-infant denominator.
4. Cost per eligible birth, participating infant, valid screen, completed pathway and confirmed diagnosis have explicit denominator/window identities.
5. Clinical probabilities, timing, assay scope and rates are versioned programme inputs; no synthetic fixture is presented as clinical evidence.
6. When reporting support is advertised, applicable CHEERS/GHCC/AGREEDT coverage includes evidence and exclusions through the qualified optional profile adapter; lifetime outcomes remain the linked model owner's responsibility.

## Risks and constraints

Flattening specimens or batches into independent infants duplicates costs. Programme costs alone do not establish clinical benefit, eligibility or cost-effectiveness.

## Migration and rollback

Version recipes, population/window definitions and source packs separately. Preserve synthetic qualification fixtures and restore previous programme packs without overwriting historical studies.

## Open implementation decisions

Choose one programme/jurisdiction and a bounded initial assay scope. Inclusion of family time and downstream care follows the specified perspective and horizon, not a universal default.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
