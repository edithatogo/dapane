# Dated comparator review — 2026-11-15

This is the bounded implementation review for static F1/F2.1–2. It is not a
literature review or a comparison with the strongest available costing products.

| Comparator/reference | Identity | Selection and limits |
| --- | --- | --- |
| Full recomputation | Dapane `e34f87c9df39a2132fecee142431cdeefb732471`; CLI point and interval methods | Existing exact CPU evaluator with validation, provenance and complete reports. Same artifact used by both paths. |
| Complete-request cache | Protocol v1.2; exact implementation SHA in handoff | Avoids repeated native evaluations only. Changed requests still enter Rust. No intra-request dependency engine or production API. |
| Independent oracle | Python standard-library Fraction and built-in rational round | Separately implemented arithmetic, with hand-derived literals. No Dapane function or generated output used as numerical truth. Not a performance competitor or independent human reviewer. |
| Authored truth inventory | Twenty-four synthetic cases | Distinguishes known defects from what the supplied contract can detect. Not independent external data. |

## Primary references inspected

- Pinned [point contract](https://github.com/edithatogo/dapane/blob/e34f87c9df39a2132fecee142431cdeefb732471/docs/contract-v0.1.md)
  and [interval contract](https://github.com/edithatogo/dapane/blob/e34f87c9df39a2132fecee142431cdeefb732471/docs/interval-contract-v0.1.md):
  exact quantities, selected quotes, half-even per source line/generated segment,
  conserving allocation and caller source declarations.
- Existing [CLI benchmark](https://github.com/edithatogo/dapane/blob/e34f87c9df39a2132fecee142431cdeefb732471/scripts/benchmark_cli.py):
  full recomputation, process/JSON boundary and aggregate child RSS. Left unchanged.
- Python 3.12 [Fraction documentation](https://docs.python.org/3.12/library/fractions.html):
  rational arithmetic from strings/integer pairs. The reference rejects floats.
- Python 3.12 [statistics documentation](https://docs.python.org/3.12/library/statistics.html#statistics.median):
  descriptive medians, without significance claims.
- Python 3.12 [resource documentation](https://docs.python.org/3.12/library/resource.html):
  platform-dependent process/children accounting, not a portable per-case peak.

The Python documentation was retrieved on this date; versioned documentation URLs
are not immutable package pins. Actual interpreter/source digests belong in each
executed result bundle. No third-party comparator installation, spreadsheet
analyst experiment, provider performance comparison or external-data study was run.

## Native comparisons on 20 November 2026

The new comparison charges each declared pool once in the object-centric case and copies its total consumption to each joined recipient in the flattened case. Five synthetic newborn requests and one executed PNML trace were evaluated in both forms by the same Rust CLI. Flattening the two-recipient primary pathway raised AUD 150 to 250. Repeat assay work added AUD 20 in both forms. Above capacity, three recipients sharing two instrument blocks cost AUD 230 with a residual of 50. Charging each recipient the full blocks gave AUD 630 and concealed that residual. This experiment demonstrates the consequences of the specified duplicating join. A correctly allocated case-centric representation could preserve the same totals.

A paired measurement experiment ran the installed Voiage EVPI method for two explicitly per-assay synthetic payoff matrices. Staff time had an EVPI of AUD 10 per assay and the comparison AUD 1. An independent adoption scenario ran Innovate's Bass predictor before and after an assumed response to a fiscal valuation. It exceeded capacity in two initial months and zero revised months. The original benchmarks' zero detections for false source assertions remain in the record. [Full results and archive digest](evidence/native-experiments.json)

## Publication fit

The software target is the *Journal of Open Source Software*. The reproducible software contribution fits its scope. A submission would also need evidence of actual research use and substantial, sustained development. These computational comparisons establish behavior on declared inputs. [JOSS submission criteria](https://joss.readthedocs.io/en/latest/submitting.html)

A separate methods article would target *Medical Decision Making* if a study compares the proposed approach against a strong, correctly allocated alternative and establishes a decision-relevant methodological result. For an applied study using an authorised programme dataset and an actual policy decision, the target is *MDM Policy & Practice*. The current experiments support a software benchmark report. Neither submission nor clinical effectiveness has been established. [Medical Decision Making scope](https://smdm.org/medical-decision-making-journal/) · [MDM Policy & Practice scope](https://smdm.org/about-mdm-policy-practice/)
