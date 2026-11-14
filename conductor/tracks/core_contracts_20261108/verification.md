# Core-contract verification and closeout

Date: **15 November 2026** (Australia/Brisbane).
Track: `core_contracts_20261108`. Candidate status: `synthetic_candidate`.

## Implementation and review identity

The original bounded runtime and capacity profiles were integrated through
`ae00b2e37802a43d29c58729875aff961ff3ae54`. PR #9 adds bundle 0.1 without
changing the original request/report schemas or Rust financial methods.

- `96b178c0f2b21cd8fc702a86dec2f0cde8fa8504`: original bundle implementation
  and implementer review.
- `bc92e9b1d34198d8164349734cf79090fdc2bc4c`: independent review corrections
  for immutable release identity and the chronology regression.
- `5996d7cb0adbdd8d433a0395caefd7a3ac37423e`: retained concurrent fix requiring
  completed tasks and passed verification for archived tracks.

The [independent review](independent-review.md) records both findings and their
remediation. A separate read-only re-review of `bc92e9b` found them resolved
and found no further blocking defect. The [earlier review](review.md) retains
the original fail-first and implementer-review history.

## Observed hosted evidence

The earlier exact head `96b178c0f2b21cd8fc702a86dec2f0cde8fa8504` passed all
11 configured checks. Inspected Runtime
[43609831820](https://github.com/edithatogo/dapane/actions/runs/43609831820)
contained 40 passing native tests and 119 installed-wheel tests on each CPython
3.12, 3.13, 3.14 and 3.15 job. CLI references, schema checks, formatting/lint and
Conductor validation passed. Privacy/secrets and CodeQL checks also succeeded.

Those observations are historical; they do not qualify the later changes.
The current implementation at `5996d7cb0adbdd8d433a0395caefd7a3ac37423e` is
awaiting hosted qualification in Runtime
[43650466658](https://github.com/edithatogo/dapane/actions/runs/43650466658).
Track closure and archival remain pending until the latest required checks and
context reconciliation are verified. The local workspace became unavailable;
no local native or installed-wheel execution is claimed for this continuation.

The existing workflow executes:

- `cargo fmt --all --check`
- `cargo clippy --workspace --locked --all-targets -- -D warnings`
- `cargo test --locked`
- Release build and installed CLI evaluation outside the source tree.
- `python scripts/validate_contract.py --cli target/release/dapane`
- `python scripts/validate_conductor.py`
- Ruff lint and formatting over the Python package, tests and bundle verifier.
- Native wheel build/install, then `pytest --import-mode=importlib` over
  `tests/python` outside the source tree for CPython 3.12–3.15.

## Acceptance map

| Original criterion | Executable/reference evidence | Scope |
| --- | --- | --- |
| Distinct resource and activity quotations; kind/unit rejection | [Activity fixture](../../../fixtures/activity-funding.json), [native evaluation tests](../../../crates/dapane-core/tests/evaluation.rs), installed consumer/error tests | No activity-to-resource inference. |
| Exact fractional duration and decimal quotation transport | [Workforce fixture](../../../fixtures/workforce.json), native exact-value and installed transport cases | No binary-float round trip. |
| Effective, knowledge and price-year dates; half-open boundaries | Native applicability cases, [segmented reference](../../../fixtures/core-contracts/references.json), bundle source/window and history tests | Rate-boundary segments are explicit producer inputs. |
| Missing, zero, synthetic, observed and unsupported states | Native missing/zero cases, installed fabricated source-state/exclusion tests, [capacity cases](../../../fixtures/genomics-capacity/README.md) | Source/access/validation are separate declarations; unknown capacity remains unknown. |
| Residuals, duplicate use/components and alternative capital treatments | Existing sub-cent/capacity cases and [bundle acceptance tests](../../../tests/python/test_core_contract_completion.py) | Alternative prepared asset views are exclusive; no capital formula is inferred. |
| Independent expected values and calculation notes | [Original expectations](../../../fixtures/expected.json), [core reference notes](../../../fixtures/core-contracts/README.md), capacity derivations | Invented inputs with independently authored arithmetic, not legacy-output oracles. |

The original interval reference is `(1/3)*90 + (2/3)*120 = 110`.
Correcting the first duration gives `(1/2)*90 + (2/3)*120 = 125`.
Correcting its quotation under a new source version gives
`(1/2)*100 + (2/3)*120 = 130`. The original snapshots are retained.
Acquisition `12000` and a prepared charge `12000/60 = 200` are alternative
views; a declared mixed `12200` asset treatment is rejected.

The [review regressions](../../../tests/python/test_bundle_review.py) rebuild
native reports and reseal history before checking conflicting release identity.
They cover temporary omissions, new-version corrections, publication dates,
source digests and permitted ordering/subset/retrieval changes.
The [archive regressions](../../../tests/python/test_conductor_archive.py)
exercise real isolated project records, including unfinished tasks and failed
or missing verification.

## Compatibility and downstream work

Bundle 0.1 is independently versioned and wraps valuation profiles 0.1/0.2.
The original fixture digests, numerical methods, dependency pins and minimal
Rust execution boundary remain unchanged. The Python verifier is repository
conformance tooling; financial arithmetic stays in the installed Rust engine.

This contract closes full-snapshot replacement/retraction and synthetic
reference coverage. It does not complete every broader RQ-01–03 capability:

- Rust kernel: automatic interval integration and newly supported numerical,
  capital or financial-correction methods.
- Provider/Python/MCHS tracks: real source releases, recipes, eligibility,
  source correction qualification and full field preservation.
- Process models: event-level corrections, richer timestamps and interval semantics.
- Release/consolidation: licensing, binary/source attestation, broader platforms,
  migration qualification and production publication.

Stable track paths and dependency IDs are retained under the
[archive policy](../../archive/README.md). Archival records contract acceptance;
it does not qualify a provider, economic model, operational service or release.
