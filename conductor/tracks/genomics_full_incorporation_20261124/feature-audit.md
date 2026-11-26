# G3.5 legacy feature audit

The 25 November 2026 audit matches the installed successor to the Dapane
adapter source at `8125597034a8f87a4d788212b011ab88ee7263a9` and the frozen
[legacy source](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8).
The [source crosswalk](feature-audit-crosswalk.tsv) assigns all 812 frozen plan
and issue rows, 18 additional design and example ranges, all 109 modules, 74
source commands, 21 legacy web routes, and the other frozen package and
documentation surfaces. Each row points to one or more named outcomes below.
Historical notes, dependency snapshots and scheduling estimates are context.
Coordinates for GitHub issues refer to the frozen issue bodies in the retained
inventory.

## Findings

| Disposition | Outcomes |
| --- | ---: |
| Passed for the recorded scope | 71 |
| Implementation needed | 16 |
| Further evidence needed | 23 |
| External changes or acceptance | 4 |

The installed wheel matched all 109 frozen modules, 1,129 public declarations,
21 registered legacy method/path pairs, two console targets and nine package
resources. All 19 configuration files are in the source distribution. The
wheel includes 17 of them. The other two are the project manifest and lock.
Of 74 retained source commands, 52 ship in the source distribution. The audit
established 44 command or supported console behaviors and recorded 30 with
additional command evidence to collect.

With networking sockets disabled, all 1,339 inherited and 173 packaged tests
passed. Their combined line coverage is 12,477 of 16,267 across the 122
installed Python files, or 76.70 percent. The private audit lists passing test
selectors and executable-line counts per file. It also links test execution
candidates to 521 of 677 declared callable bodies. Execution candidates help
select checks. The disposition of each behavior uses its observed assertion
or recorded functional result.

The implementation gaps include the planned API extractor and preparation
pipeline migration, model and lab YAML integration, user management and
rate limits in the web app, lab setup tools, deployment automation, tutorial
videos and the Codecov OIDC job. The installed route map also lacks the nine
proposed testing, performance, monitoring and quality API routes. The feature
matrix below keeps the individual gaps visible.

GitHub reported secret scanning and push protection enabled. It reported
`main` as unprotected with no active branch rules. The native Dependency
Dashboard handoff, publication rights and lab pilot acceptance need separate
evidence or action. The [official exact-main run](https://github.com/edithatogo/dapane/actions/runs/45596868242)
passed the network-disabled source scan and the image advisory review.

## Reproduction

Use the [clean install procedure](verification.md#standalone-installed-artifacts)
with CPython 3.15.1, the identical wheel and the installed Dapane binding.
Use the retained authorised inputs for historical comparisons. The two
per-test receipts were produced as follows, from the inherited harness and
from a separate consumer directory for the packaged suite. Set
`audit_python` to the installed environment's Python executable and
`audit_sdist` to the extracted source distribution directory.

```sh
MPLBACKEND=Agg COVERAGE_CORE=ctrace COVERAGE_FILE=inherited.coverage \
  "$audit_python" -IB -m pytest --disable-socket -q tests \
  -o junit_family=xunit1 --junitxml=inherited.xml \
  --cov=genomics_microcosting --cov=dapane_genomics --cov-context=test --cov-report=

MPLBACKEND=Agg COVERAGE_CORE=ctrace COVERAGE_FILE=packaged.coverage \
  "$audit_python" -IB -m pytest --disable-socket -q \
  -c "$audit_sdist/pyproject.toml" "$audit_sdist/tests" \
  -o junit_family=xunit1 --junitxml=packaged.xml \
  --cov=genomics_microcosting --cov=dapane_genomics --cov-context=test --cov-report=
```

In the matrix, `I:` selects an inherited test file and `P:` selects one
shipped in the source distribution. The private receipts record the passing
individual selectors. The previous [workbook replay](verification.md#exact-historical-formula-replay),
[source command checks](verification.md#source-command-qualification),
[web and report checks](verification.md#reports-web-and-compatibility-tools),
[planned implementations](verification.md#planned-feature-implementations),
[hosted qualification](verification.md#hosted-qualification) and
[retention evidence](verification.md#retirement-decision) identify their
actual inputs and result checks. The package workflow also exercised the
[installed dashboard image](https://github.com/edithatogo/dapane/actions/runs/45581128943).

The focused probes used three synthetic costs, 2, 4 and 6, overlapping two
categories, and a second column equal to twice the first. The installed
histogram matched the three values, the bar chart matched category totals
of 8 and 4, and the two-column correlation matrix contained four ones. The
HTML dashboard contained four Plotly traces. A separate base/low/high
fixture produced tornado widths of 8 and 20 percent with the assay labels
retained. The normal report command rendered a caller-supplied layout with
three rows and a mean of 4. The installed template command generated and
reopened a 20-row Panel CSV with the unit-cost field blank. The app's route
map provided the comparison for the proposed API endpoints.

Source review locators for missing capabilities are `prepare_data.main`,
the installed `extractors` classes, `config.yaml`, `model_tables.main`,
`ResearchFlask` route registration, the installed JavaScript and templates,
and `genomics-package.yml`. Native controls were checked with read-only
repository, branch, branch-rules and commit-status requests. The audit bundle
contains the scripts, JUnit and coverage receipts, per-declaration
comparison, native readbacks and the full feature dispositions.

| Receipt | SHA-256 |
| --- | --- |
| Frozen legacy inventory | `aa17ce9b28b137c67ad58741681fb56840f07cabbcfd792a76314eef81d3c11e` |
| Installed genomics wheel | `69db5a10006654084e508c5009a0e9e3b14b4ac45c94811c147d5c07579a5031` |
| Genomics source distribution | `cf0a613e5eb393847ad138ce68f83e13bd2fdc5c53ecb85049a95002824014b2` |
| Inherited test receipt | `c5ec60c5e999ad742b85156f3898378970a07f587e7e35240c391bfdbbcec5e0` |
| Packaged test receipt | `52add1fae6779e5db0494dfeeec92a7753b072f808988d0db32902f26220e450` |
| Combined installed coverage | `4ace71c1fb9f938bc108a3cd1e3a30aedc0adee49338cb531ec4679f88a12e19` |
| Source crosswalk | `5c62b384a2b705057d54522f98827c4d4357a77846bc3538ec8df7938dbc2794` |
| Restricted detailed audit receipt | `55e0329cd422c4a1d99273c211d01c9f7d452eb589ef22d36c66e5c07fc1664d` |

## Outcome matrix

**Passed** means the displayed scope has a reproduced result. **Code** means
the intended behavior is absent or lacks the required entry point.
**Evidence** means an interface or partial result is available and its
stated acceptance remains open. **External** records native configuration,
rights or user acceptance required outside the package. These are outcome
counts. Several source rows may point to a single outcome.


### Workbook, files and cost model

| Outcome ID | Status | Entry point | Reproducer and result |
| --- | --- | --- | --- |
| `package` | Passed | genomics-microcosting wheel and source distribution | Surfaces, P:test_package_payload.py. The wheel contains both namespaces and 17 configuration assets. The source archive retains all 19 configuration files, including the project manifest and lock. The two legacy CLI targets and nine package resources match. |
| `signatures` | Passed | genomics_microcosting public declarations | Surfaces. All 109 frozen modules and 1,129 declared signatures match the installed wheel. The per-declaration record identifies source and installed lines. |
| `workbook-selection` | Passed | SheetManager and configured loaders | I:test_workbook_selection.py, I:test_reader_options.py, I:test_loader_options.py. Explicit and configured source paths, workbook selection, reader modes and missing-file errors are exercised by the installed suites. |
| `workbook-headers` | Passed | SheetManager, excel_utils and DataManager | I:test_excel_utils.py, I:test_data_manager_multi_level_headers.py. Multi-row and merged headers retain named data columns and sheet locations. |
| `formula-evaluation` | Passed | CalculationEngine, FormulaParser and strategies | I:test_formula_parser.py, I:test_calculation_engine.py, I:test_strategy_edge_cases.py, I:test_formula_dependency_recalculation.py, P:test_v15_replay.py. Parsed arithmetic, lookup, conditional, aggregate and annuity cases reproduce expected values and errors. The dependency cases exercise recalculation and cache identity. |
| `historical-replay` | Passed | dapane-genomics-inventory, dapane-genomics-replay, dapane-genomics-pathways | Workbook replay. Installed replay covered all 35 sheets and 36,411 formula coordinates, including seven historical errors. All ten AUD and USD valuation pathways matched the booked comparator. |
| `workbook-dependencies` | Passed | Packaged workbook catalogue and WorkbookReplay | Workbook ledger. The catalogue and frozen ledger identify workbook regions, aliases, source coordinates, dependency edges and denominators. |
| `prepare-tables` | Passed | prepare-data and DataManager | Workbook exports, I:test_prepared_tables.py, I:test_csv_conversion.py. Installed preparation reproduced all 35 CSV and 35 Parquet exports. The preserved data and workbook hashes identify the comparator. |
| `native-pipeline` | Passed | DataPipeline, ExcelExtractor, CSVExtractor, ParquetExtractor and transformers | I:test_native_pipeline.py. The installed component pipeline reads tabular sources, transforms known values, and stops on invalid intermediate data. |
| `prepare-migration` | Code | prepare-data and DataPipeline | Source review. The supported CLI still uses its separate preparation flow. The planned migration of that CLI to the extractor/transformer/loader pipeline has no normal-entry integration. |
| `api-extraction` | Code | extractors and MultiSourceExtractor | Source review. The installed extractor module supports Excel, CSV and Parquet. The planned API source extractor is absent. |
| `detailed-parity` | Passed | validate-engine and legacy replication commands | Source command qualification, P:test_legacy_cost_commands.py. Normal entry points matched original detailed cells, independent unit/rate cases, and original process and server/equipment/storage blocks. |
| `table-comparison` | Passed | DataConsistencyValidator and validation_pipeline | P:test_legacy_cost_commands.py, I:test_data_consistency_validator.py. Checks detect a changed value and retain other sheets and the failed receipt. Original worksheet coordinates remain available. |
| `data-history` | Passed | data_management.DataManager and manage_data | P:test_legacy_cost_commands.py, I:test_data_management.py. Versioned data is restored and exported as CSV and Parquet. Tested provenance includes version fingerprints and lineage. |
| `data-governance` | Evidence | data_management.DataManager and provenance_ledger | I:test_data_management.py, I:test_provenance_ledger.py. Lineage and version operations have assertions. The full data-governance policy, permissions and ownership across operations need an end-to-end receipt. |
| `publication-export` | Passed | prepare_publication_tables and packaged metadata | P:test_legacy_cost_commands.py, I:test_polars_publication.py. A synthetic export reopened with the expected records and metadata. |
| `publication-rights` | External | Authorised workbook and generated publication tables | Retention decision. Restricted source tables are supplied independently. Actual publication of study data requires the source and citation permissions recorded by the track. |
| `base-cost-components` | Passed | CostComponent, formula strategies and component allocations | I:test_component_allocations.py, I:test_strategy_units.py, I:test_cost_properties.py. Installed component contracts preserve amounts, units and allocated residuals in tested cases. |
| `resource-ledgers` | Passed | inventory_ledger, provenance and execution reconciliation | I:test_inventory_ledger.py, I:test_execution_reconciliation.py, I:test_resource_accounting.py. Quantity, source identity and accounting reconcile against independent ledger cases. |
| `provenance` | Passed | Parameter provenance, price/quantity units and workbook lineage | I:test_parameter_provenance.py, I:test_parameter_units.py, I:test_t1_baseline_lineage.py, I:test_uncertainty_provenance.py. Tests check input identity, lineage and incompatible or missing inputs at the installed boundary. |
| `denominators` | Passed | cost_denominators and comparable cost reporting | I:test_reportable_cost.py, I:test_costing_guards.py. Known and incompatible denominator and sizing cases are checked at the supported reporting boundary. |
| `exact-valuation` | Passed | dapane_adapter and dapane.evaluate | I:test_dapane_adapter.py, I:test_dapane_stage_replay.py, Workbook replay. Installed calls reproduce exact totals and source attribution with the maintained JSON request. |
| `compute-breakdown` | Passed | compute_cost, onprem_cost and cloud_billing | P:test_compute_cost.py, I:test_compute_workbook_sources.py, I:test_cloud_billing.py, I:test_onprem_cost.py. Installed comparison covers measured compute, workbook source rates, and exact cloud and on-prem costing cases. |
| `compute-stage-coverage` | Evidence | compute_cost and native usage adapters | I:test_native_compute_cost.py, Source command qualification. Named compute and storage cells matched in the historical workbook. A row-level case explicitly asserting each planned stage breakdown is pending. |
| `storage` | Passed | storage_usage and trace workload | P:test_storage_usage.py, I:test_storage_usage.py, I:test_trace_workload.py. Tests distinguish recorded and retained storage, quantities, units and resource attribution. |
| `storage-stage-coverage` | Evidence | storage_usage, workbook and source-typed adapters | P:test_storage_usage.py, I:test_trace_capacity_reference.py. Storage and retention cases pass. One end-to-end receipt covering separate raw, processed and archive allocations would establish the complete planned breakdown. |
| `dynamic-batches` | Passed | static_batch, dynamic_batch and workflow scheduling | I:test_static_batch_cost.py, I:test_dynamic_batch_cost.py, I:test_workflow_schedule.py, I:test_workflow_rework.py. Installed cases verify realized batches, repeat and rework cost, and quantity effects. |
| `batch-search` | Passed | batch_policy_search and batch_compute_search | I:test_batch_policy_search.py, I:test_batch_compute_search.py, I:test_fifo_batch_search.py, I:test_batch_resource_uncertainty.py. Tests check feasible policies, exact ranking and explicit uncertainty under the supplied synthetic workload. |
| `workflow-costs` | Passed | workflow_cost, workflow_allocations and workflow_mdt | I:test_workflow_cost.py, I:test_workflow_allocations.py, I:test_workflow_mdt.py, I:test_workflow_baseline.py. Known workflow, workload, overhead and multidisciplinary labour allocations reproduce expected cost and keys. |
| `trace-input` | Passed | nextflow_trace, trace_registry and native_usage | I:test_nextflow_trace.py, I:test_nextflow_export_profile.py, I:test_trace_registry.py, I:test_native_usage.py. Frozen and synthetic traces are translated to typed usage with source and run identity. |
| `volume-scaling` | Passed | value_with_prices and batch cost | P:test_planned_pricing.py, I:test_variable_batch_runs.py. A known volume tier reduces exact booked compute cost from AUD 50.00 to AUD 43.75. Batch cases preserve quantities as volume changes. |
| `advanced-allocation` | Passed | value_with_prices and workflow_allocations | P:test_planned_pricing.py, I:test_workflow_allocations.py, I:test_sample_allocations.py. The installed fixture allocates the shared AUD 43.75 as AUD 14.58 and AUD 29.17 with zero residual. |
| `price-provider` | Passed | value_with_prices | P:test_planned_pricing.py. A deterministic read-only provider returns a pinned price release. Its resulting request can be replayed without another source read. |
| `price-provider-operation` | Evidence | value_with_prices and caller-supplied source | P:test_planned_pricing.py, Source review. The offline quote handoff is qualified. A named adapter's stale, unavailable and repeated-release behavior still needs proof. |
| `cost-prediction` | Passed | fit_cost_model and fitted model prediction | P:test_planned_pricing.py. A held-out fixture reproduces two independently specified outputs and rejects an underidentified fit. |
| `lab-adjustments` | Passed | value_with_prices and calculate_lab_equipment_cost | P:test_planned_pricing.py, P:test_lab_equipment.py. Exact labour and depreciation adjustments retain the original quote and profile evidence. |
| `profile-yaml` | Code | Structured lab profiles and config.yaml | Source review. The installed commands use a separate JSON lab profile. The planned user_customizations section in the main YAML config has no applied cost-adjustment path. |
| `standard-labels` | Passed | genomics-model standardize and HeaderNormalizer | P:test_model_tables.py, I:test_native_pipeline.py, Source command qualification. Installed normalization preserves original amounts, typed output and documented aliases. |
| `taxonomy` | Evidence | genomics-model standardize and installed taxonomy | P:test_model_tables.py. Tests report known, missing and unknown categories. The full authorized dataset still needs a comparison against the legacy greater-than-90-percent category and 85-percent subcategory targets. |
| `model-identity` | Passed | Template definitions and lab profile | P:test_model_tables.py, P:test_v15_replay.py. All six named template definitions are installed. Exact model selection, local labels and historical model identity exercise normal entry points. |
| `model-config` | Code | AnalysisConfig, config.yaml and CalculationEngine | Source review. Worksheet and analysis defaults are configurable. The proposed typed model registry for efficiency/resource inputs feeding the general engine is absent. |
| `schema-extension` | Passed | Lab profiles, template schema and ExtensionManager | P:test_model_tables.py, I:test_extensibility_framework.py. Custom categories and extension metadata can be accepted and invalid attributes are rejected in the supplied cases. |
| `templates` | Passed | genomics-model template and web template endpoint | P:test_model_tables.py. JSON resources and editable CSV and XLSX templates preserve empty unit-cost fields and lab labels. |
| `template-time` | Evidence | genomics-model and web templates | P:test_model_tables.py, Focused probes. The installed command generated a 20-row Panel CSV in about 0.007 seconds. The validation and user setup time targets still need a representative workflow receipt. |
| `config-schema` | Passed | AnalysisConfig and config_validation | P:test_config_validation.py, I:test_config_contract.py, I:test_analysis_config.py. Installed cases validate options, YAML and known analytical configuration errors. |
| `config-environment` | Passed | Environment-specific configuration loader | P:test_config_validation.py, I:test_config_validation.py. Installed cases distinguish environment overrides and reject invalid values. |
| `config-history` | Passed | ConfigurationVersionManager | P:test_config_validation.py, I:test_config_authenticity.py. Tests create and reload saved versions with digest validation and reject tampered configuration. |
| `config-update` | Passed | DynamicConfigurationUpdater | P:test_config_validation.py, I:test_config_validation.py. Refresh and change-handler behavior reproduce configuration changes in the test suite. |
| `config-rollback` | Evidence | ConfigurationVersionManager and genomics-model | I:test_config_authenticity.py, P:test_model_tables.py. Version readback and model validation are tested. An end-to-end lab configuration restore and revaluation needs a named acceptance case. |

### Analysis, data quality and security

| Outcome ID | Status | Entry point | Reproducer and result |
| --- | --- | --- | --- |
| `scenario-analysis` | Passed | scenario_modeling and advanced_scenario_modeling | I:test_scenario_modeling.py, P:test_legacy_cost_commands.py. Known changes have expected comparison totals. Packaged scenario commands retain the expected report fields. |
| `cost-drivers` | Passed | cost_driver_analysis and dsa_analysis | I:test_cost_driver_classification.py, P:test_cost_driver_dsa_integration.py. Driver tables retain expected ranking and scenario grids use the appropriate driver amounts. |
| `psa-voi` | Passed | psa_analysis and voi_analysis | P:test_psa_voi_integration.py, I:test_voi_analysis.py. The suites reproduce expected uncertainty and decision outputs from declared inputs and check compatibility across analysis steps. |
| `monte-carlo` | Passed | monte_carlo_optimizer and uncertainty adapters | I:test_monte_carlo_optimizer.py, I:test_uncertainty_provenance.py, P:test_checkpoint_restart.py. A seeded run has explicit checkpoint restoration and compares deterministic quality and uncertainty outcomes. |
| `analysis-tools` | Passed | benchmarking_analysis, break_even_analysis, budget_impact_analysis, cost_effectiveness_analysis, alternative_research and resource_comparison | I:test_benchmarking_analysis.py, I:test_break_even_analysis.py, I:test_budget_impact_analysis.py, I:test_cost_effectiveness_analysis.py, I:test_alternative_research.py, I:test_resource_comparison_e2e.py. Each analysis has an independent synthetic input and numeric or schema assertion in the inherited installed suite. |
| `end-to-end` | Passed | prepare-data, calculation and reports | I:test_complete_workflow.py, I:test_end_to_end_workflow.py, I:test_cross_module_consistency.py, Workbook exports. Installed suites check known calculated and exported values through the preparation and analysis workflows. |
| `full-analysis-chain` | Evidence | Installed analytical entry points | I:test_complete_workflow.py, P:test_cost_driver_dsa_integration.py, P:test_psa_voi_integration.py. Named handoffs and reports pass. A single row-level acceptance record for each analysis from raw input through its final report remains open. |
| `incomplete-data` | Passed | CalculationEngine, quality checks and missing-input policies | I:test_edge_cases.py, I:test_error_recovery_scenarios.py, I:test_native_raw_quality.py, P:test_legacy_cost_commands.py. Known gaps retain explicit missing values or errors and the affected rows are identified. |
| `error-runtime` | Passed | error_handling, input validation and exception middleware | I:test_error_recovery_scenarios.py, I:test_detailed_error_logging.py, I:test_input_validation.py. Installed tests retain diagnostics, errors and recovery outcomes for defined numerical and configuration failures. |
| `checkpoint-recovery` | Passed | monte_carlo_optimizer checkpoint files | P:test_checkpoint_restart.py. An interrupted checkpoint write retained the previous valid result. Replaying 2,000 draws matched the uninterrupted case within the 30-second target. |
| `data-quality` | Passed | DataQualityAssurance, ValidationChecker and validation_pipeline | P:test_data_quality_assurance.py, I:test_data_quality_assurance.py, P:test_legacy_cost_commands.py. Known anomalies, missing values and altered financial rows are detected. The valid synthetic model scored 100 percent. |
| `distribution-quality` | Evidence | DataQualityAssurance and standardized model outputs | P:test_data_quality_assurance.py, P:test_model_tables.py. Cross-table and anomaly cases pass. A named cross-model distribution comparison and the 99.5 percent operational quality target need a reproducible dataset receipt. |
| `logging` | Passed | logging_config and error middleware | I:test_logging_config.py, I:test_detailed_error_logging.py, I:test_logging_boundary.py. The installed suites verify structured logging, retained exception identity and bounded log output. |
| `request-tracing` | Evidence | MonitoringMiddleware and ResearchFlask | P:test_monitoring.py, I:test_web_table_boundaries.py. Local timing and request data paths exist. The audit lacks a single trace identity through an entire web-to-calculation-to-report request. |
| `input-sanitization` | Passed | InputSanitizer, workbook reader and formula parsing | I:test_security.py, I:test_input_validation.py, I:test_workbook_xml_security.py, P:test_security_hardening.py. Installed malformed-input cases preserve the stated data and calculation boundaries. |
| `role-controls` | Passed | AccessControlManager and credential-free role selection | I:test_access_control_fail_closed.py, I:test_security.py. Library tests reject unsupported privileges and authorize the declared synthetic roles. |
| `security-audit` | Passed | AuditTrail and SecureConfigStorage | I:test_security.py, I:test_config_authenticity.py. Recorded synthetic operations can be read back. Encrypted configuration and tamper rejection pass in the supported runtime. |
| `secured-web` | Code | genomics-web and ResearchFlask | Source review, Surfaces. The dashboard serves local data and monitoring routes. It lacks an integrated user login and per-request application of the tested role and audit policies. |
| `rate-limits` | Code | ResearchFlask REST routes | Source review, Surfaces. The installed route map has table, chart and monitoring APIs. No application-level rate-limiting policy is wired to those routes. |
| `lab-management-api` | Evidence | ResearchFlask data and template APIs | I:test_web_table_boundaries.py, P:test_model_tables.py. Installed APIs return bounded table data and generate templates. A lab-management consumer has no demonstrated versioned exchange contract. |

### Reports, visualization and web

| Outcome ID | Status | Entry point | Reproducer and result |
| --- | --- | --- | --- |
| `static-visuals` | Passed | visualization and chart-generating commands | P:test_legacy_cost_commands.py, Source command qualification. Installed normal commands produce PNG files for synthetic data and three cost charts for the authorized source copy. |
| `interactive-visuals` | Passed | advanced_visualization and DSAAnalyzer | Focused probes. The histogram and category totals matched independent synthetic values. The dashboard exported four Plotly traces. The correlation matrix contained four ones and the sorted tornado bars were 8 and 20 percent. |
| `advanced-chart-variants` | Evidence | advanced_visualization and generate_advanced_visualizations | Surfaces, Focused probes. Specific charts and the combined dashboard have a fixture. Standalone time trends, box plots and all report variants still need their own acceptance result. |
| `report-formats` | Passed | genomics-report and comprehensive_reporting | P:test_legacy_cost_commands.py, Report and web qualification. Installed output and independent readback cover Markdown, HTML, JSON and PDF. The archived scenario input produced six analytical reports. |
| `report-customization` | Passed | genomics-report --template | Focused probes. The installed command rendered a supplied layout and read back the expected three rows and a mean of four. |
| `dashboard` | Passed | genomics-web, create_app and the installed templates | Surfaces, I:test_web_table_boundaries.py, Report and web qualification. Twenty-one legacy method/path entries match. Browser and installed tests establish populated navigation, pagination, exports and explicit error responses. |
| `responsive-ui` | Evidence | genomics-web and installed CSS and JavaScript | Surfaces, Report and web qualification. All static assets are installed and desktop navigation was exercised. The claimed responsive experience needs a narrow-viewport interaction check. |
| `profile-upload` | Passed | Web model template form | P:test_model_tables.py, Planned implementations. An uploaded synthetic profile yields the requested template and expected local labels. Invalid profiles produce a bounded error. |
| `drag-and-drop` | Code | Web model template form | Source review. The installed form supports text and file submission. A drag-and-drop workflow is absent. |
| `setup-wizard` | Code | Genomics model and dashboard entry points | Source review. The dashboard has direct form-based actions. No guided lab setup workflow is installed. |
| `configuration-builder` | Code | Web template form and genomics-model | Source review. The form consumes a supplied profile. An interactive editor that builds and validates the profile is absent. |
| `plugins` | Passed | PluginManager, EnhancedPluginManager and ExtensionManager | I:test_plugin_system.py, I:test_extensibility_framework.py, I:test_native_analysis_plugins.py, Source command qualification. Installed tests and the packaged demo exercise discovery, metadata, execution and isolated errors. |
| `strategy-plugin` | Evidence | ExtensionManager and calculation strategy registration | I:test_extensibility_framework.py, I:test_native_analysis_plugins.py. Analysis extension execution is checked. A lab plugin that changes a calculation strategy and validation rule through the supported engine entry needs an installed receipt. |
| `workbook-history` | Passed | ExcelVersionControl and version demonstration | I:test_excel_version_control.py, P:test_legacy_cost_commands.py. Distinct same-second revisions are preserved, verified and restored. Comparison and existing metadata use the inherited tests. |
| `workbook-migration` | Evidence | ExcelVersionControl and installed reader | I:test_excel_version_control.py, Workbook replay. Recovery and version comparison pass. Migration across a separately versioned workbook layout needs a specific old-to-new comparator. |
| `health` | Passed | ResearchFlask /health and SystemHealthChecker | P:test_monitoring.py, P:test_optional_plotting.py, Hosted package. The selected directory is reflected in health results, including empty or unavailable inputs. The isolated container reaches the expected health endpoint. |
| `metrics` | Passed | PerformanceMetricsCollector and ResearchFlask /metrics | P:test_monitoring.py, I:test_memory_monitoring.py, I:test_processing_time.py. Tests check history, summaries, measured resource use and failed-operation timing. |
| `usage-analytics` | Passed | UsageAnalytics and the dashboard | P:test_monitoring.py, I:test_monitoring.py. Installed tests reproduce bounded counts across known actions and timezone offsets. |
| `alerts` | Passed | AlertManager and the dashboard | P:test_monitoring.py, I:test_monitoring.py. Stored alerts can be retrieved within the requested time window. Tests use local synthetic events. |
| `operational-monitoring` | Evidence | ResearchFlask health, metrics and alerts | Hosted package, P:test_monitoring.py. Installed endpoints and local alert records pass. A consumer-side monitoring and alert readback is outstanding. |
| `test-service-api` | Code | Pytest, CI run receipts | Source review, Surfaces. The test harness and results exist. The planned HTTP test-run and filtered test-result endpoints are absent. |
| `benchmark-service-api` | Code | genomics-benchmark and HTTP dashboard | Source review, Surfaces. The command measures numeric workloads. The planned HTTP benchmark request and filtered historical performance endpoints are absent. |
| `monitoring-api-contract` | Code | ResearchFlask /health and /metrics | Source review, Surfaces. Legacy endpoints exist. The proposed namespaced monitoring interface, metric filtering and per-sheet quality endpoint are absent. |
| `quality-service-api` | Code | DataQualityAssurance and validation_pipeline | Source review, Surfaces. Installed local validation exists. The planned HTTP validation request and date-filtered quality reports endpoints are absent. |

### Performance, deployment and maintenance

| Outcome ID | Status | Entry point | Reproducer and result |
| --- | --- | --- | --- |
| `benchmark` | Passed | genomics-benchmark and performance record | P:test_benchmark.py, P:test_load_testing.py, P:test_scalability.py, Planned implementations. The 1k, 5k and 10k workloads reproduce known totals and met the observed 5 percent comparison gate. The comparator detects a deliberate slower result. |
| `analysis-performance` | Evidence | performance and Monte Carlo benchmark entry points | I:test_scalability.py, I:test_monte_carlo_optimizer.py, I:test_memory_monitoring.py. The bounded native benchmark is measured. The same-host timing and resource targets for every analytical module and larger Monte Carlo analysis are not established. |
| `parallel-cache` | Passed | performance, memoized calculation and data pipeline | P:test_performance.py, I:test_validation_cache_identity.py, Source command qualification. Installed cases check correct results across parallel/cache paths and changed source identity. |
| `dashboard-container` | Passed | Genomics Dockerfile and the installed web app | Hosted package. The hosted package job verified the non-root process, read-only data mount, network isolation, health and table API. |
| `deployment-templates` | Passed | AWS CloudFormation and Azure Bicep templates | Planned implementations. AWS lint and Azure compilation succeeded. The outputs keep private ingress and health readiness. |
| `deployment-pipeline` | Code | Installed package workflow and deployment templates | Source review. The workflow builds and exercises the image. The roadmap's automatic deployment step is absent. |
| `api-docs` | Evidence | Installed README, docstrings and Dapane contract | Source review. Packaging, provider, model and report entry points have maintained guidance. Complete generated API and public-interface docstring coverage has not been demonstrated. |
| `guides` | Evidence | Installed README and usage documentation | Source review. Quickstarts and runnable commands exist. Comprehensive tutorials for every major analysis, troubleshooting and contribution examples still need an inventory and readback. |
| `training` | Code | Lab setup and user guides | Source review. The maintained written instructions exist. The promised lab setup video tutorials are absent. |
| `research-reporting` | Evidence | Published provenance records and reporting guidance | Source review, Retention decision. Software citation and source provenance are present. A complete current journal reporting cross-check requires the actual study deliverables. |
| `pilot-acceptance` | Roadmap | Genomics web and lab configuration workflow | Deferred on 26 November 2026. The [roadmap](../../roadmap.md#representative-genomics-lab-pilot) retains the original acceptance criteria. |
| `source-command-behavior` | Evidence | Source-distribution modules and repository-only wrappers | Surfaces, Source command qualification. All 74 paths are retained, 52 in the source distribution. Every path has a handoff in the command register. The named evidence gaps remain visible there. |
| `coverage-targets` | Evidence | Installed test suites and coverage report | Packaged and inherited coverage. The two suites cover 12,477 of 16,267 measured lines across 122 installed files, or 76.70 percent. The stated legacy thresholds still require their named scopes and additional coverage evidence. |
| `deterministic-ci` | Passed | GitHub Conductor, Runtime and Installed genomics package workflows | Hosted main, Hosted package. The installed and deterministic checks completed on their recorded source revisions. The package gate exercises clean install and network-disabled dashboard readback. |
| `extended-ci` | Evidence | Workflow policies, mutation and contract checks | Source review, Hosted main. Standard workflow gates ran. Applicability and scheduled receipts for the planned mutation, metamorphic and contract tests still need a recorded disposition. |
| `repo-context` | Passed | AGENTS.md, security policy and validation commands | Source review, Hosted main. The installed component has security and usage guidance. The root Conductor implementation and validation run supply the canonical context. |
| `branch-controls` | External | Dapane main branch settings | Native repository readback. GitHub reported an unprotected branch and no active rules. The planned deletion and force-push protections, required checks and owner recovery need native evidence. |
| `secret-push-controls` | Passed | Dapane repository security settings | Native repository readback. GitHub reports both secret scanning and push protection enabled. This is a readback of the configured native controls. |
| `dependency-updates` | External | GitHub dependency update configuration | Native repository readback, Source review. The repo has a Dependabot configuration. The frozen commitment also requires verifying the intended Renovate handoff and coverage before changing providers. |
| `coverage-oidc` | Code | GitHub Actions and Codecov | Native repository readback, Source review. The coverage suite can produce a local report. The checked workflows have no genomics Codecov OIDC upload to exercise. |
| `retention` | Passed | Frozen source bundle, Dapane package and cited workbook | Retention decision. The authorised bundle and original workbook restored and replayed. The old repository is a published source and software reference. |
| `roadmap-context` | Context | Frozen source notes | Inventory. Historical dates, staffing estimates, author comments, dependency snapshots and headings supply context for the linked outcome rows. |
