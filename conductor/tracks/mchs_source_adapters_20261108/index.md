# MCHS activity and quotation-source adapters

Track: `mchs_source_adapters_20261108`

Status: in_progress

Connect classified hospital activity and versioned quotation sources without
conflating tariffs, funding, resource cost and actual payment.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Pinned provider contracts](contracts.md)
- [Candidate package](../../../adapters/mchs_sources/README.md)
- [Verification and limitations](verification.md)
- [Implementation review](review.md)
- [Exact-source handoff](handoff.md)
- [Shared-change requests](shared-change-requests.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-05, RQ-01, RQ-03.

Capability status: source candidate with synthetic transport tests. An earlier
24-test working version passed; the recovered final source, added review fixes
and 34-test suite remain unexecuted after the execution environment became
unavailable. M1.3/M2 acceptance and installed-package qualification remain open.
M3 live-provider migration is outside this bounded lane. The integrator owns the
matching central registry update.
