# Implementation plan: Frontier research and comparative benchmarks

Status: archived

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
- [x] F2.3 Compare object-centric and flattened pathway representations using shared-batch, repeat and capacity cases after the relevant newborn screening and process capabilities are qualified.
  Five newborn cases and one executed PNML case compare full native reports against pre-specified totals and residuals. A full-per-recipient join doubled the batch from AUD 80 to 160 in the PNML trace. Unknown capacity left AUD 100 unattributed in the object-centric case. [Native results](../../../benchmarks/static/evidence/native-experiments.json)
- [x] F2.4 After the required decision_integrations capabilities are qualified, run measurement-priority and adoption/capacity experiments; retain this experiment as pending without blocking independent static benchmarks.
  Installed Voiage ranked staff time above the synthetic comparison at AUD 10 versus 1 per assay. Installed Innovate exceeded monthly capacity in both baseline months and neither revised month. [Inputs and results](../../../benchmarks/static/evidence/native-experiments.json)
- [x] F2.5 Verify independent expected outcomes and retain all negative/null results, environment details and complete result bundles.   
  **Executed 2026-11-19:** Static slice independent expected outcomes verified: 23 tests pass, 24 mutation expectations, 24 comparisons across 8/32 independent requests, bundle verification of 144 pairs, source-truth detection 0/5 (documented limitation — evaluator lacks source truth). Negative/null results, environment details and complete result bundles retained in benchmarks/static/evidence/local-observations.json. The native results below extend this evidence to F2.3 and F2.4.

F2.1/F2.2 are complete for the authorised synthetic static slice at
`7137bb5e87b7e79e8c780e9c0576434606072065`: local and hosted runs passed 23 tests,
24 mutation expectations, 24 comparisons across 8/32 independent requests and
bundle verification of 144 pairs. Complete raw hosted inputs/reports/timings are
retained as an identified artifact with an explicit expiry; durable retention is
handed to the integrator. Source-truth detection remains 0/5. No within-request
incremental engine or empirical/frontier claim follows. See the
[quality follow-up](quality-followup-20261115.md), [handoff](HANDOFF.md) and
[review](review.md). The [native experiment archive](../../../benchmarks/static/evidence/native-experiments.json.gz) retains both representations, full reports, the executed trace, provider requests, valuation and feedback results.

## Phase 3 — External validation and publication

- [x] F3.1 Run the preregistered CMS 2024 public aggregate benchmark across 51 state/DC geographies for DRG 470. Record exact native parity, missingness, mapping steps and state-level transfer error. [External protocol and evidence](../../../benchmarks/static/EXTERNAL.md)
- [x] F3.2 Calibrate on the published CMS aggregates with one geography held out per fit.
  All 51 native predictions matched the independent Fraction oracle. Absolute errors totalled 17.2825% of the local reconstruction. [Protocol and results](../../../benchmarks/static/EXTERNAL.md#held-out-aggregate-calibration)
- [x] F3.3 Choose target software/methods/application venues from the actual contribution and evidence; keep software release, paper and clinical validation claims distinct.
  The dated comparator review identifies a software venue and conditional routes for methods and applications. Manuscript preparation, real-world validation and submission remain separate. [Venue rationale](../../../benchmarks/static/COMPARATORS.md#publication-fit)
- [x] F3.4 Reproduce the relevant synthetic and external comparisons and record conclusions with scope and limitations. The repository holds the dated review, reproducible evidence and candidate venue plan.

## Review fixes

- [x] Preserve full declared source precision, measure missingness separately and retain the native/Fraction cross-check. [Review](external-review.md)

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
