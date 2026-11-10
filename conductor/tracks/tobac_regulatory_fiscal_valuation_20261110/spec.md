# Regulatory public-finance and health-system valuation handoff for tobac

## Outcome and users

Provide versioned public-finance and health-system perspective valuation, excise/GST tax-transfer separation and subgroup equity-weighting interfaces for `tobac` (`edithatogo/tobac`) while retaining `tobac`'s ownership of tobacco/vaping cohort dynamics, customs/wastewater partial identification and regulatory decision models.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-01, RQ-02, RQ-07, RQ-11** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Value cohort health-state occupancy, cessation-service activity and enforcement resource quantities under explicit health-system (`health_system_direct_cost`) and public-finance (`public_finance_fiscal_flow`) perspectives.
- Separate tobacco/vaping excise and GST fiscal transfers (`discounted_tax_transfer`) from real resource consumption so broader societal totals never double-count transfers.
- Preserve draw, strategy, replication, perspective and equity-subgroup (`Māori`, `non-Māori`, `First Nations`, `SEIFA/NZDep`) keys across discounting and net monetary benefit (`NMB`) aggregation before handoff to `voiage`.

## Deliverables

- Versioned regulatory valuation and fiscal-transfer separation schema profile compatible with `tobac` F04 (`src/tobac/economics.py`, `src/tobac/decision.py`).
- Independent exact reference cases for differential discounting, tax-transfer separation and subgroup equity-weighted cost/QALY summaries.
- Bounded consumer adapter verification with `tobac` and `voiage` paired-draw inputs.

## Prerequisites and interfaces

Local track dependencies:

- [core_contracts_20261108](../core_contracts_20261108/index.md)
- [rust_kernel_20261108](../rust_kernel_20261108/index.md)
- [decision_integrations_20261108](../decision_integrations_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/tobac: tobacco/vaping cohort state trajectories, cessation intervention pathways and customs/excise policy scenarios (`F04`, `F05`).
- edithatogo/voiage: paired-outcome and value-of-perspective contracts (`tobac_credal_endogenous_voi_20261110`, `simulation_outcome_boundary_20261107`).

## Acceptance criteria

1. Health-system direct medical costs and public-finance excise/GST transfers are represented as distinct typed accounting lines; societal totals never add transfer payments to real resource costs without an explicit net-transfer rule.
2. Differential and uniform discounting reference cases match independent exact arithmetic across annual and sub-annual cohort steps.
3. Subgroup and equity-stratum identities survive valuation and discounting without silent pooling across `Māori` / `non-Māori` or socioeconomic quintiles.
4. Paired parameter/replication draw keys are preserved end-to-end when exporting valued net-benefit tables to `tobac` and `voiage`.
5. Disabling the optional `dapane` adapter in `tobac` leaves `tobac`'s standalone reference oracle intact.

## Risks and constraints

Confusing fiscal excise revenue changes with societal resource savings invalidates regulatory cost-effectiveness analysis. Keep unit, currency/price-year, perspective and transfer labels mandatory at the schema boundary.

## Migration and rollback

Pin contract and package versions in `tobac` only after independent reference cases pass. Roll back to `tobac`'s internal reference valuation oracle if schema or perspective checks fail.

## Open implementation decisions

Select the minimal scalar and Polars/Arrow tabular interchange needed by `tobac`'s `ValuationInputs` and `PolicyOutcome` contracts before adding broader multi-country tariff catalogues.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
