# Release assurance and conditional consolidation

Track: `release_consolidation_20261108`

Status: blocked

The owner selected GitHub Releases under `edithatogo/dapane` for the
`v0.1.0` prerelease on candidate `d02095d`. PyPI and crates.io are deferred.
Hosted release assurance, the installed target matrix and five signed artifact
subjects passed verification. The central offline-security scan for the
candidate is queued with no runner assigned. [Decision and evidence](evidence.md#github-prerelease-selection-21-november-2026)

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

The remaining work is the exact-source offline scan, GitHub prerelease and
readback, then the authorised track archival.

The [latest control review](evidence.md#publication-control-review--20-november-2026)
records the exact-source security requirement in candidate receipts and the
current runner evidence.
