# Implementation plan: Optional Power Platform delivery

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Manual standard-connector baseline

- [ ] A1.1 Define list fields, bundle locations, schema/version references, job states and result summary contracts with the CareOps consumer.
- [ ] A1.2 Provide reproducible list/library setup and permitted synthetic input/output examples; keep full result bundles as the archive of record.
- [ ] A1.3 Exercise manual export, CLI execution and result import; verify exact transport, identity and incomplete-output presentation.

## Phase 2 — Operational worker option

- [ ] A2.1 If selected, implement an independently authorised worker with bounded polling/queue handling, scoped identity and explicit host operation.
- [ ] A2.2 Implement job claiming, duplicate-request handling, retries, cancellation, input immutability and auditable result publication.
- [ ] A2.3 Verify restart/duplicate/partial-output cases and the actual app, flow, environment and service entitlements for the chosen deployment.

## Phase 3 — Independent interactive options

- [ ] A3.1 If selected, qualify an authenticated OpenAPI/custom-connector service and its operating/licensing boundary.
- [ ] A3.2 Independently test a bundled Rust/WASM PCF candidate against target web/mobile host, CSP, asset packaging, memory and lifecycle constraints.
- [ ] A3.3 Verify native parity and supported authentication for each selected route; retain manual operation when an option is unsupported.

## Phase 4 — Handoff

- [ ] A4.1 Document deployment/rollback, data-boundary requirements and per-route capability evidence without claiming a universal standard-app entitlement.
- [ ] A4.2 Verify that no app/report formula duplicates the core and that the optional surface can be removed without changing numerical results.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
