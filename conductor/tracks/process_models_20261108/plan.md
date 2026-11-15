# Implementation plan: Observed events, Petri nets and BPMN adapters

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Owner formatting follow-up — 15 November 2026

- [~] Correct the three owner-file formatting findings from hosted run 43686522588
  at `63e3f8368510641513b5fd84ae3074bb80e79c6f`, repeat the standalone checks,
  and hand exact-source evidence to PR #20. Preserve coordinator commits and
  shared CI/registry; native import qualification remains blocked.

## Phase 1 — Observed records

- [x] X1.1 Specify event/object identity, timestamps, correction rules and mapping of observed/assumed/simulated usage.
- [!] X1.2 Qualify XES and OCEL 2.0 import using a pinned rust4pm/provider revision; preserve many-to-many batch relationships.
- [~] X1.3 Verify duplicate, incomplete, reordered and censored event cases against independent resource-use expectations.

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

The [event/process/object model](../../../docs/event-process-object-model.md) and [provider review](../../../docs/provider-boundaries.md) establish the independent-core boundary. Contract0.1 validates context without executing processes or deriving resource duration. That historical checkpoint left X1.1 partial. The 15 November contract specifies explicit timestamps, basis, correction rejection and censoring. X1.2 remains blocked; X1.3 retains native-import and recovered-source verification work. X3.1 and all X2 work remain pending; the earlier Kairos observation is not requalified by this lane.

Historical core-context scope and commands remain in [runtime verification](../../../docs/runtime-verification.md). The new [verification record](verification.md) separates local pre-outage execution from the recovered, unverified source. This track remains in progress.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.

## X1 lane — 15 November 2026

Dylan authorised X1 in ordinary Pro ChatGPT, owning only this track and a
dedicated new namespace. Main was pinned at
`e34f87c9df39a2132fecee142431cdeefb732471`. Initial live PR/track inspection found
no competing X1 owner. PR #17 remained the release owner's work. Later
[coordination PR #20](https://github.com/edithatogo/dapane/pull/20) reserved
`adapters/observed_events/`; recovery uses that path. No additional worker was
created and no shared/root/upstream file was edited.

Mailweft main `14b3de557a7654708f6066f70f4d8bc1e3d1e564` locks
`process_mining 0.6.2` and `quick-xml 0.37.5`; its issue #4 is open. This lane
uses the authorised independent-contract/fixture fallback. There is no raw
decoder, competing dependency patch or advisory suppression.

### Bounded acceptance

| Task | State and evidence |
| --- | --- |
| X1.1 | Specification complete for the typed contract: stable identity, explicit instants/pairs, correction rejection, observed/assumed/simulated basis, qualified relationships and censoring. No full correction protocol or native import claim. |
| X1.2 | Blocked on qualified Rust4PM and native input evidence; no native parser/schema/round-trip or XML exposure pass. |
| X1.3 | Partial: local candidate passed 37 Rust contract and 12 fixture-audit cases. The recovered exact source needs rerun, and native-import cases still need a qualified decoder. |

The local execution environment failed before commit/push. Source, tests and
fixtures were reconstructed through GitHub. These bytes cannot inherit the
earlier local results. [Review](review.md) keeps that blocking finding explicit;
[integration requests](integration-requests.md) identify the exact rerun/adoption
work. The PR remains draft. X2 and X3 remain outside this lane.

Track state stays `in_progress`, matching the untouched registry. Root cargo/CI
does not discover the separate package; adding that coverage is integrator-owned.
