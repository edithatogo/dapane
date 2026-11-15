# Core-contract implementation review

Review scope: base `ae00b2e37802a43d29c58729875aff961ff3ae54` through PR #9.
Review mode: focused implementer self-review against this track's specification,
with executable regression tests. This is not an independent human/agent approval.
Only synthetic repository material is used. Conditional security PR #5 and
provider/CareOps files are outside this change.

## Plan alignment

C2.3 is implemented as a separate run-bundle 0.1 envelope and repository-side
conformance verifier, wrapping unchanged numerical requests/reports 0.1 and 0.2.
It defines immutable snapshot replacements, nonfinancial retraction tombstones,
rate-release and observation-window metadata, exact native replay and caller-held
head checkpoints. C3.3 requires the final acceptance/evidence and archive update;
it remains open until all checks on the final head are successful.

The interval case is explicitly presegmented, and alternative capital charges
are explicitly prepared synthetic inputs. This satisfies contract/reference
coverage without claiming automatic interval integration, annuity/depreciation
formulae or a production bundle publisher. Those remain kernel/provider/release
work. All numerical evaluation still calls the installed Rust wheel.

## Findings and fixes

| Finding | Evidence | Disposition |
| --- | --- | --- |
| New exclusion and asset IDs used schema character lengths but did not enforce native UTF-8 byte bounds. | Two regression failures on `fa8c8094187643f0deb295c39d833c6357432e71`. | Added token-byte, whitespace and control validation across all new annotation identities. |
| Malformed local schemas and unresolved references escaped as library exceptions. | Two regression failures on the same head. | Added structured `schema_unavailable` failures; unregistered references still have no network retrieval. |
| Numeric metadata can compare equal in Python despite differing JSON types. | Explicit 2026 versus 2026.0 regression. | Exact canonical-byte replay comparison rejects resealed altered reports. |
| A valid prefix could hide a withdrawn final snapshot. | Truncated-chain regression. | Caller-supplied retained head checkpoint is mandatory for history verification. It is not a digital signature. |
| New verifier was not covered by the existing lint command. | Workflow-target inspection. | Added it to the existing Ruff targets without weakening any gate or changing dependencies. |
| Test formatting differed from the pinned formatter. | Hosted native logs on `fa8c809`; no numerical test failures. | Applied the formatter's indicated test changes and shortened verifier diagnostics. |

## Observed red evidence

- Initial fail-first head `aca58aefdb0c077cda9fb5734758629d820b1d32`,
  [Runtime 43606616201](https://github.com/edithatogo/dapane/actions/runs/43606616201):
  the inspected installed-wheel job had 79 passes, one missing-artifact failure
  and 19 missing-verifier setup errors before implementation.
- Review-test head `fa8c8094187643f0deb295c39d833c6357432e71`,
  [Runtime 43607765244](https://github.com/edithatogo/dapane/actions/runs/43607765244):
  the inspected Python job had 115 passes and the four targeted failures above.
  Native numerical tests passed all 40 cases; formatting was not yet clean.
- Fix head `91d7c164b6692798624ddb9aaa9e22ada00ae33e` contains the two functional
  fixes and the expanded lint target. Final formatting and evidence changes are
  in its descendant commits on PR #9. Earlier green jobs do not qualify a new head.

## Deliberately separate acceptance

Source truth, attestation that a binary matches `source_revision`, undisclosed or
aliased capital assets, production publishing, real provider recipes and economic
formula validation are not established by this candidate. The manifest is an
explicit declaration checked for consistency and replay; a source hash is not a
signature or permission grant. The verifier is repository conformance tooling,
not a new Python dependency of the minimal Rust library or future R/Julia bindings.

Final disposition: pending exact-head hosted verification. No archive or merge is
authorised by this review record alone; use the actual latest PR checks and record
the successful reviewed commit before changing this track's status.
