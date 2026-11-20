# Observed events, Petri nets and BPMN adapters

Track: `process_models_20261108`

Status: archived

Produce resource-use records from observed or explicitly executed process models while keeping resource execution, discovery and monetary valuation independently owned.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-10, RQ-01, RQ-03.

Qualified scope includes bounded raw XES 2.0, OCEL 2.0 JSON, PNML and BPMN
fixtures and the independently reviewed Kairos staged occupancy provider.
[Native import and staged Kairos usage acceptance](native-and-kairos-review.md)

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

The original lane owned the typed X1 fallback. Its source and handoff above
remain the historical checkpoint. The integration checkout added the raw
profiles and the pinned Kairos consumer.
