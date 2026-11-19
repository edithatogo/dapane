# D1/T1 lane handoff

## Current owner follow-up — 15 November 2026

The [bounded quality repair](owner-quality-20261115.md) records clean-source execution at
`9c177166899e588dc3dacadb13e4a0a3750bbce2` (tree `db6e32d39ae8960da9d30a24ed37eb965caea36d`). Rustfmt, Clippy with `-D warnings`,
18 D1 + 19 T1 tests, locked/offline Cargo metadata, Conductor validation and
12 lifecycle tests passed. The five Rust changes exactly equal pinned formatter
output; assertions, fixtures, manifests, locks, numerical methods and shared
coordinator files are unchanged.

Handoff requests 1–3 are satisfied within the bounded computational scope:
the integrator supplied recovered-source replay, registry reconciliation and
standalone CI; this owner corrected the remaining formatting failure. The final
documentation descendant is checked separately and its exact-head results are
handed to PR23/PR20. No earlier result is relabelled as evidence for a later head.

Request 4 (production signed-fiscal method/profile), D2/D3, T2/T3, required
offline-security and coordinator privacy/release acceptance remain open. No
provider method is qualified, no extra worker created, and no merge or release
performed. Both tracks remain `in_progress` and PR23 remains draft.

## Initial recovery record — historical, superseded where stated above

The retained text below describes the earlier recovery-stage source and blockers.
Its not-run, registry-pending and missing-CI statements are historical; current
execution and request dispositions are recorded above and in the owner follow-up.

Owner: **Dapane — Release assurance and consolidation**, chat
`6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

This is the bounded synthetic implementation candidate for D1.1–D1.3 and
T1.1–T1.3. Current-source native qualification is blocked. It must remain a draft
until re-executed and the integrator-owned requirements below are resolved.
No later phase, provider qualification, merge or release is requested here.

### Revision boundaries

- Base/main inspected: `e34f87c9df39a2132fecee142431cdeefb732471`.
- Main tree: `c07a6b2589b9d665f619f5d977d66e513180bab4`.
- Integrator PR #17 inspected at `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`.
- Ownership PR #20 inspected at `e615454c9f3f41f96e9e310f446d2440d98cf5eb`.
- Published [source checkpoint](https://github.com/edithatogo/dapane/commit/dc9c42877bdab05967de731023ff9901541fc7f9):
  `dc9c42877bdab05967de731023ff9901541fc7f9`.
- Source tree: `4eeb598fb4101296d0c9fbf1ddd02c01aad665f9`.
- Draft PR: [#23](https://github.com/edithatogo/dapane/pull/23), branch `feat/paired-decisions-fiscal-d1-t1`.
- This final handoff is carried by a documentation-only child of that source
  checkpoint. Adapter source/test/fixture/lock bytes are unchanged in the child.
- Earlier unpublished local D1 commit
  `8c2a8589e005bf14a6cde5365fb218ed09f3ca98` is not a usable remote dependency.
- Read-only upstream Tobac: `891f79e07292b7754f78d7193130623bd5f9e243`.

The recovered source is not asserted to be byte-identical to the earlier tested
checkout. See [verification](VERIFICATION.md) and [review](REVIEW.md).

All 13 published adapter files were fetched from the exact source checkpoint
and matched the prepared content byte-for-byte. The remote base/source comparison
reported 29 changed files, all within the three owned roots.
[The publication receipt](evidence/publication-readback.json) records Git blob
identities and SHA-256 content digests. These checks establish publication
identity, not native execution. At 2026-11-15 05:25:01 UTC, all five source-commit
hosted workflows were queued with no conclusion; none is claimed passed.

### Owned changes

Only `adapters/decision_draws/`,
`conductor/tracks/decision_integrations_20261108/` and
`conductor/tracks/tobac_regulatory_fiscal_valuation_20261110/` are changed.
The single optional crate shares strict transport, exact values and six-key
identity between D1 and T1. Its nested workspace deliberately leaves root Cargo
files untouched; no parent adapter index is added.

D1 evaluates existing point/interval cost models over complete explicit joint
vectors and joins separately identified outcomes. It retains full native
reports, raw request boundaries, unknown capacity and the accepted generated
segment rounding rule.

T1 specifies and implements an isolated synthetic exact reference for medical,
enforcement, excise and GST flows, signed increments, compatible perspectives,
resource basis and effective per-step discounting. Tax payer/recipient legs
balance exactly within the declared domestic boundary.

### Concrete integrator requests

#### 1. Re-execute the exact recovered source

Run the three isolated crate commands in [verification](VERIFICATION.md), fix
recovery/formatting findings in owned paths, record the resulting exact SHA,
and preserve raw logs. Earlier local D1 18-test and T1 19-test passes do not close
this gate. The last local T1 Clippy and all recovered-source native checks were
unexecuted. Do not promote phase-1 completion based on static checks alone.

#### 2. Update the two shared registry rows

In the integrator-owned `conductor/tracks.md`, change only the two following
track rows from `[ ]` / `new` to `[~]` / `in_progress`:

- `decision_integrations_20261108`
- `tobac_regulatory_fiscal_valuation_20261110`

Owned metadata, indexes and plans already state `in_progress`; acceptance
tasks stay active/blocked and later phases pending. The unchanged validator
therefore predicts two central marker/status mismatches. This lane does not
edit the registry or waive the validation gate. Run the actual validator after
the coordinated integration update.

#### 3. Add explicit isolated adapter CI coverage

The root workflow at the base SHA runs only its workspace. It will not discover
this nested optional crate. Add scoped formatting, Clippy and tests in the shared
workflow, using the existing pinned Rust 1.99.1 toolchain:

```sh
cargo fmt --manifest-path adapters/decision_draws/Cargo.toml --all --check
cargo clippy --manifest-path adapters/decision_draws/Cargo.toml --locked --all-targets -- -D warnings
cargo test --manifest-path adapters/decision_draws/Cargo.toml --locked --all-targets
```

A separate shared workspace-membership decision is optional; explicit
manifest-path execution suffices for the current isolation. Keep all existing
core/CLI/Python, source/privacy, security and release gates. This lane requests
no new core API, CLI command, Python binding or shared schema.

#### 4. Decide any production signed-fiscal method/profile

The local T1 evaluator is a synthetic reference candidate. Before a production
bridge or public core method is considered, explicitly decide:

| Concern | Proposed reference contract |
| --- | --- |
| Input sign | Signed strategy-minus-comparator increments; cost increases positive; tax increases positive government receipts |
| Resource basis | Public finance requires public expenditure; societal requires economic cost; no automatic conversion |
| Transfer | Matching signed government/household legs within the domestic economy; exact net zero; no deadweight or cross-border model |
| Timing | Integer k at k × explicit step-years; rates effective per declared step, independent for resources/health/transfers |
| Numerical method | Exact rational `(1+r)^(-k)`; no fractional-power/continuous approximation |
| Precision | 96 digits per input component, 4096-bit intermediates, at most 1200 steps and 256 flows per collection |
| Rounding | Reference output remains exact; existing core per-generated-segment half-even remains unchanged; production bridge must specify whether it consumes native exact or rounded values |
| NMB scope | Medical only for health-system; declared medical+enforcement resources for societal; no NMB in pure public-finance view |
| Qualification | No provider method is registered or selected; published-source native tests and a reviewed production boundary are prerequisites |

These choices are fully described in
[CONTRACT.md](../../../adapters/decision_draws/CONTRACT.md). This handoff requests
a decision, not permission to bypass it. T2/T3 and broad production support
remain open.

### Upstream inspection and non-duplication

At the pinned Tobac revision, `src/tobac/economics.py` and
`src/tobac/decision.py` from the original plan are absent. Related functions
are in [health.py](https://github.com/edithatogo/tobac/blob/891f79e07292b7754f78d7193130623bd5f9e243/src/tobac/health.py)
(blob `af8024367001bf75fa849267d73fd1b0dcb12927`):
`discounted_qalys`, `_discounted_flows`, `discounted_resource_cost` and
`discounted_tax_transfer`. Their float/annual-time interface is not presumed
equivalent to this exact per-step reference.
[interchange.py](https://github.com/edithatogo/tobac/blob/891f79e07292b7754f78d7193130623bd5f9e243/src/tobac/interchange.py)
(blob `786a93cb037a07823865718e34bb372f53aed755`) handles evidence packets,
not an already-qualified fiscal consumer.

[Tobac source-adjudication issue #3](https://github.com/edithatogo/tobac/issues/3)
and its owner remain untouched. Upstream inspection was read-only. No empirical
observation, clinical record, current legal/tax rate or private source was used.

### Acceptance that remains open

Current-source Rustfmt/Clippy/tests/lock acceptance; central Conductor registry
reconciliation; explicit adapter CI; and any production numerical-method
qualification remain open. D2/D3 and T2/T3 have not been implemented or tested.
No claims are made for installed package, OS-matrix, VOI, game, cohort, equity
or upstream consumer parity. Integration and all merges/releases remain solely
with the named owner.
