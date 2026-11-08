# Release assurance and conditional consolidation

## Outcome and users

Release only evidenced capabilities with reproducible artifacts and a practical migration path. The first core/Python release must not wait for optional domains, language bindings, process models or Power Platform.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-12, RQ-04** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Establish capability-specific release, compatibility, security and dependency evidence using existing portfolio practices.
- Verify installed artifacts, clean builds, bounded performance and reproducible source/result provenance.
- Review duplicated code and archive candidates only after their unique assets and successors are established.

## Deliverables

- Release/capability manifest, reproducible build and artifact evidence, dependency/licence record and SBOM/provenance route.
- A supported-platform matrix and migration/deprecation/rollback guide.
- A repository consolidation inventory with successor and preservation evidence for each actual proposal.

## Prerequisites and interfaces

Local track dependencies:

- [python_two_consumers_20261108](../python_two_consumers_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/repository-standards and existing portfolio CI/release practices: select applicable maintained controls rather than invent a new governance layer.
- Domain package maintainers: migration, public API compatibility and archive/successor decisions remain repository-specific.
- Package registries and source licensors: package identity/rights and any external release conditions must be verified at publication.

## Acceptance criteria

1. A core/Python release can qualify after contracts, kernel and the two consumers; optional integration tracks remain independently planned or experimental.
2. Advertised capabilities match exact source, artifact, platform, method and data versions actually checked.
3. Dependency licences/advisories, permissions, provenance and source-data redistribution constraints have recorded outcomes.
4. Installed artifacts exercise native functionality and reference cases; passing source-tree tests alone is insufficient.
5. Existing consumer APIs have a documented migration and recovery path before shared machinery is removed.
6. No archive is executed from a recommendation alone; unique history/research, rights, successor behaviour and any required authorization are retained.

## Risks and constraints

A broad all-tracks gate would unnecessarily block a useful first release. Conversely, automatic badges or successful builds must not imply scientific or platform support beyond the evidence.

## Migration and rollback

Retain old artifacts, source packs and consumer adapters; use a new corrective release for defects. Preserve repository history and reproducible scholarly versions during any later consolidation.

## Open implementation decisions

Choose release channels and package licensing explicitly when publishing. Retain a small capability manifest rather than requiring an additional approval board or duplicated evidence store.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
