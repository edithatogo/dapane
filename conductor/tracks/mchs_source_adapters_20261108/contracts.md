# M1: pinned provider contracts and mapping

Inspected on 15 November 2026 against Dapane main
`e34f87c9df39a2132fecee142431cdeefb732471`. Upstream repositories remain
read-only. These are inspected source-contract pins, not installed-provider or
official-rate qualification.

## Exact evidence

| Provider | Inspected revision | Boundary |
| --- | --- | --- |
| MCHS master | `125933c7770e9a6bed9b62e354a6380d3dac3d47` | [AcuteEpisodeOutputDecimal and calculate_acute_decimal](https://github.com/edithatogo/mchs/blob/125933c7770e9a6bed9b62e354a6380d3dac3d47/rust/crates/nwau-core/src/acute.rs) expose exact Decimal result fields, error code, NWAU and separately calculated funding. |
| MCHS Python/Polars | Same revision | [nwau-py bindings](https://github.com/edithatogo/mchs/blob/125933c7770e9a6bed9b62e354a6380d3dac3d47/rust/crates/nwau-py/src/lib.rs) include float-based paths. Those values are not admitted by this exact transport. |
| Atlas main | `a93516ed416118bc51c1db2b71ab540fa4d0fe52` | [contracts.py](https://github.com/edithatogo/reimbursement-atlas/blob/a93516ed416118bc51c1db2b71ab540fa4d0fe52/src/reimburse_atlas/contracts.py) defines items, provenance and snapshots. [models.py](https://github.com/edithatogo/reimbursement-atlas/blob/a93516ed416118bc51c1db2b71ab540fa4d0fe52/src/reimburse_atlas/models.py) defines source releases and parser status. |

The [machine-readable pins](../../../adapters/mchs_sources/src/dapane_mchs_atlas/provider_pins.json)
retain contract blob IDs. Changed provider revisions require contract review.
No provider runtime, data or source code is copied into the package.

## Mapping

| Source information | Adapter treatment | Unsupported/missing evidence |
| --- | --- | --- |
| MCHS error_code | Require integer zero before admitting activity. | A provider error yielding zero NWAU is not valid zero activity. |
| Decimal nwau | Exact-string quantity on an activity_measure row. | Float outputs, negative corrections and unsupported methods fail. |
| Classification system/code/edition and pricing edition | Explicit caller annotations, retained independently; quotation context must match. | No implicit edition, grouper or classification-validity claim. |
| MCHS total_funding | Preserve only as upstream comparison metadata. | Never sum or substitute it for a missing quotation. The provider's NEP fallback is not reused. |
| Atlas ScheduleItemRecord | Reuse normalized metadata after provider parsing. | payment_amount is float or null; every non-null amount is rejected. Stringifying a float cannot recover original precision. |
| Exact supplement | Original exact amount/denominator, field/locator and matching snapshot checksum. | New Dapane contract, not a claim of an existing upstream export. |
| SourceVersionRecord, SourceSnapshotRecord, item provenance | Match source/release/URL/retrieval/checksum identities; preserve complete snapshots. | Missing hashes, unknown parser state, conflicting links and non-permissive gates fail. |
| Effective applicability | Explicit half-open convention, item dates within release dates. | No guessed or silently converted end date. |
| Knowledge date and price year | Independent from classification/pricing editions, retrieval and service dates. | No price-year inference or latest-release lookup. |
| Funding and tariff | Separate native funding and charge requests. The charge-to-tariff interpretation is explicit in the outer profile. | Schedule amounts never become resource costs or payment observations. |
| Resource cost | Separate supplied core 0.1 request with resource-use rows and matching source-rights declarations. | No activity-to-resource inference. |
| Payment | Explicit observation or named model, exact amount retained, no aggregation. | Core 0.1 has no payment basis; no silently substituted basis or tariff-to-payment inference. |
| Source status/rights/access | Independent declarations. Synthetic inputs remain synthetic/unvalidated. | Public accessibility does not establish redistribution rights or scientific validity. |

## Qualification scope and M3 requests

The selected capability is synthetic **exact transport and existing native
valuation**. The synthetic classification, dates and rates do not qualify
AR-DRG, NEP26, any hospital programme, or an official Atlas release.

MCHS needs a caller-owned exact export of its existing Decimal result plus the
classification/pricing/source context. The projection's separation category is
an integer 1–4; this is an explicit Dapane wire convention, not a claim of an
existing serde or Python endpoint.

Atlas needs original exact lexical values bound to its source snapshots before
live monetary imports can be admitted. This candidate does not reconstruct
amounts from the float-based normalized field. Conditional tariffs, restricted
source gates and patient components require separate profiles.

Provider-owned exporters, installed consumer tests, official source rights and
classification/rate qualification remain M3 work. Upstream APIs stay untouched.
