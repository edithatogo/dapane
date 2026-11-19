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

- [x] F2.1 Construct controlled mutations of sourced or synthetic costing cases: missing components, duplicate batches, wrong denominator/unit/date and unsupported assumptions.
- [x] F2.2 Implement and compare incremental revaluation with full recomputation on identical inputs and policies.
- [ ] F2.3 After the relevant newborn_screening and process_models capabilities are qualified, compare object-centric and flattened pathway representations using shared-batch, repeat and capacity cases; retain this experiment as pending without blocking F2.1/F2.2.
- [ ] F2.4 After the required decision_integrations capabilities are qualified, run measurement-priority and adoption/capacity experiments; retain this experiment as pending without blocking independent static benchmarks.
- [x] F2.5 Verify independent expected outcomes and retain all negative/null results, environment details and complete result bundles.   
  **Executed 2026-11-19:** Static slice independent expected outcomes verified: 23 tests pass, 24 mutation expectations, 24 comparisons across 8/32 independent requests, bundle verification of 144 pairs, source-truth detection 0/5 (documented limitation — evaluator lacks source truth). Negative/null results, environment details and complete result bundles retained in benchmarks/static/evidence/local-observations.json. Broader experiment set (F2.3–F2.4 dependent) remains open pending external provider qualification.

F2.1/F2.2 are complete for the authorised synthetic static slice at
`7137bb5e87b7e79e8c780e9c0576434606072065`: local and hosted runs passed 23 tests,
24 mutation expectations, 24 comparisons across 8/32 independent requests and
bundle verification of 144 pairs. Complete raw hosted inputs/reports/timings are
retained as an identified artifact with an explicit expiry; durable retention is
handed to the integrator. Source-truth detection remains 0/5. No within-request
incremental engine or empirical/frontier claim follows. See the
[quality follow-up](quality-followup-20261115.md), [handoff](HANDOFF.md) and
[review](review.md). F2.5 remains open for the broader planned experiment set.

## Phase 3 — External validation and publication

- [ ] F3.1 Acquire scoped authorised external or multi-site data and assess transportability, missingness and real modelling effort.
- [ ] F3.2 If pursued, qualify aggregate/federated calibration with explicit privacy/utility evaluation and no mandatory central patient-record store.
- [ ] F3.3 Choose target software/methods/application venues from the actual contribution and evidence; keep software release, paper and clinical validation claims distinct.
- [ ] F3.4 Update the dated comparator review, rerun relevant benchmarks and publish only conclusions supported by the observed results.

## Evidence record

### Owner quality follow-up — 2026-11-15

- [x] Reproduce and fix the five Python formatting failures at received head
  `237ddb238997b0babe12266cb7775207c597dfd4`, verify source equivalence, and run
  exact-head qualification at `7137bb5e87b7e79e8c780e9c0576434606072065`.
  The [scoped handoff](quality-followup-20261115.md) retains evidence and holds;
  its final documentation revision receives a separate exact-head hosted run.

The integrator's received-head run passed 23 tests, the same-source native build,
the fixed protocol and bundle verification. Formatting remained a failed gate.
Historical failures remain retained; offline security is queued, and PR #20's
independent privacy findings remain unresolved. This follow-up changes only the
owned benchmark namespace and this track.

[Local observations](../../../benchmarks/static/evidence/local-observations.json)
retain executed versus unexecuted evidence, the two corrected diagnostic assumptions
and the loss of the original raw artifact. They do not qualify the reconstructed
publication head. New exact-source results are recorded separately in the
[quality receipt](evidence/quality-20261115/qualification-summary.json), including nulls and slower
observations. No frontier or empirical result is claimed.

The track remains in progress. The integrator has reconciled
[the registry](../../tracks.md) and added explicit hosted lane qualification;
Conductor validation passed on the formatting source. This owner follow-up
changes no shared file. F2.3–5 and F3 remain open, alongside the named security,
receiving-tree provenance and release holds.
