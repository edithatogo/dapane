# Independent core-contract review — 15 November 2026

Reviewed implementation: `96b178c0f2b21cd8fc702a86dec2f0cde8fa8504`.
Comparison base: `ae00b2e37802a43d29c58729875aff961ff3ae54`.
Two independent agent reviews examined contract correctness and acceptance
coverage. This record supplements the earlier implementer [review](review.md).

## Findings and remediation

1. **P2: immutable rate-release identity was not enforced across snapshots.**
   A source/version/quote identity could retain its label while its amount changed.
   The reviewer demonstrated that both original and changed snapshots passed the
   release component check; no local native replay was available. The remediation
   retains publication dates, non-null source digests and exact quote snapshots
   across the whole supplied history, including temporary omissions. Conflicts
   produce `release_conflict`; a new source version permits a real correction.
   Installed-wheel regressions rebuild native reports and digests to ensure that
   rejection depends on source identity rather than arithmetic or broken links.
2. **P3: the backdated-history regression failed before reaching chronology.**
   Its original knowledge cutoff exceeded the changed recording date. The
   corrected regression first validates every individual snapshot, then requires
   the history-specific `backdated_revision` code.
3. **Context closeout:** C3.3 requires synchronized requirement/decision records,
   schema/compatibility discovery and track/archive state. Keep this pending until
   the final implementation checks and context reconciliation are verified.

The arithmetic oracle for a corrected quote is independent:
`(1/2)*100 + (2/3)*120 = 130`. The original `110` snapshot remains reproducible.
Quote subsets/order and retrieval dates remain variable; valuation stays in Rust.
No method, original request schema, engine dependency or provider code changed.

## Verification status and concurrent work

The prior head had 40 native tests and 119 tests per installed CPython
3.12–3.15 job passing in Runtime
[43609831820](https://github.com/edithatogo/dapane/actions/runs/43609831820).
Those receipts do not qualify these new changes.

The separate concurrent archive-validator regression commit
`207ebd96db7e8eee9b993ae9558dbca2a1356f46` is retained as an ancestor.
This review does not modify its tests or validator ownership.
The local environment disconnected before implementation execution; the existing
hosted exact-head workflows are the acceptance runtime for this remediation.
Final verification, context reconciliation and archival remain pending.

## Acceptance boundary

All six original track criteria have concrete native/installed reference cases.
This contract defines full-snapshot replacement and nonfinancial retraction;
automatic interval integration, capital formulae, real provider/source
qualification, event-level corrections, signed binary provenance and production
publication remain with their existing kernel, provider, process and release
tracks. Synthetic arithmetic does not establish economic or empirical validity.
