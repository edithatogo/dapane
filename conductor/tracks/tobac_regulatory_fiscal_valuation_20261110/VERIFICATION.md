# Tobac fiscal verification

## Checkpoint verification — 20 November 2026

The tested implementation is `4d567f366c93103870f15c16a1a4918f77e46898`
(tree `d2e85d720c760dd8283713421d20778467a55cae`), based on Dapane main
`5c035f6`. The incoming checkpoint build failed because the equity aggregator
moved values that it later needed for its subgroup rows. The recovered source
at `21dce9a` passed 24 fiscal and 18 paired tests. The follow-up restored four
T1 regressions and added compatibility, context and precision checks.

Local verification used Rust and Cargo 1.99.1 on macOS 27.2.1 arm64 and Python
3.15.2 for Conductor. Executed from the repository root:

```sh
cargo fmt --manifest-path adapters/decision_draws/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets
cargo metadata --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --format-version 1
python -m unittest discover -s tests -p 'test_conductor_validation.py' -v
python scripts/validate_conductor.py
git diff --check
```

Formatting, Clippy, locked dependency resolution and Conductor validation
passed. All 31 fiscal tests, 18 paired-draw tests and 12 Conductor lifecycle
tests passed. The 0.1 NZ fixture reproduced its input and output digests
from `5c035f6`. The 0.2 tests discounted supplied amounts of 500 and 250 at
the declared one-step factor of 4/5 to 400 and 200, with the fiscal ledger
unchanged by either schedule.

With two invented NZ subgroup packets, unit weights give sums of 160 cost,
2 QALYs and 40 NMB on both totals. A different pair with weights 1 and 3
gives unweighted sums of 120, 3 and 180 and weighted sums of 200, 7 and 500.
Separate tests reject mismatched draw-set digests, comparators, resource
bases, discount declarations and thresholds, and retain exact values above
the input rational digit limit. [Fiscal tests](../../../adapters/decision_draws/tests/fiscal.rs)

Tobac main was inspected read-only at `891f79e07292b7754f78d7193130623bd5f9e243`.
It contains `src/tobac/health.py`. The `economics.py` and `decision.py` modules
named in the original plan are absent from that tree. T2.3 oracle parity and
T3 consumer execution remain pending. The results above cover local synthetic
adapter execution. Hosted checks are recorded separately on the pull request.

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

T1 has 19 synthetic test declarations. The final earlier local 19-test run passed,
but the current published source was reconstructed after execution-environment
loss and has not been executed. T1.3 stays blocked; T1.1/T1.2 stay active.

See the shared lane [verification record](../decision_integrations_20261108/VERIFICATION.md),
[historical observation receipt](../decision_integrations_20261108/evidence/historical-execution-observations.json)
and [recovery static checks](../decision_integrations_20261108/evidence/recovery-static-checks.json).
The shared optional crate is in [adapters/decision_draws](../../../adapters/decision_draws/README.md).
T2/T3 consumer, cohort, equity and oracle-parity work is unexecuted and out of scope.
