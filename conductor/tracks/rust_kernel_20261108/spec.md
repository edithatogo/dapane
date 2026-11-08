# Minimal Rust valuation kernel and CLI

## Outcome and users

Implement one authoritative numerical core for exact valuation, component accounting and shared-pool allocation. The native library and CLI must work without a language wrapper, table engine, simulator or cloud account.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-01, RQ-02, RQ-03, RQ-12** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Build a minimal Rust workspace with core types/arithmetic and a CLI. Add separately enabled IO only when a selected consumer requires it; otherwise record that capability as deferred.
- Apply resource and activity-kind quotations under explicit valuation policies, preserving input and method lineage.
- Enforce economic, unit, date, rounding, allocation and reproducibility invariants on the independent contract fixtures.

## Deliverables

- Rust workspace, qualified toolchain/MSRV and locked dependency selection.
- Core API and CLI for versioned requests/results with deterministic diagnostics.
- Reference-fixture runner, focused invariant/property tests and a bounded CPU baseline.

## Prerequisites and interfaces

Local track dependencies:

- [core_contracts_20261108](../core_contracts_20261108/index.md)

External readiness, checked separately from the local dependency graph:

No external provider runtime is required for this track.

## Acceptance criteria

1. All supported exact reference cases match independently derived results; invalid quantity/unit/date/valuation combinations return structured errors.
2. Allocated pool values plus explicit residuals equal source pools; duplicate resource and loaded-component charges are detected or rejected under the declared policy.
3. The CLI preserves exact numeric transport, immutable source selection and complete/incomplete result status.
4. Synthetic 2.50 weighted units at 17.00 per unit produce 42.50 in the declared funding view without manufacturing resource-use records.
5. Repeated native runs reproduce the agreed output digest after excluding explicitly non-semantic metadata; no implicit current date or network selection changes results.
6. The minimal feature build runs without Arrow/Polars, ontology, simulation, GPU or web-service dependencies.

## Risks and constraints

A passing calculation test is not empirical validation of a costing method. Parallel reductions and fixed-width decimals can change results unless precision, overflow and ordering are bounded explicitly.

## Migration and rollback

Keep immutable schema and reference fixtures; callers pin the last qualified engine/method release. Use explicit corrected method versions when repairing economic semantics.

## Open implementation decisions

Select existing exact arithmetic, serialization, error and date crates after fixture-based evaluation. GPU/distributed backends, arbitrary expressions and native dynamic plugin loading are outside this first kernel.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
