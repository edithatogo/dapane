# Frontier research and comparative benchmarks

## Outcome and users

Test whether evidence-linked, object-centric costing provides measurable advantages over strong current alternatives. Treat novelty and frontier claims as empirical questions.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-12, RQ-06, RQ-10, RQ-11** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Preregister comparator questions, independent oracles, data rights and outcome measures before collecting comparative results.
- Evaluate evidence-chain error detection, shared-resource costing, incremental revaluation, measurement planning and adoption/capacity feedback.
- Extend to external/multi-site transportability and privacy-preserving summaries only when the required data and methods are available.

## Deliverables

- A dated comparator review and executable benchmark protocols with explicit scope.
- Synthetic mutation and real/authorised external-data benchmark suites.
- Reproducible result bundles and a publication plan tied to observed findings.

## Prerequisites and interfaces

Local track dependencies:

- [python_two_consumers_20261108](../python_two_consumers_20261108/index.md)

The base benchmark suite needs only the two installed consumers. The object-centric newborn experiment additionally requires the relevant newborn/process capabilities; the measurement/adoption experiment additionally requires its decision adapter. These are experiment-specific prerequisites, not blockers for static error-detection or incremental-revaluation work.

External readiness, checked separately from the local dependency graph:

- Independent reference/calculation reviewers and authorised programme-data owners: external validation cannot be inferred from agent-generated fixtures.
- edithatogo/voiage, edithatogo/innovate, edithatogo/paignia and process providers: each experiment requires the exact qualified capability it uses.

## Acceptance criteria

1. Comparators are selected from a dated review and use equivalent inputs, methods and declared capabilities.
2. Controlled omissions, double counts, unit/date changes and unsupported assumptions have independent expected outcomes.
3. Incremental revaluation is identical to full recomputation under the agreed exact contract before speed improvements are reported.
4. Process benchmarks preserve many-to-many objects and compare allocation/denominator errors as well as runtime.
5. Measurement-planning and capacity experiments use qualified decision/provider contracts and distinguish epistemic uncertainty, heterogeneity and transfers.
6. External validation reports transportability, missingness, model limitations and analyst effort; synthetic success is not described as empirical programme validation.
7. Any privacy-preserving or federated experiment measures disclosure risk and utility rather than merely asserting privacy.

## Risks and constraints

Additional bindings, GPU use or larger ontology counts are not themselves evidence of frontier performance. Do not change benchmark scope after observing results without recording the change.

## Migration and rollback

Retain preregistered protocols, data/source versions and negative results. Revisions create new benchmark versions rather than silently replacing unfavourable outputs.

## Open implementation decisions

Set effect-size/error-detection targets and venue candidates after the comparator review. Research hypotheses do not create mandatory dependencies for the first Dapane release.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
