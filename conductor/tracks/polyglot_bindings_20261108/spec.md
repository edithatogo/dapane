# R and Julia bindings

## Outcome and users

Expose the same Rust numerical implementation to R and Julia with explicit ownership, exact transport and installed-artifact parity. R and Julia are independent delivery branches.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-09, RQ-02** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Build an extendr/rextendr R package calling Rust directly.
- Define a bounded versioned C ABI for Julia and package native artifacts for its qualified targets.
- Keep wrapper crates and host-language objects outside the scalar core.

## Deliverables

- An independently installable R package for a qualified matrix.
- A versioned C header/library ownership and error contract.
- A Julia package and native artifact/JLL route qualified for its selected targets.

## Prerequisites and interfaces

Local track dependencies:

- [rust_kernel_20261108](../rust_kernel_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- R/extendr/rextendr and Julia/native artifact toolchains: recheck documented host support and package terms at implementation.
- Existing MCHS and Voiage binding work: reuse qualified patterns where appropriate without importing their domain equations or assuming their matrices apply.

## Acceptance criteria

1. The R wrapper calls the core directly and can be completed without the C ABI, Julia or Python bindings.
2. The C ABI specifies buffer lengths, ownership/free symmetry, errors, version negotiation and panic containment; no Rust layout/unwinding crosses it.
3. Julia calls the qualified ABI without requiring Python or R.
4. Installed R/Julia results match the same independent exact fixtures and reject invalid/missing values according to documented host conventions.
5. Host GC, lifetime and thread restrictions are exercised rather than inferred from a successful source build.
6. Only installed and tested platform combinations are advertised.

## Risks and constraints

Floating-point coercion, foreign allocation mismatches and host GC/thread errors may pass simple smoke tests. Native ABI stability must be narrower than Rust type stability.

## Migration and rollback

Version the ABI and host packages independently with explicit compatibility ranges. Keep prior native artifacts installable and preserve shared reference fixtures.

## Open implementation decisions

Select initial R/Julia versions and native targets based on installed-artifact evidence. A common C ABI is not a prerequisite for the R design.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
