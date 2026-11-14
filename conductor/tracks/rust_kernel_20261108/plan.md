# Implementation plan: Minimal Rust valuation kernel and CLI

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Workspace and type boundary

- [~] K1.1 Select and document tested stable versions, Rust MSRV and dependency/licence compatibility; keep preview toolchains in an optional canary.
- [x] K1.2 Create the core and CLI crates; keep wrapper, IO and accelerator dependencies outside the scalar core.
- [x] K1.3 Implement typed input construction and serialization; verify exact round trips and minimal-feature build behaviour.

## Phase 2 — Valuation and allocation

- [~] K2.1 Implement supported quotation application, rate-boundary segmentation and explicit decimal/rational conversion.
- [x] K2.2 Implement component ledgers, pool allocation, residual handling and configured rounding order.
- [x] K2.3 Reject incompatible valuation views, duplicate source use, missing quotes, unsupported precision and arithmetic overflow.
- [~] K2.4 Run independent reference cases and focused property tests for conservation, ordering and segmentation invariants.

## Phase 3 — CLI and execution qualification

- [x] K3.1 Implement versioned request/result bundles, digests, source pinning and explicit completeness/error output.
- [-] K3.2 If a selected first consumer requires Arrow/Parquet IO, qualify it behind a separate feature/crate and demonstrate exact numeric preservation. Otherwise record its deferral to a later IO capability with a rationale; scalar kernel/CLI and core/Python qualification must not wait for optional IO.
- [x] K3.3 Measure CPU time/memory for bounded valuation and allocation workloads; keep acceleration unsupported until it earns separate evidence.
- [x] K3.4 Run formatting, lint, native tests, clean CLI installation and supported-feature checks; record commands, versions, limits and rollback evidence.

## Evidence record

### Completion execution — 15 November 2026

Reconciled main `d7063cecc26abe96a3f28fca575b99b450241430`. Core-contract PR #9
owns immutable bundle/lifecycle acceptance; this track owns interval segmentation
and kernel qualification. The separate setup and conditional security work are
outside this implementation. Existing checkouts and local work are preserved.

- [~] K4.1 Add independent interval references and negative/invariant tests, then
  implement an explicitly versioned Rust/CLI calendar-day segmentation contract.
  Preserve point-contract 0.1/0.2 semantics, source identities and historical digests.
- [~] K4.2 Verify the pinned compiler/MSRV, locked dependency inventory and minimal
  core/CLI graph; retain the project-licence decision in release consolidation.
- [~] K4.3 Review independently, fix findings, verify the final native/installed
  artifact head and reconcile prerequisite PR #9.
- [ ] K4.4 Record qualification and limitations, synchronise context and archive
  this track in place with all evidence and dependency links retained.

Expected interval reference: one hour explicitly distributed uniformly over
`[2026-01-31, 2026-02-03)` gives `1/3 × 90 + 2/3 × 120 = 110`.
The interval method rounds each generated line half-even before summation; it
makes no arbitrary splitting invariance claim for rounded values. Coverage,
component/parent-use identity, knowledge cutoff, expansion bounds and source
lineage must fail closed. The local workspace disconnected after a local test
commit; the GitHub connector and existing hosted workflows retain and qualify
this work. No local Rust execution is claimed.

Native evidence is in [runtime verification](../../../docs/runtime-verification.md). K1.1 retains the unresolved project-licence/release qualification despite pinned dependencies. K2.1/K2.4 retain automatic interval segmentation; callers currently supply explicitly segmented dated quantities. K3.2 is deferred because all five first reference consumers use exact JSON and require no Arrow/Parquet IO. The 5,000-row/recipient measurements are bounded observations, not a scalability or acceleration claim.

Full scope and observed commands/results are recorded in [runtime verification](../../../docs/runtime-verification.md). This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
