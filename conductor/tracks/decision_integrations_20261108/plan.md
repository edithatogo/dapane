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

- [x] D2.1 Inspect current Voiage contracts and qualified methods; implement a bounded paired-output adapter including perspective and subgroup identity.  
  **Executed 2026-11-20:** The paired adapter keeps scenario, strategy, draw, replication, perspective and subgroup. Installed Voiage 3.1.0 `value_of_perspective` returned `alternative` for both perspectives, and `voiage._runtime.compute_evpi` returned 10 per assay for the staff-time matrix. The wheel digest is `sha256:71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140`.
- [!] D2.2 Implement one Innovate utilisation/adoption-to-resource scenario with explicit capacity thresholds and feedback orchestration.  
  **Blocked 2026-11-20:** Innovate main `fd7e259bb9a685d620f80907c6815d4837da3e53` accepts `innovate-native predict` only for operation `predict_model`. The repository has no `dapane_adoption_capacity` operation. `innovate-core` also depends on Kairos `a1f6283575ad26918230adc122a99b5c08fc4da3`, whose public resource-usage contract is still pending. Dapane still refuses to invent a price response; the earlier native backlog example remains a local arithmetic replay, not a provider execution.
- [x] D2.3 Implement one optional Paignia input adapter with an explicit supported-game and payoff transformation contract.  
  **Executed 2026-11-20:** Paignia `44bebdae9ca53a113681041e8fe5dcc16f57b918` admitted the static profile `paignia/static-finite-perfect-information-sparse-zero/1.0.0` and selected action B with utility 20 over action A with utility 10. The draw key `draw-a` stayed on the packet. Paignia publishes no solver command, so the call used a local harness linked to `paignia-core` and `paignia-solve` from that commit. The harness digest is `sha256:d793ab5174c4bf2f725480e10850fd8db2f2d5c9e50c066511e4a7fb3e4b641f`.
- [x] D2.4 Verify provider version negotiation, unsupported-method diagnostics, transfer accounting and independently derived decision examples.  
  **Executed 2026-11-20:** Negotiation rejects a non-commit revision and returns the selected contract. Unsupported methods are rejected. A nonzero domestic transfer is rejected, and transfer changes do not alter societal or health-system net benefit. Independent examples are the staff-time value of 10 per assay and the Paignia choice of B at utility 20. Innovate's installed execution remains the separate block in D2.2.

## Phase 3 — Evidence and measurement planning

- [x] D3.1 Use a qualified Voiage capability to evaluate a bounded additional-evidence question such as staff time, repeat rate or utilisation measurement.  
  **Executed 2026-11-20:** Installed Voiage 3.1.0 `DecisionAnalysis.evpi` returns 10.0 for the staff-time matrix `[[-60, -80], [-120, -80]]`. The wheel file `voiage-3.1.0-cp315-abi3-macosx_11_0_arm64.whl` hashes to `71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140`, matching its install record. No population scaling was applied. Earlier copies that did not match this digest remain historical.
- [x] D3.2 Document method maturity, source assumptions, external outcome limitations and alternative-perspective interpretations.
  The [D3 preparation dossier](../../../adapters/decision_provider_d2/D3-EVIDENCE.md) records the evidence assumptions, distinctions across perspectives and limits of the synthetic example.
- [x] D3.3 Run the selected installed/provider integration cases and confirm that disabling all decision adapters leaves static costing available.  
  **Executed 2026-11-20:** `native_voiage.run_evpi` called `voiage._runtime.compute_evpi` on the installed 3.1.0 wheel `sha256:71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140` at source revision `0978497b5047de9459ed2fca9b349a4e2a9c45d3`. The staff-time result is 10.0 per assay, and the native extension digest is `sha256:abc8048bde189318db3bb9d83e5966029fce6b71e0909a3d05d9076339b8ebf7`. The shipped `_runtime.py`, `analysis.py` and `methods/basic.py` match that revision. The earlier standalone native CLI returned AUD 150.00 with decision providers disabled.

The [19 November verification](VERIFICATION.md#decision-provider-evidence-review--19-november-2026)
records the replays, artifact identities and remaining evidence for D2 and D3.

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
