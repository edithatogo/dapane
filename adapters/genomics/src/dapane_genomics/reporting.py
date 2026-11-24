# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Generate the legacy multi-format report directly from prepared Polars tables."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from functools import partial
from os.path import relpath
from pathlib import Path
from typing import Any

import jinja2
import polars as pl
import polars.selectors as cs

from genomics_microcosting.visualization import (
    VisualizationUnavailableError,
    load_prepared_data,
    plot_category_costs,
    plot_cost_distribution,
    plot_top_costs,
    plotting_backend,
)

_TITLE = "Microcosting Analysis Report"
_HEADERS = 10
_TEMPLATE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{{ title }}</title></head>
<body>
<h1>{{ title }}</h1>
<p>Generated on {{ generated_date }}</p>
<h2>Data Overview</h2>
<p>{{ summary.total_tables }} tables, {{ summary.total_rows }} records</p>
{% if figures %}
<h2>Visualizations</h2>
{% for figure in figures %}<img src="{{ figure }}" alt="Cost analysis chart" width="600">{% endfor %}
{% endif %}
<h2>Detailed Statistics</h2>
{% for name, table in tables.items() %}
<h3>{{ name }}</h3>
<p>{{ table.rows }} rows, {{ table.columns }} columns, {{ table.missing_values }} missing values</p>
{% for column, statistics in table.numeric_summary.items() %}
<h4>{{ column }}</h4>
<table><thead><tr><th>Statistic</th><th>Value</th></tr></thead><tbody>
{% for statistic, value in statistics.items() %}
<tr><th>{{ statistic }}</th><td>{{ value if value is not none else "" }}</td></tr>
{% endfor %}
</tbody></table>
{% endfor %}
{% if table.category_counts %}
<h4>Categorical Columns</h4>
<ul>{% for column, count in table.category_counts.items() %}
<li>{{ column }}: {{ count }} unique values</li>
{% endfor %}</ul>
{% endif %}
{% endfor %}
</body>
</html>
"""


def _numeric_columns(frame: pl.DataFrame) -> list[str]:
    return frame.select(cs.numeric()).columns


def _table_summary(frame: pl.DataFrame) -> dict[str, Any]:
    clean = frame.with_columns(cs.float().fill_nan(None))
    numeric = _numeric_columns(clean)
    categories = clean.select(cs.string() | cs.categorical() | cs.enum()).columns
    preview = numeric[:_HEADERS]
    numeric_summary = {}
    if preview:
        stats = clean.select(preview).describe(interpolation="linear")
        for column in preview:
            numeric_summary[column] = dict(
                zip(stats["statistic"], stats[column], strict=True)
            )
    return {
        "rows": frame.height,
        "columns": frame.width,
        "numeric_columns": len(numeric),
        "categorical_columns": len(categories),
        "missing_values": sum(clean.null_count().row(0)) if clean.width else 0,
        "column_names": frame.columns,
        "numeric_summary": numeric_summary,
        "category_counts": {
            column: clean[column].drop_nulls().n_unique()
            for column in categories[:_HEADERS]
        },
    }


def _document(data: dict[str, pl.DataFrame]) -> dict[str, Any]:
    return {
        "title": _TITLE,
        "generated_date": datetime.now(UTC).isoformat(),
        "summary": {
            "total_tables": len(data),
            "total_rows": sum(table.height for table in data.values()),
        },
        "tables": {name: _table_summary(table) for name, table in data.items()},
    }


def _images(directory: str | Path | None, output: Path) -> list[str]:
    if directory is None:
        return []
    return [
        relpath(path.resolve(), output.resolve().parent)
        for path in sorted(Path(directory).glob("*.png"))
    ]


def generate_markdown_report(
    data_dict: dict[str, pl.DataFrame],
    output_file: str | Path,
    figures_dir: str | Path | None = None,
) -> None:
    """Write source-derived summaries and relative chart links."""
    output = Path(output_file)
    record = _document(data_dict)
    summary = record["summary"]
    lines = [
        f"# {_TITLE}",
        "",
        "## Data Overview",
        "",
        f"{summary['total_tables']} tables, {summary['total_rows']} records.",
        "",
    ]
    for figure in _images(figures_dir, output):
        lines.extend([f"![Cost analysis chart]({figure})", ""])
    for name, table in record["tables"].items():
        lines.extend(
            [f"## {name}", "", f"{table['rows']} rows, {table['columns']} columns.", ""]
        )
        for column, stats in table["numeric_summary"].items():
            lines.append(f"- **{column}**")
            lines.extend(
                f"  - {key}: {value}"
                for key, value in stats.items()
                if value is not None
            )
        lines.extend(
            f"- **{column}**: {count} unique values"
            for column, count in table["category_counts"].items()
        )
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def generate_html_report(
    data_dict: dict[str, pl.DataFrame],
    output_file: str | Path,
    figures_dir: str | Path | None = None,
    template_file: str | Path | None = None,
) -> None:
    """Render a default or caller-supplied template with safe text escaping."""
    output = Path(output_file)
    template_path = Path(template_file) if template_file is not None else None
    environment = jinja2.Environment(autoescape=True)
    source = template_path.read_text(encoding="utf-8") if template_path else _TEMPLATE
    text = environment.from_string(source).render(
        **_document(data_dict),
        data_dict=data_dict,
        figures=_images(figures_dir, output),
    )
    output.write_text(text, encoding="utf-8")


def generate_pdf_report(html_file: str | Path, output_file: str | Path) -> bool:
    """Render a report PDF with the optional WeasyPrint backend."""
    try:
        from weasyprint import HTML
    except ImportError, OSError:
        return False
    HTML(filename=html_file).write_pdf(output_file)
    return True


def generate_json_report(
    data_dict: dict[str, pl.DataFrame], output_file: str | Path
) -> None:
    """Persist report statistics without requiring a Pandas conversion."""
    Path(output_file).write_text(
        json.dumps(_document(data_dict), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def create_cost_analysis_plots(
    data_dict: dict[str, pl.DataFrame], output_dir: str | Path
) -> list[str]:
    """Reuse the native cost-chart generators and retain their figures."""
    frame = data_dict.get("detailed_table")
    if frame is None:
        return []
    numeric = _numeric_columns(frame)
    if not numeric:
        return []
    plotter = plotting_backend()
    cost = next((col for col in numeric if "cost" in col.lower()), numeric[0])
    category = next((col for col in frame.columns if "category" in col.lower()), None)
    figures = [
        ("cost_distribution.png", partial(plot_cost_distribution, frame, cost)),
        ("top_costs.png", partial(plot_top_costs, frame, cost, top_n=20)),
    ]
    if category is not None:
        figures.append(
            ("category_costs.png", partial(plot_category_costs, frame, category, cost))
        )
    for name, draw in figures:
        figure = draw()
        try:
            figure.savefig(Path(output_dir) / name, bbox_inches="tight", dpi=150)
        finally:
            plotter.close(figure)
    return [name for name, _ in figures]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/prepared"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--template", type=Path)
    parser.add_argument("--pdf", action="store_true", help="Require PDF rendering")
    args = parser.parse_args()
    data = load_prepared_data(args.data_dir)
    if not data:
        parser.error("No prepared tables were found")
    output = args.output_dir
    images = output / "enhanced_visualizations"
    images.mkdir(parents=True, exist_ok=True)
    try:
        create_cost_analysis_plots(data, images)
    except VisualizationUnavailableError:
        pass
    html = output / "enhanced_microcosting_report.html"
    generate_markdown_report(data, output / "enhanced_microcosting_report.md", images)
    generate_html_report(data, html, images, args.template)
    generate_json_report(data, output / "enhanced_microcosting_report.json")
    if args.pdf and not generate_pdf_report(
        html, output / "enhanced_microcosting_report.pdf"
    ):
        parser.error(
            "Install the reporting extra and WeasyPrint system libraries to generate PDF"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
