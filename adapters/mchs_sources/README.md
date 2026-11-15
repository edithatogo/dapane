# Optional MCHS and Atlas adapters

The separate `dapane_mchs_atlas` package implements the bounded M1/M2 source
candidate. It does not change the shared Rust crates, schemas, ordinary Python
package or dependency graph. Preparation needs only the Python standard library;
valuation calls a qualified installed Dapane native wheel or a trusted native CLI
bridge.

**Final-head qualification is pending.** An earlier working version passed 24
tests, including native CLI valuation. The execution workspace then became
unavailable. The 34-test recovered source candidate, review fixes and installed
package smoke test have not executed. See the
[verification record](../../conductor/tracks/mchs_source_adapters_20261108/verification.md).
This is synthetic transport work, not a qualified live-provider integration.

## Provider boundary

[Provider pins](src/dapane_mchs_atlas/provider_pins.json) identify the inspected
MCHS and Atlas source revisions and file blobs. Both upstream repositories remain
read-only; neither provider was built or run. No source collector, parser,
classification equation, rate table, private record or programme data is copied.

MCHS's acute Decimal result contains exact `nwau` and separate `total_funding`.
Its inspected funding calculation can use a default NEP. The adapter admits exact
NWAU as `activity_measure`, requires explicit quotation selection, and retains
upstream funding only as comparison metadata. It never infers physical resources
from weighted activity or substitutes default funding for a missing rate.

Atlas's `ScheduleItemRecord.payment_amount` is `float | None`. Every non-null
normalized amount is rejected, including a decimal string placed in that float
field. The admitted metadata projection has null there plus an **explicit exact
supplement** containing original exact amount/denominator, source field/locator,
and snapshot checksum. This is a new Dapane supplement, not an existing Atlas
export. Callers must preserve exact values before float conversion. Nulling a
float and stringifying it does not recover source precision; the adapter cannot
authenticate such a caller declaration.

## API and input

```python
from pathlib import Path
from dapane_mchs_atlas import evaluate, loads, prepare

bundle = loads(Path("parallel-views.json").read_text(encoding="utf-8"))
prepared = prepare(bundle)  # status=prepared; no monetary arithmetic
result = evaluate(bundle)  # installed Dapane native wheel required
print(result["views"]["funding"]["totals"]["rounded"])
```

`evaluate(bundle, evaluator=callable)` accepts a trusted bridge implementing the
existing `dapane.evaluate(dict) -> dict` boundary. The test harness invokes the
native CLI through this seam. It is not a plugin loader or an alternate pricing
engine. Complete status and policy identity are checked; the callable itself is
trusted to execute the correct core. `AdapterError` exposes `code`, `message`,
`path`, and `as_dict()`. Any failure raises; no partial complete result is returned.

The [expanded synthetic fixture](fixtures/parallel-views.json) specifies the
`dapane-mchs-atlas/0.1` profile.

| Field | Required meaning |
| --- | --- |
| `run_id`, `knowledge_cutoff` | Explicit identity and date; no current-date lookup. |
| `activities` | Nonempty exact acute Decimal result projections, pinned provider revision, supported method, zero error code, classification code/context, service date and source declarations. All provider Decimal fields are strings. |
| `context` | Acute stream, classification system, classification edition and pricing edition. Opaque provider declarations are retained; literal unknown/unspecified context fails. No classification validity is inferred. |
| `quote_packs` | Nonempty source-version, snapshot and item metadata, exact supplement, and explicit quotation application context. |
| `views` | Unique funding and/or tariff entries, each with a complete policy and explicit line/activity/quote selection. Every activity needs a selection in every requested view. |
| `resource_cost` | Optional separate core 0.1 request containing resource-use quotes/rows and economic/financial-cost basis. Run ID is `<run_id>:resource_cost`; cutoff must match. |
| `resource_sources` | Required with resource costs: full rights/status declarations matching each native usage and quotation source. No extra declarations. |
| `payments` | Optional exact observation/model records, explicit activity scope, currency/date, source, and observation reference or named/versioned model. Observations cannot occur after cutoff. |

Unknown adapter fields, provider revisions and methods fail closed. Native request
validation remains with the native core. Inputs are copied. JSON transport rejects
duplicate object keys, nonfinite values, cycles, excessive depth/size, unsupported
host objects and invalid exact-number syntax.

## Applicability and evidence

Classification code is preserved separately from the quotation context. The core
target is a full SHA256 of that context, with all original text retained in the
provenance envelope. Classification edition, pricing edition, economic price
year, service date, knowledge date and retrieval timestamp remain distinct.
Quotes must match view, context, unit, currency and price year exactly.

Effective dates require an explicit half-open convention:
`valid_from <= service_date < valid_to`. Item dates must fit the source release.
There is no automatic edition conversion, source selection, inclusive-end-date
conversion, or zero substitution.

Source declarations separately retain evidence, access, validation, official
status, known-from date, and rights status/licence/evidence reference. Rights must
be explicitly declared permitted; missing or unknown rights fail. Synthetic
evidence remains synthetic and unvalidated. The fixture licence identifier
`SYNTHETIC-RIGHTS-FIXTURE` is fictional test metadata, not a legal grant.

Atlas imports are limited to permissive source gates and public raw/derived
snapshot scopes. Local paths, metadata-only snapshots, conditional restrictions,
patient components, unknown parser status and non-synthetic prototype output
fail. Source/release IDs, version labels, URLs, retrieval timestamps and checksums
must agree. Declared checksum links are checked; no external content is fetched
or independently authenticated. Fixture tests separately check the included
synthetic quotation bytes and exact values.

## Separate views and arithmetic

| View | Representation | Independent synthetic expectation |
| --- | --- | ---: |
| Funding | Native funding report; activity measures only | 2.50 × 17.00 = **42.50** |
| Tariff | Separate native charge report, explicitly labelled tariff | 2.50 × 20.00 = **50.00** |
| Resource cost | Separate economic/financial-cost report | 3/2 hours × 10.00 = **15.00** |
| Payment | Supplied observation/model records; aggregation not performed | **40.00** supplied fixture |

There is no combined total. Payments are not revalued, rounded or summed. Core
0.1 has no payment basis; no substitute basis is introduced. An absent payment
view stays absent, not zero. Synthetic observation labels never imply actual
transactions.

Python performs no valuation, allocation, summation or rounding arithmetic.
Native reports retain exact quantities, method identities and their input/output
digests. The envelope retains complete original input and a domain-separated
SHA256 over canonical JSON; input-list order remains part of that identity.
Native request canonicalization remains the core's responsibility.

The existing interval API and accepted half-even rounding **per generated
segment** are unchanged. This profile does not implement intervals, capacity
requests, automatic rate-boundary splitting, signed corrections, conditional
tariffs, live source acquisition or payment aggregation.

## Candidate installation and checks

The separate build uses `setuptools==84.2.1`; there are no runtime dependencies
for preparation. The optional `native` extra declares `dapane==0.1.0` for later
package resolution, but no public registry package is assumed. Install the exact
qualified local native wheel and the locally built adapter wheel.

From the repository, with the qualified native CLI available:

```sh
PYTHONPATH=adapters/mchs_sources/src DAPANE_TEST_CLI=/absolute/path/to/dapane \
  python -m unittest discover -s adapters/mchs_sources/tests -v
```

For installed qualification, build/install this package, change outside the
checkout, and run the same tests with `python -I` and an absolute test directory.
Also run `tests/installed_smoke.py --fixture /absolute/path/to/parallel-views.json`
to exercise the installed native wheel through the default API. Native tests
fail if the CLI is unavailable; they never silently skip.

Root CI does not yet discover or install this optional package. The
[integration handoff](../../conductor/tracks/mchs_source_adapters_20261108/handoff.md)
requests explicit coverage and registry reconciliation from the sole integrator.
Publication remains disabled. M3 live-provider migration remains open.
