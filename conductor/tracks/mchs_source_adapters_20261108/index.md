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
- [Owner quality repair and current evidence boundary](owner-quality-20261115.md)
- [Exact-source handoff](handoff.md)
- [Shared-change requests](shared-change-requests.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-05, RQ-01, RQ-03.

Capability status: synthetic source candidate pending integrator acceptance.
The received head `8281042676c1d9cafab69e9c57cdfd064a9a5adf` passed 34 installed
tests and default-native smoke; lint/format failures remained. The
[bounded quality repair](owner-quality-20261115.md) preserves those historical
outcomes and identifies the corrected source. Its later exact-head qualification
is recorded on PR #25. M1.3/M2 acceptance and M3 provider qualification remain
separate. The integrator has supplied the central registry and standalone CI.
