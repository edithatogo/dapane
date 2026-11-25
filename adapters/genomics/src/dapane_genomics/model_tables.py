# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Generate templates and validate model taxonomy with native Polars tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Mapping
from fractions import Fraction
from importlib.resources import files
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, cast

import polars as pl
import yaml
from openpyxl import Workbook
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

MODELS = ("base", "panel", "wes_p", "wes_t", "wgs", "wgs_t")
FORMATS = ("json", "csv", "xlsx")
_IDENTITY = ("Test", "Category", "Sub-Category")


def _label(value: str) -> str:
    normalized = value.strip()
    if (
        not normalized
        or len(normalized) > 100
        or not value.isprintable()
        or normalized.startswith(("=", "+", "-", "@"))
    ):
        raise ValueError("Labels must be plain text between 1 and 100 characters")
    return normalized


class LabCostAdjustments(BaseModel):
    """An exact labour-rate multiplier and optional equipment useful life."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    labor_multiplier: str = Field(default="1", max_length=64)
    equipment_depreciation_years: int | None = Field(default=None, gt=0)

    @field_validator("labor_multiplier")
    @classmethod
    def check_multiplier(cls, value: str) -> str:
        """Require a positive exact amount represented as text."""
        try:
            multiplier = Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(
                "Labour multiplier must be a positive exact number"
            ) from exc
        if multiplier <= 0:
            raise ValueError("Labour multiplier must be a positive exact number")
        return value


class LabProfile(BaseModel):
    """Optional lab name and local extensions to the standard input taxonomy."""

    model_config = ConfigDict(extra="forbid", strict=True)

    lab_name: str = Field(default="", max_length=100)
    custom_categories: dict[str, list[str]] = Field(default_factory=dict, max_length=25)
    cost_adjustments: LabCostAdjustments = Field(default_factory=LabCostAdjustments)

    @field_validator("lab_name")
    @classmethod
    def check_lab_name(cls, value: str) -> str:
        """Keep names safe to write in a plain-text input template."""
        return _label(value) if value else ""

    @field_validator("custom_categories")
    @classmethod
    def check_categories(cls, value: dict[str, list[str]]) -> dict[str, list[str]]:
        """Validate each category and its labels before export."""
        labels: dict[str, list[str]] = {}
        for name, subcategories in value.items():
            category = _label(name)
            if category in labels or not 1 <= len(subcategories) <= 25:
                raise ValueError(
                    "Each distinct category requires 1 to 25 subcategories"
                )
            entries = [_label(entry) for entry in subcategories]
            if len(set(entries)) != len(entries):
                raise ValueError("A category cannot contain duplicate subcategories")
            labels[category] = entries
        return labels


class _ExactYaml(yaml.SafeLoader):
    """Keep decimal scalars in their original exact representation."""


_ExactYaml.add_constructor("tag:yaml.org,2002:float", _ExactYaml.construct_scalar)


class _NamedCategory(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    subcategories: list[str]


_NAMED_CATEGORIES = TypeAdapter(list[_NamedCategory])


def load_model_yaml(payload: bytes) -> dict[str, Any]:
    """Parse project model configuration with unrounded YAML decimal scalars."""
    loader = _ExactYaml(payload)
    try:
        document: object = loader.get_single_data()
    finally:
        loader.dispose()
    if not isinstance(document, dict):
        raise ValueError("Genomics configuration must be a mapping")
    return cast("dict[str, Any]", document)


def load_lab_profile(path: Path) -> LabProfile:
    """Read the existing JSON profile or the project's YAML customization block."""
    payload = path.read_bytes()
    if path.suffix.lower() not in {".yaml", ".yml"}:
        return LabProfile.model_validate_json(payload)
    document = load_model_yaml(payload)
    selected: object = document.get("user_customizations", document)
    if not isinstance(selected, dict):
        return LabProfile.model_validate(selected)
    profile = cast("dict[str, Any]", selected)
    custom = profile.get("custom_categories")
    if not isinstance(custom, list):
        return LabProfile.model_validate(profile)
    entries = _NAMED_CATEGORIES.validate_python(custom)
    categories = {entry.name: entry.subcategories for entry in entries}
    if len(categories) != len(entries):
        raise ValueError("Lab configuration repeats a custom category")
    return LabProfile.model_validate({**profile, "custom_categories": categories})


def _configuration():
    return files("genomics_microcosting").joinpath("configuration")


def model_template(model: str) -> dict[str, Any]:
    """Load a named shipped model template, with its required columns."""
    if model not in MODELS:
        raise ValueError(f"Unknown genomics model template: {model}")
    path = _configuration().joinpath("templates", f"{model}_template.json")
    return json.loads(path.read_bytes())


def _taxonomy() -> dict[str, Any]:
    path = _configuration().joinpath("standard_categories.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _merge_taxonomy(
    standard: Mapping[str, list[str]],
    profile: LabProfile | None,
) -> dict[str, list[str]]:
    categories = dict(standard)
    if profile is not None:
        for category, additions in profile.custom_categories.items():
            categories[category] = list(
                dict.fromkeys([*categories.get(category, ()), *additions])
            )
    return categories


def standardize_models(
    source: pl.DataFrame,
    profile: LabProfile | None = None,
) -> tuple[pl.DataFrame, dict[str, Any]]:
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
    allowed = _merge_taxonomy(taxonomy["standard_subcategories"], profile)
    model_specific = taxonomy["model_specific_subcategories"]
    rules = taxonomy["validation_rules"]
    counts: list[dict[str, Any]] = []
    model_categories: list[set[str]] = []
    model_subcategories: list[set[tuple[str, str]]] = []
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


def _overlap[Value](groups: list[set[Value]]) -> dict[str, int]:
    if not groups:
        return {"common": 0, "total": 0}
    first, *others = groups
    return {
        "common": len(first.intersection(*others)),
        "total": len(first.union(*others)),
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8") as output:
        json.dump(data, output, indent=2)
        output.write("\n")


def model_template_bytes(
    model: str,
    format_name: str,
    profile: LabProfile | None = None,
) -> bytes:
    """Return the selected model's JSON, CSV, or editable Excel template."""
    if format_name not in FORMATS:
        raise ValueError("Model templates support JSON, CSV and Excel")
    template = model_template(model)
    if format_name == "json":
        if profile is not None:
            template["lab_profile"] = profile.model_dump()
        return (json.dumps(template, indent=2) + "\n").encode()

    columns = template["column_order"]
    categories = _merge_taxonomy(_taxonomy()["standard_subcategories"], profile)
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
    if format_name == "csv":
        with StringIO(newline="") as output:
            csv.writer(output).writerows([columns, *rows])
            return output.getvalue().encode()

    book = Workbook()
    try:
        sheet = book.active
        if sheet is None:
            raise RuntimeError("The default workbook sheet is unavailable")
        sheet.title = "Model input"
        sheet.freeze_panes = "A2"
        sheet.append(columns)
        for row in rows:
            sheet.append(row)
        with BytesIO() as output:
            book.save(output)
            return output.getvalue()
    finally:
        book.close()


def write_model_template(
    model: str,
    path: Path,
    profile: LabProfile | None = None,
) -> None:
    """Write a model template to a new file."""
    template = model_template_bytes(
        model, path.suffix.lower().removeprefix("."), profile
    )
    with path.open("xb") as output:
        output.write(template)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    template = commands.add_parser("template", help="Write a shipped model template")
    template.add_argument("model", choices=MODELS)
    template.add_argument("output", type=Path)
    template.add_argument(
        "--profile", type=Path, help="Optional lab profile JSON or YAML"
    )
    standardize = commands.add_parser(
        "standardize", help="Normalize labels and audit a model table"
    )
    standardize.add_argument("source", type=Path)
    standardize.add_argument("output_directory", type=Path)
    standardize.add_argument(
        "--profile", type=Path, help="Optional lab profile JSON or YAML"
    )
    args = parser.parse_args()
    profile = load_lab_profile(args.profile) if args.profile else None
    if args.command == "template":
        write_model_template(args.model, args.output, profile)
        return 0
    frame, audit = standardize_models(pl.read_parquet(args.source), profile)
    args.output_directory.mkdir(mode=0o700)
    frame.write_parquet(args.output_directory / "standardized.parquet")
    _write_json(args.output_directory / "taxonomy-audit.json", audit)
    return 0
