# Tobac fiscal handoff

## Checkpoint follow-up — 20 November 2026

The fiscal source follow-up starts at merged Dapane main `5c035f6` and carries
the Tobac checkpoint through `21dce9a`. The verified implementation is
`4d567f366c93103870f15c16a1a4918f77e46898`. Its changes are in
`adapters/decision_draws/` and this track. The existing standalone CI covers
the adapter crate. T2.3 still needs the Tobac interface mapping and an executed
parity comparison. T3.2 documents the perspective and fallback policy. Table
handoff and installed consumer verification remain in T3.1 and T3.3.
[Verification](VERIFICATION.md) · [Fallback](FALLBACK.md)

## T1 owner follow-up — 15 November 2026

The [bounded quality repair](../decision_integrations_20261108/owner-quality-20261115.md) records clean-source execution at
`9c177166899e588dc3dacadb13e4a0a3750bbce2` (tree `db6e32d39ae8960da9d30a24ed37eb965caea36d`). Rustfmt, Clippy with `-D warnings`,
18 D1 + 19 T1 tests, locked/offline Cargo metadata, Conductor validation and
12 lifecycle tests passed. The five Rust changes exactly equal pinned formatter
output; assertions, fixtures, manifests, locks, numerical methods and shared
coordinator files are unchanged.

Handoff requests 1–3 are satisfied within the bounded computational scope:
the integrator supplied recovered-source replay, registry reconciliation and
standalone CI; this owner corrected the remaining formatting failure. The final
documentation descendant is checked separately and its exact-head results are
handed to PR23/PR20. No earlier result is relabelled as evidence for a later head.

Request 4 (production signed-fiscal method/profile), D2/D3, T2/T3, required
offline-security and coordinator privacy/release acceptance remain open. No
provider method is qualified, no extra worker created, and no merge or release
performed. Both tracks remain `in_progress` and PR23 remains draft.

## Initial recovery record — historical, superseded where stated above

The retained text below describes the earlier recovery-stage source and blockers.
Its not-run, registry-pending and missing-CI statements are historical; current
execution and request dispositions are recorded above and in the owner follow-up.

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

### Immutable implementation identity

Published source checkpoint: [`dc9c42877bdab05967de731023ff9901541fc7f9`](https://github.com/edithatogo/dapane/commit/dc9c42877bdab05967de731023ff9901541fc7f9).
Draft lane PR: [#23](https://github.com/edithatogo/dapane/pull/23). Base: `e34f87c9df39a2132fecee142431cdeefb732471`.
This handoff-only child leaves the adapter bytes unchanged. The
[readback receipt](../decision_integrations_20261108/evidence/publication-readback.json)
records the exact source blobs; native qualification remains blocked.
