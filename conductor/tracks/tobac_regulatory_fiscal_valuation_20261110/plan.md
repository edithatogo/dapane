# Implementation plan: Regulatory public-finance and health-system valuation handoff for tobac

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Perspective and fiscal-transfer contracts

- [x] T1.1 Freeze the versioned contract distinguishing `health_system_direct_cost`, `enforcement_resource_cost` and `discounted_tax_transfer` (excise/GST) with mandatory currency, price-year and perspective tags.  
  **Executed 2026-11-19:** Contract `dapane-fiscal/0.1` implemented in `adapters/decision_draws/src/fiscal.rs` with `Perspective`, `Rule`, `Currency`, `Jurisdiction`, `MoneyUnit`, `AccountingBasis` enums; exact rational arithmetic; explicit perspective tags; currency/price-year/unit matching enforced. See `CONTRACT.md` and `adapters/decision_draws/README.md`.
- [x] T1.2 Construct independent exact arithmetic reference cases for NZ/AU tobacco excise transfers, differential discounting and societal versus health-system net monetary benefit.  
  **Executed 2026-11-19:** Reference cases in `tests/fiscal.rs` (19 tests) and `adapters/decision_draws/fixtures/fiscal-nz-synthetic.json`. Exact discounted values: medical 80, enforcement 16, government receipts 40, payer flow -40, net domestic transfer 0, health-system NMB 20, societal NMB 4, public net outlay 56. All pass.
- [x] T1.3 Verify that invalid perspective combinations, missing price-year metadata or unlabelled transfer additions fail closed.  
  **Executed 2026-11-19:** Fail-closed tests in `tests/fiscal.rs` reject perspective/currency/source mismatches, missing price-year metadata, unbalanced tax transfers, unsupported discount methods, unknown fields and numeric floats. All pass.

## Phase 2 — Cohort occupancy valuation and subgroup equity preservation

- [ ] T2.1 Evaluate cohort state-occupancy and cessation-resource schedules over indexed parameter draws while preserving `draw_id`, `strategy_id`, `perspective` and `subgroup_id`.
- [ ] T2.2 Implement subgroup equity-weight and distributional cost-effectiveness aggregation rules with exact unweighted-sum conservation checks when weights are unity.
- [ ] T2.3 Verify parity against `tobac`'s standalone reference oracle (`src/tobac/economics.py` and `src/tobac/decision.py`) on synthetic NZ/AU policy fixtures.

## Phase 3 — Paired-draw handoff to tobac and voiage

- [ ] T3.1 Export valued strategy/draw/perspective tables to `tobac` and `voiage` value-of-perspective / credal dominance workflows without losing joint draw identity.
- [ ] T3.2 Document perspective assumptions, excise deadweight-loss / transfer boundaries and fallback behaviour when `dapane` is not installed.
- [ ] T3.3 Run installed-package consumer checks and record exact producer/consumer revisions in the track metadata.

## Bounded owner quality pass — 15 November 2026

- [x] T1.Q1 Resolve the received Rust formatting failures; verify the unchanged bounded synthetic implementation with exact-source format, warnings-denied Clippy, all 37 D1/T1 tests and Conductor checks; record the scoped review and handoff.

## Evidence record

The [owner quality record](../decision_integrations_20261108/owner-quality-20261115.md) and [local command receipt](../decision_integrations_20261108/evidence/owner-quality-20261115.json)
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
