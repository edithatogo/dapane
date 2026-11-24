# TapeStation genomic DNA quality-control replay

The `Process` sheet identifies gDNA QC before library preparation. In
`Labour - Usage - VCGS`, the TapeStation QC block follows the manual and TECAN
extraction alternatives. Its two labour lines use the same stored loaded rate.
The consumable sheet identifies the seven direct per-sample costs before the
next library-preparation heading.

## Source and scope

The replay used the preserved v15 workbook identified by SHA-256
`2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4`.
The source workbook and selected cell observations remain outside Dapane's Git
history and hosted artifacts.

| Cost component | Source cells | Comparison cells |
| --- | --- | --- |
| QC labour | `Labour - Usage - VCGS!G32:G33,L32:L33` | `AB32:AB33` |
| QC consumables | `Cons -  Costs and Util - VCGS!E13:F19` | `J13:J19` |

The provider verifies the source digest and mapped formulas and reads the
original workbook caches. It emits an exact 0.1 request with two labour uses
and seven separate consumable uses. Labour time comes from the literal source
formulas. Consumable quotes and use quantities retain the XML decimal strings.
The Dapane kernel applies the original charged rates and its existing rounding
policy. The original source digest was unchanged after replay.

The newborn-screening fixture retains its original provider identities. Its
regression checks the programme bytes and exact source pins against its own
dated qualification receipt as the installed-consumer pin advances.

## Results

The native CLI and installed Python wheel returned identical complete reports.
Independent exact arithmetic agreed with all nine Dapane lines and the total.
The greatest absolute difference from an original workbook cell was
AUD `3.8e-16`. The installed historical reader also matched all nine original
caches within AUD `1e-12` per line. LibreOffice Calc 26.8.3.1 recalculated
the nine selected formulas in a macro-free workbook with the upstream loaded
rate held at its original cached value. Its greatest residual was AUD `3e-15`.

| Cost component | Dapane sum of rounded lines (AUD) | Exact subtotal rounded once (AUD) |
| --- | ---: | ---: |
| Labour | 8.82 | 8.83 |
| Consumables | 7.04 | 7.04 |
| Selected direct costs | 15.86 | 15.87 |

The one-cent difference comes from rounding both labour lines individually.
The original cells contain unrounded amounts. Rounding their sum once gives
AUD 15.87. The workbook supplies separate source lines for this comparison.
The Dapane report keeps the exact totals and existing line-rounding behaviour.

## Reproduction

The provider function `historical_gdna_qc_request(path)` emits the exact
request from the original workbook. It can be serialized as JSON and evaluated
with the native CLI or passed to the installed Python binding.
[Provider-verification runner](../../../scripts/verify_provider_consumers.py)
checks the workbook, the two Dapane interfaces and the retained historical
reader as part of the installed genomics consumer. It writes the request and
comparison in its temporary evidence directory. The prior manual-extraction
request serialized identically on the same workbook.

The local check ran the CLI and native wheel built with Rust 1.99.1 on macOS
ARM64. The [genomics provider revision](https://github.com/edithatogo/microcosting_genomics/commit/523b84ecc332bc32b09627e86853edeb40e2a8bc)
contains the workbook mapping. The separately installed genomics and workforce providers ran under
CPython 3.15.1 and 3.15.2 respectively, using the pinned source revisions and
locked dependencies. The workbook and extraction regression selection passed
72 tests. Conductor passed its validator and 12 lifecycle tests.

## Remaining gaps

The equipment worksheet prices the TapeStation across declared instrument
throughput and lists it for both WES and WGS. A stage-specific share remains
unqualified. The replay retains the opaque loaded labour rate and the
original direct consumable weights. Cost component decomposition, a full
inventory and overhead roll-up, other QC blocks, pathway-level totals and
library preparation remain outside this result.
