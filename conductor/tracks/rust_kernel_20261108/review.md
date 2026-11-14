# Conductor review: Rust valuation kernel and CLI

Date: **15 November 2026** (Australia/Brisbane).
Track: `rust_kernel_20261108`.
Review status: **three findings corrected in source; final hosted qualification pending**.

## Scope and source identity

The review compared the implementation against the [specification](spec.md),
[plan](plan.md), [framework design](../../design.md), exact numerical rules and
existing 0.1/0.2 behavior.

- Comparison base: `d7063cecc26abe96a3f28fca575b99b450241430`.
- Initial source review: `7a816a79c4129f3ca1f6064e7dff0c1d6afa10df`.
- Diagnostic fixes and schemas inspected: `d19d62722764bd296bb99c344348c6ef90c4773a`.
- Final source/checker revision inspected: `f9e78ddcaa979186385b95fa71f7df5fde8eb73c`
  ([commit](https://github.com/edithatogo/dapane/commit/f9e78ddcaa979186385b95fa71f7df5fde8eb73c)).

Scope included the interval evaluator, shared validation and ledger integration,
typed DTOs, JSON parsing, CLI transport, 0.3 schemas, contract documentation,
reference checker and independent native/CLI tests. This was a separate review
from implementation. Existing core-contract bundle work in PR #9 retains its
own acceptance and ownership.

## Findings and remediation

### R1 — Medium: projected interval diagnostics named a nonexistent field

The shared component validator originally returned
`/interval_usage/1/quote_id` for a duplicate interval component.
Interval inputs contain `quote_ids`; the reported pointer did not resolve
against the supplied request.

Reproduction: create two interval component lines sharing one use, then change
the second schedule's component set to repeat the first schedule's salary
component. The monetary rejection itself was correct, but its diagnostic
pointed to the internal point-date projection.

**Fixed:** shared validation selects the actual field name for each input type.
The interval diagnostic now points to `/interval_usage/1/quote_ids`.
The corresponding regression asserts both the exact pointer and that it
resolves in the original input.

Source fix independently inspected at the final review revision. New regression
runtime qualification remains pending in this review record.

### R2 — Medium: arithmetic errors used normalized indices

The evaluator initially formed computation-stage interval paths after sorting
interval parents by identifier. A precision failure could consequently identify
the wrong record in the caller's original array.

Reproduction: supply a harmless `z-simple` interval first and an
`a-overflow` interval second. The latter selects 500 adjacent one-day
rates whose reciprocals have distinct prime denominators. Exact accumulation
exceeds the 4096-bit bound. Sorting puts this parent first, so the old diagnostic
incorrectly pointed to input index zero.

**Fixed:** the evaluator retains an input identifier-to-index map before
normalization and uses the caller's index for interval computation diagnostics.
The regression exercises both input orders and verifies that the pointer
identifies `a-overflow`.

Source fix independently inspected at the final review revision. New regression
runtime qualification remains pending in this review record.

### R3 — Medium: the reference checker normalized immutable input spellings

The interval checker originally applied its reduced-rational assertion to the
entire report, including quotation snapshots. A valid unreduced rational quote
such as `4/2` must remain intact as source provenance even though its
calculated value is two.

Reproduction: replace the first rate-boundary fixture quote's amount with
`{"numerator":"4","denominator":"2"}`. Its independent expected total
remains 26.00. The original checker would reject the retained source fraction
as noncanonical despite valid financial results.

Capacity reports also preserve supplied available-capacity and observed-use
number spellings. Those fields must not be mistaken for calculated rationals.

**Fixed:** the checker applies canonical-rational assertions to calculated ledger
sections only. It retains full source snapshots for lineage/digest comparison.
An additional actual-CLI check supplies the unreduced quotation and verifies
the independently expected result, unchanged source representation and canonical
digests through the same checker.

The revised checker and regression were independently inspected at the final
review revision. Runtime qualification remains pending in this review record.

## Correctness and boundary review

No additional monetary correctness or accounting defect was identified in the
reviewed source. The following properties were checked by code inspection:

- Exposure is an explicit `uniform_calendar_days` declaration over strict
  half-open Gregorian date intervals. The engine does not infer working hours,
  event duration, business days or equipment availability.
- Selected quotations are explicit, known at the cutoff, compatible with the
  parent and policy, and have a consistent component set. Clipped applicability
  covers the parent exactly once; gaps, overlaps and irrelevant selected quotes
  are rejected.
- Segments preserve exact rational quantities and values. Their quantities sum
  to the parent quantity, and rounding occurs once after exact parent summation.
- Point and interval parent identities share duplicate-line, component,
  resolved-context, direct-attribution and pool-exclusivity validation.
  The internal projection is not evaluated as an additional financial line.
- Shared full-pool and capacity allocation consume each parent's rounded amount
  once. Unknown capacity stays explicit.
- Combined point/interval parents are limited to 10,000; each schedule to 10,000
  selections; aggregate interval selections/output segments to 20,000. The
  evaluator traverses rate boundaries rather than every calendar date.
- Existing transport, input precision, intermediate precision and identifier
  bounds apply to typed and JSON entry points. The CLI emits no financial report
  on rejection.
- Normalization orders parent identifiers and quote references; explicit source,
  method and input spellings participate in identity. The evaluator has no
  current-time, random or external lookup dependency.

## Compatibility and schema evidence

Exact text comparisons against the comparison base confirmed that the original
point-date valuation block and the existing full-pool/capacity arithmetic blocks
are unchanged in the final reviewed source. Existing Usage, UnitQuote,
ValuationLine, ValuationPolicy, Totals, Allocation and CapacityAllocation DTOs
were unchanged. New interval arrays are omitted when empty, preserving earlier
profiles' digest material by construction.

This is source-comparison evidence; retained fixture digests and installed
artifacts must still be verified on the final source revision.

The reviewer independently resolved **231 references across nine versioned
common/request/report schema documents**, with no missing reference targets.
The 0.3 field sets, required/optional/null behavior, exposure enumeration,
rational bounds and parent/segment shapes were reconciled with the Rust DTOs.
This reference-resolution check is distinct from running the JSON Schema
validator against actual executable reports.

The contract correctly states that 0.3 does not silently widen a separate
run-bundle or provider contract. Earlier JSON profiles reject interval fields.
Adding fields to public Rust structs requires updated struct literals; no new
pre-1.0 source-compatibility promise is inferred.

## Regression and qualification status

The final inspected revision contains **27 interval-core tests and four
interval-CLI tests**, including the two diagnostic regressions and typed/native
parity and downgrade rejection. The tests cover independent exact references,
parent rounding, calendar boundaries, duplicate components, context inheritance,
allocation conservation, unknown capacity, ordering, limits and failure output.
A property-style case exercises 27 equivalent rate subdivisions.

The original fail-first tests were authored before implementation. After the
execution environment became unavailable, their source was reconstructed and
preserved through GitHub blobs. Reconstructed formatting and the three later
core tests require hosted requalification; earlier local checks are not claimed
as evidence for these final bytes.

The reviewer did not execute the final runtime suite, formatting, lint,
installed CLI, wheel matrix or final schema/reference checks. The integration
coordinator must append exact tested source and workflow evidence before
converting this record to final qualification or archiving the track.

## Acceptance criterion 3: completeness interpretation

The existing specification's phrase "complete/incomplete result status" needs
an explicit interpretation. The public report enum contains only
`Complete`; this increment does not add an
`incomplete` report or partial financial totals.

Computational completeness and source completeness are different:

- A valid request is fully evaluated and returns `status: "complete"`.
- Unknown capacity observations and incomplete coverage remain explicitly
  represented, including nullable shares and unallocated value.
- Invalid or missing required financial inputs return a structured error and
  no financial report. A failed calculation cannot acquire complete status.

This preserves the accepted 0.1/0.2 behavior and the design requirement to keep
missing, zero and unsupported inputs distinguishable. The acceptance mapping
must say that criterion 3 covers computational completeness, explicit source or
observation incompleteness, and structured rejection without partial financial
output. It must not claim an implemented partial-result enum. If criterion 3
were instead interpreted as requiring such a public enum, that capability would
remain unimplemented and could not be marked complete without a separately
versioned change.

## Assumptions and remaining boundaries

The cases are explicitly synthetic computational references. They do not
establish empirical costing validity, actual uniform usage, provider migration
or external source verification.

Project licence, registry publication and broader release assurance retain their
release-track ownership. The core remains unpublished. Optional Arrow/Parquet,
simulation, language adapters, acceleration and operational activation are not
qualified by this interval implementation.

The three review findings above are closed by source inspection. At this record's
revision, final executed qualification and track synchronization remain open.

## Concurrent implementation and method decision

Read-only comparison examined [PR #16](https://github.com/edithatogo/dapane/pull/16)
at `2d4698a33249845182ee41e2184040eb088af475`. It targets this same track with
a separate interval envelope, generated point-date lines and rounding on each
segment. The methods are financially different: two exact half-cent segments
round to zero separately, while their original parent rounds to one cent in 0.3.

The original specification left the interval rounding point to an explicit
method decision. This completion selects the original usage as the monetary
source line, making equal-rate subdivision financially invariant. ADR-013 records
that decision; it does not claim this rule had already been settled by the
original plan. Profiles 0.1/0.2 retain independently rounded point observations.

The independent comparison recommended PR #15 as the integration candidate.
PR #16's branch and evidence are preserved, and its incompatible public envelope
is not merged into 0.3. Two useful independent acceptance cases are adapted to
the chosen method: rational duration conservation across 25 interval lengths,
and a valid input whose computed segment needs more than the input's digit limit
while remaining inside the separate intermediate-precision bound. These cases
retain the useful boundary evidence without copying the alternative method's
rounding or scalar-replay restrictions.
