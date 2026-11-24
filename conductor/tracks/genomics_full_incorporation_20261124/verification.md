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
