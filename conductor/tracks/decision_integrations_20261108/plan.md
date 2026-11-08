# Implementation plan: Uncertainty and decision-library integration

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Draws and paired outcomes

- [ ] D1.1 Specify parameter draws, correlation inputs, scenario/strategy/replication keys and separation of epistemic uncertainty from heterogeneity.
- [ ] D1.2 Evaluate the supported costing model for explicit indexed draws; accept outcomes only through a separately identified model contract.
- [ ] D1.3 Verify pairing, reproducibility, missing-draw rejection and scenario-comparison cases against independent expectations.

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

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
