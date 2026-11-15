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
