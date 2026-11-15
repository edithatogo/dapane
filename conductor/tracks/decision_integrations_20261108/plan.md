# Implementation plan: Uncertainty and decision-library integration

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Draws and paired outcomes

- [~] D1.1 Specify parameter draws, correlation inputs, scenario/strategy/replication keys and separation of epistemic uncertainty from heterogeneity.
- [~] D1.2 Evaluate the supported costing model for explicit indexed draws; accept outcomes only through a separately identified model contract.
- [!] D1.3 Verify pairing, reproducibility, missing-draw rejection and scenario-comparison cases against independent expectations.

## Phase 2 — Provider adapters

- [ ] D2.1 Inspect current Voiage contracts and qualified methods; implement a bounded paired-output adapter including perspective and subgroup identity.
- [ ] D2.2 Implement one Innovate utilisation/adoption-to-resource scenario with explicit capacity thresholds and feedback orchestration.
- [ ] D2.3 Implement one optional Paignia input adapter with an explicit supported-game and payoff transformation contract.
- [ ] D2.4 Verify provider version negotiation, unsupported-method diagnostics, transfer accounting and independently derived decision examples.

## Phase 3 — Evidence and measurement planning

- [ ] D3.1 Use a qualified Voiage capability to evaluate a bounded additional-evidence question such as staff time, repeat rate or utilisation measurement.
- [ ] D3.2 Document method maturity, source assumptions, external outcome limitations and alternative-perspective interpretations.
- [ ] D3.3 Run the selected installed/provider integration cases and confirm that disabling all decision adapters leaves static costing available.

## Evidence record

## Bounded owner quality pass — 15 November 2026

- [~] D1.Q1 Reproduce and correct the five received Rust formatting failures; run exact-source format, warnings-denied Clippy, all 37 D1/T1 tests and Conductor checks, then publish scoped review/evidence to the existing PR and coordinator.

Received head: `f9f85e5f54a38447eab91ae459aad2f372bcbb7e`. Coordinator
registry and standalone CI changes are present and must be preserved. The fresh
hosted receipt passed Clippy and 37 tests; formatting alone failed. This pass
does not change numerical methods or complete later provider/release obligations.

The bounded phase-1 implementation and synthetic tests are in
[the isolated adapter](../../../adapters/decision_draws/README.md). Current-source
native qualification is blocked: the execution environment became unavailable
after earlier local tests and before those sources were pushed. The published
implementation was reconstructed from recorded patches. Earlier local results
do not qualify the recovered bytes.

D1.1 and D1.2 retain active markers pending exact-SHA qualification and any
integrator method/profile decision; D1.3 is blocked. Later phases remain
pending and no provider method is qualified by this PR.

See [verification](VERIFICATION.md), [review](REVIEW.md), [metadata](metadata.json)
and the [exact-SHA handoff](HANDOFF.md). The central [registry](../../tracks.md)
still records `new`; changing its two rows to `[~]` / `in_progress` is a
concrete request to the sole integrator, who owns that shared file. The resulting
validation mismatch is an open integration requirement, not a waived gate.
