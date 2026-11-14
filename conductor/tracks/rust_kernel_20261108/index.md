# Minimal Rust valuation kernel and CLI

Track: `rust_kernel_20261108`

Status: in_progress

Implement one authoritative numerical core for exact valuation, component accounting and shared-pool allocation. The native library and CLI must work without a language wrapper, table engine, simulator or cloud account.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-01, RQ-02, RQ-03, RQ-12.

Capability status: implemented_bounded_profiles_0_1_and_0_2. See [runtime evidence](../../../docs/runtime-verification.md); full track acceptance remains open.

The [synthetic capacity increment](../../../docs/genomics-capacity-verification.md) records the separate 0.2 scope and checks.

## Interval completion in progress

The separately versioned [interval contract](../../../docs/interval-contract-v0.1.md)
adds declared calendar-day exposure, pinned rate selection, parent-use/component
checks and replayable native/CLI output. [Dependency qualification](../../../docs/kernel-dependencies.md)
retains Rust 1.99.1 and disabled registry publication. [Review](review.md) records
independent findings and fixes; hosted acceptance is still pending in
[PR #16](https://github.com/edithatogo/dapane/pull/16). The track is not archived
until the prerequisite and exact-head verification are complete.
