# R and Julia bindings

Track: `polyglot_bindings_20261108`

Status: blocked

Direct R calls and a proposed versioned C ABI wrap the existing Rust kernel.
Installed R tests passed before an execution-environment interruption. The
published source was reconstructed from the submitted edits and needs exact-head
qualification. The C consumer is unexecuted; Julia remains gated on its success.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Executed and pending evidence](verification.md)
- [Binding source and reproduction](../../../bindings/polyglot/README.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-09, RQ-02.

Capability status: implementation candidates only; no final-source host, ABI,
Julia, cross-platform or release qualification is claimed. Publication is disabled.
Shared registry/CI/path-map changes belong to the existing sole integrator.
