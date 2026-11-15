# Observed events, Petri nets and BPMN adapters

Track: `process_models_20261108`

Status: in_progress

Produce resource-use records from observed or explicitly executed process models while keeping resource execution, discovery and monetary valuation independently owned.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-10, RQ-01, RQ-03.

Capability status: independent X1 contracts implemented and source-verified;
raw XES/OCEL imports remain blocked on dependency qualification. Verification
is bound to the commits in the owner follow-up, not to an arbitrary later head.
Historical [runtime evidence](../../../docs/runtime-verification.md) remains
limited to the existing core context. Full track acceptance remains open.

## X1 lane — 15 November 2026

- [Independent contract package](../../../adapters/observed_events/README.md)
- [Verification and recovery record](verification.md)
- [Author review and open findings](review.md)
- [Dependency inspection](dependency-inspection.json)
- [Integrator requests](integration-requests.md)
- [Exact-source handoff](handoff.md) and [machine-readable receipt](handoff.json)
- [Owner formatting follow-up](owner-quality-20261115.md) and [executed command receipt](owner-quality-20261115.json)

Owner: Dapane — Observed XES and OCEL imports. This lane owns this track and
`adapters/observed_events/`. The sole integrator remains Dapane — Release
assurance and consolidation, chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.
X1.2 and native-import X1.3 acceptance remain open. X2 and X3 are untouched.
No additional worker, upstream remediation or Kairos execution is introduced.
