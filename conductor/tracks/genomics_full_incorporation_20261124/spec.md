# Full genomics workbook and feature incorporation

## Outcome

Full workbook and full feature coverage are both minimum acceptance conditions.
An installed Dapane successor must reproduce the original genomics workbook and
deliver every existing feature and planned deliverable in the frozen legacy
scope. It must run without cloning or fetching executable code from
`microcosting_genomics`. The workbook and any rights-restricted study sources
are explicit, versioned inputs supplied through authorised access.

## Source baselines

- **Original VCGS v15 workbook.** SHA-256
  `2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4`. A
  read-only inventory found 35 worksheets, including three hidden sheets, and
  36,411 formula cells. Use the existing sheet IDs and region notes to seed
  coverage. [Workbook catalogue](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs/table_overview.md)
- **Legacy feature baseline.** Start at `fc8d4178bc3f5ce67cfc0547f7417272562c18a8`.
  Reconcile the executable interfaces, documented support, tests, retained
  versions and roadmap commitments. Include additional maintained sources or
  plans found during the freeze. [Legacy source](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8)
- **Dapane baseline.** Start at `c5480da26d83d306b2df647d3ccd8b7be717a524`.
  Reuse verified manual extraction labour, QC with equipment and overhead,
  three loaded hourly rates, and five library-preparation replays.
  [Prior installed-provider evidence](../../../docs/python-provider-verification.md)
  and [QC and library replay evidence](../genomics_legacy_qc_20261124/verification.md).

## Required coverage

The **workbook ledger** accounts for every worksheet, populated region, input
and formula cell. Retain coordinates, references and output types, including
hidden and working sheets, static tables, validation and assumptions, scenario
branches, summaries and graph inputs. Reconcile the full detailed cost ledger,
labour, consumables, equipment and capital, bioinformatics compute and storage,
all process pathways and the overhead, discount, throughput, labour-price and
currency variants. Trace each output to its source and denominator. Where the
historical workbook has a broken reference or division error, reproduce the
historical error state and evidence any corrected calculation as a separate
version. Resolve the known subtotal, branch and additivity gaps.

The **feature ledger** gives each shipped behaviour and planned deliverable a
stable ID, source, expected result, successor entry point, test and evidence.
Include maintenance and compatibility behaviours that consumers rely on.
Duplicate roadmap and source entries may share a tested outcome. An unfinished,
unmapped or unsupported item stays open.

| Required feature area | Scope to reconcile |
| --- | --- |
| Workbook and model interfaces | Supported workbook editions and version selection, readers, formula engine, data preparation and validation, Python APIs, compatibility imports, CLI commands, configuration and input templates. [Package manifest](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/pyproject.toml) and [API reference](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs/API_REFERENCE.md) |
| Costing and workflow behaviour | Pathway and scenario engines, rate and quantity provenance, schedules, batches, repeats, rework, allocations, data-quality rules and reconciliation. Include deterministic and probabilistic sensitivity, Monte Carlo and their reporting inputs. [Legacy implementation](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/src/genomics_microcosting) |
| Consumer-facing behaviour | Supported CSV, Parquet and report outputs, visualization, web interactions, plugin loading and configuration, workbook revision handling, and documented error, recovery and monitoring behaviours. [Legacy feature summary](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/IMPLEMENTATION_PLAN_COMPLETION_SUMMARY.md) and [user documentation](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs) |
| Planned deliverables | Every distinct commitment in the legacy refactoring, standardization and robustness plans and other maintained plans found during the freeze. Include detailed compute and storage, volume scaling, extensible inputs and external price interfaces, advanced allocation and prediction, and planned quality, performance and security features. [Refactoring plan](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/GENOMICS_REFACTORING_PLAN.md), [standardization plan](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs/STANDARDIZATION_PLAN.md) and [robustness plan](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_PLAN.md) |

## Implementation boundary

Move or reuse the maintained provider code in one optional genomics package.
Keep the existing domain interpretation and compatibility interfaces close
to that code. Reuse the workbook reader, catalogue, formula engine and tests
where they cover the required behaviour. Route common valuation, rounding and
allocation through the existing Dapane kernel with exact JSON. Legacy table
and report formats belong at the compatibility boundary. Implement a new
method or dependency only for a named coverage gap.

## Acceptance

1. **100% workbook coverage.** Evidence accounts for all 35 sheets and every
   one of the 36,411 formula cells, as well as the populated inputs and
   workbook outputs in the frozen inventory. Compare original results and
   representative branch changes with independent oracles. Require exact
   Dapane arithmetic and reconciliation. Record per-comparison precision
   rules where historical Excel caches use binary arithmetic.
2. **100% feature coverage.** Each existing and planned item has an executable,
   qualified successor and traceable evidence. Test the supported imports,
   CLI, formats, UI and plugins through their normal entry points. For
   stochastic and prediction features use frozen inputs, declared seeds or
   appropriate statistical or holdout checks.
3. **Independent installation and reproduction.** Build and install the
   supported artifacts from Dapane in clean environments. Supply authorised
   sources separately, reproduce both ledgers with the legacy checkout absent,
   and retain exact-source CI, including the official offline-security run.
   Keep raw workbook data and restricted receipts in authorised storage.
4. **Preservation and recovery.** Verify a working replacement and rollback,
   retain licensed code, history, workbook and scholarly assets, and record
   consumers' migration paths. Compare a restored baseline after recovery.
   Changing a legacy repository's visibility or archive state requires a
   separately authorised cutover. [Consolidation requirements](../../../docs/release-consolidation.md)
