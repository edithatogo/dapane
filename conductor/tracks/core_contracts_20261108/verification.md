# Core-contract verification and closeout

Date: **15 November 2026** (Australia/Brisbane).
Track: `core_contracts_20261108`. Candidate status: `synthetic_candidate`.
Disposition: completed, integrated, then archived in place.

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
- `ea2cbffae505475108bfa5fb67e290f44349fee0`: final reviewed PR #9 head,
  including ADR-012 and acceptance/context reconciliation.
- `224cf91dbcf513feaa022b2cf5aa310a965472ce`: PR #9 integration, before archival.

The [independent review](independent-review.md) records both findings and their
remediation. Its recorded read-only re-review of `bc92e9b` found them resolved
and no further blocking defect. The [earlier review](review.md) retains the
original fail-first and implementer-review history. The coordinator's
[final-head review](https://github.com/edithatogo/dapane/pull/9#pullrequestreview-5907712786)
is an implementer review, not an additional independent approval.

## Observed hosted evidence

Historical head `96b178c0f2b21cd8fc702a86dec2f0cde8fa8504` passed all 11
configured checks. Its Runtime
[43609831820](https://github.com/edithatogo/dapane/actions/runs/43609831820)
recorded 40 native tests and 119 installed-wheel tests per CPython 3.12–3.15 job.
These observations remain historical, not a substitute for final-head acceptance.

The final head `ea2cbffae505475108bfa5fb67e290f44349fee0` subsequently passed
all 11 configured checks before integration:

| Check | Observed outcome and receipt |
| --- | --- |
| Runtime: native and installed CPython 3.12, 3.13, 3.14, 3.15 | All five jobs passed in [43651136979](https://github.com/edithatogo/dapane/actions/runs/43651136979). Inspected native logs show 40 tests passed; all four installed-wheel logs were independently inspected and each records 133 passing tests. |
| CLI/schema/format/lint | Native job passed installed CLI evaluation, five independent reports and original digests, 37 negative schema/parser cases, 14 runtime rejections, three identity/context cases, Cargo fmt/Clippy and Ruff. |
| Conductor | [43651136990](https://github.com/edithatogo/dapane/actions/runs/43651136990) passed. The native log also records 14 tracks, 12 requirements, 145 tasks and 455 local links. |
| Privacy and secrets | [43651137061](https://github.com/edithatogo/dapane/actions/runs/43651137061) passed. |
| CodeQL | All three language/action jobs passed in [43651132670](https://github.com/edithatogo/dapane/actions/runs/43651132670); the [aggregate check](https://github.com/edithatogo/dapane/runs/132622678744) succeeded with no new alerts in changed code. |

The tested checkout was merge candidate
`4d3b71ea59d2449c08fc0b534681d84a87975e5c` against main
`d7063cecc26abe96a3f28fca575b99b450241430`. Its tree and the actual integration
commit's tree are identical: `6af2f8194cebd032fbad495cff95d3acf0066a10`.
The merge used an expected-head guard. No required check or protection was bypassed.

The archive-validator regression was also reproduced locally from the exact
original blob: six intended failures and one pass, then seven passes after the
fix on Python 3.13.5. Hosted installed-wheel acceptance remains authoritative
for the native integration. No local Rust execution is claimed for closeout.

Executed workflow commands included:

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

## Compatibility, archival and downstream work

Bundle 0.1 is independently versioned and wraps valuation profiles 0.1/0.2.
The original fixture digests, numerical methods, dependency pins and minimal
Rust execution boundary remain unchanged. The Python verifier is repository
conformance tooling; financial arithmetic stays in the installed Rust engine.

The user requested merge, then archive. PR #9 was merged first. The subsequent
original archive commit updates seven documentation/metadata files, retaining all
14 completed tasks, the six original criteria, review records and stable paths.
A subsequent compatibility review adds the missing `Status: archived` declaration
to the synthetic archive-test plan. This keeps that valid fixture compatible
with the stricter status validation proposed in setup PR #14.
The pull request retains the existing hosted gates; it introduces no financial
runtime, schema, workflow, dependency or other track implementation changes.

The compatibility defect was reproduced against PR #14 validator revision
`09e81c6e0ab1a80580258f82b5c1506fafd3d45f`: the original synthetic plan failed
the exactly-one-status rule. Adding the status line eliminated that error while
all six unfinished-task/verification negative cases retained their intended
failures. The corrected fixture also passed all seven archive tests and Ruff
lint/format locally against integrated main. These are targeted conformance
checks; archive-head hosted verification remains required before merge.

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
