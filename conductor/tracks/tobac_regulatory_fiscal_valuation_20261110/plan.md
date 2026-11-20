# Implementation plan: Regulatory public-finance and health-system valuation handoff for tobac

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Perspective and fiscal-transfer contracts

- [x] T1.1 Freeze the versioned contract distinguishing `health_system_direct_cost`, `enforcement_resource_cost` and `discounted_tax_transfer` (excise/GST) with mandatory currency, price-year and perspective tags.
  The 20 November run reproduced the 0.1 fixture's input and output digests from the reconciled base.
- [x] T1.2 Construct independent exact arithmetic reference cases for NZ/AU tobacco excise transfers, differential discounting and societal versus health-system net monetary benefit.
  The existing NZ/AU, annual and subannual fixtures passed. The NZ reference gives medical cost 80, enforcement 16, government receipts 40, payer flow −40, health-system NMB 20, societal NMB 4 and public net outlay 56.
- [x] T1.3 Verify that invalid perspective combinations, missing price-year metadata or unlabelled transfer additions fail closed.
  The rerun retained all 19 T1 cases, including the checks for an incompatible resource basis, a missing ledger category and an invalid perspective rule. [Fiscal tests](../../../adapters/decision_draws/tests/fiscal.rs)

## Phase 2 — Cohort occupancy valuation and subgroup equity preservation

- [x] T2.1 Evaluate cohort state-occupancy and cessation-resource schedules over indexed parameter draws while preserving `draw_id`, `strategy_id`, `perspective` and `subgroup_id`.
  The synthetic 0.2 profile reproduced the exact schedule amounts and retained the packet key and row perspectives. Schedule values are reported separately from the incremental ledger.
- [x] T2.2 Implement subgroup equity-weight and distributional cost-effectiveness aggregation rules with exact unweighted-sum conservation checks when weights are unity.
  The synthetic equity profile conserved cost, QALYs and NMB at unit weights. Tests also checked non-unit weights, exact precision and rejection of repeated subgroups or incompatible valuation contexts.
- [!] T2.3 Verify parity against `tobac`'s standalone reference oracle on synthetic NZ/AU policy fixtures.
  **Blocked 2026-11-20:** Tobac `891f79e07292b7754f78d7193130623bd5f9e243` has no `src/tobac/economics.py` or `src/tobac/decision.py`. The published scalar identity in `tests/test_workstream_integration.py` was executed from that tree: `discounted_resource_cost((100, -55), (0, 1), 0.10)` returned 50 and `discounted_tax_transfer((66, 22), (0, 1), 0.10)` returned `(86, -86)`. The exact adapter reproduces those integers, and the societal total stays 50 after the transfer pair cancels. `equity_weighted_qaly_score` weights population QALY totals and accepts a zero weight; the Dapane sum requires a strictly positive weight on cost, QALYs and NMB. Cohort and cessation schedules were not compared, so this is not policy-fixture parity.

## Phase 3 — Paired-draw handoff to tobac and voiage

- [~] T3.1 Export valued strategy/draw/perspective tables to `tobac` and `voiage` value-of-perspective / credal dominance workflows without losing joint draw identity.  
  **In progress 2026-11-20:** `export_perspective_table` emits the six-part key. `arrange` keeps all eight cells of the synthetic two-draw table, and the installed Voiage 3.1.0 `value_of_perspective` returns `alternative` for both perspectives without changing strategy or perspective order. Tobac is not installed and has not imported the table.
- [x] T3.2 Document perspective assumptions, excise deadweight-loss / transfer boundaries and fallback behaviour when `dapane` is not installed.  
  **Executed 2026-11-20:** [FALLBACK.md](FALLBACK.md) records the three perspective boundaries, the refusal to treat excise or GST as deadweight loss, and the requirement that a missing adapter leave `tobac` and `voiage` on their own code.
- [~] T3.3 Run installed-package consumer checks and record exact producer/consumer revisions in the track metadata.  
  **In progress 2026-11-20:** The wheel file `voiage-3.1.0-cp315-abi3-macosx_11_0_arm64.whl` hashes to `71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140`, the same digest recorded in its install `direct_url.json`. With `polars` and `pyarrow` available, the perspective-table test called that install and kept the eight joint keys. Tobac is not installed, and the Dapane producer itself is not an installed package, so the consumer revision record is incomplete.

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

The track remains `in_progress`. The 20 November checkpoint verification covers
T1 and the bounded synthetic T2.1–T2.2 implementation. T2.3 stays blocked on
the missing Tobac oracle paths. T3.2 is recorded in [FALLBACK.md](FALLBACK.md).
T3.1, T3.3 and production method qualification remain open.
[Verification](VERIFICATION.md) · [Metadata](metadata.json) · [Handoff](HANDOFF.md)
