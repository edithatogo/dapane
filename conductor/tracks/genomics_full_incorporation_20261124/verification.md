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

The [inventory command](../../../adapters/genomics/src/genomics_microcosting/workbook_ledger.py)
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
