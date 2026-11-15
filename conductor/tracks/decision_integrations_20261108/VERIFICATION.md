# Verification and source-recovery limits

## Current acceptance state

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

## Earlier local executions actually observed

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

## Static recovery checks

[Recovery checks](evidence/recovery-static-checks.json) records checks executed
in the available JavaScript orchestration runtime: fixture/metadata JSON parsing,
37 test declarations, scoped path allowlist, fixture draw-set SHA verification,
unchanged root-lock package identities, local link resolution and independent
exact arithmetic for the reference values. These checks inspect text and data.
They do not compile Rust, execute Rust tests, run rustfmt/Clippy or certify a
complete Conductor validation.

## Required exact-SHA re-execution

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

## Coverage and unexecuted boundaries

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
