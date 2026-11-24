# Genomics legacy quality-control costing

The VCGS labour workbook places TapeStation genomic DNA quality control after
the extraction routes. The two labour rows are the next scope after manual
extraction. The genomics provider owns the workbook mapping. Dapane owns the
valuation, rounding and report.

## Acceptance

1. Bind the replay to the original workbook and preserve the formulas, input
   quantities and rates, and cached row results used for comparison.
2. Produce a runnable exact JSON request for the two quality-control labour rows
   through the genomics provider. Preserve the existing extraction and legacy APIs.
3. Check each exact line and the combined total through the native CLI and an
   installed Dapane wheel. Compare each line with the original workbook cache and
   the installed historical calculator. Record differences and their sources.
4. Record source, runtime and artifact evidence and remaining gaps. Retain the
   track in the registry after verification.

This increment covers labour only. It leaves reagents, equipment, overhead,
new assay or batch assumptions, and later library preparation for separate
qualification. Historical labour inputs retain the workbook's original cost basis.
