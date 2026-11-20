# R and Julia bindings

Track: `polyglot_bindings_20261108`

Status: archived

The direct R wrapper and the Julia package call the same Rust kernel. The
selected macOS arm64 local packages independently passed fresh installs and
24 shared cases each. Instrumented C and standalone Linux checks retain their
recorded platform scope.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Distribution review and archive evidence](distribution-review.md)
- [Current owner quality and acceptance record](owner-quality-20261115.md)
- [Machine-readable commands and review](owner-quality-20261115.json)
- [Executed and pending evidence](verification.md)
- [Exact-source integrator handoff](handoff.md)
- [Binding source and reproduction](../../../bindings/polyglot/README.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-09, RQ-02.

The [macOS qualification](verification.md#macos-host-and-abi-review) covers
R 4.6.2, instrumented C and ABI v1 source review. Registry publication and any
future JLL selection belong to [release assurance](../release_consolidation_20261108/index.md).
