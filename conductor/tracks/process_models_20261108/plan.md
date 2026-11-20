# Implementation plan: Observed events, Petri nets and BPMN adapters

Status: archived

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Owner formatting follow-up — 15 November 2026

- [x] Correct the three owner-file formatting findings from hosted run 43686522588
  at `63e3f8368510641513b5fd84ae3074bb80e79c6f`. All standalone checks and author
  review passed at `0621fecedd41bc99957d0042e32338e780f42dd2`; see the
  [exact-source receipt and handoff](owner-quality-20261115.md). Coordinator
  commits and shared files were preserved. This checkpoint predated native import.

## Phase 1 — Observed records

- [x] X1.1 Specify event/object identity, timestamps, correction rules and mapping of observed/assumed/simulated usage.
- [x] X1.2 Qualify the supported raw XES 2.0 XML and OCEL 2.0 JSON profiles. The separate adapter locks maintained parser versions, retains original bytes and projects the same many-to-many links.
- [x] X1.3 Execute duplicate, incomplete, reordered, equivalent-offset and censored input cases. The same fixture preserves three explicit uses and the shared half-hour batch.

## Phase 2 — Bounded process models

- [x] X2.1 Specify a PNML/Petri-net profile with initial/final markings, firing multiplicity, timing and resource assumptions.
- [x] X2.2 Qualify a named BPMN subset covering selected start/end events, tasks and exclusive/parallel gateways; reject unsupported constructs.
- [x] X2.3 Add loops, richer gateways/events and subprocesses only through separate supported-subset cases.
- [x] X2.4 Verify sequential, alternative, concurrent, rework, shared-resource and cancelled paths; record limitations and source licences.

## Phase 3 — Provider integration

- [x] X3.1 Consume the immutable Kairos staged usage revision through the public DES runtime. The release contract covers committed staged occupancy.
- [x] X3.2 Bind the explicit domain recipe and carry engine, model, window, lease and causal event identity into the downstream valuation request.
- [x] X3.3 Revalue the same executed use under two quote releases. The replay fixture yields NZD 18.00 and 30.00 with identical usage. The observed and static paths remain available for rollback.

## Review fixes

- [x] Keep native file identity, reject ambiguous JSON record shapes and unknown time offsets, and preserve distinct bounded window IDs and physical units. [Review and executed evidence](native-and-kairos-review.md)

## Evidence record

The [event/process/object model](../../../docs/event-process-object-model.md) and [provider review](../../../docs/provider-boundaries.md) establish the independent-core boundary. Contract0.1 validates context without executing processes or deriving resource duration. That historical checkpoint left X1.1 partial. The 15 November contract specifies explicit timestamps, basis, correction rejection and censoring. The original X1 fallback predated the qualified bounded raw import. On 19 November 2026, [`dapane-process-models`](../../../adapters/process_models/README.md) delivered the bounded X2 PNML (`pnml-bounded-v1`) and BPMN 2.0 (`bpmn-core-acyclic-v1` and `bpmn-extended-rework-subprocess-v1`) adapters with `X2.1`–`X2.4` verified across 31 Rust tests and independent CLI/wheel oracle fixtures; see the [X2 verification record](x2-verification.md) and [X2 machine receipt](x2-verification.json). The [native/Kairos review](native-and-kairos-review.md) records the new pinned source and executed checks.

Historical core-context scope and commands remain in [runtime verification](../../../docs/runtime-verification.md). The [verification record](verification.md) retains the recovery history; the [owner follow-up](owner-quality-20261115.md) records the later exact-source execution. This track remains in progress.
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
| X1.3 | Partial: exact-source execution passed 37 Rust contract and 12 fixture-audit cases. Native-import cases still need a qualified decoder. |

The local execution environment failed before commit/push. Source, tests and
fixtures were reconstructed through GitHub. These bytes cannot inherit the
earlier local results. The coordinator subsequently replayed the recovered
source and added dedicated CI; this owner follow-up fixes the resulting format
findings. [Review](review.md) retains that chronology and the open native gate.
[Integration requests](integration-requests.md) record the accepted shared work.
The PR remains draft. X2 and X3 remain outside this lane.

Track state stays `in_progress`, matching the untouched registry. Root Cargo
does not discover the package; explicit standalone CI is now integrator-owned
and present. This owner follow-up does not change its aggregation or gates.
