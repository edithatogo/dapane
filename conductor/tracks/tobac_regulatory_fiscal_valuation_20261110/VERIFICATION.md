# T1 verification

## Current owner follow-up — 15 November 2026

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

T1 has 19 synthetic test declarations. The final earlier local 19-test run passed,
but the current published source was reconstructed after execution-environment
loss and has not been executed. T1.3 stays blocked; T1.1/T1.2 stay active.

See the shared lane [verification record](../decision_integrations_20261108/VERIFICATION.md),
[historical observation receipt](../decision_integrations_20261108/evidence/historical-execution-observations.json)
and [recovery static checks](../decision_integrations_20261108/evidence/recovery-static-checks.json).
The shared optional crate is in [adapters/decision_draws](../../../adapters/decision_draws/README.md).
T2/T3 consumer, cohort, equity and oracle-parity work is unexecuted and out of scope.
