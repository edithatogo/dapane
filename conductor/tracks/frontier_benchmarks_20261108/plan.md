# Implementation plan: Frontier research and comparative benchmarks

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Protocol and comparators

- [x] F1.1 Prepare the comparator review, hypotheses, independent oracles and analysis plan; protocol drafting may start before dependent runtime tracks finish.
- [x] F1.2 Define numerical correctness, missing-cost/double-count detection, reporting coverage, analyst effort, latency and memory measures.
- [x] F1.3 Verify that each experiment names its required provider/runtime capabilities, data permissions and limits before execution.

F1 evidence: the scoped [comparator review](../../../benchmarks/static/COMPARATORS.md),
[protocol](../../../benchmarks/static/PROTOCOL.md) and source/capability boundaries
are authored. This completes the static protocol slice only, not a broad empirical
comparison or frontier literature review.

## Phase 2 — Controlled experiments

- [!] F2.1 Construct controlled mutations of sourced or synthetic costing cases: missing components, duplicate batches, wrong denominator/unit/date and unsupported assumptions.
- [!] F2.2 Implement and compare incremental revaluation with full recomputation on identical inputs and policies.
- [ ] F2.3 After the relevant newborn_screening and process_models capabilities are qualified, compare object-centric and flattened pathway representations using shared-batch, repeat and capacity cases; retain this experiment as pending without blocking F2.1/F2.2.
- [ ] F2.4 After the required decision_integrations capabilities are qualified, run measurement-priority and adoption/capacity experiments; retain this experiment as pending without blocking independent static benchmarks.
- [ ] F2.5 Verify independent expected outcomes and retain all negative/null results, environment details and complete result bundles.

F2.1/F2.2 implementation is published in `benchmarks/static/`. The earlier local
counterpart passed 21 tests, including 24 mutation cases and twelve update
scenarios at eight independent requests. The execution environment then became
unavailable. Reconstruction, namespace/locator changes, the new runner/verifier
and the exact published source remain unexecuted. Both increments stay blocked
pending exact-head tests, paired measurements and complete retained bundles.
See [handoff](HANDOFF.md) and [review](review.md).

## Phase 3 — External validation and publication

- [ ] F3.1 Acquire scoped authorised external or multi-site data and assess transportability, missingness and real modelling effort.
- [ ] F3.2 If pursued, qualify aggregate/federated calibration with explicit privacy/utility evaluation and no mandatory central patient-record store.
- [ ] F3.3 Choose target software/methods/application venues from the actual contribution and evidence; keep software release, paper and clinical validation claims distinct.
- [ ] F3.4 Update the dated comparator review, rerun relevant benchmarks and publish only conclusions supported by the observed results.

## Evidence record

### Owner quality follow-up — 2026-11-15

- [~] Reproduce and fix the five Python formatting failures at received head
  `237ddb238997b0babe12266cb7775207c597dfd4`, verify source equivalence, and run
  exact-head qualification before issuing a new scoped integrator handoff.

The integrator's received-head run passed 23 tests, the same-source native build,
the fixed protocol and bundle verification. Formatting remained a failed gate.
Historical failures remain retained; offline security is queued, and PR #20's
independent privacy findings remain unresolved. This follow-up changes only the
owned benchmark namespace and this track.

[Local observations](../../../benchmarks/static/evidence/local-observations.json)
retain executed versus unexecuted evidence, the two corrected diagnostic assumptions
and the loss of the original raw artifact. They do not qualify the reconstructed
publication head. No timing, memory, frontier or empirical result is claimed.

The track remains in progress. The integrator owns [the registry](../../tracks.md)
and must apply its matching lifecycle update before Conductor validation can pass.
That expected coordination failure is not waived. F2.3–5 and F3 remain open.
