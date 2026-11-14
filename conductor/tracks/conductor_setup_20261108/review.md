# Setup review and archival

Review date: **15 November 2026**, Australia/Brisbane.
Status: in progress.

## Scope and reconciliation

The original setup is complete. This follow-up reviews its acceptance evidence,
corrects lifecycle-validation defects and archives only this track. It does not
implement or qualify a runtime, provider integration, release or deployment.

The reviewed starting point is main commit
`d7063cecc26abe96a3f28fca575b99b450241430`. Its clean local checkout matched
the live branch. The original setup publication commit
`6579591366d746cde267bfae8950219a56da6855` remains an ancestor. The original
[Conductor run](https://github.com/edithatogo/dapane/actions/runs/42445514505)
was independently read again: its exact head matches that publication commit,
and its conclusion is success. The historical [setup evidence](../../verification.md)
is retained unchanged.

Open PRs were reconciled before editing: #9 owns core-contract completion, #10
owns contribution guidance and #5 owns conditional offline security. Their
implementation files are outside this change. The review used an isolated
checkout and preserved the existing main checkout and other owners' work.

## Findings and corrections

1. **Archived status bypassed completion checks.** Only `completed` required
   finished plan tasks and passed verification. Archival must preserve those
   conditions so it cannot conceal incomplete work.
2. **Plan status was unchecked.** Metadata, registry and index could agree while
   the plan still stated another lifecycle status. The independent correction
   review also reproduced acceptance of contradictory status headings whenever
   one matched metadata. Require exactly one well-formed status declaration in
   both index and plan, consistent with the registry and metadata.
3. **Physical relocation would break existing discovery and dependencies.**
   Apply the existing archive policy by retaining this track under
   `conductor/tracks/`, with its ID and links unchanged. No new relocation
   mechanism is needed.

The initial correction suite exposed 10 expected failures against the original
validator: three unfinished-task cases, three missing/failed/unrun verification
cases, three stale-plan-status cases and one missing-status case. After the
first corrections, all eight test methods (14 CLI fixture executions) passed.
The independent review then reproduced the contradictory-status failure
through the CLI. The follow-up adds strict status declarations and regression
coverage for that ambiguity, malformed quoting and cross-line whitespace.

The review also requested explicit historical labelling of the original metadata
completion claims. `initial_setup_verification` and
`initial_setup_completion_evidence` preserve those original values separately
from the current review and archive outcome.

## Executed local evidence

- Baseline `python3 scripts/validate_conductor.py`: passed with **14 tracks,
  12 requirements, 143 tasks and 426 local links**.
- Initial correction suite: **8 methods / 14 CLI fixture executions passed**.
- Context validation after the first corrections: **14 tracks, 12 requirements,
  147 tasks and 432 local links**.
- `git diff --check`: passed on that initial corrected tree.
- Interpreter: Python **3.12.14**. Fixtures invoke the actual validator CLI in
  temporary repositories and require no Git, network or third-party dependencies.

## Final verification

The local execution environment disconnected before the strict-status follow-up
could be applied or run locally. The corrected files were reconstructed against
the same immutable GitHub base. The final strict-status changes require the
existing hosted Conductor job and independent review before archival. Earlier
local results do not qualify the reconstructed final head.

## Limits

These checks concern project records and archival integrity. They do not verify
numerical, source, clinical, economic or deployment validity. The original
13-track setup count remains a dated observation; it is not the current count.
