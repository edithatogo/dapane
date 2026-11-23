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

Track states also permit `cancelled` and `archived`. Keep metadata, registry,
track index and the plan's single `Status:` heading consistent. The index also
has exactly one status declaration. Archived tracks retain finished or explicitly
omitted tasks and passed verification; unfinished or cancelled work retains its
own state rather than using archival as completion.
Follow the [archive policy](archive/README.md) to preserve stable links and evidence.
A date or completion checkbox is not evidence of a runtime capability. Retain
earlier evidence as a dated observation when a later change invalidates its relevance.

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
python3 -m unittest discover -s tests -p 'test_conductor_validation.py' -v
```

This checks required context, relative links, metadata/registry consistency,
requirement ownership and acyclic local dependencies. The regression suite checks
that lifecycle inconsistencies and incomplete archival are rejected. Neither
establishes numerical, clinical, source or deployment validity. Runtime commands
and actual outcomes
are recorded in [runtime verification](../docs/runtime-verification.md) and the
affected tracks.

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

The active [parallel ownership map](parallel-ownership.md) assigns the seven
existing roadmap lanes and reserves shared files to the sole integrator. Read it
and refresh live PR/path ownership before editing. A lane's status change must
include a requested central registry update; the integrator applies that shared
change before final Conductor validation. Keep the consistency gate intact while
the request is pending. New lane tests need explicit execution evidence and an
integrator-owned CI/packaging decision before capability promotion. Do not create
duplicate workers or implement another lane's scope.

## Release and research claims

The offline-security workflow runs on GitHub-hosted Ubuntu. It scans each
pull request's exact head SHA and the exact source of each push to `main`
in a read-only container with networking disabled.
For a staged release candidate, set `candidate_ref` to its branch or tag
and `candidate_sha` to the full qualified source SHA.

```sh
gh workflow run offline-ai-security.yml --ref "$candidate_ref"
gh run list --workflow offline-ai-security.yml --event workflow_dispatch --commit "$candidate_sha"
```

Use a successful run whose head SHA equals `candidate_sha` for release
verification.

Qualify capabilities independently. The initial core/Python release must not wait
for every optional language, Power Platform or process adapter. A release states
its actual methods, data sources, platforms and installed-consumer evidence.

Keep reporting completeness, method appraisal, implementation verification and
external validation separate. Publication requires the chosen project licence,
redistribution rights for included artefacts, reproducible release inputs and
the user's applicable publication authority. Research claims require the
comparator and independent-data evidence in [research-validation](research-validation.md).
