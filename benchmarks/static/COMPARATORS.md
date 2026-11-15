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
