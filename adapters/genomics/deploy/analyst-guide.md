# Run a genomics costing case

Use CPython 3.15.1 and the installed tools described in the [package guide](../README.md#installation).
Run the examples from a fresh consumer directory. Keep operational data,
input workbooks and populated reports in authorised storage.

## Prepare and check model inputs

Follow the [lab setup walkthrough](lab-setup.md) to create a profile and generate
an input template. The following separate fixture supplies completed synthetic
component costs for one test of each model. Select component rows only when
preparing an actual table. Preserve the source coverage of blanks and subtotals
in a separate audit.

```sh
python - <<'PY'
import polars as pl

pl.DataFrame({
    "Test": ["Panel", "Panel", "WGS (T)"],
    "Category": ["Labour", "Equipment", "Labour"],
    "Sub-Category": ["Specimen Receipt", "Compute", "Specimen Receipt"],
    "cost": [8, 12, 26],
}).write_parquet("components.parquet")
PY
genomics-model standardize components.parquet normalized --cost-column cost
```

Open `normalized/taxonomy-audit.json`. The distribution section counts valid,
missing, nonfinite and negative costs for each model with quartiles and
statistical flags. Its denominator is every supplied row. The optional profile
extends the taxonomy. Review taxonomic exceptions and missing categories before
treating a table as complete. `normalized/standardized.parquet` preserves the
source cost column and row order.

## Run the linked analysis

Save the following synthetic case as `planning.json`. Values use the same
currency, price year and per-test basis. The cost draws, reference and yield
come from the case author. In a real case retain their source and selection
decision with the request.

```json
{
  "assay": "Panel",
  "cost_table": "normalized/standardized.parquet",
  "cost_column": "cost",
  "currency": "AUD",
  "price_year": 2026,
  "low_cost": 16,
  "high_cost": 25,
  "cost_draws": [20, 28],
  "volumes": [10, 20],
  "fixed_cost": 120,
  "price_per_test": 26,
  "reference_cost": 25,
  "reference_source": "Synthetic comparator",
  "diagnostic_yield": 0.25
}
```

```sh
genomics-report --planning planning.json --output-dir reports
```

In `reports/planning-analysis.json`, the two contributions sum to AUD 20.
The bounds change the unit cost by −20% and +25%. The two simulated costs have
a median of AUD 24 and a legacy cost-only approximation of AUD 2. Budget
costs at the declared volumes are AUD 200 and 400. The break-even threshold
is 20 tests, the cost is 80% of the reference, and the cost per diagnosis is
AUD 80. Use the two SHA-256s to identify the request and component table.

The planning report calculates summaries on the supplied draws and labels
the legacy cost-only VOI approximation. A decision-level VOI study needs
paired decision alternatives, appropriate outcomes and separate methods
validation. Historical workbook formula and pathway replay uses the original
ledger and its own exact outputs. [Workbook replay](../README.md#original-workbook-replay)

## Migrate a workbook layout

Write a mapping that names each source and target sheet and cell. This example
carries a numeric input from `Old!A1` to `New!C4`.

```json
[
  {"source": {"sheet": "Old", "cell": "A1"}, "target": {"sheet": "New", "cell": "C4"}}
]
```

```sh
genomics-model migrate previous.xlsx new-layout.xlsx mapping.json migrated.xlsx
```

Open `migrated.xlsx` and compare the values and neighbouring formulas with
the mapping and template. A migration accepts static input cells. Duplicate
targets, formula cells and an existing output path are errors.

## Read back from a lab management client

Use the operator-configured credentials and connection described in the
[dashboard instructions](README.md). Use TLS when the consumer connects over
a network. Read `GET /api/tables` for table names and `GET /api/table/<name>`
for the ordered column names and the first 50 records. The integration owner
declares column names, specimen identifier representation, currency and unit.
For exact decimals supply strings and parse them with a decimal type.

An authorised analyst can send a quality request to
`POST /api/microcosting/data-quality/validate`, then read matching receipts
through `GET /api/microcosting/monitoring/data-quality?sheet_name=<name>`.
Check `schema_version` is 1 and match the POST response's `X-Request-ID` with
the stored `request_id`. A request without credentials receives HTTP 401.

## Troubleshoot and contribute

If a planning request fails, verify the assay, the cost column, all component
prices, and that the declared bounds bracket the baseline. Review the
standardization audit before changing inputs. Use a fresh output directory for
each rerun. If a lab exchange fails with 403, use the documented role for the
operation. An authenticated read and an analysis write have different role
requirements. Record the `X-Request-ID` with the problem and keep credential
material out of logs.

After making a code change, build and install the wheel into a fresh locked
environment and use these focused checks from a consumer directory. The test
paths are relative to the unpacked source distribution.

```sh
python --version
python -m pytest /path/to/sdist/tests/test_planning_analysis.py \
  /path/to/sdist/tests/test_model_tables.py /path/to/sdist/tests/test_workbook_migration.py
```

From a source checkout with the installed wheel active, generate the Python
reference from the installed module declarations.

```sh
python adapters/genomics/tools/feature_inventory.py --installed-api /path/to/genomics-api.md
```

The generator reports the counts of modules, public declarations and
declarations with docstrings. Use `python -m pydoc genomics_microcosting`
for an individual runtime lookup. [Repository contribution checks](../../../CONTRIBUTING.md)
