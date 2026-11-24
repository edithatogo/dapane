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

## Reports and dashboard

Use `genomics-report --data-dir <prepared-tables> --output-dir <new-output>`
for Markdown, HTML, JSON and the available charts. Use `--pdf` with the
reporting extra and its WeasyPrint system libraries. On this macOS host,
the tested command used `python -m dapane_genomics.reporting` with the
Homebrew GLib and Pango library paths.

`genomics_microcosting.web.create_app(data_dir)` uses the same directory
for the data views and health check. The base installation serves the
table and monitoring routes. The visualization extra adds chart rendering.
The comprehensive analytical reports use the archived PSA data separately.

## Source and licence

The legacy implementation comes from
[`fc8d4178bc3f5ce67cfc0547f7417272562c18a8`](https://github.com/edithatogo/microcosting_genomics/tree/fc8d4178bc3f5ce67cfc0547f7417272562c18a8).
[CITATION.cff](CITATION.cff) preserves its software attribution and
[LICENSE](LICENSE) records Apache-2.0 terms for project-owned code.
See the [incorporation track](../../conductor/tracks/genomics_full_incorporation_20261124/verification.md)
for the workbook comparison, compatibility tests and remaining qualifications.
