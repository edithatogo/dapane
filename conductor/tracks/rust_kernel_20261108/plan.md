# Implementation plan: Minimal Rust valuation kernel and CLI

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Workspace and type boundary

- [ ] K1.1 Select and document tested stable versions, Rust MSRV and dependency/licence compatibility; keep preview toolchains in an optional canary.
- [ ] K1.2 Create the core and CLI crates; keep wrapper, IO and accelerator dependencies outside the scalar core.
- [ ] K1.3 Implement typed input construction and serialization; verify exact round trips and minimal-feature build behaviour.

## Phase 2 — Valuation and allocation

- [ ] K2.1 Implement supported quotation application, rate-boundary segmentation and explicit decimal/rational conversion.
- [ ] K2.2 Implement component ledgers, pool allocation, residual handling and configured rounding order.
- [ ] K2.3 Reject incompatible valuation views, duplicate source use, missing quotes, unsupported precision and arithmetic overflow.
- [ ] K2.4 Run independent reference cases and focused property tests for conservation, ordering and segmentation invariants.

## Phase 3 — CLI and execution qualification

- [ ] K3.1 Implement versioned request/result bundles, digests, source pinning and explicit completeness/error output.
- [ ] K3.2 If a selected first consumer requires Arrow/Parquet IO, qualify it behind a separate feature/crate and demonstrate exact numeric preservation. Otherwise record its deferral to a later IO capability with a rationale; scalar kernel/CLI and core/Python qualification must not wait for optional IO.
- [ ] K3.3 Measure CPU time/memory for bounded valuation and allocation workloads; keep acceleration unsupported until it earns separate evidence.
- [ ] K3.4 Run formatting, lint, native tests, clean CLI installation and supported-feature checks; record commands, versions, limits and rollback evidence.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
