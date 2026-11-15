# Paired decisions and fiscal reference adapters

This optional Rust crate implements the bounded D1 paired-draw envelope and T1
synthetic fiscal reference contract. It lives in the `adapters/decision_draws/`
namespace reserved for this lane in
[ownership PR #20](https://github.com/edithatogo/dapane/pull/20).
It has its own manifest and lockfile. The root workspace, core/CLI/Python crates,
schemas and CI are unchanged.

**Qualification is blocked for the published source.** The execution environment
became unavailable after the earlier local D1 18-test and T1 19-test runs and
before the local implementation was pushed. This source was reconstructed from
recorded patches, moved from the unpublished `adapters/decision-fiscal/` path to
the reserved namespace, and statically reviewed. Those earlier results do not
qualify these recovered bytes. See the [verification record](../../conductor/tracks/decision_integrations_20261108/VERIFICATION.md)
and [exact-SHA handoff](../../conductor/tracks/decision_integrations_20261108/HANDOFF.md).

## Interfaces

The library exports three JSON functions returning `Result<String, DapaneError>`:

| Interface | Scope |
| --- | --- |
| `paired::draw_set_digest_json` | Validate and fingerprint an explicit joint draw set for the independent outcome model. |
| `paired::evaluate_paired_json` | Prepare the actual supported native cost model for each cell/draw, evaluate it, and join separately supplied outcomes on all six keys. |
| `fiscal::evaluate_fiscal_json` | Evaluate one signed incremental synthetic fiscal packet using explicit perspective, expenditure/economic basis, discount timing and domestic transfer rules. |

The versioned input/output, identity, error and precision rules are in
[CONTRACT.md](CONTRACT.md). The fiscal function is an isolated reference candidate,
not a qualified Tobac or Voiage method. It does not extend the core's nonnegative
resource-valuation API.

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

## Re-execution required

From a checkout of the final PR revision, with the pinned toolchain and a populated
cache, execute:

```sh
cargo fmt --manifest-path adapters/decision_draws/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/decision_draws/Cargo.toml --locked --offline --all-targets
```

There are 18 D1 and 19 T1 test declarations. Counting declarations is not executing
tests. If formatting or compilation finds recovery defects, fix only owned paths,
rerun the commands, and record the new exact SHA. An offline dependency-cache
failure is a blocked execution, not a test pass. The supplied lockfile selects
27 registry packages with identities/checksums already present in main's
lockfile; `cargo --locked` acceptance of the recovered lock remains unexecuted.

Root CI does not discover this nested workspace. The integrator must add explicit
manifest-path commands and reconcile the two central registry status rows.
No gate has been disabled or waived.

## Boundaries

Only invented public synthetic declarations are accepted. A syntactic
`evidence: synthetic` tag or SHA identifies a declaration, not the truth of its
source. There is no network, RNG, private-record reader, provider dispatch, VOI
estimator, cohort model, tax calculator, equity weighting or production price
catalogue here. Outcomes remain external to D1; T1's declared draw digest is not
an implemented D1-to-T1 consumer join.

D2/D3 and T2/T3 remain open. Upstream Tobac was inspected read-only at
`891f79e07292b7754f78d7193130623bd5f9e243`; source adjudication stays with its
existing owner. Removing this optional directory leaves all shared runtime
surfaces unchanged.
