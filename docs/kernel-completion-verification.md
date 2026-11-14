# Rust kernel completion qualification

Track: [rust_kernel_20261108](../conductor/tracks/rust_kernel_20261108/index.md).
Status: implementation checkpoint; final review and hosted acceptance pending.

## Source and boundaries

Starting main: `d7063cecc26abe96a3f28fca575b99b450241430`.
Recovered source checkpoint: `7a816a79c4129f3ca1f6064e7dff0c1d6afa10df`.
Only the existing kernel track is being completed. Core-contract PR #9 owns
immutable run bundles and presegmented references; provider, release and
conditional security work retain their owners.

## Observed local checks before execution-environment loss

The local pinned Rust 1.99.1 candidate passed `cargo test --locked`:
6 prior CLI + 4 interval CLI + 9 capacity + 25 prior evaluation + 24 interval core
tests, **68 total**. The capacity suite verified the five original 0.1 fixture
digests unchanged. The new tests include 27 independent rate-subdivision cases.

A detached unchanged baseline with the new tests returned 22 failing/2 passing
core interval tests and 3 failing/1 passing CLI interval tests, demonstrating
missing interval support. These are historical observations, not test results
for a reconstructed commit.

The interval verifier passed 3 independent exact results, 7 schema negatives,
canonical digests, replay/order invariance, parent rounding/pool conservation and
5 semantic rejections using the local debug CLI. The dependency checker passed
an offline comparison of 36 locked package metadata records and a 27-package
native closure; 19 checker tests and its Ruff checks passed.

## Recovery and remaining qualification

The execution environment became unavailable before final lint, installed-wheel
acceptance and independent implementation review. Source, tests and contract
artefacts were recovered through the repository API. Recovered formatting and
bytes must be checked anew; earlier local results do not qualify the published
head. Existing Runtime CI plus the dedicated kernel job are the acceptance
runtime for the recovered change.

Before archival: pass all relevant workflows at the final source, record review
findings/fixes, verify old 0.1/0.2 contracts, independent 0.3 fixtures, strict
minimal build, clean CLI install, CPython 3.12–3.15 installed wheels, dependency
qualification and bounded CPU observations. No completion, archive or release
claim is made by this checkpoint.

## Scientific and publication limits

The only new exposure method is explicitly declared uniform calendar days.
Synthetic arithmetic is computational evidence, not empirical method validation.
Unknown instrument use/availability remains explicit under profile 0.2 semantics.
No real provider, capital model, FX/escalation method or optional IO is qualified.

Dependency inventory verification does not select the Dapane project licence.
Release L1.2/L1.3 retain licensing, redistribution notices, registry identity and
publication compatibility; all packages retain `publish = false`.
