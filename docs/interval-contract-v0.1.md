# Explicit interval valuation 0.1

This separately versioned Rust/CLI contract implements rate-boundary segmentation.
It wraps an ordinary valuation request 0.1 or 0.2 and explicit interval uses.
Point/capacity contracts, method identities and historical point-report digests
retain their existing meaning. Arithmetic remains in the Rust core.

This is synthetic computational qualification. A caller's source and exposure
declarations do not establish empirical validity or source truth.

## Request and exposure

The envelope has schema_version "0.1", request (the ordinary request template),
and a nonempty intervals array. Each interval has id, use_id, kind, target, unit,
exact total quantity, half-open start/end dates, selected quote_ids, source and
the mandatory exposure value "uniform_calendar_day". Ordinary optional event,
process, activity and object context is retained. Context does not allocate money.

Uniform exposure is an explicit caller assumption: total quantity Q is distributed
over Gregorian calendar days, and a segment containing d of the interval's D days
receives exactly Q × d / D. Quantity is never inferred from duration. Dates follow
the ordinary strict YYYY-MM-DD/year 0001–9999 contract. A calendar day is an exposure
convention, not a claim that a local day always contains 24 elapsed hours.

Timestamp, timezone, working-day, holiday and irregular observed-exposure methods
are unsupported. Missing/unknown exposure rules fail instead of acquiring a default.

One explicitly uniform hour over [2026-01-31, 2026-02-03) with a rate change on
1 February becomes 1/3 hour at 90 and 2/3 hour at 120. Independently:
(1/3 × 90) + (2/3 × 120) = 30 + 80 = 110.

## Explicit selection and parent identity

Every selected quote must exist, overlap the interval and be known by the supplied
knowledge cutoff. Selected half-open intervals must cover the requested interval
exactly once. Gaps, overlaps, duplicate/irrelevant selections, incompatible kind,
target, unit, currency, price year, valuation basis or component sets fail.
The evaluator never selects a latest release, retrieves a source or interprets
supersession implicitly. An unchanged monetary rate in a new release still creates
a separately identified segment.

Original line IDs are unique across point and interval rows. One underlying use
cannot be supplied as both a point and an interval. Rows sharing a parent use_id
must have the same start, end, exact total, source and resolved context, and may
charge only disjoint components. The original identities and allocation references
are validated BEFORE expansion. Generated identities cannot bypass double-counting
or component protection.

Generated line and use IDs are separately namespaced SHA-256 hashes of explicit
JSON tuples containing the original identity and segment start/end. They do not
concatenate unrestricted user strings with ambiguous delimiters. A collision with
a caller-supplied identity is rejected. Each segment retains original interval ID,
parent use ID, selected quote ID, generated line ID, dates and exact quantity.

## Rounding and conserving allocation

The new method is dapane-intervals-v0.1.0. Every generated segment is an ordinary
source line: round half-even at the policy scale, then sum and allocate using the
existing evaluator. Exact segment quantities conserve the original total; exact
values match independently presegmented cases under the same exposure rule.

Rounded values are not claimed invariant to arbitrary splitting. Two segments
each worth exactly 0.005 round to 0.00 + 0.00 at scale two although their exact
sum is 0.01. The scalar report preserves that explicit rounding adjustment.

Allocation source IDs name original point or interval line IDs. An interval
reference expands to all its generated lines, including in capacity allocations.
The unchanged evaluator enforces direct/pool exclusivity, conserving pools,
unknown-capacity semantics and explicit unallocated values. Generated child IDs
are output identities, not an input namespace for selecting part of an interval.

## Self-contained evidence and replay

The interval report contains:

- request_snapshot: normalized ORIGINAL request template, including parent references.
- interval_snapshots: normalized original interval uses and exposure assumptions.
- segments: ordered parent-to-generated-line lineage with exact quantities.
- expanded_request: normalized ordinary point/capacity request.
- report: the unchanged native evaluator's result for expanded_request.
- schema_version, method_version, input_digest and output_digest.

The report is returned only after successful validation/evaluation. Invalid inputs
return a structured error and no partial financial output.

Reconstruct the original normalized envelope as schema_version "0.1",
request = request_snapshot and intervals = interval_snapshots. Its SHA-256 input
domain is the UTF-8 bytes of "dapane:interval-input:0.1\n" followed by canonical
JSON. The output domain is "dapane:interval-output:0.1\n", followed by canonical
JSON of the interval report with ONLY output_digest omitted. Canonicalization
sorts object keys, emits UTF-8 without insignificant whitespace and sorts set-like
collections. Original exact-number spellings remain part of input provenance.

The inner report must equal evaluate(expanded_request), including its own
input/output digests, sources and method identity. Hashes provide content identity,
not authorship, licensing permission or independent source validation.

## Limits and transport

The original envelope, including typed native inputs, is limited to 4 MiB.
Intervals are nonempty, at most 10,000, and original point rows plus aggregate
selected quotation references cannot exceed 10,000. Each selected overlapping
quotation generates one segment. Parent and expanded requests must satisfy the
ordinary collection, aggregate 20,000-record, 4 MiB and exact-number limits.
Generated quantities exceeding the 96-digit replay-input bound fail explicitly.
Expanded encoded sizes, including escaped identifiers, are budgeted before cloning
large context records. Original allocation-reference size changes are accounted
before row expansion, including replacements that shrink. Final byte accounting
must match the serialized expanded request.

The algorithm walks selected rate boundaries rather than individual days.
Duplicate JSON keys are rejected at every nesting level. Nested raw request 0.1
still rejects capacity_allocations even when the supplied array is empty; a wrapper
cannot silently relax that historical contract.

## Invocation and rollback

Native callers use evaluate_intervals or evaluate_intervals_json. CLI:

    dapane evaluate-intervals fixtures/intervals/rate-boundary.json
    dapane evaluate-intervals - < fixtures/intervals/rate-boundary.json

The existing Python wrapper retains point/capacity evaluation. Exposing the new
interval API through language wrappers is separate delivery work; the Rust library
and CLI work independently. Ordinary evaluate rejects interval fields.

Rollback pins the prior point/capacity implementation and externally supplies
explicit point segments. Retain original assumptions and use the same rounding
convention for comparison. A changed exposure/rounding convention is a new method.
No registry release, real-provider qualification or project licence is established.
