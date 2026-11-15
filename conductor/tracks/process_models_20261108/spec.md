# Observed events, Petri nets and BPMN adapters

## Outcome and users

Produce resource-use records from observed or explicitly executed process models while keeping resource execution, discovery and monetary valuation independently owned.

This is the full acceptance specification. The first bounded profile is implemented; [runtime evidence](../../../docs/runtime-verification.md) records its scope. Unmet criteria below remain open.

## Scope and requirements

Owning requirements: **RQ-10, RQ-01, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Qualify observed events, XES and object-centric OCEL 2.0 before bounded PNML/Petri-net and BPMN integration.
- Reuse rust4pm and existing process tools through optional adapters.
- Consume Kairos usage events when its provider contract is qualified; leave healthcare process definitions in CareOps-Sim or domain packages.

## Deliverables

- Versioned event/object-to-resource-use mapping and supported-format matrix.
- A bounded PNML/Petri-net execution mapping and a named BPMN 2.0 subset.
- Independent branching, parallelism, batch, rework, cancellation and censored-interval fixtures.

## Prerequisites and interfaces

Local track dependencies:

- [rust_kernel_20261108](../rust_kernel_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/rust4pm: pin and qualify actual XES/OCEL/PNML support and licence terms.
- edithatogo/kairos: Track 114 or its successor must supply a qualified neutral resource-execution contract.
- edithatogo/careops-sim: healthcare process models remain provider-owned.
- OMG BPMN/PNML and optional PM4Py: supported semantics and licence obligations must be assessed for the selected adapter.

## Acceptance criteria

1. Infant/specimen/assay/batch object relationships survive observed-event import without forcing one flat independent case per event.
2. Each advertised Petri/BPMN construct has explicit timing, marking/branching and resource semantics; unsupported elements fail visibly.
3. Transfers, occupancy and consumption remain distinguishable; shared staff or batch use is not charged multiple times by trace duplication.
4. Changing only a quotation release leaves process execution and resource-use identities unchanged.
5. Kairos remains independent of Dapane; app-level feedback is explicit when prices affect behaviour.
6. Selected dependency versions/licences and supported subsets are recorded; an imported diagram is not advertised as a general BPMN simulator.

## Risks and constraints

Flattened event logs can duplicate shared costs; notation conversion can silently erase concurrency or timing. PM4Py optional use does not remove its AGPL/commercial obligations merely through a subprocess.

## Migration and rollback

Keep versioned event imports and static resource recipes available. Pin process-model/provider releases and preserve execution traces used by historical results.

## Open implementation decisions

Start with a deliberately bounded process profile. A real need and explicit cases must precede a broader BPMN claim or a new process execution engine.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.

## Authorised bounded X1 fallback — 15 November 2026

When dependency qualification blocks native execution, implement independent
contracts and synthetic raw fixtures in a dedicated namespace. Preserve the full
acceptance specification above. Fallback work does not complete native import,
process execution or provider integration.

The bounded contract specifies stable source identity, already-decoded UTC
instants, explicit event pairing, immutable source revisions, correction
rejection, observed/assumed/simulated basis, consumption/occupancy/transfer and
all censoring states. Qualified context does not multiply use. Quantities are
explicit; missing/censored use blocks the complete observed selection. No
duration, price, allocation or exposure is inferred.

The native model/source remains authoritative for typed attributes, history,
qualifiers and unprojected data. The costing projection is not a replacement
OCEL implementation. Full schema/round-trip, unknown native data, duplicate
members, resource limits and XML safety require the selected qualified Rust4PM
revision. Final source verification is additionally pending after environment
loss and reconstruction; see [verification](verification.md).

Shared schema/core/CLI/Python and root Cargo/CI/registry changes are
[integrator requests](integration-requests.md). Accepted per-generated-segment
half-even monetary semantics remain unchanged.
