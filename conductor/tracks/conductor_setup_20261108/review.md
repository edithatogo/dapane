# Setup review and archival

Review date: **15 November 2026**, Australia/Brisbane.
Status: completed; track archived in place.

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
the same immutable GitHub base and independently reviewed at
`77ec86710de00eea7374b7db8c4bf0e8d1180e3d`, with no remaining findings.

[Conductor run 43650452721](https://github.com/edithatogo/dapane/actions/runs/43650452721)
passed for that exact PR head. Its
[job log](https://github.com/edithatogo/dapane/actions/runs/43650452721/job/132617513294)
records **14 tracks, 12 requirements, 147 tasks and 432 local links** and
**12 tests passed** (35 CLI fixture executions). The runner was Ubuntu 24.04.5.
The tested PR merge commit `38606fae3554caadc5408607f5ffad5e4b88fa5f`
has the same tree `3fec022dcc4e0fc5c3bd5b41cb6bdbd9b7869423` as the
reviewed candidate. Earlier local results are retained as separate observations.

Only after that pass and the independent review was this track archived in place.
The archive commit changes lifecycle records and navigation, not the verified
validator or tests. Its subsequent exact-head checks are attached to
[PR #14](https://github.com/edithatogo/dapane/pull/14); the run above qualifies
the reviewed code and pre-archive records rather than claiming to execute a
later commit.

## Acceptance and retained evidence

| Setup acceptance | Review outcome |
| --- | --- |
| Links and lifecycle records agree | Hosted context validation passed; archive status is synchronised across metadata, registry, index and plan. |
| Every requirement has an owner and acceptance criteria | The existing 12 requirements remain covered by the 14 registered tracks; no implementation scope was reassigned. |
| Local prerequisites remain acyclic | The validator checks the graph; the archive fixture confirms that an in-place archived prerequisite remains registered and usable. |
| Setup completion does not qualify runtime capability | Capability remains `documentation_ready`; the original setup evidence and later runtime records retain their separate scopes. |
| Reviewed setup and publication evidence are retained | Original publication and CI references remain unchanged; the corrections and closure are versioned in PR #14. |

## Archive outcome

Archived on **15 November 2026** at the original
`conductor/tracks/conductor_setup_20261108/` path. All original tasks and the
four review/closure tasks are complete. The archive catalogue points to this
authoritative record; no duplicate track or relocated dependency was created.

The current archive outcome is separate from
`initial_setup_verification` and `initial_setup_completion_evidence`.
No provider or external repository is archived by this change.

## Integration with core-contract completion

All 11 configured checks passed on archive commit
`09e81c6e0ab1a80580258f82b5c1506fafd3d45f`. Its
[final Conductor run](https://github.com/edithatogo/dapane/actions/runs/43651158094)
passed 12 tests and validated 14 tracks, 12 requirements, 147 tasks and 434
local links. Its tested merge tree was identical to the archive commit's tree.

While those checks ran, PR #9 merged to main at
`224cf91dbcf513feaa022b2cf5aa310a965472ce`. The integration preserves that
run-bundle implementation, its independent tests and context. Its equivalent
archived-task/verification safeguards are retained alongside this track's stricter
status checks. The project-index conflict was resolved by retaining both the
archived setup link and the expanded core-contract entry.

The new upstream archive-test fixture omitted its plan status. Executing its
unchanged fixture helper reproduced rejection by the strict status check.
The fixture now declares `Status: archived`; its seven valid/invalid combinations
pass direct validation, and all 12 public-CLI regression methods pass. The
combined project context also passes. No numerical or bundle behaviour changed.

Pytest is unavailable in the local interpreter. Direct fixture-helper execution
is not reported as a pytest run; the existing installed-wheel matrix must execute
the actual suite on the updated PR head. Earlier hosted results remain attached
to their stated commits and do not claim execution of this later integration.

## Limits

These checks concern project records and archival integrity. They do not verify
numerical, source, clinical, economic or deployment validity. The original
13-track setup count remains a dated observation; it is not the current count.
