# Implementation plan: Observed events, Petri nets and BPMN adapters

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Observed records

- [ ] X1.1 Specify event/object identity, timestamps, correction rules and mapping of observed/assumed/simulated usage.
- [ ] X1.2 Qualify XES and OCEL 2.0 import using a pinned rust4pm/provider revision; preserve many-to-many batch relationships.
- [ ] X1.3 Verify duplicate, incomplete, reordered and censored event cases against independent resource-use expectations.

## Phase 2 — Bounded process models

- [ ] X2.1 Specify a PNML/Petri-net profile with initial/final markings, firing multiplicity, timing and resource assumptions.
- [ ] X2.2 Qualify a named BPMN subset covering selected start/end events, tasks and exclusive/parallel gateways; reject unsupported constructs.
- [ ] X2.3 Add loops, richer gateways/events and subprocesses only through separate supported-subset cases.
- [ ] X2.4 Verify sequential, alternative, concurrent, rework, shared-resource and cancelled paths; record limitations and source licences.

## Phase 3 — Provider integration

- [ ] X3.1 Consume Kairos resource-execution events after its provider contract is qualified; keep healthcare recipes in their domain owner.
- [ ] X3.2 Attach recipes to executed activities and apply quotations in a separate step; retain model and execution version identities.
- [ ] X3.3 Verify that price-only revaluation changes monetary results without rerunning execution; document rollback to observed/static recipes.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
