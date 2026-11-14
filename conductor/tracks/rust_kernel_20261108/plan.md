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

Work resumes from main `d7063cecc26abe96a3f28fca575b99b450241430` on
`feat/rust-kernel-completion-20261115`. The existing core-contract PR #9 owns
run-bundle lifecycle and presegmented reference acceptance; this increment owns
automatic interval valuation, its native/CLI qualification and this track.

- [~] K2.1/K2.4: qualify a separate 0.3 interval profile with explicit uniform
  calendar-day exposure, exact quote-boundary segments, parent-line rounding,
  component accounting, deterministic provenance and independent negative cases.
- [~] K1.1: enforce pinned toolchain, inventory and minimal dependency checks for
  the unpublished candidate. Reconcile the duplicated project-licence decision
  with the existing release-track L1.2/L1.3 ownership; publication stays disabled.
- [ ] Complete independent review, apply fixes, verify the final source, and
  archive in place with evidence and stable links after acceptance passes.

The pre-publication checkout passed 68 native tests and the independent 0.3
fixture validator. A clean baseline with the new tests failed 22 core and three
CLI assertions for missing interval support. The execution environment became
unavailable before the final lint, installed-wheel and review pass. The source
was recovered through the repository API and must be qualified on its exact
published commit; the earlier local test result does not qualify a reconstructed
commit. No archive or completion claim is made at this checkpoint.

Native evidence is in [runtime verification](../../../docs/runtime-verification.md). K1.1 retains the unresolved project-licence/release qualification despite pinned dependencies. K2.1/K2.4 retain automatic interval segmentation; callers currently supply explicitly segmented dated quantities. K3.2 is deferred because all five first reference consumers use exact JSON and require no Arrow/Parquet IO. The 5,000-row/recipient measurements are bounded observations, not a scalability or acceleration claim.

Full scope and observed commands/results are recorded in [runtime verification](../../../docs/runtime-verification.md). This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
