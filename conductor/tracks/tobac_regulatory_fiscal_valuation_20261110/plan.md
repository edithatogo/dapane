# Implementation plan: Regulatory public-finance and health-system valuation handoff for tobac

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Perspective and fiscal-transfer contracts

- [ ] T1.1 Freeze the versioned contract distinguishing `health_system_direct_cost`, `enforcement_resource_cost` and `discounted_tax_transfer` (excise/GST) with mandatory currency, price-year and perspective tags.
- [ ] T1.2 Construct independent exact arithmetic reference cases for NZ/AU tobacco excise transfers, differential discounting and societal versus health-system net monetary benefit.
- [ ] T1.3 Verify that invalid perspective combinations, missing price-year metadata or unlabelled transfer additions fail closed.

## Phase 2 — Cohort occupancy valuation and subgroup equity preservation

- [ ] T2.1 Evaluate cohort state-occupancy and cessation-resource schedules over indexed parameter draws while preserving `draw_id`, `strategy_id`, `perspective` and `subgroup_id`.
- [ ] T2.2 Implement subgroup equity-weight and distributional cost-effectiveness aggregation rules with exact unweighted-sum conservation checks when weights are unity.
- [ ] T2.3 Verify parity against `tobac`'s standalone reference oracle (`src/tobac/economics.py` and `src/tobac/decision.py`) on synthetic NZ/AU policy fixtures.

## Phase 3 — Paired-draw handoff to tobac and voiage

- [ ] T3.1 Export valued strategy/draw/perspective tables to `tobac` and `voiage` value-of-perspective / credal dominance workflows without losing joint draw identity.
- [ ] T3.2 Document perspective assumptions, excise deadweight-loss / transfer boundaries and fallback behaviour when `dapane` is not installed.
- [ ] T3.3 Run installed-package consumer checks and record exact producer/consumer revisions in the track metadata.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
