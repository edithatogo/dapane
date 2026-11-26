# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Read, standardize and validate the model tables used by legacy commands."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl

from genomics_microcosting.config import load_config
from genomics_microcosting.sheet_manager import SheetManager

from .legacy_workbooks import DETAILED_SHEET, csv_ready, evaluate_sheet, same_value
from .model_tables import LabProfile, model_template, standardize_models

MODEL_KEYS = {
    "Panel": "panel",
    "WES (P)": "wes_p",
    "WES (T)": "wes_t",
    "WGS (P)": "wgs",
    "WGS (T)": "wgs_t",
}
LABOUR_SHEET = "Labour - Usage - VCGS"
_REQUIRED_COSTS = ("Unit Cost (AUD $/unit)", "Units", "Total Cost (AUD)")
_TEMPLATE_SOURCES = {
    "Item": ("Item", "Step"),
    "Unit Cost (AUD $/unit)": (
        "Unit Cost (AUD $/unit)",
        "Estimates Price (AUD $/unit) Estimate",
        "Price (AUD $/unit) Estimate",
    ),
    "Units": ("Units", "Estimates Quantity of Use per Test Estimate", "Estimate"),
    "Total Cost (AUD)": (
        "Total Cost (AUD)",
        "Estimates Unit Cost (AUD $/unit) Estimate",
    ),
}


def _default_workbook() -> Path:
    config = load_config()
    return Path(config["workbooks"][config["default_workbook"]]["path"])


def read_model_source(
    path: Path, sheet: str = DETAILED_SHEET, *, calculate: bool = False
) -> pl.DataFrame:
    """Retain source row numbers and the workbook's original mixed values."""
    if path.suffix.lower() == ".parquet":
        frame = pl.read_parquet(path)
        return (
            frame
            if "Source_Row" in frame.columns
            else frame.with_row_index("Source_Row", offset=5)
        )
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if {"Test", "Category", "Sub-Category"}.issubset(
                    value.strip() for value in row
                ):
                    start = reader.line_num
                    break
            else:
                raise ValueError("No identifiable detailed-table header in the CSV")
        frame = pl.read_csv(path, skip_rows=start - 1, infer_schema_length=None)
        return (
            frame
            if "Source_Row" in frame.columns
            else frame.with_row_index("Source_Row", offset=start + 1)
        )

    config = None
    if sheet == LABOUR_SHEET:
        config = {sheet: {"header_rows": 3, "data_starts_at": 4}}
    if calculate and config is None:
        _, frame, first = evaluate_sheet(path, sheet)
    else:
        workbook = SheetManager(path, sheet_configs=config)
        try:
            frame = workbook.get_ground_truth(sheet)
            first = workbook.sheet_configs[sheet].get("data_starts_at", 2)
        finally:
            workbook.close()
    if sheet == LABOUR_SHEET:
        frame = frame.with_columns(pl.lit("Labour").alias("Category")).rename(
            {"Stage": "Sub-Category"}
        )
    return csv_ready(frame).with_row_index("Source_Row", offset=first)


def model_rows(frame: pl.DataFrame) -> pl.DataFrame:
    """Follow merged test labels and retain every recognized model component row."""
    names = "Test", "Category", "Sub-Category"
    prepared = frame.with_columns(
        pl.col(name).cast(pl.String).str.strip_chars().replace("", None)
        for name in names
    ).with_columns(
        pl.col("Test").forward_fill().replace({"WGS": "WGS (P)"}),
    )
    labelled = (
        prepared.with_columns(
            pl.col("Category")
            .is_not_null()
            .cum_sum()
            .over("Test")
            .alias("_category_group")
        )
        .with_columns(
            pl.col("Category").forward_fill().over("Test"),
            pl.col("Sub-Category").forward_fill().over("Test", "_category_group"),
        )
        .drop("_category_group")
    )
    item = next(
        (name for name in _TEMPLATE_SOURCES["Item"] if name in frame.columns), None
    )
    occupied = prepared["Category"].is_not_null()
    if item is not None:
        occupied |= prepared[item].is_not_null()
    result = labelled.filter(pl.col("Test").is_in(list(MODEL_KEYS)) & occupied)
    if result.is_empty():
        raise ValueError("No identified model component rows in the source")
    return result


def apply_template(frame: pl.DataFrame, key: str) -> pl.DataFrame:
    """Map known source columns and keep absent prices and quantities null."""
    columns = model_template(key)["column_order"]
    expressions = []
    for name in columns:
        variants = _TEMPLATE_SOURCES.get(name, (name,))
        source = next(
            (candidate for candidate in variants if candidate in frame.columns), None
        )
        dtype = pl.Float64 if name in _REQUIRED_COSTS else pl.String
        column = (
            pl.col(source).cast(dtype, strict=False) if source else pl.lit(None, dtype)
        )
        expressions.append(column.alias(name))
    result = frame.select("Source_Row", *expressions)
    if not any(name in frame.columns for name in _TEMPLATE_SOURCES["Total Cost (AUD)"]):
        return result.with_columns(
            (pl.col("Unit Cost (AUD $/unit)") * pl.col("Units")).alias(
                "Total Cost (AUD)"
            )
        )
    return result


def _model_filename(name: str, suffix: str) -> str:
    return f"{name.replace(' ', '_').replace('(', '').replace(')', '')}_{suffix}.csv"


def _normalise(
    source: pl.DataFrame, profile: LabProfile | None = None
) -> tuple[pl.DataFrame, dict]:
    """Normalize known labels and keep unclassified rows visible in the receipt."""
    labels = ("Test", "Category", "Sub-Category")
    classified = source.drop_nulls(labels)
    mapped, audit = standardize_models(classified, profile)
    revised = (
        source.join(
            mapped.select("Source_Row", "Category", "Sub-Category"),
            on="Source_Row",
            how="left",
            validate="1:1",
            suffix="_standard",
            maintain_order="left",
        )
        .with_columns(
            pl.coalesce(f"{column}_standard", column).alias(column)
            for column in labels[1:]
        )
        .drop("Category_standard", "Sub-Category_standard")
    )
    audit["unclassified_rows"] = source.height - classified.height
    return revised, audit


def write_models(
    source: pl.DataFrame,
    output: Path,
    suffix: str,
    *,
    template: bool = False,
    profile: LabProfile | None = None,
) -> int:
    """Write per-model tables and an audit using the installed taxonomy."""
    if template or suffix == "standardized":
        source, audit = _normalise(source, profile)
    else:
        audit = {"models": []}
    output.mkdir(parents=True, exist_ok=True)
    exports = []
    for (name,), frame in source.group_by("Test", maintain_order=True):
        if template:
            frame = apply_template(frame, MODEL_KEYS[name])
        path = output / _model_filename(name, suffix)
        frame.write_csv(path)
        exports.append(
            {
                "model": name,
                "rows": frame.height,
                "sha256": sha256(path.read_bytes()).hexdigest(),
            }
        )
    (output / "model-audit.json").write_text(
        json.dumps({**audit, "exports": exports}, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(exports)


def extract_main(
    default_dir: str,
    suffix: str,
    *,
    sheet: str = DETAILED_SHEET,
    calculate: bool = False,
) -> int:
    """Run workbook extraction with the requested cache or formula path."""
    parser = argparse.ArgumentParser(
        description="Export model tables from a selected workbook"
    )
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=sheet)
    parser.add_argument("--output-dir", type=Path, default=Path(default_dir))
    args = parser.parse_args()
    source = read_model_source(
        args.workbook or _default_workbook(), args.sheet, calculate=calculate
    )
    if args.sheet == LABOUR_SHEET:
        # WES (S) is the source's shared labour-use label. Preserve it as written.
        source = source.with_columns(pl.col("Test").cast(pl.String).forward_fill())
        source = source.filter(pl.col("Test").is_in([*MODEL_KEYS, "WES (S)"]))
        if source.is_empty():
            raise ValueError("No identified labour-use rows in the source")
    else:
        source = model_rows(source)
    count = write_models(source, args.output_dir, suffix)
    sys.stdout.write(f"Exported {count} model tables\n")
    return 0


def standardize_main(
    report: str, *, template: bool = False, enhance: bool = False
) -> int:
    """Run model taxonomy standardization or template projection."""
    parser = argparse.ArgumentParser(
        description="Standardize source-backed genomics model tables"
    )
    parser.add_argument("--source", type=Path, default=Path("data/Detailed Table.csv"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/enhanced" if enhance else "data/standardized"),
    )
    parser.add_argument("--report", type=Path, default=Path(report))
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    profile = (
        LabProfile.model_validate_json(args.profile.read_bytes())
        if args.profile
        else None
    )
    count = write_models(
        model_rows(read_model_source(args.source)),
        args.output_dir,
        "enhanced" if enhance else "standardized",
        template=template,
        profile=profile,
    )
    audit = json.loads((args.output_dir / "model-audit.json").read_bytes())
    report = [
        "# Model standardization",
        "",
        f"Exported {count} models.",
        f"Rows with incomplete taxonomy {audit['unclassified_rows']}.",
        "",
    ]
    for row in audit["models"]:
        report.extend(
            (
                f"## {row['model']}",
                "",
                f"- Missing categories {', '.join(row['missing_categories']) or 'none'}",
                f"- Categories below minimum {', '.join(row['short_subcategories']) or 'none'}",
                f"- Unknown subcategories {json.dumps(row['unknown_subcategories'])}",
                "",
            )
        )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report), encoding="utf-8")
    sys.stdout.write(f"Exported and audited {count} models\n")
    return 0


def verify_model(frame: pl.DataFrame, model: str) -> dict:
    """Check required fields, taxonomy, bounds and multiplication independently."""
    key = MODEL_KEYS[model]
    template = model_template(key)
    required = template["required_columns"]
    missing = sorted(set(required) - set(frame.columns))
    if frame.is_empty() or missing:
        return {
            "model": model,
            "rows": frame.height,
            "missing_columns": missing,
            "valid": False,
        }
    amounts = frame.select(
        pl.col(name).cast(pl.Float64, strict=False) for name in _REQUIRED_COSTS
    )
    price, units, total = (pl.col(name) for name in _REQUIRED_COSTS)
    cost_checks = amounts.select(
        (~pl.all_horizontal(pl.all().is_finite()).fill_null(False)).alias(
            "missing_or_nonfinite_cost"
        ),
        (~(price.is_between(0, 10000) & units.is_between(0, 10000)))
        .fill_null(False)
        .alias("outside_editable_bounds"),
        ((total - price * units).abs() > 1e-8)
        .fill_null(False)
        .alias("extended_cost_disagrees"),
    )
    bad_identity = (pl.col("Test") != model).fill_null(True) | pl.any_horizontal(
        pl.col("Category", "Sub-Category", "Item")
        .cast(pl.String)
        .str.strip_chars()
        .replace("", None)
        .is_null()
    )
    cost_failures = cost_checks.select(pl.any_horizontal(pl.all())).to_series()
    identity_failures = frame.select(bad_identity).to_series()
    cost_issues = cost_failures.sum()
    identity_issues = identity_failures.sum()
    complete_rows = frame.height - (cost_failures | identity_failures).sum()
    quality_target_passed = complete_rows * 200 > frame.height * 199
    _, audit = standardize_models(
        frame.select(
            pl.col("Test", "Category", "Sub-Category").cast(pl.String)
        ).drop_nulls()
    )
    model_entry = next((item for item in audit["models"] if item["model"] == model), {})
    taxonomy_issues = sum(
        len(model_entry.get(key, ()))
        for key in (
            "missing_categories",
            "short_subcategories",
            "unknown_subcategories",
        )
    )
    return {
        "model": model,
        "rows": frame.height,
        "cost_issues": cost_issues,
        "identity_issues": identity_issues,
        "cost_issue_counts": cost_checks.sum().row(0, named=True),
        "data_quality_score": complete_rows / frame.height,
        "data_quality_target_passed": quality_target_passed,
        "taxonomy": model_entry,
        "valid": quality_target_passed
        and not (cost_issues or identity_issues or taxonomy_issues),
    }


def _compare_model_rows(expected: pl.DataFrame, actual: pl.DataFrame) -> dict:
    comparable = disagreements = matching_rows = 0
    same_shape = actual.columns == expected.columns and actual.height == expected.height
    if same_shape:
        for left, right in zip(expected.iter_rows(), actual.iter_rows(), strict=True):
            differences = 0
            for saved, observed in zip(left, right, strict=True):
                if saved is not None or observed is not None:
                    comparable += 1
                    differences += not same_value(saved, observed)
            disagreements += differences
            matching_rows += differences == 0
    return {
        "schema_and_count_match": same_shape,
        "expected_rows": expected.height,
        "matching_rows": matching_rows,
        "compared_cells": comparable,
        "different_cells": disagreements,
        "valid": bool(comparable and not disagreements),
    }


def quality_main(report: str, *, history: str | None = None) -> int:
    """Audit every selected model and retain results even when validation fails."""
    parser = argparse.ArgumentParser(
        description="Validate prepared model values and taxonomy"
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data/enhanced"))
    parser.add_argument(
        "--suffix", default="enhanced", choices=("enhanced", "standardized")
    )
    parser.add_argument("--model", action="append", choices=tuple(MODEL_KEYS))
    parser.add_argument("--report", type=Path, default=Path(report))
    parser.add_argument(
        "--workbook",
        type=Path,
        help="Validate enhanced historical exports against the selected workbook",
    )
    parser.add_argument(
        "--profile", type=Path, help="Profile used to enhance the export"
    )
    if history is not None:
        parser.add_argument("--history", type=Path, default=Path(history))
    args = parser.parse_args()
    reference = {}
    workbook_digest = None
    selected = args.model or MODEL_KEYS
    if args.workbook:
        if args.suffix != "enhanced":
            parser.error("Workbook-backed validation requires enhanced model exports")
        payload = args.workbook.read_bytes()
        workbook_digest = sha256(payload).hexdigest()
        profile = (
            LabProfile.model_validate_json(args.profile.read_bytes())
            if args.profile
            else None
        )
        # Read the same bytes that identify this receipt.
        with TemporaryDirectory() as directory:
            workbook = Path(directory) / args.workbook.name
            workbook.write_bytes(payload)
            source = model_rows(read_model_source(workbook))
        source, _ = _normalise(source, profile)
        reference = {
            name: apply_template(frame, MODEL_KEYS[name])
            for (name,), frame in source.group_by("Test")
        }
    elif args.profile:
        parser.error("A profile requires workbook-backed validation")
    findings = []
    for name in selected:
        path = args.data_dir / _model_filename(name, args.suffix)
        if path.is_file():
            data = path.read_bytes()
            if args.workbook:
                expected = reference.get(name)
                if expected is None:
                    finding = {"model": name, "valid": False, "missing_reference": True}
                else:
                    actual = pl.read_csv(data, schema_overrides=expected.schema)
                    finding = {"model": name, **_compare_model_rows(expected, actual)}
            else:
                finding = verify_model(
                    pl.read_csv(data, infer_schema_length=None), name
                )
            finding["sha256"] = sha256(data).hexdigest()
        else:
            finding = {"model": name, "valid": False, "missing_file": path.name}
        findings.append(finding)
    receipt = {"timestamp": datetime.now(UTC).isoformat(), "models": findings}
    scope = "Editable model validation"
    if workbook_digest:
        receipt["workbook_sha256"] = workbook_digest
        scope = f"Historical workbook export validation for SHA-256 `{workbook_digest}`"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        f"# Model validation\n\n{scope}\n\n"
        + "\n".join(f"- {item['model']}: {json.dumps(item)}" for item in findings)
        + "\n",
        encoding="utf-8",
    )
    if history is not None:
        args.history.parent.mkdir(parents=True, exist_ok=True)
        earlier = json.loads(args.history.read_bytes()) if args.history.exists() else []
        with TemporaryDirectory(dir=args.history.parent) as directory:
            staged = Path(directory) / args.history.name
            staged.write_text(
                json.dumps([*earlier, receipt], indent=2) + "\n", encoding="utf-8"
            )
            staged.replace(args.history)
    return int(not all(item["valid"] for item in findings))


def compare_models_main(default_dir: str, suffix: str) -> int:
    """Compare the exported model values against the selected workbook revision."""
    parser = argparse.ArgumentParser(
        description="Compare model output with workbook cached values"
    )
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=DETAILED_SHEET)
    parser.add_argument("--data-dir", type=Path, default=Path(default_dir))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    reference = model_rows(
        read_model_source(args.workbook or _default_workbook(), args.sheet)
    )
    if suffix == "enhanced":
        reference, _ = _normalise(reference)
    comparisons = []
    failed = False
    for (name,), expected in reference.group_by("Test", maintain_order=True):
        path = args.data_dir / _model_filename(name, suffix)
        if suffix == "enhanced":
            expected = apply_template(expected, MODEL_KEYS[name])
        if not path.is_file():
            comparisons.append(f"{name}: missing {path.name}")
            failed = True
            continue
        actual = pl.read_csv(path, schema_overrides=expected.schema)
        comparison = _compare_model_rows(expected, actual)
        if not comparison["schema_and_count_match"]:
            comparisons.append(f"{name}: schema or row count mismatch")
            failed = True
            continue
        comparisons.append(
            f"{name}: {comparison['compared_cells']} cells checked, "
            f"{comparison['different_cells']} differences"
        )
        failed |= not comparison["valid"]
    output = "\n".join(comparisons) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    sys.stdout.write(output)
    return int(failed)
