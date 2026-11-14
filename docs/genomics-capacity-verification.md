# Synthetic genomics capacity increment: verification

Date: 14 November 2026. This record qualifies a bounded computational candidate;
it does not establish empirical genomics validity or validated economic formulae.
Only repository material and synthetic fixtures were used.

## Integration and ownership reconciliation

The single Dapane coordinator reconciled current main
`e1f033a2ce6eeacf39588035869391d40ff5b47d` with PR #2's inspected/current head
`14b34896b983e53fc053b405ff800504b2add678`. No active overlapping implementation
owner was found in the session or open PR inventory. Conditional offline-security
PR #5 explicitly remained unmergeable until its separate infrastructure gates;
it was not edited or merged. Tobac's planned track remains separately owned.

PR #2 was refreshed at `2e67d74329f664f0f2e4861869774425c82e176a`, preserving the
current privacy workflow, Renovate and Tobac additions. The dated dependency note
was reconciled with the existing runtime. Before integration, all seven checks
on that exact head succeeded: native, Python 3.12/3.13/3.14/3.15, Conductor, and
privacy/secrets. Their workflow receipts are:

- [Runtime 43596047453](https://github.com/edithatogo/dapane/actions/runs/43596047453)
- [Conductor 43596047502](https://github.com/edithatogo/dapane/actions/runs/43596047502)
- [Privacy 43596047521](https://github.com/edithatogo/dapane/actions/runs/43596047521)

PR #2 then merged at `056e8e3f78f6843bcd55e5d3816e7a23b167305f`. This increment
builds on that runtime, rather than implementing another kernel. Core-contract
C4.1/C4.2 and existing Python-consumer P2.2/P2.4 own the work; their broader tracks
remain in progress. CareOps, provider repositories and security PR #5 are untouched.

## Numerical and contract evidence

[Five new candidate requests](../fixtures/genomics-capacity/README.md) compare
time and sample allocation, missing use and unknown capacity, and first-period
versus recurrent-only costs. Expected values were authored from independent hand
calculations before the evaluator was extended. A separate read-only reviewer
also recomputed the five cases with exact rational arithmetic.

The first capacity test run failed as intended: six new capacity tests failed
because `capacity_allocations` was unsupported; two 0.1 compatibility tests passed.
After implementation, nine capacity tests pass, including the review-added
composition of direct attribution, full-pool allocation and partial capacity.

The tests establish:

- Independent recurring-pool results: known capacity `30 / 60 / 210`; missing B
  use `30 / null / 270`; unknown availability `null / null / 300`; full-pool sample
  allocation `120 / 180 / 0`, with the last value representing unallocated cost.
- Device preparation `12,000 / 60 = 200`, maintenance `2,400 / 24 = 100`, and a
  separate one-time `600`; maintenance is not divided by device useful life.
- Unknown/zero distinction, retained observations, strict unsupported-input
  rejection, bounded explicit denominators, canonical order and no inferred
  utilisation. Unknown shares cannot acquire a rounding unit.
- Conservation including the unallocated bucket, deterministic sub-cent ties,
  and successful composition of disjoint direct/full/partial views.
- All five original 0.1 fixture input/output digests remain unchanged from the
  integrated runtime. The frozen digest file is a regression receipt, not an
  independent scientific oracle.

## Local commands and results

Observed environment: Rust 1.99.1, Linux x86_64, CPython 3.15.2. The existing
lockfile, requirements pins and dependency graph were retained; no new dependency
or feature was adopted. `cargo tree --locked -d` reported no duplicates in the
selected graph. This is not a new advisory/security/licensing audit or benchmark.

| Command/check | Observed result |
| --- | --- |
| `cargo test --locked` and targeted capacity/CLI checks after additions | 25 existing core + 9 capacity + 6 CLI tests pass (40 total). |
| `cargo fmt --all --check` | Pass. |
| `cargo clippy --workspace --locked --all-targets -- -D warnings` | Pass. |
| `cargo build --locked --release -p dapane-cli` | Pass. |
| `cargo install --locked --path crates/dapane-cli --root <isolated-prefix>`; evaluate all five new requests from `/tmp` | Installed CLI reports match the installed native Python reports exactly; version output lists both contracts. |
| `python scripts/validate_contract.py --cli target/release/dapane` | Original 4 schemas, 5 cases, 37 schema/parser negatives, 14 semantic rejections and 3 identity/context cases pass. |
| `maturin build --locked --release --interpreter <isolated-python> --out <wheel-dir>` | Native CPython 3.15 wheel built and installed into a clean environment. |
| Installed `python -m pytest --import-mode=importlib <checkout>/tests/python -q`, run from `/tmp` | 74 pass; includes 20 new genomics tests, all 8 schema documents registered locally and native Python parity. |
| Ruff check/format for Python/tests and the existing contract/benchmark scripts | Pass. |
| `python scripts/validate_conductor.py` and `git diff --check` | Pass; tracks remain open beyond the bounded candidate. |

The wheel was `dapane-0.1.0-cp315-cp315-manylinux_2_34_x86_64.whl`. This local
artifact's SHA-256 is `a48a9ee12208b105f6ae472bae32730abad8a8d8b62b5a656a23df2085616a30`.
The
run qualifies that observed interpreter/platform only. Existing hosted CI
independently exercises CPython 3.12–3.15 for a published PR head. Consult the
increment's exact-head GitHub checks for that revision; the older PR #2 receipts
above are not evidence for the new capacity implementation.

## Limits and remaining lanes

The prepared quotes are candidate assumptions, not an implemented capital or
maintenance economic method. Available hours must match equipment and period by
explicit source qualification. The current profile supports incomplete
instrument-hour observations only. It does not reconstruct complete utilisation,
infer idle time, convert units, allocate uncertainty probabilistically, or validate
source assertions. The package remains unpublished and has no chosen project
licence; production release, real provider migration and qualified bundle
publication remain open.

After this ownership reconciliation, future lanes can remain nonoverlapping:

| Lane | Owner boundary and next evidence |
| --- | --- |
| Shared contract and bundle qualification | Dapane core-contract/Python tracks; source-qualified fixtures and review of equipment/period assumptions. |
| Genomics recipes and economic preparation | Genomics provider owner; independently reviewed device, contract, repeat/failure and recurrent-cost preparation. No second allocator. |
| Bundle presentation and workflow | CareOps owner; consume qualified Dapane versions, display null/unallocated amounts and keep calculation in Dapane. No CareOps changes are made here. |
| Conditional offline security | Existing PR #5/infrastructure owner; retain its actual runner/image/model qualification gates. |

These lanes are proposed boundaries, not claims that new owners have accepted
work. No deployment, library archival, private-data import or economic-method
validation is implied by this increment.
