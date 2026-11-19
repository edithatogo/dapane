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

Capability status: independent X1 contracts and X2 bounded PNML/BPMN adapters
are implemented and source-verified on synthetic fixtures; raw XES/OCEL imports
(`X1.2`) remain blocked on `edithatogo/mailweft#4`, and Kairos provider
integration (`X3.1`–`X3.3`) remains pending on `edithatogo/kairos` Track 114.
Historical [runtime evidence](../../../docs/runtime-verification.md) remains
limited to the existing core context. Full track acceptance remains open.

## X2 bounded PNML and BPMN adapters — 19 November 2026

- [X2 adapter package](../../../adapters/process_models/README.md) (`adapters/process_models/`, zero external crates, Apache-2.0)
- [X2 CI workflow](../../../.github/workflows/process-models.yml)
- [X2 verification record](x2-verification.md) and [X2 machine receipt](x2-verification.json)

Covers `X2.1`–`X2.4`: `pnml-bounded-v1`, `bpmn-core-acyclic-v1`, and
`bpmn-extended-rework-subprocess-v1`, with explicit transfer/occupancy/consumption
separation, shared-batch non-duplication, and Dapane `0.1` valuation parity
across independent quotation releases.

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
