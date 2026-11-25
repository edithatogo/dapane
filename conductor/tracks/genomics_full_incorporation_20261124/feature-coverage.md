# Legacy feature coverage

The source baseline is [`fc8d4178bc3f5ce67cfc0547f7417272562c18a8`](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8).
The [inventory command](../../../adapters/genomics/tools/feature_inventory.py)
records each module, callable and constructor signature, registered Flask
route, console entry point, package resource, source command, configuration
file and candidate test. Module and qualified symbol names identify shipped
interfaces. The private ledger also retains each source plan's heading,
line, text and version. A test importing a module is a candidate for review.
Completion requires a test of the installed behaviour.

## Existing interfaces

The successor keeps the `genomics-microcosting` distribution and the
`genomics_microcosting` import, including module paths, call signatures,
resource loading and command names. The v0.2.0 release already uses this
namespace. Historical configuration paths, positional calls, workbook
versions and pre-rename sources are retained as separate compatibility and
reproduction cases. G3.1 confirms the observed behaviour, including any
documented aliases, before G3.2–G3.4 change package or entry-point code.

| ID | Required outcome | Successor entry points and qualification |
| --- | --- | --- |
| F01 | Read and validate all supported workbook versions, merged headers, worksheet views, prepared data and exact source identity. Preserve formula parsing, evaluation strategies, cache and errors. | `sheet_manager`, `excel_utils`, `loaders`, `formula_parser`, `calculation_engine`, and `validate-engine`. G2.2 covers the original workbook and G3.2 covers other supported inputs. |
| F02 | Prepare source tables, transform and standardize records, convert formats, track data versions, and validate dependencies. Preserve CLI options and failure modes. | `prepare-data`, `data_manager`, `data_management`, `data_pipeline`, `extractors` and `transformers`. G3.2 verifies installed CLI and Python round trips. |
| F03 | Preserve quoted components, execution and inventory ledgers, source and unit provenance, keys, allocations and exact reconciliation. | `cost_components`, `component_allocations`, `inventory_ledger`, `parameter_provenance`, `provenance_ledger` and `dapane_adapter`. G2.3 qualifies the original values and G3.2 covers general inputs. |
| F04 | Preserve static and dynamic batches, repeats and rework, workloads, utilization, MDT and compute/storage/labour/consumable/equipment costing. | `workflow_*`, `static_batch*`, `dynamic_batch`, `trace_*`, `nextflow_trace`, `compute_cost`, `onprem_cost`, `cloud_billing` and `storage_usage`. G3.2 verifies scheduled, resource and accounting cases. |
| F05 | Preserve deterministic and advanced scenarios, batch/compute search, cost drivers, PSA, DSA, VOI, Monte Carlo and evidence provenance. | `scenario_*`, `advanced_scenario_modeling`, `batch_*_search`, `batch_uncertainty`, `monte_carlo_optimizer`, `cost_driver_*`, `dsa_analysis`, `psa_analysis` and `voi_analysis`. G3.2 verifies deterministic and seeded paths. |
| F06 | Preserve benchmarking, break-even, budget impact, cost effectiveness, alternate research and comparisons. | `benchmarking_analysis`, `break_even_analysis`, `budget_impact_analysis`, `cost_effectiveness_analysis`, `alternative_research` and `resource_comparison`. G3.2 includes independent synthetic expectations. |
| F07 | Preserve YAML/config fallbacks, workbook and model selection, extensible input schemas, templates, dependency validation and error/recovery contracts. | Installed config, data/configuration APIs and input templates. G3.2 verifies historical paths, version selection, defaults, malformed inputs and recovery behaviour. |
| F08 | Preserve prepared-table and analytical exports, comprehensive reports, static and interactive plots, and all optional media formats. | `comprehensive_reporting`, `visualization`, `advanced_visualization` and their source command entry points. G3.3 opens generated output and compares schema, data, content and format. |
| F09 | Preserve Flask dashboard, table browsing, charts, health, API routes, pagination and exports with their error behaviour. | `web.create_app`, `web_viz`, installed templates/static files and the local launcher. G3.3 exercises the complete registered route map with synthetic data and verifies the dashboard. |
| F10 | Preserve baseline and enhanced plugin discovery, metadata, hooks, built-in examples and error isolation. Preserve workbook history, comparison and restore. | `plugin_system`, `enhanced_plugin_system`, `plugins` and `excel_version_control`. G3.3 verifies installed load, use and recovery. |
| F11 | Preserve defensive access and configuration storage, audits, data quality, metrics, alerts, logging and performance profiles. | `security`, `data_quality_assurance`, `monitoring`, `logging_config`, `performance` and their integration points. G3.3–G3.4 test role/data boundaries, diagnostics and measured behaviour. |
| F12 | Preserve the shipped package metadata, discoverable Python/source entry points, config examples, provenance and support documentation. | G4.1 checks wheel and source package manifests, extras, package data and runnable compatibility commands. G3.5 verifies each inventory row using an installed entry point or a reproduced source-command contract. |

These families organize the detailed source rows. Each interface retains its
own source coordinate and candidate tests. The installed wheel matched all
109 legacy module paths, 1,129 declared signatures and 21 legacy route
registrations. The [verification record](verification.md#standalone-installed-artifacts)
links the installed tests and the private workbook replays.

## Source command audit

The packaged compatibility commands use Polars and the installed costing
and workbook APIs. The old source interfaces remain available through the
verified private bundle. The replacement commands use explicit inputs
and source coordinates. The [runtime evidence](verification.md#source-command-qualification)
records what was compared.

| Commands | Observed outcome |
| --- | --- |
| `create_ground_truth`, `replicate_calculations`, `validate_calculations` | Projected the cached reference, calculated each retained row and compared 1,014 values by its physical worksheet coordinate. |
| `replicate_detailed_table`, `advanced_validation`, `validate_calculation_engine` | Recalculated the detailed table and compared 17,897 populated cells. The independent legacy engine command also passed 2,894 selected numeric comparisons. |
| `replicate_bi_comp_stor_costs`, `validate_bi_comp_stor_costs` | Recalculated and compared 99 cells in the original server, equipment and storage blocks. |
| `replicate_consumable_costs`, `replicate_labour_costs`, `replicate_equipment_costs` | Synthetic source CSVs reproduced independent expected prices, quantities, hourly rates and depreciation. |
| `prepare_reference_tables`, `validate_simple_tables` | Prepared both historical reference layouts from an independent synthetic workbook and compared their populated numeric cells. |
| `validate_labour_usage`, `extract_excel_data_properly` | Compared the original labour sheet and exported its shared assay classification as stored. |
| `transfer_validate_tables`, `prepare_publication_tables` | Round-tripped all 35 sheets through native formats. A separate synthetic case verifies publication CSV and metadata. |
| `enhanced_reporting` | The source command and installed package use the same report generator. The packaged alias produces HTML, Markdown and JSON from a synthetic table. |
| `manage_data`, `run_scenario_analysis`, `run_advanced_scenario_analysis`, `validate_process_sheet` | Restored a versioned dataset to CSV and Parquet. Checked two scenario comparison reports against independent synthetic costs, and matched 39 original process worksheet cells. |
| `validate_data_consistency`, `visualize_costs` | Validated all 35 freshly generated workbook tables, retained the error report for a mismatched CSV, and generated three charts from the original workbook exports. |
| `analyze_scenarios` | Read 70 workbook DSA records and five archived PSA summaries. New scenarios use native exact requests. |
| `analyze_model_consistency`, `automated_standardization`, `model_transformation`, `phase3_data_enhancement` | Produced the five model audits and exports. Original values and physical row identity remain available in the source-backed exports. |
| `excel_data_extractor`, `extract_excel_comprehensive`, `validate_excel_comparison`, `validate_data_integrity` | Verified the exported and projected model values against the selected workbook revision. |
| `validate_standardization`, `validation_pipeline` | Reported historical empty fields and inconsistent rows. The synthetic model passed. Changing one booked cost failed validation and appended a second receipt. |
| `generate_templates`, `demonstrate_plugins`, `demonstrate_excel_version_control` | Generated the six templates and optional plugin source. The revision demo restored the first of two distinct same-second versions. |
| `establish_performance_baselines`, `compare_performance`, `profile_and_optimize` | Measured native contribution workloads, checked values during optimization, and exercised parallel and cache equivalence. Compare only receipts with matching runtime and workload identities. |

The command audit supplements the structural inventory and inherited tests.
All 37 legacy commands with Pandas imports are present in the source
distribution with native implementations. The Dapane source tree retains
all 74 registered command paths, including development and diagnostic
commands.
The [G3.5 audit](feature-audit.md) records 44 qualified command outcomes and
30 command rows that need further evidence. The
[source crosswalk](feature-audit-crosswalk.tsv) identifies each command and
its installed counterpart or follow-up.

## Planned deliverables

The [dashboard and operational controls](verification.md#dashboard-and-operational-controls)
close implementation gaps in role enforcement, request limits, the lab setup
wizard and the nine operational API routes. The evidence includes installed
diagnostic, benchmark and quality results and an interactive template download.

The [delivery changes](verification.md#delivery-and-remaining-acceptance)
add protected promotion, opt-in Codecov OIDC and a reproducible lab setup
tutorial. Read the outstanding acceptance items against the original audit.

The inventory retains overlapping source rows so a shared implementation
can refer back to every relevant commitment. The rows below state the
behaviour to test even where the provider describes the task as complete.
The [completed G3.5 audit](feature-audit.md) maps individual roadmap rows to
observed results. G3.4 addresses its implementation findings. G4.2 and G4.3
retain the outstanding installed and native qualification.

The [installed input and costing results](verification.md#input-and-costing-gaps)
close the preparation migration, API extraction, YAML profile and typed
model-configuration findings. That receipt also covers pinned price files,
stage-level compute reconciliation and native valuation of separate storage
stages.

The planned pricing, shared allocation, template and prediction paths have
synthetic installed evidence. Lab profiles apply exact multipliers to selected
labour-only quotes and override equipment useful lives with separate
provenance. The benchmark records measured resource use on a verified workload.
The dashboard container and provider templates are packaged independently of
the original workbook. The named quality and maintenance evidence is recorded
in the [qualification report](verification.md#planned-feature-implementations).

| Source rows | Required outcome and verification |
| --- | --- |
| R, phases 1–4 | Standardize package, column, abbreviation and model identities while preserving compatibility. Validate component contracts for compute and storage, scripted allocation, typed YAML models, engine integration and extractor/transformer pipeline migration by comparing legacy prepared outputs. [Refactoring plan, phases 1–4](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/GENOMICS_REFACTORING_PLAN.md#L71-L173) |
| R, phase 5 | Verify raw, processed and archived storage with retention. Price bioinformatics stages, including alignment, calling and annotation. Check batch efficiency, throughput and explicit volume discounts against workbook or independent scenario cases. [Refactoring plan, phase 5](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/GENOMICS_REFACTORING_PLAN.md#L174-L192) |
| R, phase 6 | Qualify extensible inputs, external pricing/database interfaces, more advanced allocation and reproducible learned cost prediction. Exercise the integration, cache and failure contracts through an authorised source or a deterministic test provider. [Refactoring plan, phase 6](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/GENOMICS_REFACTORING_PLAN.md#L193-L211) |
| R, phases 7–9 | Preserve architecture and API docs, install/usage, reference comparisons, integration/performance regression testing, deployment automation, CI coverage and monitoring. Verify commands and recorded runtime. [Refactoring plan, phases 7–9](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/GENOMICS_REFACTORING_PLAN.md#L212-L245) |
| S, phases 1–2 | Measure cross-model consistency. Validate shared taxonomy, schema, model-specific adaptation, automated standardization and output metrics against reproducible source tables. [Standardization plan, phases 1–2](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs/STANDARDIZATION_PLAN.md#L19-L203) |
| S, phases 3–4 and adoption proposals | Verify robust errors, data quality and performance, configuration-driven changes, templates, UI and lab plugins. Keep training, troubleshooting, configuration audit/restore and API contracts. Exercise synthetic data, local container packaging and cloud deployment templates with the tested environment identified. [Standardization plan, phases 3–4](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/docs/STANDARDIZATION_PLAN.md#L204-L370) |
| Q and E, integration and benchmarking | Verify cost-driver to DSA, PSA to VOI, consistency across analytical modules and end-to-end preparation/reporting. Add benchmark inputs, timing and memory thresholds, replayable load cases and meaningful coverage. [Robustness plan, tests and performance](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_PLAN.md#L9-L35) |
| Q and E, data quality and recovery | Verify diagnostic logging, known missing/invalid data, anomaly and consistency checks, integrity metrics and interrupted Monte Carlo recovery. Test stable failure codes and recoverable cases. [Robustness plan, errors and data quality](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_PLAN.md#L36-L55) |
| Q and E, security/configuration | Verify environment-based and versioned configuration, validation and update behaviour. Verify role-based access, sanitization, audit records and encrypted configuration against synthetic boundaries. [Robustness plan, configuration and security](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_PLAN.md#L56-L75) |
| Q and E, documentation and operations | Verify API/tutorial/troubleshooting coverage, research provenance documentation, health checks, usage and performance metrics, alerting and named quality targets. Preserve documentation and runbook continuity. [Robustness plan, documentation and monitoring](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_PLAN.md#L76-L196) |
| T, I and A | Reproduce the detailed table and translations for every supporting sheet, expand edge checks, document dependencies, provide source-authorised export commands, and transfer planned data management, workflow, reports, visualization, web and plugin tooling. Distinguish publication-ready source rights from executable CSV export. [Checklist](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/TODO.md) and [implementation plan](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/.qoder/quests/implementation_plan.md) |
| C and B | Exercise reported completion claims for export/reporting, scenarios, performance, plugins, workbook revision, views, reliability, security and monitoring against the installed successor. [Feature completion summary](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/IMPLEMENTATION_PLAN_COMPLETION_SUMMARY.md) and [robustness completion summary](https://github.com/edithatogo/microcosting_genomics/blob/fc8d4178bc3f5ce67cfc0547f7417272562c18a8/ROBUSTNESS_IMPROVEMENT_COMPLETION_SUMMARY.md) |
| GH163–GH165, GH170 | Preserve planned quality outcomes in Dapane's delivery: deterministic suites, bounded PR and scheduled checks, protected branches and owner recovery, security/context documentation, independent dependency updates and OIDC coverage readback. Record Dapane-specific equivalents and remaining native settings or provider dependencies with evidence in G4.3. [Test/CI](https://github.com/edithatogo/microcosting_genomics/issues/163), [security/maintenance](https://github.com/edithatogo/microcosting_genomics/issues/164), [parent](https://github.com/edithatogo/microcosting_genomics/issues/165), [dependency dashboard](https://github.com/edithatogo/microcosting_genomics/issues/170) |
