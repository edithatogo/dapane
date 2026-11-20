# Verification and source-recovery limits

## Decision provider evidence review — 19 November 2026

The Dapane source tested was `7c2f23dd337341366c65faf79e7c271991d7bc3f`.
On macOS arm64 with CPython 3.15.2, all 78 tests passed with
`python -B -m unittest discover -s tests -v` from
`adapters/decision_provider_d2/`. These tests check declared provider
compatibility, including source revision format and supported contracts and
methods. The focused Rust test
`transfer_changes_do_not_change_societal_or_health_nmb` also passed in
`adapters/decision_draws/tests/fiscal.rs`.

| Case | Observed result | Remaining qualification evidence |
| --- | --- | --- |
| Innovate adoption and capacity | Dapane's native wrapper called `dapane_adoption_capacity`. At 0.5 staff hours per adoption and capacity of 4 hours, the first period's 10 adoptions produced demand of 5 hours, 4 served and 1 carried forward. The second period's 2 adoptions produced demand of 2 hours including the carryover, all served. Executable SHA-256 `5d2d1cc8d40c2298773e0530528e9d241edfcfa9d575c7af2471d26b0f87ca29`. | A reviewed source-to-binary build record and a provider execution case for the price-feedback path. |
| Paignia finite game | Dapane's native wrapper solved the one-player case with explicit utilities of 10 and 20. The solver selected action B and returned 20. Executable SHA-256 `3ddf588cb7b425e0a036d4359741311b33fb34fce33aa658f53bf4db484f4922`. | A reviewed source-to-binary build record and application validation against the selected Paignia profile. |
| Voiage staff-time EVPI | The four synthetic net-benefit cells give an analytical reference of AUD 10 per assay. Available copies of `voiage-3.1.0-cp315-abi3-macosx_11_0_arm64.whl` differed from the claimed SHA-256 `71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140`. Native EVPI was unverified. | The selected wheel, its source-to-wheel and installed extension evidence, and a native execution receipt for the four-cell case. |

Dapane's standalone CLI was built from the tested source with Rust 1.99.1
using `cargo build --locked --offline --release --no-default-features -p dapane-cli`.
The executable SHA-256 was
`d6b365cee5da744cfb37a77101b94e3e2a084001d82739593d8e39a9d4b950e2`.
From isolated Python (`-I -S`), `study.run_static_without_providers` ran
`dapane evaluate -` on [the synthetic newborn-screening fixture](../../../fixtures/newborn-screening.json).
The total was AUD 150.00, and all six object totals matched the
[hand-calculated expectations](../../../fixtures/expected.json). The native
report output digest was `sha256:a38641e5373cb775f84fec290cb48e7e030a344bf86e44c0d1f76e1b44cd0d9c`.

D3.3's standalone costing check is verified. The selected installed-provider
integration cases remain pending in this 19 November record. The 20 November
execution below supersedes the Voiage row's remaining-evidence cell.

## Installed Voiage execution — 20 November 2026

The wheel file
`voiage-3.1.0-cp315-abi3-macosx_11_0_arm64.whl` hashes to
`71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140`, matching
its install `direct_url.json`. Its shipped `_runtime.py`, `analysis.py` and
`methods/basic.py` match source revision
`0978497b5047de9459ed2fca9b349a4e2a9c45d3`.
`native_voiage.run_evpi` called `voiage._runtime.compute_evpi` and returned
10.0 per assay for `[[-60, -80], [-120, -80]]`. The native extension digest is
`sha256:abc8048bde189318db3bb9d83e5966029fce6b71e0909a3d05d9076339b8ebf7`.
The 19 November observation that available copies differed from this digest
remains historical. Innovate and Paignia are not installed.

## D1/T1 owner follow-up — 15 November 2026

The [bounded quality repair](owner-quality-20261115.md) records clean-source execution at
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
performed. Both tracks were `in_progress` and PR23 was draft at that checkpoint.

## Initial recovery record — historical, superseded where stated above

The retained text below describes the earlier recovery-stage source and blockers.
Its not-run, registry-pending and missing-CI statements are historical; current
execution and request dispositions are recorded above and in the owner follow-up.

### Current acceptance state

Native qualification of this PR's recovered source is **blocked / not run**.
The local execution environment became unavailable before publication. The
complete source/tests were reconstructed from recorded implementation patches
through the GitHub connector and placed under the integrator-reserved
`adapters/decision_draws/` namespace. No byte-equivalence claim is made between
the previously tested checkout and these recovered files.

The 18 D1 and 19 T1 declarations in this tree are not evidence that this exact
tree compiles or passes. Rustfmt, Clippy, Cargo lockfile acceptance and all native
tests must be rerun at the published SHA. The lane remains a draft and both
phase-1 acceptance tasks remain open.

### Earlier local executions actually observed

These are historical observations from tool results during this session, not
byte-preserved log files or an attestation for the recovered source. The
unpublished D1 local commit was
`8c2a8589e005bf14a6cde5365fb218ed09f3ca98`; GitHub could not resolve it.
T1 changes were not committed when the environment failed.

| Earlier local check | Observed outcome | Limit |
| --- | --- | --- |
| D1 integration tests | 18 passed; 0 failed | Old unpublished checkout/path |
| D1 formatting check | Passed | Before source recovery |
| D1 Clippy, all targets, warnings denied | Passed | Before T1 final changes/recovery |
| Initial T1 integration tests | 17 passed | Before basis/completeness review fixes |
| Initial T1 Clippy, all targets, warnings denied | Passed | Before final two T1 tests/fixes |
| Final local T1 integration tests | 19 passed; 0 failed | Uncommitted local files, not recoverable for byte comparison |
| Final local T1 formatting command | Executed before 19-test run | No subsequent final `fmt --check` result |
| Final local T1 Clippy | Not executed | Next tool call failed as environment became unavailable |
| Earlier `git diff --check` | Passed | Before final T1/recovery changes |
| Adapter/root registry-package comparison | 27 optional packages were already in the root lock | Does not establish runtime compatibility |

The common command forms below were executed at the **old** unpublished path.
Toolchain: Rust `1.99.1 (58cf8f9c3 2026-10-13)`, Cargo
`1.99.1 (5f94df478 2026-08-27)`, Linux x86_64. A private copied Cargo cache
and task-specific temporary target directory enabled offline execution;
no credentials or toolchain installations were changed.

```sh
cargo test --manifest-path adapters/decision-fiscal/Cargo.toml --locked --offline --test paired
cargo fmt --manifest-path adapters/decision-fiscal/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision-fiscal/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/decision-fiscal/Cargo.toml --locked --offline --test fiscal
```

The final historical 19-test run followed a `cargo fmt` invocation. The earlier
Clippy result must not be attributed to that final source. The initial test-first
missing-module failures, an SHA-256 hexadecimal-format compilation error and a
non-reduced fixture spelling mismatch were corrected before the historical
passing D1 run. External outcome spelling was preserved; the fixture expectation
was corrected explicitly.

[Historical observation receipt](evidence/historical-execution-observations.json)
records this separation in machine-readable form. Original temporary logs are
unavailable; this receipt was written from the observed session outputs.

### Static recovery checks

[Recovery checks](evidence/recovery-static-checks.json) records checks executed
in the available JavaScript orchestration runtime: fixture/metadata JSON parsing,
37 test declarations, scoped path allowlist, fixture draw-set SHA verification,
unchanged root-lock package identities, local link resolution and independent
exact arithmetic for the reference values. These checks inspect text and data.
They do not compile Rust, execute Rust tests, run rustfmt/Clippy or certify a
complete Conductor validation.

### Required exact-SHA re-execution

Use the source and handoff SHAs in [HANDOFF.md](HANDOFF.md); checkout the final
PR revision, record `git rev-parse HEAD`, and run from the repository root:

```sh
cargo fmt --manifest-path adapters/decision_draws/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets
git diff --check
python3 scripts/validate_conductor.py
```

Use an already populated dependency cache for `--offline`; an absent cache is a
blocked run, not a successful test. Formatting discrepancies from manual recovery
may require an owned-path formatting commit followed by another exact-SHA run.
Do not change shared manifests or gates to make these commands appear to pass.

The central registry still lists these tracks as `new`. Static inspection of
the unchanged validator predicts two marker/status mismatches against the
owned `in_progress` metadata/index/plan. The native Conductor command above has
not been executed in this recovery environment. Its registry fix belongs to
the integrator; the mismatch is not waived.

### Coverage and unexecuted boundaries

D1 test cases cover actual point-model expected costs, all six keys, correlated
vector identity, complete Cartesian panels, independently supplied outcomes,
reordering reproducibility, replay of prepared native requests, interval
half-even segment rounding, unknown capacity preservation, bindings, duplicates,
unsupported methods, monetary/source mismatches and exact/size bounds.

T1 references cover NZ differential and AU uniform discounting, annual/subannual
equivalence, separate resource/transfer totals and signs, health-system/scoped
societal NMB, public outlay, explicit expenditure basis, complete categories,
Unicode subgroup retention, replay/digests and invalid metadata/perspective/
precision/unknown-field controls.

Not executed in this lane: a recovered-source native test/build/lint run, full
root regression suite, installed CLI/Python adapters, OS matrix, provider
consumer tests, independent-agent review, source admission, release/security
qualification or publication. Hosted root checks, if available, do not exercise
this isolated manifest. No additional workers were created.
