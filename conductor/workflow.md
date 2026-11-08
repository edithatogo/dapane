# Development workflow

## Start from a ready task

Read the [index](index.md), [requirements](requirements.md), [design](design.md)
and selected track. Inspect git status and current provider readiness. Choose a
bounded task whose local prerequisites are satisfied. External source or release
dependencies are recorded separately; they must not make unrelated local work
appear blocked.

Use the user's existing authorisation and make routine reversible implementation
decisions within scope. Record material design changes in [decisions](decisions.md)
and affected requirements. Do not add a separate approval form for every task or
repeat an approval already supplied in the session.

## State conventions

| Plan marker | Meaning | Track metadata state |
| --- | --- | --- |
| `[ ]` | Pending | `new` before work starts |
| `[~]` | In progress | `in_progress` |
| `[x]` | Complete with evidence | `completed` only when all required work is done |
| `[!]` | Blocked with a named reason and next action | `blocked` when the entire track cannot advance |
| `[-]` | Intentionally omitted with rationale | Does not itself imply `cancelled` or `archived` |

Track states also permit `cancelled` and `archived`. Keep metadata, registry and
track index consistent. A date or completion checkbox is not evidence of a
runtime capability. Retain earlier evidence as a dated observation when a later
change invalidates its relevance.

## Execute and verify

1. Mark the selected task in progress and state its expected observable outcome.
2. For numerical behaviour, derive independent fixtures or invariants before
   implementing the calculation. Historical outputs can be regression
   comparators; they are not automatically independent scientific references.
3. Make the smallest coherent change. Keep domain rules and optional adapters
   outside the core. Avoid duplicate formulas in wrappers and UIs.
4. Run checks proportionate to the change: the documentation validator for
   context edits, affected behavioural checks for code, installed-artifact tests
   for packaging, and source/method review for scientific claims.
5. Inspect the diff and record commands, results, limits and relevant source or
   environment identity once in the track evidence/metadata.
6. Update task markers, track state and relevant context. Keep unmet acceptance
   criteria open, including optional integrations that have not been exercised.

Do not repeat broad tests without a concrete unresolved risk or a required gate.
Do not create tests that merely mirror implementation details. Verify negative
cases that matter: incompatible units, stale quotes, missing inputs, double
counting, allocation imbalance, malformed transport and unsupported methods.

## Current repository check

```sh
python3 scripts/validate_conductor.py
```

This checks required context, relative links, metadata/registry consistency,
requirement ownership and acyclic local dependencies. It never marks numerical,
clinical, source or deployment validity. Runtime commands are added to their
tracks once there is an implementation to run.

## Commits and collaboration

Use bounded descriptive commits, for example `feat(core): reconcile allocation
residuals` or `docs(conductor): update newborn pathway acceptance cases`. Stage
only task-owned files. Keep a consumer's compatibility behaviour documented
during migrations and preserve a reversible adapter/release path.

The initial setup may populate an empty default branch. Subsequent work should
normally use a branch and reviewable PR, following user instructions and actual
repository rules. Do not rewrite shared history or archive repositories as an
incidental part of implementation.

Parallel agents should own non-overlapping files or tasks, agree shared contracts
first, and reconcile their outputs before publication. One coordinating Dapane
track should point to provider-owned work instead of maintaining another copy of
the provider's implementation plan.

## Release and research claims

Qualify capabilities independently. The initial core/Python release must not wait
for every optional language, Power Platform or process adapter. A release states
its actual methods, data sources, platforms and installed-consumer evidence.

Keep reporting completeness, method appraisal, implementation verification and
external validation separate. Publication requires the chosen project licence,
redistribution rights for included artefacts, reproducible release inputs and
the user's applicable publication authority. Research claims require the
comparator and independent-data evidence in [research-validation](research-validation.md).
