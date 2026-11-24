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
