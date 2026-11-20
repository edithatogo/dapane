# R and Julia bindings

Track: `polyglot_bindings_20261108`

Status: blocked

Direct R calls and a versioned C ABI candidate wrap the existing Rust kernel.
The integrator has executed installed R and native C acceptance and accepted this
namespace, registry state and standalone CI. The bounded owner quality correction
preserves strict lint gates and Python behavior. Its exact source, actual checks
and remaining requirements are recorded below; total ABI or release qualification
is not claimed. A local Julia caller exercises the C ABI, and a staged install on this host matched the 24 prepared cases. JLL and release qualification remain open.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Current owner quality and acceptance record](owner-quality-20261115.md)
- [Machine-readable commands and review](owner-quality-20261115.json)
- [Executed and pending evidence](verification.md)
- [Exact-source integrator handoff](handoff.md)
- [Binding source and reproduction](../../../bindings/polyglot/README.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-09, RQ-02.

The [macOS qualification](verification.md#macos-host-and-abi-review) covers R 4.6.2, instrumented C and ABI v1 source review. The Julia staged package and existing Linux checks retain their own scope. Selection of public release surfaces remains open.
Publication is disabled. Shared changes remain with the sole integrator.
