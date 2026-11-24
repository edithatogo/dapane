# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Retain physical Excel row identity in native compatibility exports."""

from __future__ import annotations

from math import isclose
from pathlib import Path

import polars as pl
from openpyxl.utils import column_index_from_string, get_column_letter

from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.formula_parser import parse_formula
from genomics_microcosting.sheet_manager import SheetManager

DETAILED_SHEET = "Detailed Table"
COMPUTE_STORAGE_SHEET = "BI - Comp+Stor Costs - VCGS"
# Field mappings use one-based coordinates within the supported worksheet layout.
COMPUTE_STORAGE_BLOCKS = {
    "server_costs.csv": (
        (3, 4),
        {
            1: "Description",
            4: "CPUs",
            5: "Cores/CPU",
            6: "Threads/CPU",
            7: "Total Cores",
            8: "Total Threads",
            9: "Memory",
            10: "ex-GST",
            11: "inc. GST",
            12: "3-yr",
            13: "5-yr",
            15: "Cost/CPU",
            16: "Cost/Core",
            17: "Cost/Thread",
            18: "Cost/GB",
            19: "LL Total Hours",
            20: "UL Total Hours",
            21: "Cost/CPU/hr - 70%",
            22: "Cost/Core/hr - 70%",
            23: "Cost/thread/hr - 70%",
            24: "cost/gb/hr - 70%",
            25: "Cost/CPU/hr - 100%",
            26: "Cost/Core/hr - 100%",
            27: "Cost/thread/hr - 100%",
            28: "cost/gb/hr - 100%",
        },
    ),
    "equipment_costs.csv": (
        (8, 9),
        {
            1: "Equipment",
            4: "Useful Life",
            7: "List Price (AUD)",
            10: "Annualised cost",
            11: "WES/Panel",
            12: "WGS",
            13: "Initial Estimate",
            14: "Actual (0.7)",
            15: "Max",
            16: "Unit Cost ($/sample) - Initial",
            17: "Unit Cost ($/sample) - Actual (0.7)",
            18: "Unit Cost ($/sample) - Max",
        },
    ),
    "storage_costs.csv": (
        (15, 18, 19, 20),
        {
            1: "Description",
            4: "Total Space (GB)",
            5: "ex-GST",
            7: "Useable life (years)",
            8: "Cost/GB",
            9: "Cost/GB/year",
            10: "Cost/test",
        },
    ),
}
UNAVAILABLE = (None, "")
UNIT_COST_COLUMNS = (
    "unit_cost_labour",
    "unit_cost_equipment",
    "unit_cost_consumables",
    "unit_cost_other",
)
_CATEGORIES = {
    "Labour": "unit_cost_labour",
    "Equipment": "unit_cost_equipment",
    "Consumables": "unit_cost_consumables",
}
_IDENTITIES = {
    "Test_Type": ("Test", "Test Test Test"),
    "Cost_Category": ("Category", "Category Category Category"),
    "Cost_Sub_Category": ("Sub-Category", "Sub-Category Sub-Category Sub-Category"),
    "Cost_Step": ("Step", "Step Step Step"),
}
_NUMERIC_REFERENCE = (
    "Estimates Quantity of Use per Test LL",
    "Estimates Quantity of Use per Test LL LL",
    "Price (AUD $/unit) LL",
    "Price (AUD $/unit) LL LL",
    "Unit Cost (AUD $/unit) LL",
    "Unit Cost (AUD $/unit) LL LL",
    "Estimate",
    "UL",
    "Estimate_3",
    "UL_3",
    "Estimate Estimate",
    "Estimate Estimate_3",
    "UL UL",
    "UL UL_3",
    "DSA DSA LL SA",
    "LL NSW",
    "LL QLD",
    "LL WA",
)


def ground_truth(frame: pl.DataFrame, first_row: int) -> pl.DataFrame:
    """Project a cached detailed table without losing its source row numbers."""
    identities = []
    for target, choices in _IDENTITIES.items():
        source = next((name for name in choices if name in frame.columns), None)
        if source is None:
            raise ValueError(f"Detailed table lacks the {target} column")
        identities.append(pl.col(source).cast(pl.String).alias(target))
    quantities = [name for name in _NUMERIC_REFERENCE if name in frame.columns]
    if not quantities:
        raise ValueError("Detailed table lacks recognized reference cost columns")
    indexed = frame.with_row_index("Source_Row", offset=first_row)
    selected = indexed.select("Source_Row", *identities, *quantities)
    filtered = selected.filter(pl.any_horizontal(pl.col(quantities).is_not_null()))
    if filtered.is_empty():
        raise ValueError("No populated source rows in the selected reference columns")
    return filtered


def evaluate_sheet(
    workbook: Path | None, sheet: str, first_row: int | None = None
) -> tuple[pl.DataFrame, pl.DataFrame, int]:
    """Return cached and calculated values at the same physical sheet offset."""
    configs = (
        {sheet: {"header_rows": first_row - 1, "data_starts_at": first_row}}
        if first_row is not None
        else None
    )
    sheets = SheetManager(workbook, sheet_configs=configs)
    try:
        expected = sheets.get_ground_truth(sheet)
        engine = CalculationEngine(sheets)
        actual, errors = engine.run_engine(sheet, fail_on_error=False)
        formulas = sheets.get_formulas(sheet)
        if actual is not None and formulas is not None:
            for column, results in zip(formulas, actual, strict=True):
                for formula, value in zip(column, results, strict=True):
                    if (
                        value is None
                        and isinstance(formula, str)
                        and formula.startswith("=")
                    ):
                        parsed = parse_formula(formula)
                        if parsed is None or parsed.get("type") == "unknown":
                            errors.append(
                                "Unsupported formula with no calculated result"
                            )
        if actual is None or errors:
            raise ValueError(f"{sheet} reported {len(errors)} evaluation failures")
        start = sheets.sheet_configs[sheet].get("data_starts_at", 2)
        return expected, actual, start
    finally:
        sheets.close()


def same_value(left: object, right: object) -> bool:
    """Compare compatibility scalar outputs, including unpopulated cells."""
    if type(left) in (int, float) and type(right) in (int, float):
        return isclose(left, right, rel_tol=1e-12, abs_tol=1e-9)
    return type(left) is type(right) and left == right


def compare_sheet(
    expected: pl.DataFrame, actual: pl.DataFrame, first_row: int
) -> tuple[int, list[str]]:
    """Count compared cells and identify disagreements by Excel coordinate."""
    if expected.shape != actual.shape or expected.is_empty():
        raise ValueError("Cached and replayed data must have the same nonzero shape")
    count = 0
    differences = []
    for column_index, (reference, replay) in enumerate(
        zip(expected, actual, strict=True), start=1
    ):
        column = get_column_letter(column_index)
        for row_number, (left, right) in enumerate(
            zip(reference, replay, strict=True), start=first_row
        ):
            if left in UNAVAILABLE and right in UNAVAILABLE:
                continue
            count += 1
            if not same_value(left, right):
                differences.append(f"{column}{row_number}")
    return count, differences


def replicate_cost_rows(
    reference: pl.DataFrame, evaluated: pl.DataFrame, first_row: int, column: str
) -> pl.DataFrame:
    """Reproduce selected unit costs with original row and category identity."""
    if reference.is_empty() or reference["Source_Row"].n_unique() != reference.height:
        raise ValueError("A nonempty set of distinct physical source rows is required")
    column_index = column_index_from_string(column) - 1
    if column_index >= evaluated.width:
        raise ValueError("The cost column is outside the selected sheet")
    records = []
    for row in reference.select("Source_Row", *_IDENTITIES).iter_rows(named=True):
        offset = row["Source_Row"] - first_row
        if not 0 <= offset < evaluated.height:
            raise ValueError(
                f"Reference row {row['Source_Row']} is outside the worksheet"
            )
        value = evaluated[offset, column_index]
        amounts = dict.fromkeys(UNIT_COST_COLUMNS, 0.0)
        cost_type = _CATEGORIES.get(row["Cost_Category"], "unit_cost_other")
        amounts[cost_type] = float(value) if type(value) in (int, float) else None
        records.append(
            {
                **row,
                **amounts,
                "Source_Marker": value if isinstance(value, str) else None,
            }
        )
    return pl.DataFrame(records, schema_overrides={"Source_Marker": pl.String})


def csv_ready(frame: pl.DataFrame) -> pl.DataFrame:
    """Retain mixed worksheet cells by representing the mixed columns as text."""
    return frame.with_columns(
        pl.Series(
            name,
            [None if value is None else str(value) for value in frame[name]],
            dtype=pl.String,
        )
        for name, dtype in frame.schema.items()
        if dtype == pl.Object
    )
