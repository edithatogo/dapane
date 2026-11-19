# Release assurance and conditional consolidation

Track: `release_consolidation_20261108`

Status: blocked

Setup, core contracts, the Rust kernel and Python/two-consumer archives are
incorporated on main. Their existing owners' records supply the bounded provider
qualification. Hosted release assurance passed on `main` at source `0658d94`
(after PR #17 `f9e8fd7` and PR #22 `0658d94` merged), including the complete
dependency/Rust standard-library notices, exact-artifact provider verification
and trusted-main signed provenance (`attest` job `132994080532`, verified
offline across 20 files / 14 distinct digests). Publication stays disabled
pending channel/account choices. The central offline security run on `main`
(`43769725442`) timed out after 24 hours in queue with no runner assigned and 0
steps executed. Optional language, domain and deployment tracks do not gate this
bounded first release.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Execution and review evidence](evidence.md)
- [Post-merge main qualification and attestation (19 Nov 2026)](../../../docs/release-qualification-2026-11-19.md)
- [Exact-source main artifact receipt (0658d94)](../../../docs/release-qualification-0658d94.json)
- [Historical PR #17 handoff and qualification (15 Nov 2026)](../../../docs/release-handoff-2026-11-15.md)
- [Historical PR #17 artifact receipt (5f03f28)](../../../docs/release-qualification-5f03f28.json)
- [Integration, licensing and archive audit](../../../docs/release-integration-2026-11-15.md)
- [Dated local qualification](../../../docs/release-verification-2026-11-15.md)
- [Candidate assurance](../../../docs/release-assurance.md)
- [Supply-chain controls](../../../docs/release-controls.md)
- [Migration and recovery](../../../docs/release-migration.md)
- [Consolidation disposition](../../../docs/release-consolidation.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-12, RQ-04.

Capability status: selected-provider candidate with distribution notices, passed
ordinary hosted checks and signed trusted-main provenance at `0658d94`; central
offline security timed out unexecuted and public release remains disabled. The
user requested archival after review and fixes. Retain this track until its
required acceptance evidence is complete; no external repository archive has been
selected.
