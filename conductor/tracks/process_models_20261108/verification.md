# X1 verification and recovery record

## Current source verification

The coordinator replayed the recovered source at
`63e3f8368510641513b5fd84ae3074bb80e79c6f`: 37 Rust tests and 12 fixture audits
passed, with two formatting checks failing. The [owner follow-up](owner-quality-20261115.md)
records the formatting-only correction and successful exact-source checks at
`0621fecedd41bc99957d0042e32338e780f42dd2`. Native import remains blocked.
The recovery checkpoint below is historical; its missing replay and CI coverage
were subsequently supplied. Its native qualification limits still apply.

## Historical qualification state before coordinator intake

**The recovered published snapshot is not execution-qualified.** A local candidate
was implemented and tested, then the execution environment became unavailable
before a commit could be made. The work was reconstructed through GitHub under
the integrator's reserved `adapters/observed_events/` path. Source and test layout
were reconstructed from the authored work; raw fixtures were regenerated and
their manifest digests recalculated. A byte-for-byte comparison with the lost
checkout is unavailable. No historical local result is attributed to a later
commit SHA.

Native XES/OCEL execution was blocked before that outage and remains blocked.
No alternate runtime parser, Rust4PM patch or advisory suppression was introduced.

## Executed before environment loss

Base main: `e34f87c9df39a2132fecee142431cdeefb732471`.
Local namespace: `adapters/observed-import-contracts/`.
Platform: Linux 6.18.57 x86_64, glibc 2.41.
Rust: 1.99.1, compiler commit `58cf8f9c35b355199727627d07ae34a4e2846d67`.
Cargo: 1.99.1 (`5f94df478`).
Python: 3.12.14. Ruff: 0.17.4.

The commands below were actually run in that local candidate. Their outputs were
observed in the authoring session, but no immutable local source commit or
retained filesystem log was available after the outage.

| Command | Observed result | Scope |
| --- | --- | --- |
| `cargo test --offline --manifest-path adapters/observed-import-contracts/Cargo.toml` | Initially failed with Rust E0502 in a test's nested mutable/immutable borrow | Fixed by cloning the duplicate edge before push |
| `cargo test --locked --offline --manifest-path adapters/observed-import-contracts/Cargo.toml` | 37 integration tests passed; unit/doc suites empty | Typed contracts, including 24 event permutations |
| `cargo fmt --manifest-path adapters/observed-import-contracts/Cargo.toml` | Completed successfully | Formatting applied, not a final-head check |
| `cargo clippy --locked --offline --all-targets --manifest-path adapters/observed-import-contracts/Cargo.toml -- -D warnings` | Passed | Local native package only |
| `python3 -m unittest discover -s adapters/observed-import-contracts/tests -p 'test_fixtures.py' -v` | 12 passed | Fixed synthetic fixture audit; no runtime import |
| `ruff check adapters/observed-import-contracts/tests/test_fixtures.py` | Initial import/UTC-style findings, then passed after fixes | Local Python fixture auditor |
| `ruff format --check adapters/observed-import-contracts/tests/test_fixtures.py` | Passed after formatting | Local Python fixture auditor |
| `python3 scripts/validate_conductor.py` | Passed: 14 tracks, 12 requirements, 153 tasks, 535 links | Local documentation consistency |
| `python3 -m unittest discover -s tests -p 'test_conductor_validation.py' -v` | 12 passed | Existing lifecycle regression suite |
| `cargo metadata --manifest-path adapters/observed-import-contracts/Cargo.toml --locked --offline --format-version 1 --no-deps` | One standalone package, empty dependency list | No root workspace adoption |
| `git diff --check` | Passed for then-tracked edits | New untracked files were not covered by that command |

The subsequent staging/scope-guard command did **not** execute: the execution
server disconnected during process creation. The next minimal read also returned
no usable execution environment. No successful local commit/push is claimed.

## Retained contract cases

The recovered Rust suite contains 37 cases covering stable identity, exact and
conflicting duplicates, all 24 permutations of four events, missing and dangling
anchors, qualifier preservation, many-to-many batch context, explicit quantities,
all four censoring states, missing versus zero, transfer/assumed/simulated labels,
correction rejection, time bounds, record limits and failure atomicity.

The 12 fixture-audit cases cover 13 raw files: XES and OCEL baseline/reordered/
duplicate-ID/missing-time/right-censored/offset-equivalent variants, plus an OCEL
duplicate-JSON-member input. The OCEL fixture includes all five native attribute
types and timed batch-state history. The source-byte manifest marks every native
decoder execution false.

## Unexecuted or unresolved at the recovery checkpoint

- Recovered exact-head Rust compilation/tests, rustfmt, Clippy, Python fixture
  tests and Ruff. Existing root workflows do not discover this package.
- Native Rust4PM XES/OCEL parsing, full upstream schemas, native round-trips,
  malformed XML/JSON/resource-limit qualification and Windows/macOS checks.
- A fresh advisory database/unsuppressed dependency qualification for the selected
  Rust4PM graph. This lane inspected published evidence; it did not run a new scan.
- Shared-core mapping, timestamp/date or source-schema changes, installed delivery,
  release qualification and any Kairos/PNML/BPMN execution.

See [integration requests](integration-requests.md), particularly X1-IR-00 through
X1-IR-04. The PR must remain draft while recovered-source verification is missing.
An ordinary green root workflow cannot be relabelled as a lane test pass.
