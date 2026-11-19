# X2 Bounded PNML and BPMN 2.0 Adapters

**Status:** `X2.1`–`X2.4` implemented and source-verified on synthetic fixtures; `X1.2` native XES/OCEL raw import remains blocked on `edithatogo/mailweft#4`, and `X3.1`–`X3.3` Kairos execution integration remains pending on `edithatogo/kairos` Track 114.

This standalone zero-dependency Rust crate (`dapane-process-models`, Apache-2.0) implements bounded execution profiles for ISO/IEC 15909-2 PNML 2009 Place/Transition nets and named OMG BPMN 2.0 subsets. It keeps all XML parsing, process semantics, and simulation/rework logic outside `crates/dapane-core/` and projects physical `ExecutionTrace` records into strict Dapane `0.1` valuation requests under an independently selected quotation release.

An imported diagram under this crate is **not** a general BPMN simulator or an empirical validation claim. Unsupported elements fail visibly with structured `ErrorCode` JSON diagnostics.

## Implemented Profiles

### 1. `pnml-bounded-v1` (X2.1)

- **Standard / namespace:** `http://www.pnml.org/version-2009/grammar/pnml`, `<net type="http://www.pnml.org/version-2009/grammar/ptnet">` (ISO/IEC 15909-2).
- **Supported elements:** `<pnml>`, single `<net>`, nested `<page>`, `<place>` + `<initialMarking><text>`, `<transition>`, `<arc>` + `<inscription><text>` (positive integer weight `>= 1`), `<name>`, non-semantic `<graphics>`, and normal arc `<type value="normal"/>`.
- **Rejected constructs (`unsupported_construct` / `unsupported_net_type`):** high-level or coloured net types, inhibitor/reset/read arcs, `<toolspecific>`, zero/negative/non-integer weights or markings, place-to-place or transition-to-transition arcs, and insufficient-token transitions (`not_enabled`).
- **Execution semantics:** explicit firing schedule (`transition_id`, integer `multiplicity >= 1`), atomic token consumption/production, exact rational cumulative minutes, optional mid-run `cancel_after` halting remaining scheduled firings (`status.state = "cancelled"`), and exact `expected_final_marking` verification upon non-cancelled completion (`final_marking_mismatch`).

### 2. `bpmn-core-acyclic-v1` (X2.2)

- **Standard / namespace:** `http://www.omg.org/spec/BPMN/20100524/MODEL` (OMG BPMN 2.0.2 / ISO/IEC 19510), tolerating visual DI layout (`http://www.omg.org/spec/BPMN/20100524/DI`) inside `<definitions>`.
- **Supported executable subset:** single `<process>` (`isExecutable != "false"`), none `<startEvent>`, none `<endEvent>`, atomic tasks (`task`, `serviceTask`, `userTask`, `manualTask`), `<exclusiveGateway>` (XOR), `<parallelGateway>` (AND), and `<sequenceFlow>`.
- **Rejected in core profile:** cycles (`cycle_not_allowed_in_core_profile`), `<subProcess>`, `<terminateEventDefinition>`, `<inclusiveGateway>`, `<complexGateway>`, `<eventBasedGateway>`, `<boundaryEvent>`, intermediate/message/timer/signal/compensate events, `<multiInstanceLoopCharacteristics>`, `<standardLoopCharacteristics>`, `<adHocSubProcess>`, `<callActivity>`, and `<conditionExpression>`.
- **Timing and branching:**
  - Every XOR split requires an explicit caller entry in `branch_decisions` (`missing_branch_decision` / `ambiguous_branch_decision`); no silent default routing occurs.
  - Parallel AND joins wait until all incoming sequence flows have arrived, firing once at `max(arrival_times)` so parallel branches reflect wall-clock makespan rather than summing branch durations.

### 3. `bpmn-extended-rework-subprocess-v1` (X2.3)

Adds three explicitly bounded capabilities on top of `bpmn-core-acyclic-v1`:

1. **Bounded XOR rework loops:** cycles permitted when guarded by caller `max_node_visits` (`1..=64`); excess iterations fail visibly with `loop_bound_exceeded`. Every visit emits distinct deterministic `(step_id, event_id, use_id)` identifiers.
2. **Terminate end events (`<endEvent><terminateEventDefinition/></endEvent>`):** halts execution immediately at termination time `T`, setting `status.state = "cancelled"`. Steps whose `end_minute <= T` commit; any in-flight or unstarted branch with `end_minute > T` is aborted and emits zero resource usage.
3. **Embedded `<subProcess>` (max nesting depth 2):** preserves hierarchical `subprocess_path` on emitted steps and supports nested recipes keyed by `<subProcess>/<node>` or `<node>`. Deeper nesting fails with `size_limit_exceeded`.

All unsupported gateways (inclusive, complex, event-based), timer/message/signal/boundary events, multi-instance loops, call activities, and `triggeredByEvent="true"` event subprocesses remain strictly rejected.

## XML Security and Resource Semantics

- **XML guardrails (`src/xml.rs`):** std-only strict XML subset parser bounded to `262,144` bytes, nesting depth `<= 32`, `<= 4,096` elements, and `<= 64` attributes per element. Rejects `<!DOCTYPE`, `<!ENTITY`, `<!NOTATION`, `<![CDATA[`, non-`<?xml` processing instructions, duplicate attributes, and unknown entity references.
- **Consumption, occupancy, and transfer separation (AC 3):** `ResourceKind::{Consumption, Occupancy, Transfer}` is preserved in `ExecutionTrace`. `Transfer` rows carry `costable = false` and are excluded from projected Dapane `0.1` `usage` lines.
- **Shared batch non-duplication:** `BatchMode::SingleSharedBatch { batch_object_id }` emits one usage row per executed batch step (without direct `attribution_object_id`), referencing all participating `object_ids` and allocating conservatively through explicit `allocations` weights rather than multiplying batch charges per infant or flattened trace.
- **Quotation-release decoupling (AC 4):** `execute-pnml` and `execute-bpmn` carry zero currency or quotation data. `project-dapane` attaches a downstream `ValuationAttachment` quotation release while preserving exact `model_sha256`, `process_id`, `model_id`, `model_version`, `event_id`, `use_id`, `activity_id`, and physical `quantity`. Executed models project only as `synthetic` or `derived` (never `observed`).

## Licences and Dependency Boundary

- **Crate licence:** `Apache-2.0` (`publish = false`, zero third-party Cargo dependencies, `unsafe_code = "forbid"`, `missing_docs = "deny"`).
- **Standards referenced:** ISO/IEC 15909-2 (PNML 2009 schema URIs) and OMG BPMN 2.0.2 / ISO/IEC 19510 (namespace URIs only; no proprietary schema files or third-party parser code redistributed).
- **Avoided obligations:** uses neither PM4Py (`AGPL-3.0`) nor `quick-xml < 0.41.0` (`RUSTSEC-2026-0194` / `RUSTSEC-2026-0195`).

## Running Local Checks

```sh
PATH="$(dirname "$(rustup which rustc --toolchain 1.99.1)"):$PATH" \
  cargo fmt --manifest-path adapters/process_models/Cargo.toml --all --check
PATH="$(dirname "$(rustup which rustc --toolchain 1.99.1)"):$PATH" \
  cargo clippy --manifest-path adapters/process_models/Cargo.toml --locked --offline --all-targets -- -D warnings
PATH="$(dirname "$(rustup which rustc --toolchain 1.99.1)"):$PATH" \
  cargo test --manifest-path adapters/process_models/Cargo.toml --locked --offline --all-targets
```
