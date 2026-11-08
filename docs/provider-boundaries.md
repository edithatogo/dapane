# Provider boundaries and source mappings

Inspected on 2026-11-08. The links below pin the source revisions used for this
review. They establish what the provider exposes; they do not establish that a
Dapane adapter has been implemented or that a source rate has been validated.
The executable Dapane contract is owned by this repository.

## Dapane does not require Kairos

Dapane values explicit quantities under explicit valuation policies. Its inputs
can come from observed records, static recipes or simulations. Kairos is an
optional producer of simulated use. The valuation kernel must not import its
scheduler, ECS, RNG, domain models or economic assumptions.

Event, process and object context are complementary. A resource use can have an
event identity, refer to an activity in a process execution, and relate to several
objects such as an infant, specimen, assay and batch. These relationships must
not multiply the use. One batch use is recorded once; a separately declared
allocation produces infant views of its value.

| Producer basis | What the producer supplies | What must remain explicit |
| --- | --- | --- |
| Observed | A measured quantity or bounded interval, source record identity and observation method. | Observation window, missing/censored records, unit, corrections and links to relevant objects. |
| Static recipe | Resource quantities per declared output or activity, with a recipe version and assumption/source evidence. | Recipe denominator, throughput, batch utilisation and whether quantities are observations or assumptions. A recipe is not an observed event log. |
| Simulated | Committed use or activity output from a particular run, scenario and model revision. | Time scale, event and branch identities, uncertainty draw, admission/release semantics and rollback handling. Simulation is not empirical validation. |

These are semantic mappings, not declarations that every listed metadata field
is supported by the first runtime schema. An adapter must reject or explicitly
preserve unsupported meaning; it must not silently discard it.

## Kairos: existing mechanics and pending usage export

Snapshot: [`6b34bcb8fbae8efef31984d74135615f07997f2b`](https://github.com/edithatogo/kairos/tree/6b34bcb8fbae8efef31984d74135615f07997f2b).

The [movement/resource usage contract](https://github.com/edithatogo/kairos/blob/6b34bcb8fbae8efef31984d74135615f07997f2b/conductor/contracts/movement-resource-usage.md)
explicitly labels implementation as pending under Track 114 and scientific
obligation S17. It also says its semantic names are not existing public Rust
types or schemas. [Track 114's plan](https://github.com/edithatogo/kairos/blob/6b34bcb8fbae8efef31984d74135615f07997f2b/conductor/tracks/114-dependency-and-consumer-contracts/plan.md)
leaves scheduled movement and usage interval/export tasks open.

This is consistent with the inspected
[`staged_runtime.rs`](https://github.com/edithatogo/kairos/blob/6b34bcb8fbae8efef31984d74135615f07997f2b/crates/kairo-ecs-des/src/staged_runtime.rs):

- `StagedRequestSnapshot` exposes actor, resource, state and optional lease.
- `StagedResourceSnapshot` exposes capacity, available capacity, active leases
  and queued requests.
- A resource can have capacity greater than one, but each admitted lease uses
  one capacity unit: availability is capacity minus active lease count.
- The snapshots contain no admission/release timestamp pair, quantitative use
  record, price or economic value. A snapshot alone cannot reconstruct a
  complete resource-use ledger.

The future adapter should map actor/resource/request/lease identities and
admission/release events to neutral use records. It must distinguish consumption,
occupancy and transfer; transferring an object is not consuming another unit.
Occupancy starts at admission rather than queue submission and integrates over
half-open intervals. Open leases are censored at a declared observation boundary.
Preemption and quantity changes split intervals. Repeated releases must not add
usage. Export either committed records only or an explicit correction/retraction
protocol; provisional and rolled-back usage cannot be summed together. Preserve
integer ticks and a declared scale before converting to exact exposure quantities.

**Qualification remains required:** a real public Kairos trajectory, exported
through a versioned interface, must reproduce independently calculated occupancy
and consumption and feed Dapane without provider-private APIs. A hand-authored
simulated example tests Dapane's contract only; it is not a Kairos integration test.

## Workforce: preserve the source and employment rules

Snapshot: [`ae523fa65b45500a0b37bdfece23316808d12b73`](https://github.com/edithatogo/microcosting_healthworkforce/tree/ae523fa65b45500a0b37bdfece23316808d12b73).

[`src/unit_quotes.py`](https://github.com/edithatogo/microcosting_healthworkforce/blob/ae523fa65b45500a0b37bdfece23316808d12b73/src/unit_quotes.py)
already provides a useful narrow boundary. `price_units` multiplies the quoted
amount and supplied quantity using `Fraction`; it rejects duplicate quantity
identities, denominator mismatches and valuation dates outside the selected
quote. Its documentation leaves eligibility, conversions, inclusions and
cross-ledger duplicate economic costs to callers.

| Existing workforce field | Dapane meaning | Adapter obligation |
| --- | --- | --- |
| `UnitQuote.quote_id`, `component`, `unit`, `amount` | Identified unit quotation and denominator. | Preserve exact decimal text, component identity and unit; declare the valuation basis rather than infer it from a name. |
| `starts_on`, `ends_on`, `known_from` | Half-open effective interval and knowledge date. | Keep effective time distinct from knowledge time; reject an unavailable or inapplicable quote. |
| `source_id`, `source_sha256`, `citation`, `status` | Source edition and acceptance evidence. | Preserve the source digest and acceptance state. An accepted provider quote is not automatically accepted for every Dapane study. |
| `UnitQuoteRelease.release_id`, `currency`, `as_known_on`, `jurisdiction`, `employer`, `classification` | Immutable, scoped price release. | Retain scope and identity; do not broaden its employment applicability. |
| `QuoteQuantity.quantity_id`, `quote_id`, `unit`, `quantity`, `valued_on` | An explicit, dated resource exposure or other unit-matched quantity. | Preserve `Decimal`/`Fraction` exactly; perform any unit conversion explicitly. |
| `quantity_kind`, `basis` | Observed use versus analyst assumption and its explanation. | Keep this distinction in provenance; do not relabel assumptions as observations. |

Workforce remains the owner of award/condition interpretation, worker eligibility,
rosters, paid/productive time and derived quotations. Dapane owns generic
valuation and reconciliation. An annual salary cannot become an hourly price
without a stated annual-hours/capacity method. A new Rust multiplication test
does not demonstrate payroll or employment-rule parity.

The [manifest](https://github.com/edithatogo/microcosting_healthworkforce/blob/ae523fa65b45500a0b37bdfece23316808d12b73/pyproject.toml)
currently requires exactly Python 3.15.2, Pydantic `>=2.14.3,<3` and installs the
generic top-level package `src`. Its dependency closure also contains table and
workbook libraries. Keep these provider requirements outside Dapane's minimal
kernel and test any future installed adapter with explicit supported versions.
Renaming the provider namespace is a separate compatibility change.

## Genomics: extract domain inputs, do not transplant the workbook engine

Snapshot: [`f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41`](https://github.com/edithatogo/microcosting_genomics/tree/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41).

The existing [`CalculationEngine`](https://github.com/edithatogo/microcosting_genomics/blob/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41/src/genomics_microcosting/calculation_engine.py)
evaluates spreadsheet formulas using sheet/cell references and strategies.
[`CostComponent`](https://github.com/edithatogo/microcosting_genomics/blob/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41/src/genomics_microcosting/cost_components.py)
mostly abstracts arithmetic, reference, aggregate and financial formula handling.
Neither is a ready-made neutral resource-use contract. The valuable starting
point is the explicit workbook-to-domain mapping in
[`config.yaml`](https://github.com/edithatogo/microcosting_genomics/blob/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41/config.yaml):

| Existing configured field | Dapane meaning | Required decision |
| --- | --- | --- |
| `test`, `category`, `sub_category`, `step` | Assay/recipe identity, resource category and process activity. | Version the recipe and retain source workbook, sheet and cell evidence. |
| `quantity_per_test`, `usage_per_test` | Static quantity per declared assay/test denominator. | Declare the unit and output denominator; distinguish recipe quantity from observed use. |
| `hours_per_test`, `hourly_rate_aud` | Labour exposure and price per hour. | Convert exactly and retain the workforce quote source or documented independent rate. |
| `price_aud_per_unit`, `cost_per_unit_aud` | Candidate unit quotation. | Supply effective/knowledge dates, currency year, economic basis and source identity; field names alone do not provide these. |
| `monthly_volume`, `annual_volume`, `usage_hours_per_month` | Throughput/capacity assumptions or measurements. | State their basis and reference period; do not turn an average into a patient event. |
| `purchase_cost_aud`, `useful_life_years`, `annualized_cost_aud` | Capital inputs or already-derived annual value. | Name the annualisation and allocation method; choose raw inputs or derived value so both are not counted. |
| `unit_cost_aud_per_unit`, `total_cost_aud` | Existing calculated output. | Use as a reconciliation comparator only after qualifying its derivation; do not also count it alongside its included components. |

Shared batches, controls, unused capacity, rework and object allocations need
explicit semantics in the plugin; they must not be inferred from spreadsheet
row positions. Existing demonstration PSA/VOI or aggregate outputs are not
independent reference values for the new kernel. The
[manifest](https://github.com/edithatogo/microcosting_genomics/blob/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41/pyproject.toml)
still advertises Python `>=3.8` and a broad pandas/NumPy/SciPy/Flask/workbook
dependency set. This is a different support surface from workforce and should
not dictate Dapane's core dependencies.

## MCHS: activity and funding are separate from resource use

Snapshot: [`f6e2e4646e60dd369924a46559e1fbd0f44d6ed6`](https://github.com/edithatogo/mchs/tree/f6e2e4646e60dd369924a46559e1fbd0f44d6ed6),
default branch `master`.

The Rust [`acute.rs`](https://github.com/edithatogo/mchs/blob/f6e2e4646e60dd369924a46559e1fbd0f44d6ed6/rust/crates/nwau-core/src/acute.rs)
contains `calculate_acute_decimal`, whose output includes `nwau` and
`total_funding`; it multiplies the calculated activity weight by an NEP rate and
rounds the funding output to two decimal places. This is a funding calculation,
not a measurement of consumed labour, equipment or consumables. Its reference
tables, classification decisions, adjustment rules and pricing-year selection
remain MCHS responsibilities.

| Existing source information | Dapane meaning | Boundary |
| --- | --- | --- |
| Episode ID, stream, classification/calculator and pricing year | Activity identity and provenance. | Do not erase the classification/version context. |
| Exact `nwau` result | `ActivityMeasure` in a declared NWAU basis. | Do not synthesize resource-use rows from this scalar. |
| Supplied NEP rate and its release | Activity-targeted funding quotation. | Preserve currency, pricing year, rounding and official source evidence; no hidden default price. |
| `total_funding` | Existing funding result for reconciliation. | Choose to import it as a qualified result or recompute from activity and rate; do not count both. |

The small `2.50 × 17.00 = 42.50` fixture is wholly synthetic. It demonstrates
activity-only valuation and contains no official NWAU/NEP schedule or claim of
MCHS classification parity. Both MCHS and workforce can eventually supply data
to the same Dapane study while keeping funding and resource-cost views separate.

## Reuse, dependency and licensing decisions

Use the providers through versioned data/API adapters. Reuse their maintained
domain rules and source retrieval in their owning packages. Do not copy the
spreadsheet evaluator, a simulation scheduler or national funding rules into
the valuation kernel. The first Dapane arithmetic and synthetic fixtures are
independent implementations, with source mappings documented above.

| Repository | Inspected licence evidence | Practical consequence |
| --- | --- | --- |
| Workforce | [Apache-2.0 LICENSE](https://github.com/edithatogo/microcosting_healthworkforce/blob/ae523fa65b45500a0b37bdfece23316808d12b73/LICENSE) and Apache-2.0 manifest. | A future source transplant needs preserved notices and a component-level review; no transplant is needed for the neutral adapter. |
| Genomics | [Apache-2.0 LICENSE](https://github.com/edithatogo/microcosting_genomics/blob/f2926486f54bc2b0c79a7fa3b84a0d4bacde4f41/LICENSE). | Prefer domain mappings and qualified fixtures over copying the old engine. Data/workbook rights must be established separately. |
| Kairos | [Dual licence declaration](https://github.com/edithatogo/kairos/blob/6b34bcb8fbae8efef31984d74135615f07997f2b/LICENSE); workspace declares `Apache-2.0 OR MIT`. | Keep an optional package boundary and record the selected provider revision/licence when an adapter is qualified. |
| MCHS | [Root LICENSE](https://github.com/edithatogo/mchs/blob/f6e2e4646e60dd369924a46559e1fbd0f44d6ed6/LICENSE) is MIT; [`nwau-core/Cargo.toml`](https://github.com/edithatogo/mchs/blob/f6e2e4646e60dd369924a46559e1fbd0f44d6ed6/rust/crates/nwau-core/Cargo.toml) declares Apache-2.0. | Resolve the component-level inconsistency before copying or redistributing source. The mismatch does not require duplicating its domain rules in Dapane. |

Dapane's project licence remains a release decision; this review does not choose
one. Provider software licences do not establish permission to redistribute
underlying schedules, workbooks, institutional records or clinical data.

No provider can be archived on the strength of these mappings or synthetic
tests. Retirement requires a migrated supported consumer, source/provenance
retention, qualified behavioural parity and a documented rollback path.
