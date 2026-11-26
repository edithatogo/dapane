# Genomics microcosting for Dapane

This optional distribution preserves the `genomics_microcosting` Python APIs and
the `prepare-data` and `validate-engine` commands. The historical v15 adapter
also exposes exact workbook and pathway replay. Dapane's core remains
independently installable.

## Installation

Build or sync this project with CPython 3.15.1. The `visualization`, `reporting`
and `security` extras select the legacy optional capabilities. The `native`
extra installs the Dapane binding for valuation.

```sh
uv sync --locked --python 3.15.1 --all-extras --no-editable
.venv/bin/python --version
```

The distribution includes default configurations, templates, web resources and
the original workbook catalogue. Supply the workbook and any study data
separately through authorised access. Run the legacy commands from a consumer
directory with its own `config.yaml` or with the workbook at the configured
relative path.

## Legacy source commands

Run the scripts shipped in the source distribution with the installed
CPython environment. Pass the workbook, prepared tables and a local output
directory explicitly. `transfer_validate_tables.py --emit-test` can also
write a receipt-based check next to the transferred tables.
`phase3_data_enhancement.py` produces the model template exports, and
`validation_pipeline.py` records their validation and source digests.
Missing historical inputs remain blank and are reported by the quality
check. Use the exact workbook replay for reproducing past costing results.

The installed `prepare-data` command uses the reference sheet reader with
the data pipeline's CSV and Parquet loaders. Its configured and supporting
sheet filenames follow the legacy conventions. For a caller-managed JSON
API, add `genomics_microcosting.extractors.APIExtractor` to a
`DataPipeline`. Supply a read-only response function and the output Polars
schema. Its version `0.1` response has a `records` list with the declared
column names. JSON decimal values retain their precision. A value that
cannot fit a declared Decimal column fails validation.

## Original workbook replay

`dapane-genomics-inventory` takes the original workbook, its catalogue and a
new local ledger path. The packaged catalogue is available through
`importlib.resources.files("dapane_genomics").joinpath("data/workbook_catalog.json")`.
The workbook is verified against its frozen SHA-256 before reading.

`dapane-genomics-replay` accepts the private cell ledger and the path for a new
formula result file. It computes the original formulas, including the original
error codes, from exact decimal inputs. `dapane-genomics-pathways` takes the
same ledger and writes native AUD and USD pathway reports, including source
coordinates, stage amounts and recorded overlaps. Keep these outputs in
restricted storage and use a new file for each run.

The v15 formulas use four calculation families. A cell can return a value,
combine values with arithmetic, aggregate values with `SUM` or `AVERAGE`,
or calculate an annuity with `PMT`. These operations compose. For example,
`SUM(a,b,c) * rate` totals three inputs before applying a rate. Cell
references, literal values and the operation stay bound to the source
cell. Changing a price or quantity recalculates its dependants.

When authoring a workbook scenario with `build_workbook_copy`, a single
formula can cover disjoint target ranges on the same sheet. For example,
this synthetic change adds a fixed adjustment factor to selected charges.
The writer translates the original and replacement from the anchor and
checks the original formula at every target.

```json
{"sheet":"Costs","cell":"N2","original":"=F2*J2","replacement":"=F2*J2*$P$1","ranges":["N2:N5","N9:N10"]}
```

From the checkout or unpacked source distribution, compare two installed
genomics wheels on the authorised v15 workbook. Use separate Python 3.15.1
environments for the baseline and candidate.

```sh
/path/to/candidate/bin/python -I tools/verify_v15_scenarios.py \
  /restricted/v15.xlsm /restricted/v15-parity.json \
  --baseline-python /path/to/baseline/bin/python \
  --candidate-python /path/to/candidate/bin/python
```

The runner checks the original inputs, doubled quantity, a 25% price increase,
halved exchange rate and adjustment rates of zero and 13.75%. It compares each
exact result and Excel error by sheet ID and cell address. A difference exits
with the scenario and first affected address. The success receipt identifies
both evaluators and contains counts and digests. Cell ledgers and replay outputs
are processed in a local temporary directory.

## Reports and dashboard

`genomics-report --pathways <valued-pathways.json> --output-dir <new-output>`
writes exact totals by stage and cost component from the booked lines,
with a hash of the input receipt. The visualization extra adds a chart for
each pathway and currency. Amounts in the JSON retain exact fractions.

Use `genomics-report --data-dir <prepared-tables> --output-dir <new-output>`
for Markdown, HTML, JSON and the available charts. Use `--pdf` with the
reporting extra and its WeasyPrint system libraries. On this macOS host,
the tested command used `python -m dapane_genomics.reporting` with the
Homebrew GLib and Pango library paths.

`genomics_microcosting.web.create_app(data_dir)` uses the same directory
for the data views and health check. The base installation serves the
table and monitoring routes. The visualization extra adds chart rendering.
The comprehensive analytical reports use the archived PSA data separately.
Launch the installed interface with `genomics-web --data-dir <prepared-tables>`.
It listens on the local machine and uses the same model templates as the CLI.
The [analyst guide](deploy/analyst-guide.md) runs a synthetic case through the
source-linked planning report, model audit and workbook migration. It also
covers lab-system readback, troubleshooting and focused verification.

## Model templates, pricing and prediction

`genomics-model template <model> <output.json|output.csv|output.xlsx>`
generates the selected model's input structure. The Excel and CSV formats
include starting taxonomy rows and empty cost fields. Use
`genomics-model standardize <source.parquet> <new-output-directory>` to
normalize documented labels, preserve numeric fields and audit consistency
across models.

Add `--profile <profile.json|config.yaml>` to either model command to include
lab-specific categories. The YAML input can supply a project
`user_customizations` mapping with the same properties. The **Model
templates** page accepts the JSON profile and returns the selected template.

```json
{
  "lab_name": "Example lab",
  "custom_categories": {"Local costs": ["Shipping", "Taxes"]},
  "cost_adjustments": {
    "labor_multiplier": "1.2",
    "equipment_depreciation_years": 9
  }
}
```

`dapane_genomics.pricing.value_with_prices` accepts a caller-supplied
read-only price source that returns quotes in the
[Dapane contract](../../docs/contract-v0.1.md). It applies the exact
applicable volume tier and uses Dapane's valuation and shared-cost
allocation. Retain the resulting request and price-release digest to
reproduce a valuation without querying the source again.
For a retained release file, use `FilePriceRelease(path, expected_sha256)`
as the reader. Each read verifies the original bytes and native valuation
checks the quotation's effective dates.

Pass the profile and explicit `labour_quote_ids` to apply its multiplier to
labour-only quotes. The valuation receipt retains the source amount, source
identity, exact multiplier and profile digest. Quote prices and volumes still
pass through native Dapane valuation. Use
`dapane_genomics.pricing.calculate_lab_equipment_cost` for the separate on-prem
cost estimate with the lab's depreciation life. The original pricing record
remains available for comparison.

`dapane_genomics.prediction.fit_cost_model` fits an identifiable model to
named numeric predictors and a cost response. Its statistical estimates
are separate from exact valuation. Train and validate it on the relevant
data before adopting predictions for a study.

A project YAML file can define typed resource requirements under `models`.
`dapane_genomics.pricing.value_configured_model` selects one model, scales
its per-case quantities by the model's multiplier and case count, and
supplies the resulting exact quantities for native valuation. The caller
supplies the service date, source access and price reader. Keep the config
digest and resulting request to reproduce the calculation.

```yaml
models:
  synthetic_model:
    efficiency_multiplier: "0.8"
    resources:
      compute:
        quantity_per_case: "2.5"
        unit: hour
        quote_id: quoted-compute
```

`genomics_microcosting.compute_cost.calculate_compute_cost_breakdown`
retains each source-bound meter's exact cost and assigned share alongside
the existing total, allocation and bill reconciliation. Use separate
meter identities for independently observed stages.

## Dashboard deployment

Use the [dashboard deployment templates](deploy/README.md) to build a
non-root container and connect a read-only prepared data volume. The AWS
and Azure templates use private service boundaries and the same image.

## Performance measurements

`genomics-benchmark measure <new-baseline.json>` measures the source-backed
cost contribution calculation on synthetic rows with independently known
totals. It records median elapsed time and the largest sampled RSS change
for each workload size. Run it again on the same host, with matching software,
workload sizes and sample counts. Use
`genomics-benchmark compare <baseline.json> <candidate.json> <new-result.json>`
to report timing increases above 5%.

## Source and licence

The legacy implementation comes from
[`fc8d4178bc3f5ce67cfc0547f7417272562c18a8`](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8).
[CITATION.cff](CITATION.cff) preserves its software attribution and
[LICENSE](LICENSE) records Apache-2.0 terms for project-owned code.
See the [security policy](SECURITY.md) for configuration storage and deployment
boundaries.
See the [incorporation track](../../conductor/tracks/genomics_full_incorporation_20261124/verification.md)
for the workbook comparison, compatibility tests and remaining qualifications.
