# Paired-draw and fiscal contract candidates

This document describes the isolated synthetic implementation in this directory.
The fiscal verification record identifies the source and checks for each phase.
[Verification](../../conductor/tracks/tobac_regulatory_fiscal_valuation_20261110/VERIFICATION.md)

## Shared transport and identity

Inputs are UTF-8 JSON, at most 4 MiB. The recursive decoder rejects duplicate
object keys (including maps embedded in native requests), floating JSON numbers,
unknown typed fields and unsupported enum values. Integers for structural fields
remain JSON integers; exact values use
`{"numerator":"-3","denominator":"2"}`. Numerator and denominator use canonical
integer digits, no leading zeros, no plus sign and no negative zero. Denominators
are strictly positive. Each input component is limited to 96 digits; exact
arithmetic intermediates are limited to 4096 bits. Computed exact results are
reduced rationals. Externally supplied outcome rational spelling is retained in
the D1 report, so numerically equivalent input spellings can identify different
provenance.

IDs are 1..128 UTF-8 bytes, without outer whitespace or control characters.
An identity has `id`, `version`, `content_digest` and
`evidence: "synthetic"`. Digests are `sha256:` plus 64 lowercase hexadecimal
characters. These are explicit declarations, not signatures or scientific
source-admission certificates.

Every pair key contains all six mandatory fields:

| Field | Meaning |
| --- | --- |
| `scenario_id` | Explicit intervention/environment scenario |
| `strategy_id` | Strategy whose costs/outcomes are represented |
| `draw_id` | Epistemic parameter vector within the declared joint draw set |
| `replication_id` | Conditional replication, distinct from parameter uncertainty |
| `perspective` | Explicit valuation perspective |
| `subgroup_id` | Literal subgroup/stratum identity, without normalization or pooling |

Unicode subgroup identifiers are preserved byte-for-byte; visually similar
spellings are not equated. A replication label does not prove an outcome model
implemented the intended stochastic process.

Object keys are serialized in sorted order with no insignificant whitespace;
arrays retain their specified canonical order. Strings use serde_json escaping
without Unicode normalization. SHA-256 hashes prepend the exact domain below
(including its final newline). This is the adapter's versioned canonical format,
not a claim of generic RFC canonical-JSON conformance.

Outputs are limited to 16 MiB. Failure returns a structured `DapaneError`
(code/message/path) and no partial report. Precision, size, method or accounting
limits fail closed; no approximate fallback is selected.

## D1: explicit paired draws

Schema `dapane-paired-draws/0.1`; method
`dapane-paired-draws-v0.1.0`.

### Joint draws and complete design

The `draws` object contains a versioned ID, `axis: "epistemic_parameters"`,
`dependence_id`, synthetic generator identity, optional declarative seed,
parameter-ID-to-unit map, and rows of `draw_id` plus exact parameter values.
Every row supplies exactly the same declared parameters. There must be 1..128
parameters and 1..256 distinct draw IDs.

The adapter accepts complete correlated vectors, not a list of independent
marginal distributions or a covariance model to sample. It does not generate
random numbers. The generator identity and optional seed record external
provenance; reproducibility comes from the retained explicit vectors and model
requests.

`design` supplies nonempty, unique `scenarios`, `strategies`, `replications`,
`perspectives` and `subgroups`, plus
`replication_axis: "conditional_replication"`. The Cartesian product of these
five axes and draw rows must contain at most 256 indexed evaluations.
There is exactly one cost-model template for each five-axis cell and exactly
one externally supplied outcome for every full six-axis key. Missing, surplus
and duplicate cells/outcomes fail. No implicit replication averaging,
heterogeneity pooling or scenario weighting occurs.

### Native model evaluation and binding

Each `models` element contains its cell, synthetic model identity, method
(`point` or `intervals`), raw native JSON request, and bindings. Supported
native shapes are determined by the unchanged core entry points at the pinned
Dapane revision: point 0.1/0.2 and the interval 0.1 envelope.

A binding selects a declared parameter, kind and existing stable target ID:

| Kind | Target | Required parameter unit |
| --- | --- | --- |
| `quote_amount` | Existing quotation's `amount` | Quotation currency |
| `usage_quantity` | Existing usage's `quantity` | Usage unit |
| `interval_quantity` | Existing interval's `quantity`; interval method only | Interval unit |

The target must exist exactly once and the field must already exist. Two
bindings cannot replace the same field; one parameter can drive distinct fields.
No paths supplied by a caller, insertion, conversion or cross-currency operation
is supported. Parameters used only by the external outcome model may be
unbound in the cost model. Bound cost parameters must be nonnegative.

Before substitutions, the adapter evaluates the entire original template through
the native JSON API. An invalid default/template cannot be repaired or hidden
by a binding. It then prepares and evaluates each actual indexed draw. Therefore
there are template-validation evaluations in addition to the maximum 256 indexed
evaluations.

The cell perspective and common `money` currency, price year, valuation basis
and rounding policy must match the native policy. The adapter admits
`economic_cost` and `financial_cost` cost bases only. Every embedded native
source declaration must be `synthetic`, `public` and `unvalidated`.
Native unknown-capacity and unsupported-version behavior is retained, including
the point 0.1 prohibition on the presence of `capacity_allocations`, even an
empty array.

### Outcomes, reports and replay

`outcomes` has a separate synthetic model identity, measure ID, unit, full
draw-set digest and fully keyed exact rows. Outcomes may be signed. D1 neither
executes a clinical model nor converts a cost into benefit or utility. It checks
the draw-set digest against the complete supplied normalized draw object;
reusing a draw ID with changed joint values does not preserve identity.

The report retains normalized design, complete draw set, templates and bindings,
external outcome identity/units, and each row's keys, prepared request, parameter
draw digest, native cost report and external outcome. Native values, unknown
capacity flags, rounding policy and per-generated-segment half-even behavior
are untouched. The adapter does not aggregate or reround native cost totals.

Outer design axes, draw rows, models, bindings and outcome rows are sorted for
replay. Inner native request arrays are retained as supplied; changing their
order changes the adapter input snapshot/digest even if the native economic
answer happens to be identical.

| Digest | Domain | Payload |
| --- | --- | --- |
| Draw set | `dapane:paired-draw-set:0.1\n` | Validated draw object, draw rows sorted by ID |
| Parameter draw | `dapane:paired-parameter-draw:0.1\n` | One explicit draw row |
| Input | `dapane:paired-input:0.1\n` | Fully normalized typed input |
| Output | `dapane:paired-output:0.1\n` | Whole report before inserting only `output_digest` |

The full input can be reconstructed from the retained model/design/draw fields,
outcome contract plus keyed rows, schema version and run ID. Each prepared request
can also be replayed directly with the stated native point/interval method.

## T1: perspective and domestic transfer reference

Schema `dapane-fiscal/0.1`; method candidate
`dapane-fiscal-exact-steps-v0.1.0`.

This evaluates one supplied signed incremental packet. It does not derive costs
from a cohort, subtract strategies, infer tax liability or consume D1 output.
The input must state a distinct `comparator_strategy_id`, full pair key,
draw-set digest, jurisdiction, currency, price year, perspective, explicit
aggregation rule and resource basis. T1 validates the syntax of the declared
draw digest but does not verify it against a D1 draw set. That end-to-end join
belongs to T3.

Only `NZ/NZD` and `AU/AUD` contexts are admitted. Price years are explicit
integers in 1900..9999, equal on every monetary field. These labels do not
qualify a national source, real tax rule or currency conversion.

### Ledger and sign conventions

Every packet explicitly includes all four categories: medical, enforcement,
excise, GST. A known zero requires a labelled zero flow. Missing categories
never imply zero. There are at most 256 monetary lines with unique IDs.
Multiple distinct flows per category are permitted.

| Line kind | Source perspective | Basis | Transfer metadata |
| --- | --- | --- | --- |
| `health_system_direct_cost` | `health_system` | Packet's resource basis | Absent/null |
| `enforcement_resource_cost` | `public_finance` | Packet's resource basis | Absent/null |
| `discounted_tax_transfer` | `public_finance` | `fiscal_transfer` | Required: tax, boundary, payer, recipient |

Line amount is `undiscounted_amount`, with exact signed amount, currency, price
year and `unit: "currency"`. The transfer kind labels its resulting discounted
accounting output; callers must not prediscount the supplied amount. Positive
resource amounts mean additional use/expenditure relative to the comparator;
negative amounts mean reductions. Positive tax amounts mean additional government
receipts and equal negative household payer flows; negative tax amounts reverse
both legs.

Transfers accept only `excise` or `gst`,
`boundary: "domestic_economy"`, `payer: "domestic_households"` and
`recipient: "domestic_government"`. Both legs use the same timing and transfer
discount rate, so their domestic net is exactly zero. Tax receipts are never
added to societal resource consumption. Cross-border flows, deadweight loss,
incidence modeling and subgroup household welfare attribution are unsupported.

### Perspective, basis and aggregation

| Perspective / required rule | Allowed resource basis | Returned decision quantity |
| --- | --- | --- |
| `health_system` / `health_system_direct_only` | `economic_cost` or `public_expenditure` | NMB = threshold × discounted QALYs − medical |
| `societal` / `societal_net_domestic_transfers` | `economic_cost` only | NMB = threshold × discounted QALYs − medical − enforcement; internal transfers net to zero |
| `public_finance` / `public_finance_net_outlay` | `public_expenditure` only | Net public outlay = medical + enforcement − government tax receipts |

The key's perspective must equal the packet's perspective. All resource lines
must carry the packet's chosen basis. Merely changing a perspective does not
convert opportunity cost into expenditure; the caller must supply appropriately
valued, separately sourced amounts. Societal NMB is scoped to the declared
medical/enforcement resource boundary, not a complete societal welfare estimate.

Health-system and societal views require a separate synthetic health model,
`unit: "QALY"`, 1..256 uniquely identified signed health flows, and a
nonnegative exact threshold with `unit: "currency_per_qaly"`, matching currency
and price year, plus its own source identity. Public finance requires no health
contract (absent or null) and returns no QALYs/NMB. Inapplicable outputs are null,
not invented zeros.

### Discount timing and precision

Discount has a synthetic source, explicit `origin_id`, step length
`step_years` in (0, 1], and independent resource, health and transfer rates in
[0, 1]. The sole method is `effective_rate_per_step`. Every flow has an integer
`time_step` from 0 through 1200; valuation time is
`time_step × step_years`.

For a rate r and step k, the exact discount factor is `1 / (1 + r)^k`.
Rates are effective **per declared step**, not silently annual rates. For
example, two half-year steps at 1/4 have factor 16/25 and equal one annual step
at 9/16. Arbitrary fractional powers, negative rates, continuous discounting
and automatic annual-to-monthly conversions are rejected/unsupported.

Integer exponentiation uses exact rationals with a 4096-bit check on each
multiplication and aggregate. T1 never rounds currency: it reports exact reduced
rational values with `accounting_basis: "signed_incremental_exact_discounted"`.
It leaves the core's per-generated-segment currency rounding contract intact.
Any future production bridge needs an explicit rule for whether inputs are
native exact totals or already rounded values, rather than silently choosing.

### Audit output

The report includes the normalized complete `input_snapshot`, every valued
line and health flow with time and factor, component resource totals, separate
government/payer transfer totals, exact zero net internal transfer, selected
resource cost, excluded line IDs and only the applicable NMB/net-outlay output.
Literal subgroup/replication keys are retained without aggregation.

Input and output domains are `dapane:fiscal-input:0.1\n` and
`dapane:fiscal-output:0.1\n`. The output hash omits its own `output_digest`.
Ledger lines and health flows are sorted by ID before input hashing.
Evaluating `input_snapshot` reproduces the canonical report.

## T2 cohort and cessation schedules

The `dapane-fiscal/0.2` schema uses method `dapane-fiscal-exact-steps-v0.2.0`.
This profile extends the 0.1 ledger contract with two optional input arrays.
Use 0.1 for legacy packet replay. Schedule fields require 0.2.

| Array | Fields in addition to the common row fields |
| --- | --- |
| `cohort_states` | `from_state`, `to_state`, `population_count` |
| `cessation_resources` | `resource_type`, `quantity` |

Each row declares `id`, `time_step`, `perspective`, `basis`,
`undiscounted_amount` and synthetic `source`. Population counts and resource
quantities are nonnegative exact rationals. The supplied amount is the signed
incremental total for the row in the packet's currency and price year. The
source perspective and basis follow the perspective table above.

Each array accepts up to 256 rows with unique IDs within that array. Omission
and an empty array both produce an empty schedule. The normalised snapshot
omits empty schedules and sorts populated schedules by ID. The 0.2 output
always contains `valued_cohort_states` and `valued_cessation_resources`.

The evaluator discounts each supplied amount at the resource rate for the
row's step. The report retains the row perspective and copies `draw_id`,
`strategy_id` and `subgroup_id` from the packet key onto each row. The full key
remains at report level. The separate schedule outputs let callers report the
same activity without counting it again in the four-category ledger.
The input and output digest domains are `dapane:fiscal-input:0.2\n` and
`dapane:fiscal-output:0.2\n`.

## T2 equity-weighted subgroup sum

Schema `dapane-fiscal-equity/0.1`; method
`dapane-fiscal-equity-weighted-sum-v0.1.0`.

`packets` contains 1..32 entries. Each entry has a strictly positive exact
`weight` and a complete `fiscal` packet. A batch uses a single fiscal profile.
Subgroups must declare the same scenario, strategy, comparator, draw ID,
draw-set digest, replication, perspective, jurisdiction, currency, price year,
aggregation rule, resource basis and discount policy. Health packets must also
share a health model and threshold declaration. Each subgroup ID is unique.

The report has one row per supplied subgroup, in input order, with its weight
and its fiscal output digest. For each of `selected_resource_cost`,
`discounted_qalys` and `net_monetary_benefit`, the weighted total is the sum of
weight times component. Unit weights exactly conserve every unweighted sum.
QALYs and NMB are null for public-finance packets. The output digest domain is
`dapane:fiscal-equity-output:0.1\n`.

## Deferred capabilities

D2/D3 provider negotiation, VOI, adoption and game methods are not implemented.
T2.3 upstream oracle parity, plus T3 installed consumers and verified
cross-provider paired export, remain open. The synthetic occupancy schedule
and equity-weighted sum above are not that oracle.
There is no automatic registration or dispatch for any provider method. The
release integrator must decide any shared method/profile, schema or CI changes
using the [handoff](../../conductor/tracks/decision_integrations_20261108/HANDOFF.md).
