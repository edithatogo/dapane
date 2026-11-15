# Python delivery with workforce and genomics consumers

Track: `python_two_consumers_20261108`

Status: archived

Completed and archived in place on 15 November 2026. The selected workforce
calculation and manual DNA-extraction labour workflow run through independently
installed Python providers and the same Rust implementation.

- [Specification](spec.md)
- [Completed implementation plan](plan.md)
- [Metadata](metadata.json)
- [Review and remediation](review.md)
- [Provider qualification and exact evidence](../../../docs/python-provider-verification.md)
- [Immutable provider revisions](../../../docs/provider-consumers.lock.json)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-04, RQ-02, RQ-03.

Capability status: installed_workforce_and_manual_extraction_consumers.

The completed scope includes canonical/legacy workforce imports and resources,
a source-selected dated base-pay release, explicit genomic batch attempts and
allocation, native parity, preserved historical entry points and a controlled
rounding comparison. Provider interpreter pins remain 3.15.2 and 3.15.1.

The earlier [runtime evidence](../../../docs/runtime-verification.md) and
[synthetic capacity increment](../../../docs/genomics-capacity-verification.md)
remain as dated records. This archive preserves the original track path, links
and dependencies. Broader assays, empirical validation and release assurance
retain separate scope and gates.
