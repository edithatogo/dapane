# Python provider qualification

Track: [python_two_consumers_20261108](../conductor/tracks/python_two_consumers_20261108/index.md).
Status: installed-provider and Dapane hosted acceptance passed; final genomics coverage remediation in progress,
15 November 2026 (Australia/Brisbane; execution receipts dated 14 November UTC).

## Delivered boundary

Two independently owned Python providers compose through a digest-pinned JSON
quotation artifact and invoke Dapane's existing Rust numerical implementation.
Workforce selects and exports a dated labour quotation. Genomics constructs
explicit resource uses for one manual DNA extraction stage. Python performs
validation and transport; valuation, rounding and allocation remain in Rust.

| Repository | Reconciled main before this increment | Bounded change |
| --- | --- | --- |
| Dapane | `d7063cecc26abe96a3f28fca575b99b450241430` | Installed-consumer qualification, immutable provider pins and track evidence; no numerical-core changes. |
| [Workforce PR 305](https://github.com/edithatogo/microcosting_healthworkforce/pull/305) | `ba86fdf6843d070d257f799e061ea14d18fba387` | Canonical import namespace, legacy compatibility, selected quotation exporter and consumer. |
| [Genomics PR 173](https://github.com/edithatogo/microcosting_genomics/pull/173) | `de09042469fce2f48b1227283a9e2daa08fc7c79` | Manual extraction recipe, batch attempts, quotation admission and historical comparison. |

The exact qualification revisions and release digest are recorded in
[provider-consumers.lock.json](provider-consumers.lock.json). Provider ownership,
dependency locks and historical engines remain intact. Other Dapane tracks and
the conditional repository-consolidation proposals retain their own status.

## Selected source and component scope

The source is Queensland Health's [health practitioners wage
table](https://www.health.qld.gov.au/hrpolicies/wage-rates/health-practitioners#table36083):
HP3, pay point 1, the displayed hourly base reference effective 1 September 2026.
The selected amount is **AUD 46.0658 per hour**. The source describes hourly
figures as reference rates; this adapter does not determine employment eligibility
or payroll entitlements.

| Identity | Value |
| --- | --- |
| Workforce release | `qld-health-hp3p1-reference-20261115` |
| Source observation / knowledge date | 15 November 2026 |
| Quote validity | 1 September 2026 inclusive to 16 November 2026 exclusive |
| Included component | `base_salary` only |
| Hour quote | `qld-hp3p1-hour-20260901`: amount "46.0658", denominator "1" |
| Minute quote | `qld-hp3p1-minute-20260901`: amount "46.0658", denominator "60" |
| Captured source SHA-256 | `6948663378e34af05b8dbf91d8799ad1dc14ee831136dc57165d3241d1af17ff` |
| Canonical release snapshot SHA-256 | `160c58975b20e708fb6b46d33782391230fa97e0c033ea2341545ad1255c516c` |
| Canonical artifact SHA-256, excluding its own digest field | `9cd5e8bb48b29186b7fd4ea911f914c0e0dbf4f3fc188a1f6728cbe65947ec60` |

The artifact retains the original release snapshot, source scope, version,
validity, explicit bindings and component coverage. The consumer requires an
external expected digest. A self-reported digest alone does not select a trusted
release. The source snapshot was acquired and checked; its captured HTML is not
redistributed in Dapane.

Superannuation, allowances, loadings and productive-hours adjustments are not
included. Assigning this QLD role to the historical extraction tasks is an
explicit analyst scenario. It makes no classification-equivalence claim.

## Extraction recipe and independent cases

The selected workbook mapping declares **30 minutes of laboratory work plus
5 minutes of administration per physical batch**, with one to six named
specimens. Each explicitly declared attempt incurs both uses, including a failed
attempt and its retry. No failure probability is generated.

The adapter creates two resource lines and one allocation pool per attempt.
Allocation reconciles the rounded source ledger over the actual named specimens.
An allocation view does not create a second source cost or establish unused
capacity.

| Qualification case | Independent exact total (AUD) | Rounded total (AUD) |
| --- | --- | --- |
| Workforce exposure: one third of an hour | `230329/15000` | 15.36 |
| One physical 30 + 5 minute batch | `1612303/60000` | 26.87 |
| Failed attempt followed by one retry | `1612303/30000` | 53.74 |
| Six separate 5 + 5/6 minute specimen constructions, same current rate | `1612303/60000` | 26.88 |

The six occupancy cases expect conserving shares in stable specimen order:

| Specimens in one batch | Allocated amounts (AUD) |
| --- | --- |
| 1 | 26.87 |
| 2 | 13.44, 13.43 |
| 3 | 8.96, 8.96, 8.95 |
| 4 | 6.72, 6.72, 6.72, 6.71 |
| 5 | 5.38, 5.38, 5.37, 5.37, 5.37 |
| 6 | 4.48, 4.48, 4.48, 4.48, 4.48, 4.47 |

For three specimens across two physical attempts, each pool is allocated
separately. Their accumulated shares are **17.92, 17.92 and 17.90**. Pooling the
attempts before rounding would change the specified method.

## Historical interpretation

The unchanged provider workbook is
`Microcosting - Study 1 - Utilisation and Microcosts v15 (20230902).xlsm`,
SHA-256 `2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4`.
The selected sheet is `Labour - Usage - VCGS`; D22/D23 hold batch time,
E22/E23 the nominal six-specimen divisor, L22/L23 the historical loaded rate,
and AB22/AB23/AB24 the resulting labour values and total.

The comparison keeps four observations distinct:

1. **Mechanical extraction:** verify the source hash, expand shared formulas
   through the provider's read-only workbook reader and retain raw XML caches.
2. **Historical replay:** use the original rates and per-specimen quantities in
   Rust; compare exact expected arithmetic and native/Python reports. A tolerance
   of `1e-12` applies only to comparisons with historical binary cache values.
3. **Legacy entry point:** call the actual installed `SheetManager` and
   `CalculationEngine` through the preserved adapter. Require nonmissing
   AB22/AB23/AB24 values and compare them with separately extracted caches.
4. **Current scenario:** use the selected base-pay quotation and actual batch
   membership. Explain changed rate, component coverage and allocation scope.

No formula repair is applied. A controlled comparison under the same current
quote isolates a one-cent rounding difference: six individually rounded
per-specimen constructions total 26.88, while the physical batch totals 26.87.
Their exact totals agree. This is a ledger-granularity consequence, separate
from the historical-to-current price and component changes.

These checks qualify the selected mechanical mapping and executable paths.
They do not validate a complete assay, the rest of the workbook, a clinical
workflow or an economic study. Existing PSA/VOI demonstrations remain outside
this qualified slice.

## Installation and compatibility

Workforce retains **CPython 3.15.2**; genomics retains **3.15.1**. They run in
separate environments with their own locked dependencies, exchanging the exact
JSON artifact. Both load the same built CPython 3.15 Dapane wheel and compare
complete reports against the native CLI built from the same Rust source.
This does not assert co-installability of the differently pinned providers.

The [qualification workflow](../.github/workflows/provider-consumers.yml)
builds provider wheels and installs them without editable source imports.
The [runner](../scripts/verify_provider_consumers.py) executes from a temporary
directory with `python -I`, asserts installed module locations outside each
checkout and checks the actual native-extension suffix. Its workbook/source
reads are explicit data inputs, not Python import paths.

Workforce's canonical package is `microcosting_healthworkforce`. The historical
`src` namespace retains actual module and class identity, old pickle loading and
module entry points. The original `price_units` route remains callable. Its
original digest convention is preserved independently of the new canonical
transport digest.

Genomics keeps its previous calculator route explicit. Rolling back an analysis
selects the prior provider release or historical entry point, original source
artifact and recorded policy. It does not silently relabel historical outputs
under a corrected rate or method.

The broader native matrix remains Linux x86_64 CPython 3.12–3.15, with actual
runs in [runtime verification](runtime-verification.md) and the CI evidence below.
No new macOS, Windows, ARM, PyPy, free-threaded or stable-ABI support is inferred.
The packages remain unpublished candidates; licence and release-assurance work
retain their separate prerequisites.

## Verification record

The two noneditable provider wheels passed the complete
`verify_provider_consumers.py` stages with isolated Python execution from
`/tmp`. Module-location assertions excluded source-checkout imports. Both
consumed the identical built native wheel and matched complete native CLI
reports, including the actual installed legacy calculator route.

| Check | Observed result |
| --- | --- |
| Workforce installed stage, Python 3.15.2 | Passed export/regeneration pin, hour/minute transport, nonterminating exposure, native parity, legacy identity/pricing, component overlap and tamper rejection. |
| Genomics installed stage, Python 3.15.1 | Passed all six occupancies, failed/repeated attempts, per-pool allocation, same-rate rounding control, date/digest/mapping rejection, workbook inspection, historical native replay and actual legacy-cache parity. |
| Provider focused tests | Workforce adapter/namespace/profile: 64 passed. Genomics adapter/workbook: 69 passed. |
| Provider source checks | Ruff lint/format, strict typing and Bandit passed in both owning repositories. |
| Installed Dapane native boundary, original candidate | 74 tests passed on Python 3.15.1. |
| Installed Dapane boundary plus newly merged core-contract checks | 133 tests passed against main `224cf91dbcf513feaa022b2cf5aa310a965472ce`; Rust and Python package source remained unchanged. |
| Earlier hosted runtime matrix | [Run 43651005666](https://github.com/edithatogo/dapane/actions/runs/43651005666), revision `68d8ab37688893e3b5619dbe102c1d1c47ce994b`: native and Python 3.12–3.15 jobs passed. |
| Hosted Dapane qualification | Revision `bc96cc17f10edf604159f70d477f5e114326833e`: [installed providers](https://github.com/edithatogo/dapane/actions/runs/43653483642), [runtime matrix](https://github.com/edithatogo/dapane/actions/runs/43653483613), Conductor, privacy and CodeQL all passed. |
| Hosted workforce qualification | Revision `c351a7c6420a356c4c13d2da3010bc7e7d0341f9`: [1,085 tests passed, 91.58% coverage](https://github.com/edithatogo/microcosting_healthworkforce/actions/runs/43653350876/job/132626435859), with every required security check passing. PR 305 merged as `8fa5882e2fda6cdba9ae93c46542c5b0b874c260`. |
| Hosted genomics qualification | The prior functional, quality, integration, package and privacy gates passed, but patch coverage was 80.48% against 90%. Tests-only remediation `be2451f34a389f90e618cf37a5e8e1fcbb148dea` is in [run 43656442325](https://github.com/edithatogo/microcosting_genomics/actions/runs/43656442325). |

The earlier broad local workforce run passed 1,082 tests; three tests requiring
LibreOffice lacked that local executable. The final hosted run installed
LibreOffice and passed all 1,085 tests, resolving that environment limitation.
Its unchanged mutation gate passed with 45 of 46 mutants detected (97.826%),
one survivor and no errors, timeouts or pardons.

### Reconciliation with the completed Rust kernel

Main advanced again to `172d0ef39291a936a35c6e221eb467701ccefbba` when the
separately reviewed Rust-kernel track merged. The coordinating branch
retains its interval capability and archive records. Both installed
provider stages and all 133 Python tests passed again using a newly built
wheel and CLI from that exact Rust source. This covers the actual combined
provider integration, beyond the earlier hosted checkpoint.

| Integrated artifact | SHA-256 |
| --- | --- |
| Dapane CPython 3.15 wheel from main `172d0ef` | `f3bbba92172ec56273130ca2d7ff6f1ac3ac474ba0364886309bd2a171084790` |
| Native CLI from the same source | `912d62222ead99ef701078b00e517b1a91cd0faf9204678f44fe64eb7f807dac` |

### Earlier local artifact identities

| Artifact | SHA-256 |
| --- | --- |
| Dapane CPython 3.15 native wheel, Rust 1.99.1 | `f0b916236e7ad5ea36c905878d8d2c67cf5f38601a85e2be1ca3307d009c4c79` |
| Native CLI from the same Rust source | `c26f185ac267c9d4ded647450a3ceda8604c722cce7eceba464695ced49af6fc` |
| Workforce 0.0.1 wheel | `96eb7363e395ee236a7836fa5714efdf0e02b2572975af5e1d4814709749771c` |
| Genomics 0.2.1.dev25+g90eb19dbc wheel | `544b77517044872875a5578d81e09fc274b31b8f93b9ec68b0c149e311b19eaa` |

These identify the local qualification artifacts, not published releases.
The immutable provider source revisions are in the lock file. The root workflow
rebuilds them independently with the same locked dependencies and executes:

- `cargo build --locked --release -p dapane-cli`
- `maturin build --locked --release --interpreter <python-3.15.1>`
- Each provider: `uv sync --locked --no-install-project --python <exact-version>`,
  `uv build --wheel`, and noneditable `uv pip install --no-deps`.
- Outside the checkouts: `python -I <runner> workforce|genomics ...`.
- `python -I -m pytest --import-mode=importlib <dapane>/tests/python -q`.

The [review record](../conductor/tracks/python_two_consumers_20261108/review.md)
records findings and remediation. The initial hosted installed-provider attempt
stopped at formatting before any consumer qualification; that correction passed
locally. Earlier interrupted setup and failed attempts are not acceptance
evidence. Generated requests, workbook observations and reports stay in temporary
qualification storage; the workflow does not upload them.

## Coverage-gate remediation

The genomics production code, interpreter pin, dependency lock and source data
are byte-unchanged from the reviewed `90eb19d` implementation. Commit
`be2451f34a389f90e618cf37a5e8e1fcbb148dea` adds only meaningful regression
tests for synthetic workbook inspection, shared formulas, raw-cache preservation,
exact historical exposures, comparison classification and native delegation/error
propagation. Its test-local digest override never labels the synthetic fixture
as the original workbook evidence.

Independent review passed. On exact Python 3.15.1, the full local suite passed
**1,318 tests with four existing skips**; all 69 focused cases passed. The three
new production modules cover **319 of 328 statements (about 97.26%)**; overall
repository coverage is 78.50%. The existing 90% patch threshold is unchanged.
Ruff lint/format, strict typing, the final wheel build and package checks passed.

The new genomics wheel is version `0.2.1.dev26+gbe2451f34`, SHA-256
`8cae36ec2bb2496616cdebac4436b2dd362a30c1285b8822fa970e4bc7f1edae`.
The coordinator pins the new revision and reruns its installed-consumer job;
its preceding artifact identities remain dated evidence, not a claim that the
new wheel has the old version or hash.
