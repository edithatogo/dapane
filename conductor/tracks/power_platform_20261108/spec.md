# Optional Power Platform delivery

## Outcome and users

Deliver the manual file exchange and the versioned SharePoint setup contract for CareOps. Use synthetic requests for repository verification. On 20 November 2026 the owner deferred the live SharePoint pilot.

## Scope and requirements

Owning requirements: **RQ-08, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Use SharePoint List form values, immutable bundles and manual CLI exchange for the repository baseline.
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

## Repository acceptance

1. A synthetic request passes export, CLI execution and result import. The verified files replay through the installed wheel and need no external service.
2. The versioned contract specifies the library paths, unique revision key and native List field types. Full payloads remain files. Incomplete results show the gaps and leave the total blank.
3. An identical retry reproduces the same files and fields. A changed revision keeps the predecessor, and altered or incomplete results fail before publication of the summary.

## Deferred deployment acceptance

- For a later pilot, identify the permitted site, users and data, then verify list and library configuration, actual rights, exact download bytes and operator access. Connector classification alone cannot establish user or environment rights.
- If a worker is selected, verify idempotency, claiming, retry, cancellation and scoped access.
- If an API or browser component is selected, verify the qualified numerical implementation, host behaviour and entitlements. The application uses the shared engine for arithmetic.

## Risks and constraints

A queue or worker is not a licensing bypass. Browser feasibility does not establish approval for real patient-level data or support in every Canvas host. The app must not present partial calculations as complete.

## Migration and rollback

Retain the CLI/file path and versioned request/result bundles. Disable or roll back an optional worker/service/component independently of the core and preserve audit/result history.

## Open implementation decisions

Choose the target and constraints if a permitted-data pilot is commissioned. The worker, API and browser-local routes remain optional.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
