# Python delivery with workforce and genomics consumers

## Outcome and users

Prove that the common core is a useful independent package by running a workforce calculation and a genomics workflow through installed Python bindings and the same Rust implementation.

This is the full acceptance specification. The first bounded profile is implemented; [runtime evidence](../../../docs/runtime-verification.md) records its scope. Unmet criteria below remain open.

## Scope and requirements

Owning requirements: **RQ-04, RQ-02, RQ-03** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Add a thin PyO3/maturin wrapper and optional Polars/Arrow conveniences.
- Integrate one bounded workforce rule set and one genomic workflow through separately owned domain adapters.
- Preserve legacy entry points and scientific provenance while isolating demonstration PSA/VOI code.

## Deliverables

- Python package and wheels for an explicitly tested interpreter/OS/architecture matrix.
- Consumer contract fixtures and installation tests run outside the source tree.
- A workforce-to-genomics composition example with dated labour quotations and shared batch costs.

## Prerequisites and interfaces

Local track dependencies:

- [rust_kernel_20261108](../rust_kernel_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/microcosting_healthworkforce: rule/source ownership and import namespace migration remain provider-owned.
- edithatogo/microcosting_genomics: resource recipes and workbook/assay evidence remain provider-owned.

## Acceptance criteria

1. Both domain consumers invoke the same Rust numerical implementation rather than copying arithmetic into Python.
2. Native and independently installed Python results match the same exact fixtures, including a nonterminating exposure and sub-cent allocation.
3. One genomic workflow consumes one dated workforce quotation release without duplicating its loaded components.
4. Historical workbook comparisons identify expected differences and repairs separately from mechanical extraction.
5. Errors, missing values, ownership/lifetimes and exact-number transport are exercised through the installed wheel.
6. Declared Python support matches tested dependencies; no provider pin is loosened merely to make packaging resolve.

## Risks and constraints

Source-tree imports can conceal a broken wheel. Duplicated formulas can make independent-looking consumers share the same mistaken expectation. Keep installation evidence separate from scientific fixture evidence.

## Migration and rollback

Domain packages retain an explicit adapter to their previous qualified engine or release until the new consumer path passes. Preserve old source/workbook identities and record any intentional output changes.

## Open implementation decisions

Choose the first supported domain capabilities and platform matrix from available source evidence and build results. A wider advertised matrix needs new installed-artifact evidence.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
