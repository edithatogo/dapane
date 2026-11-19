# Implementation plan: Uncertainty and decision-library integration

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Draws and paired outcomes

- [x] D1.1 Specify parameter draws, correlation inputs, scenario/strategy/replication keys and separation of epistemic uncertainty from heterogeneity.   
  **Executed 2026-11-19:** `adapters/decision_draws/src/paired.rs` implements DrawSet with axis `epistemic_parameters`, 1..128 parameters, 1..256 draws, joint value alignment per draw, replication_axis `conditional_replication`, scenario/strategy/perspective/subgroup keys, six-key panel completeness. All 18 D1 tests pass.
- [x] D1.2 Evaluate the supported costing model for explicit indexed draws; accept outcomes only through a separately identified model contract.   
  **Executed 2026-11-19:** `evaluate_paired_json` delegates each cell/draw to the existing Dapane core entry points (point/interval 0.1/0.2), embeds native reports unmodified, joins externally supplied outcomes on all six keys (scenario_id, strategy_id, draw_id, replication_id, perspective, subgroup_id), rejects missing/extra/duplicate outcomes.
- [x] D1.3 Verify pairing, reproducibility, missing-draw rejection and scenario-comparison cases against independent expectations.   
  **Executed 2026-11-19:** 18 D1 tests cover: actual cost model with correlated draws and independent outcomes, byte reproducibility under outer row/axis reordering, missing/extra/duplicate outcome rejection, embedded core error propagation, missing model cell/pooled subgroup rejection, malformed exact value rejection, binding target/unit compatibility, perspective/currency/source mismatch rejection, joint draw identity preservation (no marginal replacement), unsupported method/unknown field/numeric float rejection, request replay to identical native reports, output digest independent reconstruction, negative outcome preservation with negative cost parameter rejection, interval per-segment rounding, capacity contract survival, key axis survival across cells/replications. All 18 D1 tests pass.

## Phase 2 — Provider adapters

- [ ] D2.1 Inspect current Voiage contracts and qualified methods; implement a bounded paired-output adapter including perspective and subgroup identity.
- [ ] D2.2 Implement one Innovate utilisation/adoption-to-resource scenario with explicit capacity thresholds and feedback orchestration.
- [ ] D2.3 Implement one optional Paignia input adapter with an explicit supported-game and payoff transformation contract.
- [ ] D2.4 Verify provider version negotiation, unsupported-method diagnostics, transfer accounting and independently derived decision examples.

## Phase 3 — Evidence and measurement planning

- [ ] D3.1 Use a qualified Voiage capability to evaluate a bounded additional-evidence question such as staff time, repeat rate or utilisation measurement.
- [x] D3.2 Document method maturity, source assumptions, external outcome limitations and alternative-perspective interpretations.   
  **Executed 2026-11-19:** `adapters/decision_provider_d2/D3-EVIDENCE.md` documents method maturity limits, source assumptions, external outcome limitations and alternative-perspective interpretations. Covers: Dapane D1 native paired costs (candidate, not accepted), D2 Voiage six-key interchange (preparation only), Voiage native EVPI (not executed), Innovate adoption/capacity (externally supplied only), Paignia finite-game input (blueprint only), measurement evidence (invented reference only), alternative perspectives (explicitly separate), uncertainty (draw_id/replication_id/perspective/subgroup identity), costs and decision welfare (separate constructs), population impact (no population EVPI claim), and exact acceptance blockers (6 items).
- [ ] D3.3 Run the selected installed/provider integration cases and confirm that disabling all decision adapters leaves static costing available.

## Bounded owner quality pass — 15 November 2026

- [x] D1.Q1 Resolve the received Rust formatting failures; verify the unchanged bounded synthetic implementation with exact-source format, warnings-denied Clippy, all 37 D1/T1 tests and Conductor checks; record the scoped review and handoff.

## Evidence record

The [owner quality record](owner-quality-20261115.md) and [local command receipt](evidence/owner-quality-20261115.json)
record clean-source checks at `9c177166899e588dc3dacadb13e4a0a3750bbce2`. Formatting, Clippy, locked/offline
dependency resolution, 18 D1 + 19 T1 tests, Conductor validation and 12 lifecycle
tests passed. The existing half-even generated-segment case passed unchanged.

The integrator has completed source replay, both central registry corrections
and explicit standalone CI. These shared files are preserved. Earlier recovery
limitations and failed formatting outcomes remain historical evidence; they are
not relabelled as current passes.

Phase-1 tasks remain active for coordinator acceptance of the bounded candidate;
the previous execution-environment block is resolved. Production signed-fiscal
method/profile qualification, later provider phases and required security/release
gates remain open. This quality repair does not complete the full track.

See [verification](VERIFICATION.md), [review](REVIEW.md), [metadata](metadata.json)
and the [exact-SHA handoff](HANDOFF.md). The [registry](../../tracks.md) already
matches this track's `in_progress` state.
