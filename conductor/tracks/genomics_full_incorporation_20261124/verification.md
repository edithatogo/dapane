# Genomics incorporation verification

## Frozen sources

| Source | Revision or digest | Retention |
| --- | --- | --- |
| Original v15 workbook | SHA-256 `2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4` | An authorised read-only copy and the exact bytes in the private source archive. |
| Legacy source | [`fc8d4178bc3f5ce67cfc0547f7417272562c18a8`](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8) | Complete committed tree in the private source archive. Archive SHA-256 `e00b3a1dd115d0deab503581c697cfce77bca9eb79fbf5e40f4d6d4eecdb609f`. |
| Dapane | [`2e9b7d61a53e9ac58bfb0f9c17a3b41f772cbf57`](https://github.com/edithatogo/dapane/commit/2e9b7d61a53e9ac58bfb0f9c17a3b41f772cbf57) | Planning merge and implementation base. Prior costing comparators remain at their qualified revisions. |
| Legacy release | [`v0.2.0`](https://github.com/edithatogo/microcosting_genomics/releases/tag/v0.2.0) at `e1cc5fdee33725af1e7d9d37f76fc05a50232fca` | Public ref and release metadata retained with the private baseline. |
| Legacy plans and issues | Plans, checklist, documentation and tests in the legacy tree. Issues [#163](https://github.com/edithatogo/microcosting_genomics/issues/163), [#164](https://github.com/edithatogo/microcosting_genomics/issues/164), [#165](https://github.com/edithatogo/microcosting_genomics/issues/165) and [#170](https://github.com/edithatogo/microcosting_genomics/issues/170) captured on 24 November 2026. | Frozen issue snapshot SHA-256 `7effc6d4ced9f389d44e0632534acc1b3a5192be729b024b761295693f86bce0`. |

The provider's Apache-2.0 code licence applies to project-owned software.
The workbook, populated exports, source archive, package environment and
private results stay in authorised storage. Their retention here means
local preservation. Any redistribution of study sources requires its own
rights evidence. The freeze receipt and comparator artifacts are in the
track owner's restricted `evidence/full-genomics-baseline.JxOhgH` directory.

## Runnable legacy comparator

On CPython 3.15.1, the noneditable `genomics-microcosting` wheel built from
[`5af1240324e3d5fa3c8d9dfb198aae81e32b361e`](https://github.com/edithatogo/microcosting_genomics/commit/5af1240324e3d5fa3c8d9dfb198aae81e32b361e)
(SHA-256 `5a81d43206a40281862c09d9446ad073ca003dc03d61ff039e11a936e242dc58`)
has the same package source, configuration, manifest and lock as the legacy
baseline. The retained Dapane wheel has SHA-256
`4bd6f77ba2c6c12e8674ded7e86cd6daa3d45fad0e387bc2cdc3d7feb74bd900`.
The dependency versions, both wheels and the Panel library-preparation
request and result are preserved together.

The installed comparator ran
`historical_library_preparation_request(original, "Panel")` followed by
`dapane.evaluate(request)` from outside both source checkouts. The exact
request produced a report with totals. The source copy and workbook member
extracted from the archived tree both matched the pinned workbook SHA-256.

## Workbook ledger

The [inventory command](../../../adapters/genomics/src/dapane_genomics/workbook_ledger.py)
reconciled populated coordinates and formula counts for every catalogue
sheet against both the raw worksheet parts and the existing workbook
reader. It retained stored numeric strings, text and errors, expanded
shared formulas, formula references, and the worksheet layout including
merged regions and hidden views.

| Observation | Count |
| --- | ---: |
| Worksheets | 35 |
| Hidden worksheets | 3 |
| Formula cells | 36,411 |
| Shared-formula cells | 17,781 |
| Populated nonformula cells | 13,525 |
| Formula caches with `#REF!` | 3 |
| Formula caches with `#DIV/0!` | 4 |

The original formulas use `SUM` (7,881 calls), `PMT` (29) and `AVERAGE`
(28). The workbook's scenario variants live in separate regions and columns.
The private ledger records their coordinates and reference expressions.
It accounts for the source cells and caches. Evaluation and economic
reconciliation are Phase 2 work.

The catalogue digest is
`85f61076a8a0a00ae615a2ac26f962c9f0f159e348017b12454afe4c36e7df21`.
Two runs using the pinned CPython 3.15.1 comparator produced identical
ledger bytes, SHA-256
`9b7a0996b0ca012315ceffcd492ef1813719d2ea56ec7bfcf81a364ffd59aba5`.
An existing output path was rejected. The original workbook digest
matched before and after the inventory.

## Feature ledger

The [feature coverage record](feature-coverage.md) maps the installed and
source entry points, configurations, reports, web and plugin contracts,
planned outcomes and retained issues to their implementation tasks.

Two runs of the source inventory produced the same private ledger, SHA-256
`aa17ce9b28b137c67ad58741681fb56840f07cabbcfd792a76314eef81d3c11e`.
It identifies 109 modules, 1,129 public-looking classes and callables,
two console entry points, 74 source command candidates, 19 configuration
assets, nine package resources, 68 documents and 161 Python test files.
The 812 plan source lines cover proposals, duplicated checklists and
maintenance receipts as well as distinct deliverables. The line count
does not measure completed features.

Installed distribution entry points matched the source manifest. The
installed web module matched the frozen source digest, and its Flask
test client registered all 21 source routes and served the table index.
This check used the provider environment with the plotting dependencies
present. The separate core-only wheel fails to import the web module
without Matplotlib. F09 retains this compatibility gap for installed
successor qualification.

## Prior replay cross-reference

The workbook and feature ledgers regenerated byte-for-byte from the frozen
sources. The private replay map (SHA-256
`e3e819acf9dd1af42f79172c1d202ea3b3d88c74ccc8d18e45cd09f3e6c10c2b`)
matches 15 prior replay records to **322 distinct formula coordinates**
by stable catalogue sheet ID. It links manual extraction and direct
TapeStation QC to the qualified cells, plus the five booked QC cases,
five library-preparation cases and three loaded hourly rates. The 13
follow-on residuals satisfy the previously declared historical comparison
precision of AUD `1e-12`.

These coordinates retain their original scope. The prior comparisons
exercise valuation from selected quantities and rates, and leave full
dependency evaluation, other workbook coordinates, cost roll-ups and the
installed feature ledger open. See the
[prior replay evidence](../genomics_legacy_qc_20261124/verification.md)
and [installed provider evidence](../../../docs/python-provider-verification.md).

Phase 1 passed the Conductor validator and all 12 lifecycle regression tests.

## Independent formula baseline

The installed legacy engine evaluated 36,404 original formulas. Seven
returned no value. The preserved Calc 26.8.3.1 oracle was generated from a
private copy with **all 36,411 caches cleared** and each formula and
formula attribute verified unchanged first. This covers all original
branch columns on WB19, WB20 and WB22–WB25 and their summary and graph inputs.

| Comparison with original caches | Legacy evaluator | Calc recalculation |
| --- | ---: | ---: |
| Stored numeric or text values and error codes agree | 17,660 | 7,134 |
| Additional values coincide at 12 significant digits | 18,728 | 29,248 |
| Remaining numeric residuals are below `1e-12` in original units | 16 | 26 |
| Remaining error-code or missing-output differences | 7 | 3 |

The significant-digit and absolute residual counts describe the independent
comparators. The historical errors all occur on WB32. Calc preserved the
four division errors and translated the three broken references to
`#NAME?`. The installed legacy evaluator returned no value for all seven.
The successor must preserve the original error codes.

The private legacy comparison has SHA-256
`140d734f17c45a44d95553f581d1eb89a8c6dff3077d6a97de0c18d3eea0ef09`.
The Calc workbook has SHA-256
`01926b302bd2752fe65c12f651f37d6627846c5a5b15de2c740a5ae02ce87c20`.
The original workbook hash was unchanged. Synthetic cases for ranges,
rates, annuity, errors and a changed numeric source independently fix
the expected results for the exact replay.

## Exact historical formula replay

The [v15 replay](../../../adapters/genomics/src/dapane_genomics/v15_replay.py)
recalculates from original literal values and coordinate dependencies using
the existing workbook reader and tokenizer. It retains exact rational
results, with no fallback to formula caches. Excel cell errors are typed
values, so a broken reference stays distinct from a divide-by-zero result.
This historical replay does not modify the source or the other legacy
formula dialects.

It produced a result for each of the 36,411 formula coordinates. All
3,227 text results and the seven historical errors matched the source.
Of 33,177 numeric results, 3,680 equal the original decimal cache exactly,
29,476 more agree at 12 significant digits and the other 21 differ by
at most `1e-12` in original units. The latter group preserves the exact
result and per-coordinate residual for inspection. The complete results
include the detailed-table subtotals and all original sensitivity sheets.

The rational result file has SHA-256
`2e8fb6133b913dfd103759eb36cedee6853a53c13c27e2f13e3fcc544b2dff4a`.
The coordinate-level comparison file has SHA-256
`616a67279b67f309993f93421b9c14e35ae032ab06d777057b28d99f15c488cc`.
Both files remain restricted. Two independent synthetic tests cover
cross-sheet ranges, exact expense arithmetic, annuity, input replacement
and distinct propagated errors. Both passed on CPython 3.15.1.

## Detailed pathway and resource costing

The [pathway adapter](../../../adapters/genomics/src/dapane_genomics/v15_pathways.py)
follows each original summary component to its detailed booked charges.
It expands exact detail subtotals, retains quantity and rate from direct
multiplication rows, and carries the source cell and formula for derived
charges. It prices the original overhead base and workbook FX rate
through the existing native Dapane engine.

The installed native binding reconciled **10 pathway/currency totals**,
**100 stage totals** and **1,610 booked lines**. These are the five original
pathways in AUD and USD. The complete replay also retains the detailed
table, labour, capital, consumables, equipment, compute and storage views,
every DSA branch and the separate summary/graph worksheets in the
coordinate ledger. Alternate views carry their original currencies,
labels, source units and denominators. They are kept outside the pathway
sum. Some original USD sensitivity rationals exceed the core request
bound. They remain exact values in the workbook replay.

The original WGS processing and storage blocks reference the same two
booked detail sources more than once in each WGS pathway. The adapter
retains each occurrence with a separate line identity so the historical
sum is reproduced and reports the repeated source coordinates. It does
not infer a prospective charge correction from a historical overlap.
The result remains identified as the original workbook financial view.

The private pathway ledger has SHA-256
`f3a729ad81f1c0d2f86dc33e627377c9cf385cda66d4fc08342b6cead2568f90`.
Baseline formula results and component and pathway sums are reconciled
before the requests are evaluated. G2.4 independently checks native CLI
parity and changed source inputs.

## Formula, branch and installed native verification

The replay regenerated the same baseline results and reconciled 49,936
populated coordinates. A separate workbook copy changed the source FX,
labour on-cost and selected consumable price. The copy used a declared
synthetic scenario and cleared all formula caches. The installed Calc
oracle and exact replay compared all 36,411 formula coordinates.
The changes affected 7,321 formula outcomes across 24 worksheets.

The variant matched 5,383 numeric values exactly, 27,781 at 12 significant
digits and 13 with absolute residuals at most `1e-12` in their original
units. It matched all 3,227 text outputs and four division errors. The
three known Calc reference translations were recorded. The successor
preserved `#REF!` for each. The changed workbook comparison has SHA-256
`68d458daa69b594717a553a9b42850d09eb55a2361d78f3d792ff3130606d484`.
The original v15 source still matches its frozen digest.

Running all ten exact requests with the separately installed Dapane
0.1.0 CLI and CPython 3.15.1 binding produced identical full reports.
All 1,610 line amounts round independently half-even, all 100 stage
totals equal their source formula and all ten exact pathway totals
reconcile. The parity receipt has SHA-256
`18e337c8643548835908353c88a5f610cbb136afa3d11f36c59889d2b42227b1`.
The workbook replays are qualified for the historical source and
tested comparisons. Installed legacy feature and full successor
qualification remain in Phases 3 and 4.

## Installed legacy feature contract

A clean private extraction of the frozen provider built and installed the
legacy distribution noneditably with the frozen lock on CPython 3.15.1.
The installed byte digests matched all 109 enumerated modules. All nine
package resources were present. The same installation supplied the legacy
test suite with visualization, reporting and security extras.

The full baseline suite passed **1,335 tests** with sockets disabled.
Four tests skipped because their prepared labour-price and throughput
tables were unavailable under their expected names. The four skips were
reproduced in a targeted run. The outcome and input paths remain in the
feature qualification inventory.

From a separate consumer directory, the installed `prepare-data` produced
35 CSV and 35 Parquet files. Installed `validate-engine` passed all 2,894
selected comparisons across three detailed-table cost columns. The fixture
copy, exports, lock log and test receipts remain in restricted storage.
The installed route-map result and Matplotlib gap are recorded in the
[feature ledger](#feature-ledger).

These baselines define the compatibility checks to run again with the
optional package built from Dapane.

## Dapane-built legacy runtime

The [optional genomics distribution](../../../adapters/genomics/README.md)
keeps the source-pinned implementation and both legacy console entry
points alongside the v15 replay commands. Its licence, citation,
configuration templates and lock are included. The native extra uses the
Dapane binding. The installed artifact contains the source catalogue and
the original package resources, with the workbook provided separately.

A noneditable CPython 3.15.1 installation built from Dapane matched the
frozen source digests of all 109 legacy modules before subsequent
compatibility fixes. It passed all 1,335 available inherited tests with
sockets disabled. The four old DSA skip cases were then exercised by
supplying the two verified export tables under their expected historical
filenames in the private test harness. The focused six-case run all passed.

An independent consumer directory used the installed entry points and
the packaged catalogue. Its workbook inventory, exact formula results
and native pathway reports reproduced the prior artifacts byte-for-byte.
The 35 CSV and 35 Parquet outputs also matched all 70 legacy export
digests. Installed validation again passed all 2,894 comparisons across
the three selected cost columns.

The remaining report, web, plugin and revision checks are G3.3. Planned
capabilities and the complete feature dispositions are G3.4 and G3.5.

## Reports, web and compatibility tools

The installed wheel passed the 21 registered Flask routes on synthetic
data, including three generated charts and CSV, Excel, JSON, Parquet,
ZIP and PDF exports. Reopening the exports verified their content.
Missing tables and invalid chart requests returned their expected errors.
The separate locked base installation served the table and monitoring
routes and reported the optional visualization dependency for charts.
The health check follows the selected data directory.

The dashboard was opened in Codex's internal browser. It displayed one
loaded table and three records and the detail link rendered all three
rows. The successor uses the actual loaded counts in the dashboard.
It also passed the focused 38 legacy web, version, plugin and recovery
tests plus the optional dependency regression.

The installed `genomics-report` uses native Polars tables and the legacy
chart generators. A synthetic fixture produced matching Markdown, HTML,
JSON and three linked charts. Installed module execution with WeasyPrint
and the existing macOS libraries generated a PDF whose text was verified.
The separate comprehensive report reused the original archived PSA data
from restricted storage and produced all six individual analytical
reports. The raw notebook and data are supplied separately as inputs.

The unqualified legacy source scripts remain visible for feature
reconciliation. The installed report command replaces the old Pandas
report implementation.

## Planned feature implementations

The installed optional wheel passed eight new adapter tests including
workbook replay, the web compatibility regression, external pricing,
cost prediction and model templates. Under synthetic input, an exact
volume tier changed the booked compute cost from AUD 50.00 to AUD 43.75.
Dapane assigned the shared amount as AUD 14.58 and AUD 29.17 with zero
residual. The returned price-release digest, applied tier and native
request permit an offline replay. The external reader was a deterministic
test provider.

The prediction test recovered an independently specified cost model on
two held-out observations and rejected an underidentified fit. Numeric
predictions are kept separate from monetary valuation.

The installed model command supplied all six template specifications and
editable Excel/CSV inputs. Label normalization kept the exact input costs
and typed output. The taxonomy audit reported common categories, model
gaps, and unknown subcategories.

A baseline regression selection covered 231 existing compute, storage,
dynamic-batch, allocation, checkpoint/recovery, security, configuration,
monitoring, quality and scenario tests. The remaining planned outcomes
and legacy source commands are still being reconciled against installed
behaviour.

The optional lab profile extends template categories and recognizes local
labels in the model audit. The installed Flask flow generated and reopened
an Excel template containing a synthetic uploaded label and rejected an
invalid profile. The CLI and web form use the same validation and template
code. A separate cost-adjustment test multiplied a synthetic AUD 12.50
labour quote by exactly 1.2, producing AUD 60 for four hours in native
Dapane. The receipt retained the original quote and the lab profile hash.
A second test changed depreciation from five to nine years on a separate
on-prem model. With the synthetic residual value of AUD 100, annual
capital cost fell from AUD 180 to AUD 100. The original valuation replayed
unchanged.

The Codex internal browser downloaded a Panel CSV with synthetic local labels.
Reopening the file verified the labels and the blank unit cost. The installed
performance command measured workloads at 1,000, 5,000 and 10,000 rows.
Each run checked the real contribution totals, recorded elapsed time and RSS,
and rejected an intentionally slower candidate in the automated comparison.
The 101-repeat same-host comparison against the earlier installed successor
measured median runtime changes of −0.65%, +3.22% and −2.90%. All three
named workloads met the 5% gate on that host.

The installed recovery test wrote a checkpoint after 1,000 seeded draws,
interrupted the next write and reopened the last valid disk checkpoint.
The resumed 2,000 draws matched the uninterrupted case, within the
30-second transient recovery target. The template quality check passed
the complete synthetic model at 100% and detected a changed cost on the
next run. The original workbook's projected model tables retained their
empty fields and showed the corresponding quality failures. The exact
workbook replay remained reproducible.

The [dashboard templates](../../../adapters/genomics/deploy/README.md)
use one non-root image, read-only prepared data mounts, and private service
boundaries. CloudFormation linting passed for the Fargate task. Bicep
compiled the Azure template and its generated ARM template retained
internal ingress and the readiness endpoint. Provider deployment and
consumer acceptance remain separate.

## Source command qualification

The source distribution contains the formerly Pandas-dependent commands
with the native replacements listed in the [command audit](feature-coverage.md#source-command-audit).
The source and installed runtime have no Pandas imports on those paths.
The installed commands completed in an independent consumer directory
without the legacy checkout on the import path. Their distinct evidence
includes 35 CSV and Parquet worksheet round trips, 17,897 detailed-table
comparisons, 1,014 cost-row comparisons, 39 process worksheet cells and
99 comparisons of server, equipment and storage fields, with zero
disagreements in those groups.
The worksheet that supplies shared labour inputs used its own assay label.
The deterministic and archived probabilistic outputs contained 70 and five
evidence rows respectively.

Coverage from the installed compatibility commands and focused package
tests measured 98% for model processing, 98% for workbook compatibility
and 100% for the performance command helpers. The measurements include
branches and subprocesses. The 35-table transfer also generated a
portable test that verified the retained export digests.
The consistency report checked all 35 regenerated table pairs. It also
reported schema disagreement when a retained CSV did not match its
Parquet counterpart and continued checking the other tables. The
standalone dashboard command wrote three PNGs from the verified exports.

The frozen feature audit remains open for individually tracing the rest
of the documented commitments and repository controls. GitHub reported that Dapane's `main` branch was
unprotected and had no active branch rules from a ruleset. Exact-head
qualification is recorded below. The repository's planned safeguards
still require native readback after any future settings change.

## Standalone installed artifacts

A locked CPython 3.15.1 environment built the wheel from a source
distribution. The distribution verifier checked allowed paths, structural
asset digests, source-to-package bytes, Apache-2.0 licence, attribution
and Python version metadata. Research workbooks, notebooks and prepared
tables are supplied separately.

The clean installed wheel passed all 151 packaged synthetic tests with
sockets disabled. The frozen interface inventory matched 109 module
paths, 1,129 declared signatures and 21 legacy route registrations.
This structural comparison and the runtime tests measure different
parts of feature coverage. Both legacy console commands ran from a
separate consumer directory and again reproduced all 70 exports
byte-for-byte and passed all 2,894 selected validation comparisons.

The native ports of the legacy all-sheet preparation and validation scripts
prepared and validated all 35 workbook sheets from a separate consumer
directory. They retain original sheet names for formula lookups, use the
Parquet schema when reading CSV, and preserve the text of mixed Excel cells.
The separate legacy reporting command produced both Markdown reports and
three linked charts using an installed Polars-backed runtime.

The clean successor replayed the restored workbook with sockets disabled.
The workbook inventory, formula results and pathway results matched the
previous installed receipts byte-for-byte.

The separate inherited suite used the same installed package with sockets
disabled, the frozen test sources and the original authorised inputs. The
full run passed 1,338 cases. The remaining case needed the candidate lock
copied into the harness and passed on the focused rerun. This covers all
1,339 inherited cases, including the four earlier prepared-input skips.

The later native source commands, lab adjustments and recovery changes
built from a checked source distribution and passed 173 packaged tests
with sockets disabled. After including the candidate lock in the test
harness, the independent inherited suite also passed all 1,339 cases in
one run. The installed replay produced the same workbook, formula and
pathway JSON bytes as the retained prior receipts.

## Hosted qualification

The official GitHub-hosted offline check passed for the frozen baseline
and full workbook replay, both before and after merge. The full replay
landed in [PR #82](https://github.com/edithatogo/dapane/pull/82) and
passed on [the exact resulting main revision](https://github.com/edithatogo/dapane/actions/runs/45418815055).

The package promotion in [PR #83](https://github.com/edithatogo/dapane/pull/83)
corrects the inherited localhost debugger setting. After the official run
identified a parser failure, the port retained deferred import behaviour
through the named module declaration and converted inline generics to
conventional typing declarations. CPython 3.15.1, strict type checking
and installed imports passed on the revised source. All 18 applicable
checks passed on the exact PR head, including the
[official offline scan](https://github.com/edithatogo/dapane/actions/runs/45428022620).
GitHub merged the package port at `3b870e185a7e824cfe982daccc05cee7c1a62026`.
The [main-push qualification](https://github.com/edithatogo/dapane/actions/runs/45485868671)
passed on that merge revision.

[PR #84](https://github.com/edithatogo/dapane/pull/84) promoted the standalone
wheel qualification. The [official PR scan](https://github.com/edithatogo/dapane/actions/runs/45486862639)
and the [official main scan](https://github.com/edithatogo/dapane/actions/runs/45488752881)
passed for its tested head and the resulting commit
`f7ab5be260206bf5dfe70a930e31040d7923d49b`.

[PR #85](https://github.com/edithatogo/dapane/pull/85) added lab adjustments
and the first costing commands. All 19 applicable checks passed, including
the [official PR scan](https://github.com/edithatogo/dapane/actions/runs/45488885966).
The merge commit is `9a63e7d7d8f313b49ffcb76963e8e1bb3b1c800f`.
Its [main-push qualification](https://github.com/edithatogo/dapane/actions/runs/45491086666)
passed on that exact merge revision.

[PR #86](https://github.com/edithatogo/dapane/pull/86) promoted the remaining
compatibility commands, dashboard images and deployment templates. Eighteen
applicable checks passed on the PR head, including the
[official offline scan](https://github.com/edithatogo/dapane/actions/runs/45496313649).
The [installed package check](https://github.com/edithatogo/dapane/actions/runs/45581128943)
also passed on merge commit `463cad0944eeb0c97d977babdf0fda056b378a50`.
On that commit the official offline workflow stopped during scanner image
preparation on [both attempts](https://github.com/edithatogo/dapane/actions/runs/45581129433/attempts/2).
The four CPython patch downloads had changed bytes. The scanner's locked
Wolfi packages, original standard-library files and patched standard-library
files all matched their existing hashes. The
[scanner policy update](https://github.com/edithatogo/repository-standards/pull/188)
refreshes the four download hashes and retains the original and patched
file checks and the network-disabled source scan. The
[official image qualification](https://github.com/edithatogo/repository-standards/actions/runs/45585316412)
passed before the update merged at `14566821013181e3b2396d6d4fb09ba6d07a8b99`.

## Preservation and restoration

The restricted source bundle contains all four public branch heads and the
v0.2.0 tag from the frozen refs receipt, with complete Git history. Its SHA-256
is `8175e779ae51148c6778e0841f31a70bd561d334a81709af8f215bb7e543c1e7`.
The hosted release has zero separately attached files. The source archive
and bundle preserve the catalogue, original workbook, notebooks, manuscript,
software citation, licence and published source history. The private freeze
records the file inventory and source digests. Workbook and study-data
redistribution requires its own rights evidence.

A new local clone restored the pinned commit and tag from the bundle.
`git bundle verify` and `git fsck --full` passed. The restored workbook bytes
matched the frozen SHA-256. A legacy wheel built in the restored checkout
using the original lock and CPython 3.15.1 was installed into a new environment
with the retained Dapane 0.1.0 build. With sockets disabled, its Panel
library-preparation request and native result matched both frozen records.

To migrate, use the [installation instructions](../../../adapters/genomics/README.md)
from a separate consumer directory. Supply the original workbook and any
supplemental research assets from the authorised store. For rollback,
restore the verified bundle and tag locally, sync the recorded lock and
repeat the frozen replay from an installed wheel.

### Retirement decision

Retain the legacy repository as a public reference for now. GitHub still
showed it as public and unarchived on 25 November 2026. Its maintenance
issues and pull requests remain open. The verified bundle, the historical
replay and the installed successor give consumers a tested migration and
rollback path.

Revisit retirement when the full frozen feature audit has closed and
dependent consumers and published references can still resolve the source
and software citation. Confirm separate rights for study assets as needed
and obtain explicit authorization for the repository's archive and
visibility changes.
