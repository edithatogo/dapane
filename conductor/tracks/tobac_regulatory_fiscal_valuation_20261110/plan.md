# Implementation plan: Regulatory public-finance and health-system valuation handoff for tobac

Status: completed

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
- [x] T2.3 Verify parity against `tobac`'s standalone reference oracle on synthetic NZ/AU policy fixtures.
  The installed Rust producer and Tobac health oracle agree for NZ annual differential and AU half-year uniform discounting across all three perspectives, cohort transitions, cessation, signed tax flows and subgroup QALYs. [Qualification](VERIFICATION.md#installed-policy-parity)

## Phase 3 — Paired-draw handoff to tobac and voiage

- [x] T3.1 Export valued strategy/draw/perspective tables to `tobac` and `voiage` value-of-perspective / credal dominance workflows without losing joint draw identity.
  **Executed 2026-11-20:** The synthetic eight-cell table keeps every joint key. Installed Voiage 3.1.0 `value_of_perspective` selects `alternative` for both perspectives. Tobac `891f79e07292b7754f78d7193130623bd5f9e243` (`tobac-regulatory-research` 0.2.0, module `__version__` 0.1.0) `credal.assess_decision` identifies `alternative` as commonly optimal for each perspective, with `draw-b` and subgroup `Māori / NZDep-1` still on the second state.
- [x] T3.2 Document perspective assumptions, excise deadweight-loss / transfer boundaries and fallback behaviour when `dapane` is not installed.
  The record describes the three perspective rules, the domestic transfer boundary and the intended fallback when the optional adapter is unavailable. [Fallback](FALLBACK.md)
- [x] T3.3 Run installed-package consumer checks and record exact producer/consumer revisions in the track metadata.
  The Rust producer exported eight distinct joint decision cells per jurisdiction. Voiage and Tobac agreed on both perspective-specific optima and preserved every cell identity. [Producer and consumer revisions](metadata.json)

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

All three phases passed on the synthetic policy fixtures. [Verification](VERIFICATION.md) · [Metadata](metadata.json) · [Handoff](HANDOFF.md)
