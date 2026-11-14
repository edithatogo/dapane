# Dapane contract 0.3: explicit calendar-day interval valuation

Contract `0.3` and method `dapane-exact-v0.3.0` add automatic rate-boundary
segmentation to the same native `evaluate` / `evaluate_json` functions and
`dapane evaluate` command. The request supplies an original interval quantity,
the exposure assumption and every selected quotation identity. Rust performs
the segmentation and valuation; wrappers must not reproduce the arithmetic.

The existing [0.1 point-date contract](contract-v0.1.md) and
[0.2 capacity contract](contract-v0.2.md) keep their semantics, method identities
and digest domains. Their immutable schemas are unchanged. A caller opts into
the new profile with `schema_version: "0.3"`. The engine/package version is a
separate identity from this financial method version.

## What the exposure declaration means

The supported exposure mode is **`uniform_calendar_days`**. A caller explicitly
asserts that the supplied total quantity is spread equally across each calendar
day in the half-open interval `[start_date, end_date)`. Both dates are required;
`start_date < end_date`. Dates use the same strict Gregorian calendar and
years 0001–9999 as the point-date contract. Leap days count as calendar days.

This is a declared modelling assumption, not an inference from a quantity, an
event timestamp or observed throughput. The kernel does not infer hours worked,
business days, daylight-saving transitions, equipment availability or utilisation.
It does not establish that the assumption is appropriate for a real service.
An absent, unknown or misspelled exposure mode is an error.

For nonuniform activity, callers can supply separate supported observations
whose quantities and dates are established by their source evidence. Deriving
those observations remains a provider responsibility. The new profile does not
accept arbitrary exposure expressions or execute a process model.

## Request

The [request schema](../schemas/0.3/request.schema.json) retains all 0.2 fields.
`usage` remains required and may be an empty array. The optional
`interval_usage` array contains records with this shape:

```text
IntervalUsage {
  id: string, use_id: string,
  kind: "resource_use" | "activity_measure",
  target: string, unit: string,
  quantity: ExactNumber,
  start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD",
  exposure: "uniform_calendar_days",
  quote_ids: string[],
  source: SourceRef,
  event_id?: string | null, process_id?: string | null,
  activity_id?: string | null, object_ids?: string[],
  attribution_object_id?: string | null
}
```

`quantity` is the **total original quantity**, not a per-day rate. Exact numbers
remain decimal strings or integer-string rational pairs. Zero quantity is
allowed; it does not bypass schedule, source or context validation. Units remain
explicit matching identifiers; a rational such as `1/3` of an hour does not
authorise automatic conversion from minutes or from sample counts.

### Pinned rate schedule

Each `quote_ids` entry selects a supplied quotation. The kernel never fetches or
chooses a more recent source. It requires:

1. A nonempty list of distinct existing quotation IDs.
2. Every selected quotation to be known by `knowledge_cutoff`.
3. The same kind, target and unit as the interval usage, and the policy's currency,
   price year and valuation basis.
4. The same component set throughout that parent schedule. Different prices and
   `per_quantity` values may apply at different dates.
5. Every selected quotation to intersect the usage interval. Its existing
   `[valid_from, valid_to)` applicability is clipped to the parent boundaries.
6. The clipped periods to cover the parent interval exactly once. A gap or
   overlap is an error; a later quote does not override another selected quote.

Input order is irrelevant. The kernel orders the applicable segments by their
calendar boundaries. A quote ending exactly at a boundary is not effective at
that boundary. Unselected supplied quotes remain in the immutable source
snapshot, as in earlier profiles, but cannot fill a selected schedule's gap.

## Exact valuation and rounding

For parent total quantity `Q`, parent duration `D` calendar days, and a segment
with duration `d`, the exact segment quantity is `Q × d / D`. Its exact value is
that quantity multiplied by the selected quote's `amount / per_quantity`.
All operations use bounded rational arithmetic. There is no intermediate decimal
rounding or floating-point conversion.

The evaluator sums the exact segment values and rounds **once per original
parent usage/component line**, using the declared half-even policy and scale.
The parent reports the exact sum, rounded amount and rounding adjustment.
Segment values are explanatory parts of that parent; they are not independently
rounded or added again to expenditure.

For example, two exact segment values of `0.005` produce a parent exact value
of `0.010`, rounded to `0.01` at scale two. Dividing an otherwise identical rate
into two adjacent releases cannot turn that parent into `0.00`. Source snapshots,
segments and digests still differ when the quoted releases differ, because
their provenance is different.

Point-date lines retain their original per-line rounding. Totals sum the rounded
point and interval parent lines. Full-pool and capacity allocations can refer to
either type of parent through `source_line_ids`; they consume those existing
values once. Their 0.1/0.2 allocation and explicit residual rules continue to
apply, including unknown or unaccounted instrument capacity.

## Identity, components and context

Line IDs must be unique across point and interval records. A `use_id` identifies
one underlying observation. Disjoint component lines can share an interval
`use_id` only when they have the same total quantity, interval endpoints,
exposure, source and resolved context. Their component schedules may have
different rate-change dates. Repeated or loaded components remain errors.

An interval and a point-date record cannot share a `use_id`: their temporal
representations are not the same observation. Supplying a different ID does
not establish that two real-world records are distinct; identity reconciliation
remains a source/provider responsibility.

Event, process, activity, object links and direct attribution have the same
validation and inheritance rules as the existing Usage record. Linking an event
does not derive the interval from that event. Context associations do not
multiply values. A directly attributed parent cannot also enter a pool, and a
parent cannot enter more than one allocation.

## Report and deterministic identity

The [report schema](../schemas/0.3/report.schema.json) retains the 0.2 fields and
adds optional `interval_lines`. Existing `lines` contains only point-date lines.
Each interval parent contains its original identity, reduced rational quantity,
date boundaries, exposure, component set, source and resolved context, plus:

```text
segments: [{
  quote_id: string,
  start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD",
  quantity: Rational, exact: Rational
}],
exact: Rational,
rounded: string,
rounding_adjustment: Rational
```

The parent has no single `quote_id` or point `service_date`. Each segment records
its own selected quote and clipped dates. Parent quantities and exact values
reconcile to their segment sums. Quotations retain their source snapshots.

The normalized input sorts parent records by ID and `quote_ids` lexically,
alongside the existing normalization rules. An empty optional interval array is
omitted from normalized transport. Output parents are ordered by ID; segments
are chronological. Digests use SHA256 over canonical JSON with these domains:

- Input: `dapane:input:0.3\n` followed by the normalized request.
- Output: `dapane:output:0.3\n` followed by the report without `output_digest`.

Decimal/rational input spellings remain part of input identity. Equivalent
numeric spellings can have the same economic result and different digests.
There is no implicit current date, network lookup, random choice or execution
timestamp in the result.

`status: "complete"` means the accepted request was fully evaluated. It does not
mean every capacity observation is known or that a source or method is
empirically validated. Capacity uncertainty remains explicit in the 0.2 fields.
Invalid requests return a structured diagnostic with no partial financial report;
the CLI writes that diagnostic to stderr and exits unsuccessfully.

## Bounds and compatibility

The existing 4 MiB transport, 96-digit numeric input, decimal scale 36,
4096-bit rational intermediate and identifier/date limits remain in force.
Point plus interval parent usage is limited to 10,000 records in total;
all top-level records together remain limited to 20,000. Each selected schedule
has at most 10,000 quotation IDs. Aggregate interval quotation selections, and
therefore segment count, are limited to 20,000. Bounds apply to native typed
calls as well as JSON. Evaluation traverses rate boundaries rather than every
calendar date.

Adding `interval_usage` to a 0.1/0.2 JSON request is rejected, even if the array
is empty. Old schemas and callers keep their existing interpretation. Consumers
that only understand 0.1/0.2 must explicitly qualify 0.3 before accepting it;
in particular, this kernel profile does not silently widen a separate run-bundle
schema or provider contract. Pin the last qualified schema/method for rollback.

## Independent references and checks

The [synthetic references](../fixtures/intervals/README.md) contain independently
derived rate-boundary, rational-exposure and parent-rounding cases. Check their
structure and then the actual native executable:

```sh
python scripts/validate_intervals.py
python scripts/validate_intervals.py --cli target/release/dapane
```

The first command checks schema structure only and explicitly reports that
native checks were not run. With `--cli`, the checker validates expected exact
amounts, segment quantities, source/context preservation, pool conservation,
independently computed canonical digests, repeated execution and reordered input,
equal-rate subdivision invariance, and semantic rejection with no partial result.
The existing contract verifier and installed-artifact suites remain necessary
for old-profile compatibility. Passing synthetic references verifies computation;
it does not validate a costing method or real provider data.
