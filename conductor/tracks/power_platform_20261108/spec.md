# Optional Power Platform delivery

## Outcome and users

Surface the shared engine through an operational Power App while keeping the calculation implementation independent and the standard-connector/file path usable.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-08, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Start with Canvas/SharePoint request metadata, immutable bundles and manual CLI exchange.
- Treat an authorised asynchronous worker, premium API/custom connector and local WASM/PCF component as separate optional delivery capabilities.
- Keep Power Fx, flows and reports as contract consumers rather than independent formula implementations.

## Deliverables

- Versioned request/status/summary/list and document-library contracts, plus reproducible setup instructions.
- A permitted-data manual exchange demonstration with a result/audit bundle.
- Separate qualification records for any subsequently implemented worker, API or browser component.

## Prerequisites and interfaces

Local track dependencies:

- [python_two_consumers_20261108](../python_two_consumers_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/careops: maintained costing module and non-premium SharePoint-oriented delivery patterns.
- Target Microsoft tenant/environment and authorised host owner: actual entitlements, identity, configuration and permitted-data scope.

## Acceptance criteria

1. The baseline demonstrates input export, CLI execution and result import without a hidden premium connector, HTTP action, gateway, Dataverse or Copilot requirement.
2. Actual user/environment rights and target-host behaviour are recorded before deployment; a Standard badge is not treated as an entitlement decision.
3. Large payloads/results use immutable files; Lists hold identities, state and summaries, and incomplete results are visibly incomplete.
4. A worker handles idempotency, claiming, retry/cancellation and scoped access without bypassing service or licensing obligations.
5. An API or browser component uses the same qualified numerical implementation and does not duplicate Power Fx calculation rules.
6. Optional routes have separate capability status; their absence does not block the CLI or core release.

## Risks and constraints

A queue or worker is not a licensing bypass. Browser feasibility does not establish approval for real patient-level data or support in every Canvas host. The app must not present partial calculations as complete.

## Migration and rollback

Retain the CLI/file path and versioned request/result bundles. Disable or roll back an optional worker/service/component independently of the core and preserve audit/result history.

## Open implementation decisions

Choose a target permitted-data pilot and actual tenant constraints during delivery. Premium API and browser-local options remain separately selected and qualified; neither is required for initial Dapane.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
