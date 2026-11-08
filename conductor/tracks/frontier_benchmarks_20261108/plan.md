# Implementation plan: Frontier research and comparative benchmarks

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Protocol and comparators

- [ ] F1.1 Prepare the comparator review, hypotheses, independent oracles and analysis plan; protocol drafting may start before dependent runtime tracks finish.
- [ ] F1.2 Define numerical correctness, missing-cost/double-count detection, reporting coverage, analyst effort, latency and memory measures.
- [ ] F1.3 Verify that each experiment names its required provider/runtime capabilities, data permissions and limits before execution.

## Phase 2 — Controlled experiments

- [ ] F2.1 Construct controlled mutations of sourced or synthetic costing cases: missing components, duplicate batches, wrong denominator/unit/date and unsupported assumptions.
- [ ] F2.2 Implement and compare incremental revaluation with full recomputation on identical inputs and policies.
- [ ] F2.3 After the relevant newborn_screening and process_models capabilities are qualified, compare object-centric and flattened pathway representations using shared-batch, repeat and capacity cases; retain this experiment as pending without blocking F2.1/F2.2.
- [ ] F2.4 After the required decision_integrations capabilities are qualified, run measurement-priority and adoption/capacity experiments; retain this experiment as pending without blocking independent static benchmarks.
- [ ] F2.5 Verify independent expected outcomes and retain all negative/null results, environment details and complete result bundles.

## Phase 3 — External validation and publication

- [ ] F3.1 Acquire scoped authorised external or multi-site data and assess transportability, missingness and real modelling effort.
- [ ] F3.2 If pursued, qualify aggregate/federated calibration with explicit privacy/utility evaluation and no mandatory central patient-record store.
- [ ] F3.3 Choose target software/methods/application venues from the actual contribution and evidence; keep software release, paper and clinical validation claims distinct.
- [ ] F3.4 Update the dated comparator review, rerun relevant benchmarks and publish only conclusions supported by the observed results.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
