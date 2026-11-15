# Independent interval references

Every date, rate, quantity and source here is synthetic and unvalidated. The
reference is authored from elementary arithmetic, not captured engine output.

`rate-boundary.json` explicitly declares one hour uniformly exposed over three
calendar days: 31 January, 1 February and 2 February. The interval is half-open.
The selected rate is 90 per hour before 1 February and 120 from that date.
The independent answer is `(1/3 × 90) + (2/3 × 120) = 30 + 80 = 110`.
`expected.json` records exact segment quantities and results.

Uniform calendar exposure is a caller assertion. The core must not infer an
hourly time series, utilisation, overnight shift, timezone or working calendar.
The [native tests](../../crates/dapane-core/tests/intervals.rs) add explicit
mutations for leap-day counting, quote boundaries, malformed dates, missing and
overlapping coverage, source knowledge, exact numbers, parent use/component
identity, allocation and deterministic replay.

The rounding counterexample is deliberate: two one-day rate segments at 0.01
with half a unit each produce 0.005 + 0.005 = 0.01 exactly, but per-segment
half-even rounding produces 0.00 + 0.00 = 0.00. Exact quantity/value conservation
does not imply that arbitrary extra segmentation preserves rounded totals.
Rate identities and original parent interval identities therefore remain part
of immutable method/input/output evidence.

The funding case uses 2.50 weighted activity units at 17.00 per unit, giving
42.50. It never invents resource-use records from activity measures.

The capacity case uses an independently supplied denominator of 10 instrument
hours for the 110.00 source pool. Three known hours receive 33.00; the other
recipient's missing use remains unknown, leaving 77.00 unallocated. Available
capacity is not inferred from the interval quantity or sample throughput.

These cases qualify computational behaviour only. They provide no empirical
evidence for workforce exposure patterns, provider rules or economic methods.
