# Core-contract reference cases

All quantities, prices, dates, assets and labels here are invented. The
[reference data](references.json) contains an explicit presegmented request and
hand-derived expected results, not outputs copied from Dapane or a legacy package.
The [installed tests](../../tests/python/test_core_contract_completion.py) apply
explicit documented mutations to this reference for positive, boundary and invalid
cases. Existing workforce, genomics, weighted activity, newborn and capacity
fixtures remain part of the full acceptance set; none is replaced.

## Independent arithmetic

An interval spans a quotation boundary: 1/3 h at 90 plus 2/3 h at 120 gives
30 + 80 = 110. Correcting the first duration to 1/2 h gives 45 + 80 = 125.
The original report remains 110; its replacement is 125; a later withdrawal
returns no financial report. These three records do not total 235 or zero.
Using the old quote on its excluded end date is invalid. An automatic interval
field or negative retraction is unsupported rather than silently converted.

An asset acquisition view contains a prepared price of 12,000. A separate
accounting view contains an explicitly prepared candidate monthly charge of
12,000 / 60 = 200. Both can be evaluated as quotations, but a bundle cannot
include both declared treatments for the same asset. The 12,200 mixed report
is deliberately a negative fixture even though its arithmetic is valid.
Neither division nor economic admissibility is inferred by the numerical core.

## Evidence and scope

Bundle/source/quote/method identities, native reports, publication/retrieval dates,
excluded/missing/unsupported inputs and observation windows are bound by the new
[run-bundle contract](../../docs/run-bundle-v0.1.md). SHA-256 is integrity evidence,
not a signature or source verification. Tests reseal corrupt requests, mismatched
reports and false release mappings to prove that semantic checks do more than
compare a supplied hash. A caller-retained head checkpoint detects missing suffixes.

The source-state transport test uses fabricated labels including `observed`,
`restricted` and `source_verified`; this tests preservation of distinct declarations
without importing observed or restricted information. Real source qualification,
automatic interval splitting, capital formulae and production bundles remain with
their existing provider/kernel/release owners.
