# Implementation plan: Uncertainty and decision-library integration

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Draws and paired outcomes

- [~] D1.1 Specify parameter draws, correlation inputs, scenario/strategy/replication keys and separation of epistemic uncertainty from heterogeneity.
- [~] D1.2 Evaluate the supported costing model for explicit indexed draws; accept outcomes only through a separately identified model contract.
- [~] D1.3 Verify pairing, reproducibility, missing-draw rejection and scenario-comparison cases against independent expectations.

## Phase 2 — Provider adapters

- [ ] D2.1 Inspect current Voiage contracts and qualified methods; implement a bounded paired-output adapter including perspective and subgroup identity.
- [ ] D2.2 Implement one Innovate utilisation/adoption-to-resource scenario with explicit capacity thresholds and feedback orchestration.
- [ ] D2.3 Implement one optional Paignia input adapter with an explicit supported-game and payoff transformation contract.
- [ ] D2.4 Verify provider version negotiation, unsupported-method diagnostics, transfer accounting and independently derived decision examples.

## Phase 3 — Evidence and measurement planning

- [ ] D3.1 Use a qualified Voiage capability to evaluate a bounded additional-evidence question such as staff time, repeat rate or utilisation measurement.
- [ ] D3.2 Document method maturity, source assumptions, external outcome limitations and alternative-perspective interpretations.
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
