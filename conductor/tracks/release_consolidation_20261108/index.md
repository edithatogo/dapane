# Release assurance and conditional consolidation

Track: `release_consolidation_20261108`

Status: blocked

Setup, core contracts, the Rust kernel and Python/two-consumer archives are
incorporated on main. Their existing owners' records supply the bounded provider
qualification. Hosted release assurance passed at source d37575ec. This increment
completes dependency/Rust standard-library notices and connects the existing
provider verifier to the exact release artifacts; the changed source requires
fresh hosted qualification. Publication stays disabled pending channel/account
choices. The central offline security jobs remain queued without a runner.
Optional language, domain and deployment tracks do not gate this bounded first release.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Execution and review evidence](evidence.md)
- [Current handoff, archive incorporation and qualification](../../../docs/release-handoff-2026-11-15.md)
- [Integration, licensing and archive audit](../../../docs/release-integration-2026-11-15.md)
- [Dated local qualification](../../../docs/release-verification-2026-11-15.md)
- [Candidate assurance](../../../docs/release-assurance.md)
- [Supply-chain controls](../../../docs/release-controls.md)
- [Migration and recovery](../../../docs/release-migration.md)
- [Consolidation disposition](../../../docs/release-consolidation.md)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-12, RQ-04.

Capability status: selected-provider candidate with distribution notices, awaiting
fresh hosted qualification and external security execution; public release remains
disabled. The user requested archival
after review and fixes. Retain this track until its required acceptance evidence
is complete; no external repository archive has been selected.
