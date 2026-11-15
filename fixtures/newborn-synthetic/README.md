# Synthetic newborn recipes, profile 0.1.0

These invented examples contain no patient records, real programme inputs, provider
quotations or clinical recommendations. The [source manifest](sources.json) declares
all rates, quantities, population and capacity assumptions synthetic and unvalidated.

The [recipe](recipe.json) is a versioned fixture profile. Its prepared requests run
through the unchanged Rust 0.1/0.2 contracts. This is not a native recipe parser,
clinical pathway executor or reporting API. [Scenario records](scenarios.json) retain
explicit branch choices, specimen/result states, episode identities and population
and observation-window references separately from native valuation requests.

## Identities and composition

Infants, episodes, collection attempts, specimens, cards, assay executions, batches,
results, recalls, confirmations and follow-up records have distinct IDs. The composed
case has two primary assays per specimen and two infants sharing one batch. Relations
and context-only events never create expenditure. No clinical probability, timing,
quantity or branch is inferred. Reporting, recall and follow-up have explicit cost
exclusions, which do not establish zero real cost.

The original [two-infant fixture](../newborn-screening.json) and integrator-owned
[shared expectations](../expected.json) remain unchanged. The richer composition
preserves the same independent calculations:

| Source expense | Calculation | Synthetic AUD |
| --- | --- | ---: |
| Collection A | 5 minutes × (1.50 salary + 0.50 oncost) | 10.00 |
| Collection B | 5 minutes × (1.50 + 0.50) | 10.00 |
| Shared batch | transport 10 + QC 10 + setup 20 + controls 10 + materials 40 + overhead 10 | 100.00 |
| Selected confirmation labour B | 15 minutes × (1.50 + 0.50) | 30.00 |
| Total | 10 + 10 + 100 + 30 | 150.00 |

Staff quotations cover disjoint components of the same underlying use. Each shared
resource is charged once. Equal full-pool weights assign 50 to each infant, giving
60/90 conserving views. These views are not added to source expenditure. Confirmation
here means the supplied labour only, not a complete diagnostic-workup costing.

## Independent branch references

Each case below has a prepared JSON request in this directory. Amounts are invented
AUD in 2026 prices. Infant views plus unallocated cost conserve the source total.

| Case | Total | Infant views A / B / C | Unallocated | Independent boundary |
| --- | ---: | --- | ---: | --- |
| `composed-two-infant` | 150.00 | 60.00 / 90.00 / — | 0.00 | Richer identities preserve the baseline |
| `repeat-collection` | 170.00 | 80.00 / 90.00 / — | 0.00 | Inadequate specimen retained; new attempt/card/specimen; +10 labour +5 transport +5 QC |
| `failed-assay-repeat` | 170.00 | 80.00 / 90.00 / — | 0.00 | Failed result and original expense retained; +20 repeat assay on the same specimen |
| `unresolved-failure` | 150.00 | 60.00 / 90.00 / — | 0.00 | Failed cost retained; A has no valid screen or completed pathway |
| `reflex-assay` | 170.00 | 60.00 / 110.00 / — | 0.00 | Trigger result retained; new assay on B's specimen: +6 labour +14 materials |
| `partial-batch` | 110.00 | 110.00 / — / — | 0.00 | One collection and the whole 100 batch pool assigned to A |
| `added-panel` | 170.00 | 70.00 / 100.00 / — | 0.00 | One extra assay per specimen at 10 each; fixed batch costs unchanged |
| `family-perspective` | 180.00 | 75.00 / 105.00 / — | 0.00 | Provider plus family: 30 minutes × 0.50 for each family |
| `capacity-below` | 110.00 | 60.00 / — / — | 50.00 | 1 known instrument-hour against 2 available; 100 instrument pool |
| `capacity-at` | 120.00 | 60.00 / 60.00 / — | 0.00 | 2 known hours against 2 available; 100 instrument pool |
| `capacity-above` | 230.00 | 60.00 / 60.00 / 60.00 | 50.00 | Two explicit blocks: 200 pool and 4 available hours; 3 known hours |
| `capacity-missing-use` | 120.00 | 60.00 / 10.00 / — | 50.00 | B's instrument share is null; 10 is assigned collection cost only |
| `capacity-unknown` | 120.00 | 10.00 / 10.00 / — | 100.00 | All instrument shares are null; known use is retained |

The instrument scenarios cover collection labour plus prepared instrument-block
costs only. Other laboratory, confirmation and overhead components are explicitly
excluded from that comparison. Instrument availability and recorded hours are
supplied independently, never inferred from samples or full-pool weights. The
second block is a prepared scenario, not a runtime capacity-planning algorithm.

Adding the second participant costs 10; adding the third in the stated two-block
scenario costs 110. Programme averages are 110, 60 and 230/3. In the added-panel
comparison, 150 → 170 means a marginal 10 per participant and a new programme
average of 85. These are scoped synthetic comparisons, not economic efficiency
claims. Unallocated amounts are not labelled idle cost, waste, utilisation or cash
savings. Missing observations remain distinct from known zero; over-capacity
inputs fail instead of triggering implicit provisioning or normalisation.

## Denominators and window

Population `invented-birth-cohort-v1` and window `screening-window-2026-06-v1`
are version 1.0.0. The half-open window is `[2026-06-01, 2026-07-01)`.
Three invented births are inside it; the fourth birth, on the exclusive end date,
is excluded. Population, window, recipe and source versions are explicit.

| Denominator | Membership definition |
| --- | --- |
| Eligible birth | Distinct infant with supplied birth date inside the window |
| Participating infant | Distinct infant with participation date inside the window |
| Valid screen | Distinct infant with valid-screen date inside the window; all selected final required results are valid and trace to that infant |
| Completed pathway | Distinct infant with an explicit completion date inside the window |
| Confirmed diagnosis | Distinct infant with an explicit synthetic confirmation date inside the window |

Repeats retain the infant and screening episode while adding resource-use identities.
The unresolved-failure case has two participants but one valid screen and completed
pathway: 150/2 = 75 per participant and 150/1 = 150 per valid screen or completed
pathway. A successful repeat restores valid-screen membership without adding an infant.

Every reference uses the entire case ledger under its declared perspective. Baseline
references are 50 per eligible birth; 75 per participant, valid screen or completed
pathway; and 150 per confirmed diagnosis. Zero denominators have undefined (`null`)
references. These independently tested ratios are not a delivered native denominator
or reporting API. No real eligibility or clinical benefit is inferred.

## Verification boundary

[Expectations](expected.json) are independent hand calculations. Tests perform
reference arithmetic, not application costing. Source references retain the manifest
SHA256; this identifies invented inputs rather than certifying external sources.
Point lines retain half-even rounding before summation; the existing interval method
retains half-even rounding for each generated segment. No shared numerical code changes.

Use an installed native wheel from outside the checkout:

```sh
python -m pytest --import-mode=importlib /path/to/dapane/tests/python/test_newborn_synthetic.py -q
dapane evaluate /path/to/dapane/fixtures/newborn-synthetic/composed-two-infant.json
```

See the [owning track](../../conductor/tracks/newborn_screening_20261108/index.md)
for source-bound evidence and limits. Real providers, programme data and reporting
qualification remain separate work.
