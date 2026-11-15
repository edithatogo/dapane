# Implementation plan: Minimal Rust valuation kernel and CLI

Status: archived

Completed and archived in place on **15 November 2026** (Australia/Brisbane).
The original specification, task identities and optional-IO decision are retained.
`[x]` means verified complete; `[-]` means intentionally omitted with rationale.

## Phase 1 — Workspace and type boundary

- [x] K1.1 Select and document tested stable versions, Rust MSRV and dependency/licence compatibility; keep preview toolchains in an optional canary.
- [x] K1.2 Create the core and CLI crates; keep wrapper, IO and accelerator dependencies outside the scalar core.
- [x] K1.3 Implement typed input construction and serialization; verify exact round trips and minimal-feature build behaviour.

## Phase 2 — Valuation and allocation

- [x] K2.1 Implement supported quotation application, rate-boundary segmentation and explicit decimal/rational conversion.
- [x] K2.2 Implement component ledgers, pool allocation, residual handling and configured rounding order.
- [x] K2.3 Reject incompatible valuation views, duplicate source use, missing quotes, unsupported precision and arithmetic overflow.
- [x] K2.4 Run independent reference cases and focused property tests for conservation, ordering and segmentation invariants.

## Phase 3 — CLI and execution qualification

- [x] K3.1 Implement versioned request/result bundles, digests, source pinning and explicit completeness/error output.
- [-] K3.2 If a selected first consumer requires Arrow/Parquet IO, qualify it behind a separate feature/crate and demonstrate exact numeric preservation. Otherwise record its deferral to a later IO capability with a rationale; scalar kernel/CLI and core/Python qualification must not wait for optional IO.
- [x] K3.3 Measure CPU time/memory for bounded valuation and allocation workloads; keep acceleration unsupported until it earns separate evidence.
- [x] K3.4 Run formatting, lint, native tests, clean CLI installation and supported-feature checks; record commands, versions, limits and rollback evidence.

## Completion execution — 15 November 2026

- [x] K4.1 Add independent interval references and negative/invariant tests, then implement an explicitly versioned Rust/CLI calendar-day segmentation contract. Preserve point-contract 0.1/0.2 semantics, source identities and historical digests.
- [x] K4.2 Verify the pinned compiler/MSRV, locked dependency inventory and minimal core/CLI graph; retain the project-licence decision in release consolidation.
- [x] K4.3 Review independently, fix findings, verify the final native/installed artifact source and reconcile prerequisite PR #9.
- [x] K4.4 Record qualification and limitations, synchronise context and archive this track in place with all evidence and dependency links retained.

## Acceptance evidence and retained decisions

The [verification record](verification.md) binds the corrected and integrated
source trees to 62 passing native tests, independently installed CLI checks,
11 dependency-tooling regressions, full fetched-dependency qualification and
133 installed-wheel tests on each of CPython 3.12, 3.13, 3.14 and 3.15.
The [review](review.md) records resource-amplification, lineage-checker and
compiler findings and their fixes. Hosted Actions observations remain separate
from the actual local checks; queued jobs are never counted as passing.

K1.1 is complete for the tested development boundary: Rust 1.99.1, the unchanged
36-package registry inventory and compatible fetched licence/MSRV declarations.
Project-licence selection and distribution/publication obligations retain their
pre-existing release/consolidation owner under [ADR-013](../../decisions.md).
Every package retains `publish = false`.

K2.1/K2.4 now include explicit `uniform_calendar_day` interval exposure, pinned
rate selection and exact segmentation. The independent reference is
`1/3 × 90 + 2/3 × 120 = 110`. Per-segment half-even rounding is explicit and
separately versioned; arbitrary splitting invariance is not promised.

K3.2 remains intentionally deferred: the five selected first reference consumers
use exact JSON and require no Arrow/Parquet IO. K3.3 retains three repetitions of
5,000-row valuation and allocation with exact-result/conservation checks; this
is a bounded observation and does not qualify acceleration or scalability.
Compatibility is demonstrated by unchanged original fixture digests and exact
replay of the expanded scalar request.

Core-contract PR #9 is integrated at `224cf91dbcf513feaa022b2cf5aa310a965472ce`;
the expanded installed suite includes its bundle and archive-validator tests.
Its separate archival and unrelated setup/provider/security work are preserved.
This kernel's stable path, dependencies and original specification remain intact.

The [metadata](metadata.json), [index](index.md), [registry](../../tracks.md) and
[archive entry](../../archive/README.md) record the same disposition.
