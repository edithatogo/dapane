# Uncertainty and decision-library integration

## Outcome and users

Connect correctly paired cost outputs to Voiage, Innovate and Paignia while retaining their existing ownership of decision methods, adoption mechanisms and strategic models.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-11, RQ-02, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Evaluate the actual costing model over explicit correlated parameter draws, retaining strategy/draw/replication/perspective/subgroup keys.
- Export aligned cost/outcome inputs to qualified Voiage methods and source-qualified payoff transformations to Paignia.
- Coordinate adoption/utilisation/capacity feedback with Innovate at the application boundary.

## Deliverables

- Versioned paired-outcome and uncertainty ingestion/export contracts.
- Bounded VOI/perspective/heterogeneity, adoption-capacity and strategic-pricing integration examples.
- Capability/error matrix identifying supported provider methods and unsupported combinations.

## Prerequisites and interfaces

Local track dependencies:

- [rust_kernel_20261108](../rust_kernel_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/voiage: qualified paired-outcome, VOI, value-of-perspective and value-of-heterogeneity contracts; recheck actual method readiness.
- edithatogo/innovate: adoption, utilisation, substitution and competition mechanisms remain provider-owned.
- edithatogo/paignia: supported game representation/solvers and explicit payoff input boundary.
- External health-economic outcome model: clinical outcomes are separately sourced and qualified.

## Acceptance criteria

1. Repeated evaluation uses the actual model; demonstration random outputs cannot substitute for missing calculation capability.
2. Costs and externally modelled outcomes retain joint draw identity; parameter uncertainty differs from within-population variation.
3. Perspective/subgroup results are preserved and transfer payments are not double-counted when presenting broader totals.
4. Voiage methods are selected by qualified capability and input contract; Dapane introduces no duplicate local VOI estimator.
5. Innovate feedback scenarios state how adoption/utilisation changes resources and when price affects behaviour.
6. Paignia receives an explicit payoff transformation with provenance; cost values do not silently become utility or clinical benefit.

## Risks and constraints

Independent marginal samples can destroy decision-relevant correlation. Cost savings, cash savings, funding transfers and utility must retain distinct meanings; provider method labels are not proof of qualification.

## Migration and rollback

Pin method/provider versions and retain paired inputs and transformation descriptions. Restore prior adapters or static cost outputs when an optional decision capability is unavailable.

## Open implementation decisions

Select one genuinely supported method/example per provider before expanding the integration surface. Do not make every research method a core dependency.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
