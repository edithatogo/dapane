# Minimal Rust valuation kernel and CLI

Track: `rust_kernel_20261108`

Status: archived

Completed and archived in place on **15 November 2026** (Australia/Brisbane).
The independently usable Rust core and CLI now satisfy this track's bounded
valuation, allocation, interval and qualification acceptance.

- [Retained specification](spec.md)
- [Completed implementation plan](plan.md)
- [Metadata](metadata.json)
- [Qualification and acceptance evidence](verification.md)
- [Independent review and fixes](review.md)
- [Evidence manifest](evidence/manifest.json)
- [Track registry](../../tracks.md)
- [Archive record](../../archive/README.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-01, RQ-02, RQ-03, RQ-12.
Capability status: qualified_native_point_capacity_and_intervals.

The separate [interval contract](../../../docs/interval-contract-v0.1.md) supports
declared uniform calendar-day exposure and pinned rate-boundary segmentation,
with parent/source identity validation and replayable scalar output. Point and
capacity profiles 0.1/0.2 and historical digests remain unchanged. The
[dependency boundary](../../../docs/kernel-dependencies.md) is qualified on
Rust 1.99.1; registry publication remains disabled.

The [verification record](verification.md) contains actual native, installed CLI,
four-interpreter installed-wheel and local privacy/secret evidence. It distinguishes
that execution from queued hosted Actions in [PR #16](https://github.com/edithatogo/dapane/pull/16).
Provider integration, richer exposure/economic methods, optional IO and release
licensing retain their explicit owners and limitations. No other track or
repository is archived by this disposition.
