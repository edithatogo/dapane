# X2 Bounded PNML and BPMN Verification Record

Date: **2026-11-19**  
Track: [`process_models_20261108`](index.md)  
Package: [`dapane-process-models`](../../../adapters/process_models/README.md) (`adapters/process_models/`, standalone `Cargo.toml`, Apache-2.0, `publish = false`, zero external crate dependencies)

## Delivered Scope (`X2.1`–`X2.4`)

1. **`pnml-bounded-v1` (`X2.1`):** ISO/IEC 15909-2 PNML 2009 Place/Transition net parser and deterministic executor supporting `<initialMarking>`, positive arc `<inscription>` weights, integer firing multiplicity, exact cumulative rational elapsed time, optional `cancel_after` halting downstream firings, and post-run `expected_final_marking` checking. Rejects non-`ptnet` net types, inhibitor/reset/other non-`normal` arcs, `<toolspecific>`, insufficient-token transitions (`not_enabled`), and marking mismatches (`final_marking_mismatch`).
2. **`bpmn-core-acyclic-v1` (`X2.2`):** OMG BPMN 2.0.2 acyclic core subset covering none `<startEvent>`, none `<endEvent>`, tasks (`task`, `serviceTask`, `userTask`, `manualTask`), `<exclusiveGateway>` (requiring explicit caller `branch_decisions`), and `<parallelGateway>` (calculating concurrent makespan at joins via `max(arrival_times)`). Rejects cycles (`cycle_not_allowed_in_core_profile`), `<subProcess>`, `<terminateEventDefinition>`, `<inclusiveGateway>`, `<complexGateway>`, `<eventBasedGateway>`, timer/message/signal/boundary events, and loop characteristics.
3. **`bpmn-extended-rework-subprocess-v1` (`X2.3`):** Adds bounded XOR rework loops guarded by `max_node_visits` (distinct visit identifiers), `<endEvent><terminateEventDefinition/></endEvent>` aborting in-flight branches whose `end_minute > cancel_time`, and embedded `<subProcess>` scopes up to nesting depth 2. Still rejects unsupported gateways, intermediate/boundary/timer/message events, multi-instance loops, call activities, and `triggeredByEvent="true"` subprocesses.
4. **Costing projection & revaluation invariance (`X2.4`):** Preserves `ResourceKind::{Consumption, Occupancy, Transfer}` in `ExecutionTrace`; excludes `Transfer` (`costable = false`) from Dapane `0.1` `usage` lines; prevents batch multiplication via `BatchMode::SingleSharedBatch`; projects into strict Dapane `0.1` requests without altering physical IDs or quantities when only the quotation release changes (`quotes-release-2026-v1.json` vs `quotes-release-2026-v2.json`).

## Inspected External Readiness & Non-Claims

Live checks on **2026-11-19**:

- `edithatogo/mailweft#4`: still **OPEN** (updated 2026-11-15); raw XES/OCEL qualification (`X1.2`) remains blocked on `process_mining` / `quick-xml >= 0.41` remediation.
- `edithatogo/rust4pm`: default branch at `85179f2aa8` (`process_mining 0.6.0` on `rust4pm` declares `quick-xml 0.37.4`; upstream `aarkue/rust4pm` at `0.7.0` uses `quick-xml 0.42.0`, not yet qualified downstream).
- `edithatogo/kairos`: `main` at `a1f6283575ad26918230adc122a99b5c08fc4da3`; Track 114 / issue `#336` remains open and `conductor/contracts/movement-resource-usage.md` still states implementation is pending. `X3.1`–`X3.3` therefore remain **pending**.
- All cases under [`adapters/process_models/fixtures/`](../../../adapters/process_models/fixtures/expected.json) are synthetic process fixtures, not empirical programme data or a general BPMN engine claim.

## Executed Checks (`feat/process-models-x2`, `Darwin arm64`)

- Toolchain: `rustc 1.99.1 (58cf8f9c3 2026-10-13)`, `clippy 0.1.99`, CPython `3.15.1`, `maturin==1.16.0`, `ruff==0.17.4`.
- `cargo fmt --manifest-path adapters/process_models/Cargo.toml --all --check`: **passed**.
- `cargo clippy --manifest-path adapters/process_models/Cargo.toml --locked --offline --all-targets -- -D warnings`: **passed** (0 warnings).
- `cargo test --manifest-path adapters/process_models/Cargo.toml --locked --offline --all-targets`: **passed** (`1` unit test + `30` integration tests = `31` passed).
- Native wheel parity run (`REQUIRE_DAPANE_WHEEL=1`, temporary CPython 3.15.1 venv outside checkout) running [`test_process_models.py`](../../../adapters/process_models/tests/test_process_models.py): **passed** (`3` test suites covering `10` positive cases across `v1`/`v2` quote releases + CLI/wheel parity + object conservation, `10` negative error-code checks, and SHA-256/model validation checks).
- `ruff check` & `ruff format --check` on `adapters/process_models/tests/test_process_models.py`: **passed**.
- `python3 scripts/check_json_hygiene.py` on all 13 fixture JSON files: **passed**.
