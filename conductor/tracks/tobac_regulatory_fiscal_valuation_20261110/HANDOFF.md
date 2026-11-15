# T1 exact-SHA handoff

Integration owner: **Dapane — Release assurance and consolidation**, chat
`6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

The authoritative [shared D1/T1 handoff](../decision_integrations_20261108/HANDOFF.md)
records the source checkpoint, scoped files, exact verification limits and
concrete registry/CI/production-method requests. This track owns only T1.1–T1.3.
The optional implementation is in `adapters/decision_draws/`, within the
integrator's reserved lane root.

T1's reference method distinguishes `public_expenditure`, `economic_cost`
and `fiscal_transfer`; requires all four labelled accounting categories; and
keeps signs, discount timing, currency/year and perspective explicit. It does
not qualify a production Tobac provider method. Native verification of the
recovered source is blocked, so the phase is not marked complete.

The read-only Tobac pin is `891f79e07292b7754f78d7193130623bd5f9e243`.
The old planned economics/decision module paths are absent at that SHA. Actual
related functions in `health.py` require later T2/T3 contract reconciliation;
source-adjudication ownership is unchanged.

## Immutable implementation identity

Published source checkpoint: [`dc9c42877bdab05967de731023ff9901541fc7f9`](https://github.com/edithatogo/dapane/commit/dc9c42877bdab05967de731023ff9901541fc7f9).
Draft lane PR: [#23](https://github.com/edithatogo/dapane/pull/23). Base: `e34f87c9df39a2132fecee142431cdeefb732471`.
This handoff-only child leaves the adapter bytes unchanged. The
[readback receipt](../decision_integrations_20261108/evidence/publication-readback.json)
records the exact source blobs; native qualification remains blocked.
