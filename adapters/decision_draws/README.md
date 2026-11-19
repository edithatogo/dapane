# Paired decisions and fiscal reference adapters

This optional Rust crate implements the D1 paired-draw envelope, T1 synthetic
fiscal contract and T2 synthetic schedule and equity calculations. It lives in the `adapters/decision_draws/`
namespace reserved for this lane in
[ownership PR #20](https://github.com/edithatogo/dapane/pull/20).
It has its own manifest and lockfile. Shared registry and standalone CI wiring
were subsequently added by the sole integrator; shared core/CLI/Python and
schemas are unchanged by this adapter lane.

The 15 November quality check covered `9c177166899e588dc3dacadb13e4a0a3750bbce2`. The received source
had already passed 37 hosted tests and Clippy. That owner pass resolved five
Rust formatting failures and reruns format, lint, tests and locked dependency
resolution on the exact corrected commit. The [owner quality record](../../conductor/tracks/decision_integrations_20261108/owner-quality-20261115.md)
and [handoff](../../conductor/tracks/decision_integrations_20261108/HANDOFF.md)
separate this evidence from the earlier source-recovery history and remaining
production-method, provider and security/release gates.

## Interfaces

The library exports four JSON functions returning `Result<String, DapaneError>`.

| Interface | Scope |
| --- | --- |
| `paired::draw_set_digest_json` | Validate and fingerprint an explicit joint draw set for the independent outcome model. |
| `paired::evaluate_paired_json` | Prepare the actual supported native cost model for each cell/draw, evaluate it, and join separately supplied outcomes on all six keys. |
| `fiscal::evaluate_fiscal_json` | Evaluate one signed incremental synthetic fiscal packet. Profile 0.2 also discounts supplied cohort and cessation schedules. |
| `fiscal::evaluate_equity_json` | Return exact weighted and unweighted cost, QALY and NMB sums across compatible fiscal packets while retaining each subgroup row. |

The fiscal functions run in the standalone reference crate.
[Contract](CONTRACT.md)

## D1 example

[paired-synthetic.json](fixtures/paired-synthetic.json) supplies two correlated
joint vectors: quantity/quotation `(1/3, 30)` and `(2/3, 60)`. The reference
strategy contains one resource use and the alternative two distinct uses. Exact
native costs are therefore `10, 40` and `20, 80`, respectively. The separately
identified outcome model supplies reference QALYs `1, 2` and alternative QALYs
`3/2, 5/2`. These invented values are independent expectations, not empirical
clinical estimates or locally generated outcome predictions.

Every result retains scenario, strategy, draw, conditional replication,
perspective and subgroup identity, prepared request and unmodified native report.
Cost-model point/interval requests still pass through the existing public JSON
entry points. The interval test deliberately generates two half-cent segments:
half-even rounding per generated segment gives rounded total `0.00`, with exact
total `0.01`. This adapter adds no new core rounding operation.

## T1 example

[fiscal-nz-synthetic.json](fixtures/fiscal-nz-synthetic.json) declares incremental
medical `100`, enforcement `20`, excise receipts `40`, GST receipts `10`,
QALYs `1`, and threshold `100`, all at step 1. Resource/transfer rates are
`1/4` per step; the health rate is zero.

| Quantity | Independent exact expectation |
| --- | ---: |
| Discounted medical / enforcement | 80 / 16 |
| Discounted government receipts / payer flow | 40 / -40 |
| Net domestic transfer | 0 |
| Health-system direct-only NMB | 20 |
| Declared-resource societal NMB | 4 |
| Public net outlay | 56 |

The cross-perspective test explicitly assumes equal *numerical* economic-cost
and public-expenditure amounts for this invented case and relabels the basis
accordingly. The runtime does not convert an economic cost into a cash outlay.
The societal scope contains only the declared medical and enforcement resources,
not every possible societal effect. AU/AUD uniform-rate and annual/subannual
references are in [the fiscal tests](tests/fiscal.rs); no current tax schedules,
discount recommendations or demographic estimates are encoded.

## Reproduce the bounded checks

From a checkout of the final PR revision, with the pinned toolchain and a populated
cache, execute:

```sh
cargo fmt --manifest-path adapters/decision_draws/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets
```

The standalone workflow explicitly executes this nested workspace. The
Conductor record gives the local results and verified source.
[Fiscal verification](../../conductor/tracks/tobac_regulatory_fiscal_valuation_20261110/VERIFICATION.md)

## Boundaries

Only invented public synthetic declarations are accepted. A syntactic
`evidence: synthetic` tag or SHA identifies a declaration, not the truth of its
source. There is no network, RNG, private-record reader, provider dispatch, VOI
estimator, cohort-dynamics model, tax calculator or production price catalogue
here. Supplied occupancy and cessation amounts can be discounted and reported
without entering the four-category ledger. `evaluate_equity_json` sums those
fiscal results with explicit positive weights and keeps each subgroup row.
Outcomes remain external to D1; T1's declared draw digest is not an implemented
D1-to-T1 consumer join.

D2/D3, T2.3 oracle parity and T3 remain open. Upstream Tobac was inspected read-only at
`891f79e07292b7754f78d7193130623bd5f9e243`; source adjudication stays with its
existing owner. Removing this optional directory leaves all shared runtime
surfaces unchanged.
