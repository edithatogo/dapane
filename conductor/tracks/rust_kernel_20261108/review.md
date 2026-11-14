# Rust kernel completion review

Track: rust_kernel_20261108. Coordinating PR:
[PR #16](https://github.com/edithatogo/dapane/pull/16).

Comparison base: d7063cecc26abe96a3f28fca575b99b450241430.
This record distinguishes independent static review from executed verification.
The final [verification record](verification.md) binds executed native and installed
artifact checks to the corrected source and integrated prerequisite. The track is
archived in place after bounded acceptance; hosted jobs are recorded separately.

## Scope and decision: kernel-interval-envelope-0.1

Implement automatic rate-boundary segmentation as an independently versioned
interval envelope. Do not change point/capacity 0.1/0.2 semantics, methods or
historical digests. The original parent identities are checked before expansion.
The explicit exposure convention is uniform calendar-day distribution; quantities
are never inferred from an event's duration. Monetary rounding remains per generated
line, followed by the existing exact valuation and conserving allocation engine.

The new API is Rust/native and CLI. Existing Python delivery remains unchanged.
The K1.1 licence inventory/compatibility work qualifies the development dependency
boundary. Selecting the project licence and registry publication remain release
consolidation decisions, with publish=false retained.

## Review passes and findings

An independent agent reviewed the existing implementation and acceptance criteria,
then the new code by exact GitHub blob identity while the local workspace was
unavailable. The first implementation reviewed included intervals.rs
808635d1b77773cb09923cd53bc7ef80ffbcef9a.

| Severity | Finding | Remediation |
| --- | --- | --- |
| High | Expanded byte limit was checked after potentially large source/context cloning. A modest input could multiply a large context across many segments before failing. | Measure bounded encoded JSON sizes before cloning each generated row; precheck expanded record count; account for reference-array changes and enforce a final size-accounting invariant. A dedicated amplified-context regression is required. |
| Design | Representative point rows do not retain the original interval end. | Compare original start AND end before shared-use/component validation. |
| Design | Synthetic child identities could otherwise bypass parent duplicate-component checks or collide with caller-supplied IDs. | Validate original identities and pools first; use separately namespaced tuple hashes and reject generated-ID collisions before source expansion. |
| Design | Rounding each segment can differ from rounding the parent total. | Separate interval method version; explicit 0.005 + 0.005 half-even fixture; preserve exact values and rounding adjustment. |
| Design | The original template cannot be reconstructed reliably from expanded allocation references alone. | Return request_snapshot and interval_snapshots for independent input-digest reconstruction, plus expanded_request for exact scalar replay. |
| Design | Direct typed envelope deserialization could relax the raw 0.1 prohibition on an empty capacity_allocations field. | Reuse strict recursive JSON loading and legacy nested-request parsing before typed interval evaluation. |
| Medium | Independent checks could miss duplicate segment identities or altered source/context lineage while checking amounts and replay. | Add pure lineage verification and 15 schema-valid tampered-report controls, including consistent generated-ID mutations; test these without digest checks masking a missing provenance assertion. |
| Build | Diagnostic-path remapping assigned to a string while a field slice still borrowed it. | Build a new path before assigning it; pinned-toolchain Clippy and all 62 native tests subsequently passed. |

The resource fix measures encoded strings rather than raw byte lengths, including
escaping and UTF-8. It applies shrinking allocation-reference replacements before
growing ones, bounds generated identifiers before copying large contexts, and
retains ordinary expanded-request validation.

## Acceptance and evidence boundaries

The independent synthetic rate boundary is 1/3 hour × 90 plus 2/3 hour × 120 = 110.
Other cases cover 42.50 activity funding, source lineage, half-open dates, leap
days, exact quantity conservation, per-segment rounding, disjoint components,
pool conservation, incomplete capacity, source selection and malformed transport.
No source labels or successful calculations establish empirical validity.

The initial test commit is
[6da9d531a30be587fbc7f4b629fbeb677934d088](https://github.com/edithatogo/dapane/commit/6da9d531a30be587fbc7f4b629fbeb677934d088).
Its hosted jobs were queued when implementation continued. After the local
workspace recovered, the retained baseline was executed retrospectively with
Rust 1.99.1 and failed with the intended unresolved interval API import. The
[retained log](evidence/red.log) records that run; it does not imply an executed
local fail-first sequence before implementation was authored.

The local workspace initially disconnected after a local acceptance-test commit;
connector commits preserved the work. After recovery, the exact pinned compiler,
complete Cargo cache and isolated build targets enabled local native qualification.
All 62 native tests, installed CLI references and the four supported installed-wheel
jobs passed. The expanded merged suite passed 133 tests on each interpreter. These
are executed local results, not a claim that queued hosted jobs have completed.

Core-contract PR #9 was reconciled at accepted main
`224cf91dbcf513feaa022b2cf5aa310a965472ce`, producing integration
`a703c93d49e782b67fe4b14588bf1fb26292bb23`. Its bundle and archive-regression tests
are included in the 133-test installed suite. Both merged Ruff commands retain
the bundle verifier alongside the kernel additions. Conditional offline-security
PR #5 and unrelated setup/provider lanes remain outside this review. The plan,
metadata, index, registry and project context were synchronised for in-place
archival; the prerequisite track's separate closeout records were preserved.

## Follow-up independent review

The independent reviewer inspected the corrected interval blob
ba6d03c449f5c66fbb192a96f782da77aa9384f6 and bounded serializer blob
05f0f22787436b86d96ba441cfcd32bb2f7d99e3. The original high-severity
resource-amplification finding was resolved structurally; no new arithmetic,
identity or replay defect was identified. Import sorting in the dependency guard
was also corrected. The eight added review regressions cover bounded expansion,
generated collisions, nested duplicate keys, component ordering, differing parent
end dates, generated precision, cross-mode allocation and aggregate row limits.
This finding disposition is static evidence, not a compiler/test/formatter pass.

## Final independent disposition

The final read-only re-review inspected local commit
`19c460ada9e810f6aedb6f53ef5d29cfec780876`, published with identical tree
`3ce4e29d8eafabf6afb837bc762ac277cf13f536` as `023dc4b…`.
It checked interval blob `328ee914436b6239f8f23a5b5eb054be2192a1eb` and checker
blob `9e4dfd8c2ec6b02108c0add3be5299950de153fe`. No remaining correctness issue
was identified in the resource bound, diagnostic mapping, schema/DTO contract,
reference arithmetic, generated identities or provenance controls.

The reviewer also checked the accepted prerequisite, workflow merge and archive
validator conditions. Actual execution is separately recorded in
[verification](verification.md), including dependency qualification and the
installed-artifact matrix. Optional IO, release licensing and richer exposure
methods retain their explicit boundaries; no unmet kernel task is hidden by
deleting or moving its plan.
