# Implementation plan: Optional Power Platform delivery

Status: archived

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Manual standard-connector baseline

- [x] A1.1 Define CareOps identity, native List fields, library paths, schema versions and result states. See the [SharePoint exchange contract](../../../power_platform/sharepoint-contract.json).
- [x] A1.2 Provide reproducible list/library setup and permitted synthetic input/output examples; keep full result bundles as the archive of record.
- [x] A1.3 Exercise local synthetic file export, installed CLI valuation and replay through the installed wheel. Verify exact bytes, native List fields and incomplete output.
- [-] A1.4 Exercise the exchange and check operator access on the selected SharePoint tenant. The owner deferred live work on 20 November 2026.

The [manual baseline](../../../power_platform/README.md) records the source mapping, field definitions and commands. The [review](review.md) records the local tests and the checks that a future pilot needs.

## Phase 2 — Operational worker option

The owner deferred live work. The manual baseline has no worker.

- [-] A2.1 If selected, implement an independently authorised worker with bounded polling/queue handling, scoped identity and explicit host operation.
- [-] A2.2 Implement job claiming, duplicate-request handling, retries, cancellation, input immutability and auditable result publication.
- [-] A2.3 Verify restart/duplicate/partial-output cases and the actual app, flow, environment and service entitlements for the chosen deployment.

## Phase 3 — Independent interactive options

Connector and PCF routes were left for separate selection and host qualification.

- [-] A3.1 If selected, qualify an authenticated OpenAPI/custom-connector service and its operating/licensing boundary.
- [-] A3.2 Independently test a bundled Rust/WASM PCF candidate against target web/mobile host, CSP, asset packaging, memory and lifecycle constraints.
- [-] A3.3 Verify native parity and supported authentication for each selected route; retain manual operation when an option is unsupported.

## Phase 4 — Handoff

- [x] A4.1 Document deployment/rollback, data-boundary requirements and per-route capability evidence without claiming a universal standard-app entitlement.
- [x] A4.2 Verify that no app/report formula duplicates the core and that the optional surface can be removed without changing numerical results.

## Review fixes

- [x] A4.3 Apply review fixes for native List field types, revision identity and incomplete or invalid archive handling in `ad6edcd`.

## Evidence record

The [review and verification](review.md) records the executed local baseline and fix commit. The [manual exchange](../../../power_platform/README.md) retains the future pilot instructions.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
