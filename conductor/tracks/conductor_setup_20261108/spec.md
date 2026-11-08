# Conductor setup and source-of-truth handoff

## Outcome and users

Give the repository maintainer and coding agents a navigable, internally consistent project definition and an executable delivery plan. Dapane becomes the coordinating home for the shared framework; the earlier MCHS plan remains a provenance record and domain-consumer reference.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-01, RQ-12** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Map the empty repository and record the approved framework direction.
- Create product, requirements, design, technology, workflow and style context; a track registry and dependency-aware roadmap.
- Record provider ownership and the difference between upstream semantic work, this setup and future runtime qualification.

## Deliverables

- Versioned Conductor project context and this 13-track programme.
- README entry points and proportionate documentation validation.
- Recorded local validation and initial repository publication evidence.

## Prerequisites and interfaces

Local track dependencies:

No local prerequisite track.

External readiness, checked separately from the local dependency graph:

- edithatogo/mchs: shared_microcosting_valuation_20261108 is the source design; Dapane now coordinates the framework.
- edithatogo/UOGTO and edithatogo/standards_check: upstream semantics and source catalogue retain their owners.

## Acceptance criteria

1. All project and track links resolve; metadata, registry status and task markers agree.
2. Every requirement has at least one owning implementation track and concrete acceptance criteria.
3. The local dependency graph is acyclic; external provider readiness is recorded separately.
4. Only setup work is marked complete. No Rust engine, domain model, binding, deployment or archive is asserted delivered.
5. The repository contains the reviewed files and publication outcome is recorded without claiming a runtime release.

## Risks and constraints

Avoid parallel authoritative roadmaps: Dapane owns framework delivery, while consumer repositories own their adapters. Preserve the distinction between an accepted design direction and implemented capability.

## Migration and rollback

Use a new corrective commit for setup defects. Preserve published history and source references; no external repository deletion or archive is part of this track.

## Open implementation decisions

Runtime package names, support versions and repository licensing are not established by documentation setup. Resolve their implementation/release requirements in the relevant tracks.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
