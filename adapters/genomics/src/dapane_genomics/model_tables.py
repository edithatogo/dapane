# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Generate templates and validate model taxonomy with native Polars tables."""

from __future__ import annotations

import argparse
import csv
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

import polars as pl
import yaml
from openpyxl import Workbook

_MODELS = ("base", "panel", "wes_p", "wes_t", "wgs", "wgs_t")
_IDENTITY = ("Test", "Category", "Sub-Category")


def _configuration():
    return files("genomics_microcosting").joinpath("configuration")


def model_template(model: str) -> dict[str, Any]:
    """Load a named shipped model template, with its required columns."""
    if model not in _MODELS:
        raise ValueError(f"Unknown genomics model template: {model}")
    path = _configuration().joinpath("templates", f"{model}_template.json")
    return json.loads(path.read_bytes())


def _taxonomy() -> dict[str, Any]:
    path = _configuration().joinpath("standard_categories.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def standardize_models(source: pl.DataFrame) -> tuple[pl.DataFrame, dict[str, Any]]:
    """Normalize declared aliases and audit each model's observed taxonomy.

    The operation preserves row order, values and the original types of
    every non-taxonomy field. Unknown labels are reported for review.
    """
    if any(source.schema.get(column) != pl.String for column in _IDENTITY):
        raise ValueError(
            "Model tables require string Test, Category and Sub-Category columns"
        )
    if source.select(_IDENTITY).null_count().sum_horizontal().item():
        raise ValueError("Model, category and subcategory identifiers must be present")

    taxonomy = _taxonomy()
    aliases = taxonomy["standardization_mappings"]
    result = source.with_columns(
        pl.col("Category").replace(aliases["category_mappings"]),
        pl.col("Sub-Category").replace(aliases["subcategory_mappings"]),
    )
    allowed = taxonomy["standard_subcategories"]
    model_specific = taxonomy["model_specific_subcategories"]
    rules = taxonomy["validation_rules"]
    counts = []
    model_categories = []
    model_subcategories = []
    for (model,), rows in result.select(_IDENTITY).group_by(
        "Test", maintain_order=True
    ):
        observed: dict[str, set[str]] = {}
        for _, category, subcategory in rows.iter_rows():
            observed.setdefault(category, set()).add(subcategory)
        allowed_for_model = model_specific.get(model, {})
        unknown = {
            category: sorted(
                subcategories
                - set(allowed.get(category, ()))
                - set(allowed_for_model.get(category, ()))
            )
            for category, subcategories in observed.items()
        }
        counts.append(
            {
                "model": model,
                "categories": sorted(observed),
                "missing_categories": sorted(
                    set(rules["required_categories"]) - set(observed)
                ),
                "short_subcategories": [
                    category
                    for category, minimum in rules["minimum_subcategories"].items()
                    if len(observed.get(category, ())) < minimum
                ],
                "unknown_subcategories": {
                    key: values for key, values in unknown.items() if values
                },
            }
        )
        model_categories.append(set(observed))
        model_subcategories.append(
            {
                (category, subcategory)
                for category, subcategories in observed.items()
                for subcategory in subcategories
            }
        )
    return result, {
        "models": counts,
        "category_overlap": _overlap(model_categories),
        "subcategory_overlap": _overlap(model_subcategories),
    }


def _overlap(groups: list[set]) -> dict[str, int]:
    shared = set.intersection(*groups) if groups else set()
    seen = set.union(*groups) if groups else set()
    return {"common": len(shared), "total": len(seen)}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8") as output:
        json.dump(data, output, indent=2)
        output.write("\n")


def write_model_template(model: str, path: Path) -> None:
    """Write a JSON specification, CSV input, or editable Excel input template."""
    template = model_template(model)
    suffix = path.suffix.lower()
    if suffix == ".json":
        _write_json(path, template)
        return
    if suffix not in {".csv", ".xlsx"}:
        raise ValueError("Model templates support .json, .csv and .xlsx")

    columns = template["column_order"]
    context = _taxonomy()
    categories = context["standard_subcategories"]
    model_name = template.get("model_name", model)
    rows = [
        [
            dict(zip(_IDENTITY, (model_name, category, subcategory), strict=True)).get(
                column
            )
            for column in columns
        ]
        for category, subcategories in categories.items()
        for subcategory in subcategories
    ]
    if suffix == ".csv":
        with path.open("x", encoding="utf-8", newline="") as output:
            csv.writer(output).writerows([columns, *rows])
        return

    book = Workbook()
    sheet = book.active
    sheet.title = "Model input"
    sheet.freeze_panes = "A2"
    sheet.append(columns)
    for row in rows:
        sheet.append(row)
    try:
        with path.open("xb") as output:
            book.save(output)
    finally:
        book.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    template = commands.add_parser("template", help="Write a shipped model template")
    template.add_argument("model", choices=_MODELS)
    template.add_argument("output", type=Path)
    standardize = commands.add_parser(
        "standardize", help="Normalize labels and audit a model table"
    )
    standardize.add_argument("source", type=Path)
    standardize.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    if args.command == "template":
        write_model_template(args.model, args.output)
        return 0
    frame, audit = standardize_models(pl.read_parquet(args.source))
    args.output_directory.mkdir(mode=0o700)
    frame.write_parquet(args.output_directory / "standardized.parquet")
    _write_json(args.output_directory / "taxonomy-audit.json", audit)
    return 0
