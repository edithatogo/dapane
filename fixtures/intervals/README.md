# Independent synthetic interval references

Every record in this directory is **synthetic**, public and unvalidated. No
patient, workforce, instrument or financial data is represented. These examples
qualify the arithmetic and transport specified by [contract 0.3](../../docs/contract-v0.3.md),
not the suitability of uniform exposure for any real-world service.

Expected values in [expected.json](expected.json) were derived from the following
small calculations before evaluating the implementation. They are not copied
from the Rust output. All date intervals are half-open and all quantities are
declared uniformly distributed over calendar days.

| Fixture | Independent derivation | Expected parent result |
| --- | --- | --- |
| [rate-boundary.json](rate-boundary.json) | Ten hours over ten days; four hours at 2 and six at 3: `4 × 2 + 6 × 3 = 26`. Quote periods extend beyond the usage interval and must be clipped. | Exact `26/1`; `26.00`, directly attributed once to the episode. Event process/activity are preserved through context inheritance. |
| [rational.json](rational.json) | One third of an hour over three days. The first two days receive two ninths of an hour at rate three; the final day receives one ninth at rate six. Each segment costs two thirds, giving a total of four thirds. | Rounded result `1.33`; the rounding adjustment is negative one three-hundredth. Exact rational pairs are retained in the expected fixture. |
| [rounding.json](rounding.json) | Two hours over two days, one hour per day at `0.005`. Each exact segment is `1/200`; their parent is `1/100` and rounds once to one cent. | `0.01`. An equal three-recipient pool assigns its single minor unit to lexical recipient `a`; `b` and `c` receive zero. |

The rounding case also has an equivalent uninterrupted rate: extend the first
quote to the second quote's end, remove the second quote and select only the
first. Parent totals, allocation and object totals must remain identical.
Provenance and output digests may differ because the selected source schedule
differs. Rounding the two segments separately would produce the wrong parent
value under this explicit method.

`scripts/validate_intervals.py --cli <binary>` reads the independent expected
values, validates the actual native reports against the locally resolved schema,
and checks exact segment conservation, source/context preservation, canonical
input/output digests, replay, schedule-order invariance, and gap/overlap/source
rejections. It never fetches schema references or quotations. Running it without
`--cli` supplies schema evidence only.

The broader native interval suite additionally exercises date boundaries,
leap years, duplicate/loaded components, mismatched parent identity, allocation
interaction, typed calls and bounded failures. Actual executed results belong in
the kernel track evidence; the existence of a fixture is not a passing result.
