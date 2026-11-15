# Synthetic genomics capacity candidates

Every value, sample cohort and observation here is invented. These are candidate
scenarios for contract/arithmetic tests, **not validated economic formulae** or
empirical genomics costing. No private email, attachment, workbook or patient
information is used. The old [genomics fixture](../genomics.json) continues to
test a fully charged batch split equally and is unchanged.

## Independent preparation assumptions

The [strict scenario manifest](scenario.json) uses a one-month period in synthetic
2026 AUD with these deliberately separate inputs:

| Component | Preparation assumption | Candidate period quote |
| --- | --- | ---: |
| Device | Acquisition 12,000 / useful life 60 months; zero residual and no discounting | 200 |
| Maintenance | Contract total 2,400 / contract duration 24 months | 100 |
| Implementation | 600 once in the first period; excluded from every recurring pool | 600 first period; absent in recurring-only case |

The recurring pool is `200 + 100 = 300`. The first-period source total is
`300 + 600 = 900`; the recurrent-only source total is `300`.
Using device life for maintenance would wrongly give `2,400 / 60 = 40` in this
candidate. These quotients are independent hand calculations recorded before
the capacity evaluator existed. The kernel receives prepared quotes; it does
not implement the preparation methods or derive recurrence from metadata.

Changing useful life requires explicitly preparing/reviewing a new device quote;
it does not change the maintenance contract duration. Changing the maintenance
term does not change device life. There is no implicit capital recovery factor,
discounting, tax, replacement, workforce, consumables or outcomes model.

## Allocation comparisons

The source pool is identical across the first-period comparison files. Only the
declared allocation assumptions change. Known capacity is independently
stipulated as **100 instrument-hours for that same month**. It is never obtained
from the 50 observed samples or from the sum of recorded use.

| Request | A assigned | B assigned | Recurring pool unallocated | Whole-ledger unattributed |
| --- | ---: | ---: | ---: | ---: |
| [Time, known capacity](time-known.json): A 10 h, B 20 h, records incomplete | 30 | 60 | 210 | 810 |
| [Time, missing B use](time-missing-use.json): A 10 h, B unknown | 30 | unknown | 270 | 870 |
| [Time, unknown capacity](time-unknown-capacity.json): A 10 h, B unknown, availability unknown | unknown | unknown | 300 | 900 |
| [Full-pool sample allocation](sample-full-first.json): A 20 samples, B 30 | 120 | 180 | 0 | 600 |
| [Full-pool recurrent period](sample-full-recurring.json): same sample weights, no implementation charge | 120 | 180 | 0 | 0 |

Independent arithmetic: time-based assigned costs are `300 * 10/100 = 30` and
`300 * 20/100 = 60`; known accounted use is 30 hours, leaving 70 unaccounted hours
and 210 unallocated cost. With B missing, only 10 hours are accounted for and
`300 - 30 = 270` remains unallocated. Neither situation establishes utilisation
or idle time. Unknown capacity leaves the full recurring 300 unallocated.

The sample scenario explicitly recovers the whole pool across observed cohorts:
`300 * 20/(20+30) = 120`, `300 * 30/(20+30) = 180`. That is a different assumption,
not an estimate of available instrument-hours or proof of full utilisation.
These two methods must not be added together.

The separate implementation line explains the additional 600 in first-period
`totals.unattributed`. The recurring capacity remainder is already included in
that total. Missing B use is encoded as unknown, never as zero. A ledger object
total of zero means no amount has been assigned; consult nullable capacity
shares before interpreting costs.

## Files and verification

- [Expected values](expected.json) are independently authored candidate oracles.
- [0.1 digest receipts](v0.1-digests.json) are regression evidence from the
  integrated runtime; they are not independent scientific references.
- [Contract 0.2](../../docs/contract-v0.2.md) defines exact semantics, rounding,
  compatibility, limits and rejected inputs.
- Rust tests in `crates/dapane-core/tests/capacity.rs` cover numerical behaviour,
  canonical ordering, unknown/zero states, invalid inputs and 0.1 identity.
- Installed Python tests in `tests/python/test_genomics_capacity.py` validate
  both request/report versions and the candidate manifest using local schemas,
  check the independent preparation arithmetic and invoke the native Rust core.

Run the CLI, for example:

```sh
cargo build --locked --release -p dapane-cli
target/release/dapane evaluate fixtures/genomics-capacity/time-missing-use.json
```

The manifest is a repository fixture-preparation profile, not a production
provider adapter or accepted evaluation request. No existing provider capability,
CareOps deployment or external validation is claimed by these cases.
