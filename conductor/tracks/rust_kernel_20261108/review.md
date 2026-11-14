# Rust kernel completion review

Track: rust_kernel_20261108. Coordinating PR:
[PR #16](https://github.com/edithatogo/dapane/pull/16).

Comparison base: d7063cecc26abe96a3f28fca575b99b450241430.
This record distinguishes independent static review from executed verification.
Runtime qualification and archival remain pending until the exact final head passes.

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
Its hosted jobs were queued when implementation continued. Do not describe that
unexecuted baseline as an observed test failure.

The local workspace disconnected after a local acceptance-test commit. Connector
blobs/trees/commits preserve this implementation on GitHub. The new code, tests and
formatting require the existing hosted native and installed-wheel matrix. No local
compiler or final hosted pass is claimed by this static review record.

Core-contract PR #9 remains a prerequisite to reconcile at its actual integrated
head. Conditional offline-security PR #5 and unrelated setup/provider lanes are
outside this review. Final qualification must preserve every applicable existing
check, verify the exact reviewed head, then update the track's plan, metadata,
index and registry together before archiving in place.

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
