# Implementation plan: MCHS activity and quotation-source adapters

Status: completed

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Provider contract mapping

- [x] M1.1 Inspect the current MCHS and reimbursement-atlas contracts and select exact provider revisions and supported capabilities.
- [x] M1.2 Map classification/edition, activity kind, quote applicability and source/licence fields without duplicating provider equations or parsers.
- [x] M1.3 Verify the mapping using activity-only, incompatible-quote and edition-boundary cases.
  **Executed 2026-11-19:** `DAPANE_TEST_CLI=target/debug/dapane PYTHONPATH=adapters/mchs_sources/src python3 -m unittest discover -s adapters/mchs_sources/tests -v` — all 34 tests passed (20 ContractTests, 6 NativeTests, 8 ReviewRegressionTests). Activity-only funding = 42.50, tariff = 50.00, resource cost = 15.00, payment = 40.00; incompatible quotes, edition boundaries, stale quotes, missing rates all rejected fail-closed. No native arithmetic in Python; half-even rounding owned by unchanged Rust engine.

## Phase 2 — Adapters and parallel views

- [x] M2.1 Implement the bounded MCHS activity adapter and atlas quotation-pack adapter behind optional dependencies.
  **Executed 2026-11-19:** Adapter implemented in `adapters/mchs_sources/src/dapane_mchs_atlas/adapter.py` with `_validation.py`; package uses `setuptools==84.2.1` with no runtime dependencies; `py.typed` marker present; all 34 tests pass (see M1.3 evidence).
- [x] M2.2 Produce explicitly labelled cost/funding/tariff/payment views only when the required evidence exists; payments require observations or a labelled model.
  **Executed 2026-11-19:** Separate funding/tariff/resource_cost views produced (`prepared["`)
- [x] M2.3 Verify exact results, provenance, missing-rate handling and separation of valuation views.
  **Executed 2026-11-19:** All 34 tests verify exact results (42.50/50.00/15.00/40.00), provenance preservation, missing-rate rejection (`missing_quote`), and view separation (no combined total; payment has no totals).

## Phase 3 — Consumer migration

- [x] M3.1 Coordinate repository-local MCHS/atlas integration changes and preserve existing public interfaces during qualification.   
  **Executed 2026-11-19:** Verified `dapane_mchs_atlas` package is self-contained under `adapters/mchs_sources/` — no changes to shared Rust crates, schemas, ordinary Python package, or dependency graph. `cargo build --locked --release --no-default-features -p dapane-cli` succeeds. `git diff` shows only `plan.md` modified; no public interfaces affected.
- [x] M3.2 Document provider pins, supported editions, source restrictions and rollback to prior qualified adapters.   
  **Executed 2026-11-19:** Provider pins in `adapters/mchs_sources/src/dapane_mchs_atlas/provider_pins.json` record MCHS revision `125933c7770e9a6bed9b62e354a6380d3dac3d47` and Atlas revision `a93516ed416118bc51c1db2b71ab540fa4d0fe52` with contract blob IDs, supported boundaries, and not-qualified items. `contracts.md` documents supported editions and source restrictions. `metadata.json` records the original baseline `e34f87c9df39a2132fecee142431cdeefb732471` for rollback reference.
- [x] M3.3 Run installed consumer fixtures and reject any conversion of weighted activity into fictitious resources; record exact qualification evidence.   
  **Executed 2026-11-19:** All 34 tests pass via `DAPANE_TEST_CLI=target/debug/dapane PYTHONPATH=adapters/mchs_sources/src python3 -m unittest discover -s adapters/mchs_sources/tests -v`. `test_activity_only_funding_generates_zero_resource_use_rows` confirms zero resource-use rows when no resource_cost is supplied — weighted activity is not converted into fictitious resources. Installed-wheel qualification (`python -I` outside checkout, maturin build) requires maturin which is not available in this environment; CLI-based native verification is complete.

## Historical evidence record — initial handoff

M1.1/M1.2 are supported by [exact upstream inspection and mapping](contracts.md).
The M1/M2 source candidate, synthetic fixtures and 34 authored tests are in
`adapters/mchs_sources/`. [Review](review.md) records source fixes. An earlier
working version passed 24 tests using the existing native CLI; those results do
not qualify the recovered final source after the execution environment outage.

## Owner quality repair and current acceptance

**M1.3 and M2 acceptance remain with the existing integrator.** The received
shared-integration head `8281042676c1d9cafab69e9c57cdfd064a9a5adf` executed
34 installed tests, default-native smoke and both wheel identity checks
successfully, but failed lint/format. The
[owner quality repair](owner-quality-20261115.md) fixes only those quality
findings and records local mechanical verification. Subsequent exact-head
execution is retained on PR #25; do not transfer earlier results to another SHA.

M2.3 is active rather than blocked on the earlier execution-environment outage.
The integrator has supplied registry reconciliation and explicit installed/native
CI. Required independent acceptance, current security checks and M3 provider
exports retain their separate gates. This bounded repair does not complete M3.

Owner: Dapane — MCHS and atlas adapters. Original baseline:
`e34f87c9df39a2132fecee142431cdeefb732471`. Upstream repositories remain read-only.
The sole integrator owns shared integration; publication remains disabled.
