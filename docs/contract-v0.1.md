# Dapane JSON contract 0.1

This is the bounded contract implemented by `dapane-core`. It supports exact,
nonnegative point-date quotation and shared-pool allocation. It does not execute
simulations or derive resource quantities from event duration. Kairos, observed
event logs and static worksheets can independently produce this contract.

## Wire types and public API

`evaluate_json(&str) -> Result<String, DapaneError>` parses, validates and returns
one JSON report. `evaluate(&Request) -> Result<Report, DapaneError>` is the typed
Rust entry point. Errors expose public string fields `code`, `message`, and `path`;
they implement `Serialize`, `Display` (JSON), and `std::error::Error`. Error paths
are JSON-pointer-like locations in the supplied request; malformed JSON uses `/`.
Successful reports have `status: "complete"`; invalid requests do not produce
partial financial totals.

An `ExactNumber` is a decimal **string** (`"2.50"`, `"0"`) or an object
`{"numerator":"1","denominator":"3"}`. JSON numeric literals, exponents,
signs, whitespace, NaN and infinity are rejected. Decimal strings require digits
on both sides of any decimal point. Integers in rational pairs are unsigned
decimal strings; denominators must be positive. Output exact values are always
reduced rational pairs with positive denominators. Output adjustments may have a
negative numerator. Missing input is an error; explicit zero remains valid.

Every object below rejects unknown fields. Optional arrays default to `[]`;
optional scalar fields, including source digest and locator, default to `null`.
Identifiers are nonempty, trimmed and free of control characters; their UTF-8
encoding is at most 128 bytes. Internal spaces and Unicode are preserved and
matched literally. Required fields are listed
without a question mark. A question mark denotes an optional field, not a literal
part of its JSON name.

## Request

```text
Request {
  schema_version: "0.1",
  run_id: string,
  knowledge_cutoff: "YYYY-MM-DD",
  policy: ValuationPolicy,
  quotes: UnitQuote[],
  usage: Usage[],
  objects?: CostObject[],
  processes?: ProcessInstance[],
  events?: Event[],
  object_relations?: ObjectRelation[],
  allocations?: Allocation[]
}
ValuationPolicy {
  id: string, version: string,
  currency: string, price_year: integer,
  perspective: string,
  basis: "economic_cost" | "financial_cost" | "funding" | "charge",
  rounding: { scale: integer, mode: "half_even" }
}
SourceRef {
  id: string, version: string,
  evidence: "synthetic" | "observed" | "derived",
  access: "public" | "restricted" | "private",
  validation: "unvalidated" | "source_verified" | "empirically_validated",
  content_digest?: string,
  locator?: string
}
UnitQuote {
  id: string,
  kind: "resource_use" | "activity_measure",
  target: string, unit: string,
  amount: ExactNumber, per_quantity: ExactNumber,
  currency: string, price_year: integer,
  basis: "economic_cost" | "financial_cost" | "funding" | "charge",
  components: string[],
  valid_from: "YYYY-MM-DD", valid_to: "YYYY-MM-DD",
  known_from: "YYYY-MM-DD",
  source: SourceRef
}
Usage {
  id: string, use_id: string,
  kind: "resource_use" | "activity_measure",
  target: string, unit: string,
  quantity: ExactNumber,
  service_date: "YYYY-MM-DD", quote_id: string,
  source: SourceRef,
  event_id?: string, process_id?: string, activity_id?: string,
  object_ids?: string[], attribution_object_id?: string
}
CostObject { id: string, kind: string }
ProcessInstance { id: string, model_id: string, model_version: string }
Event {
  id: string, occurred_on: "YYYY-MM-DD",
  process_id?: string, activity_id?: string, object_ids?: string[]
}
ObjectRelation {
  from_object_id: string, to_object_id: string, relationship: string
}
Allocation {
  id: string, source_line_ids: string[],
  weights: { object_id: string, weight: ExactNumber }[]
}
```

Input and quotation kind, target and unit must match exactly. Units are explicit
case-sensitive identifiers, not a conversion engine. Currency, economic price
year and valuation basis must match the policy. A financial cost and a funding
quotation therefore require separate runs/views. `per_quantity` is strictly
positive. A quote's half-open interval is `valid_from <= service_date < valid_to`;
`known_from <= knowledge_cutoff` is a separate availability check. Quote IDs are
selected explicitly, never by latest-date lookup. Price year, source release and
service date are different fields with different meanings.

Source/evidence/access/validation fields are caller declarations preserved in the
result; they are not certificates issued by Dapane. `content_digest`, if supplied,
is `sha256:` plus 64 lowercase hexadecimal characters. The kernel does not fetch
the source or verify that digest against external content. Explicit source IDs
and versions plus the bundle digest identify the supplied quotation snapshot.

## Identity, context and accounting

`Usage.id` identifies a valuation line. `use_id` identifies the underlying use or
activity measure. Multiple lines can price disjoint components of the same use;
their kind, target, unit, exact quantity, service date, source and context must
agree. Process/activity agreement uses the resolved identity: inheriting an ID
from an event and explicitly declaring that same ID are equivalent. Their
quotations' `components` must be disjoint. A loaded rate containing
`["salary","oncost"]` cannot be combined with a second `"oncost"` quotation for
that use. Repeating a use/component or a line ID is an error. Aliased use IDs are
not automatically detected; adapters own faithful source identity mapping.
Component tags identify inclusion and prevent repeated charges. The kernel does
not infer separate component values from an opaque combined quotation; supply
separate, disjoint component quotations when a numerical breakdown is needed.

Objects, events and process instances are optional. Event/process/object
references must resolve. An activity ID requires an associated process instance.
Explicit line process/activity IDs must agree with the referenced event when
both declare them. Report lines inherit an event's process/activity IDs when the
line did not declare them. Event dates record occurrence; the explicitly supplied
line service date controls pricing. Object relations and `object_ids` are context:
they do not copy or multiply any monetary value. The kernel does not execute
model IDs or infer quantities from relationships.

`attribution_object_id` assigns a complete source line to one object. An allocation
assigns one or more otherwise unattributed source lines across explicit recipient
weights. A source line can occur in at most one pool, cannot be repeated within
that pool and cannot be both directly attributed and pooled. Recipient objects
must exist, each can appear once per pool, weights are nonnegative and their sum
must be positive. Pools always allocate their full value. These rules make object
totals a conserving view of the source ledger, not additional source expenditure.

## Calculation and rounding

Each source line has exact value `quantity * quote.amount / quote.per_quantity`.
The selected method is `dapane-exact-v0.1.0`: round each source line half-even at
the policy scale, then sum those rounded source lines. The result also retains
the exact pre-rounding total and the rounding adjustment. A rounded sum is not
silently replaced by a rounded exact aggregate.

For an allocation, sum its already rounded source lines to obtain its integer
minor-unit pool. Multiply that integer pool by each normalized exact weight,
floor each share, and assign remaining minor units by descending fractional
remainder, breaking ties by ascending object ID. Zero-weight recipients receive
zero. `exact_share` refers to the exact share of the **rounded pool**;
`pool_exact` separately preserves the source lines' exact total. Every pool's
`residual` is zero under this full-allocation profile. A 0.05 pool split equally
over objects `a`, `b`, `c` produces 0.02, 0.02, 0.01 at scale two.

## Report

```text
Report {
  schema_version, run_id, status: "complete",
  engine_version, method_version,
  input_digest, output_digest,
  policy: ValuationPolicy,
  lines: ValuationLine[],
  quote_snapshots: UnitQuote[],
  context: {
    objects: CostObject[], processes: ProcessInstance[],
    events: Event[], object_relations: ObjectRelation[]
  },
  totals: {
    exact: Rational, rounded: string, rounding_adjustment: Rational,
    directly_attributed: string, allocated: string, unattributed: string
  },
  allocations: AllocationResult[],
  object_totals: ObjectTotal[]
}
ValuationLine {
  id, use_id, kind, target, unit, quote_id,
  quantity: Rational, components: string[], service_date,
  exact: Rational, rounded: string, rounding_adjustment: Rational,
  source: SourceRef,
  event_id, process_id, activity_id, object_ids, attribution_object_id
}
AllocationResult {
  id, source_line_ids,
  pool_exact: Rational, pool_rounded: string,
  shares: {
    object_id, weight: Rational, exact_share: Rational, rounded: string
  }[],
  residual: string
}
ObjectTotal { object_id, direct: string, allocated: string, total: string }
Rational { numerator: string, denominator: string }
```

`quote_snapshots` retains all supplied quotes, including unused ones. Context-only
objects appear in `object_totals` with zero. Summing `ObjectTotal.total` and
`totals.unattributed` equals `totals.rounded`. Do not add these object totals or
allocation results to the source ledger again. Source/quote records retain the
evidence necessary to distinguish synthetic demonstrations from observed input.

## Determinism, bounds and unsupported methods

The evaluator sorts keyed collections by identifier, context/component/source
line sets lexically, relationships by their triple and allocation weights by
object ID. It serializes canonical JSON with recursively sorted object keys and
no whitespace. Decimal spelling is preserved in input identity (`"1.0"` and
`"1.00"` are distinguishable supplied representations). The input digest is SHA256
over `dapane:input:0.1\n` followed by the canonical normalized request. The output
digest is SHA256 over `dapane:output:0.1\n` followed by the canonical report with
`output_digest` omitted. Prefix both hexadecimal digests with `sha256:`. Engine,
method, policy and source identities therefore participate in reproducibility.
There is no timestamp, random seed, implicit current date or external lookup.

Limits: JSON input 4 MiB; each top-level collection at most 10,000 records and all
top-level records together at most 20,000; each nested collection at most 10,000;
identifiers/tokens at most 128 bytes; locator at most 2,048 bytes; numeric inputs
at most 96 digits, decimal scale at most 36; intermediate rational numerator and
denominator at most 4,096 bits; currency exactly three uppercase ASCII letters;
economic price year 1–9999; rounding scale 0–12. Dates are strict `YYYY-MM-DD`,
years 0001–9999. Duplicate JSON object keys are rejected as well as duplicate
record identities. The same limits apply to typed evaluation after parsing.

This profile does not support negative corrections/retractions, interval usage,
automatic rate-boundary segmentation, tax, foreign exchange, currency escalation,
discounting, capital annualization, stochastic distributions, arbitrary formula
evaluation or process execution. Pre-segment point-date usage explicitly before
evaluation. Unknown fields/methods are errors, not ignored configuration. Provider
adapters must reject source semantics that cannot be represented without loss.
Future supported policies require a qualified method/schema update and retained
reference fixtures; this contract is not a claim that planned adapters exist.
