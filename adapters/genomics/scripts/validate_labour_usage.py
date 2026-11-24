# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compare labour usage with the prepared ground truth."""

import argparse
import sys
from math import isclose
from pathlib import Path

import polars as pl
from openpyxl.utils import get_column_letter

from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.sheet_manager import SheetManager

ERROR_PREVIEW_LIMIT = 5


def _sheet_discrepancies(
    ground_truth_df: pl.DataFrame,
    calculated_df: pl.DataFrame,
    engine: CalculationEngine,
    sheet_name: str,
    first_row: int = 1,
) -> list[dict]:
    # Compare the results
    if ground_truth_df.shape != calculated_df.shape or ground_truth_df.is_empty():
        raise ValueError(
            "Calculated and reference tables must have equal nonzero shapes"
        )
    discrepancies = []
    for r_idx in range(ground_truth_df.shape[0]):
        for c_idx in range(ground_truth_df.shape[1]):
            excel_value = ground_truth_df[r_idx, c_idx]
            calculated_value = calculated_df[r_idx, c_idx]

            if type(excel_value) in (int, float) and type(calculated_value) in (
                int,
                float,
            ):
                # This compatibility diagnostic compares Excel and engine binary floats.
                equal = isclose(
                    excel_value, calculated_value, rel_tol=1e-12, abs_tol=1e-12
                )
            else:
                equal = type(excel_value) is type(calculated_value) and (
                    excel_value == calculated_value
                )
            if not equal:
                cell = f"{get_column_letter(c_idx + 1)}{r_idx + first_row}"
                formula = engine.get_cell_formula(sheet_name, cell)
                discrepancies.append(
                    {
                        "cell": cell,
                        "formula": formula,
                        "excel_value": excel_value,
                        "calculated_value": calculated_value,
                    },
                )

    return discrepancies


def validate_sheet(sheet_name: str, workbook: Path | None = None) -> int:
    """Compare calculated labour usage with the prepared workbook values."""
    sys.stdout.write(f"--- Validating Sheet: {sheet_name} ---" + "\n")

    # Initialize the sheet manager and engine
    sheet_manager = SheetManager(workbook)
    engine = CalculationEngine(sheet_manager)

    # Get the ground truth values from the original Excel file
    ground_truth_df = sheet_manager.get_ground_truth(sheet_name)
    if ground_truth_df is None:
        sys.stdout.write(f"Could not load ground truth for sheet: {sheet_name}" + "\n")
        return 1

    # Run the engine to calculate the values
    result = engine.run_engine(sheet_name, fail_on_error=False)
    if result is None or result[0] is None:
        sys.stdout.write(f"Engine failed to run on sheet: {sheet_name}" + "\n")
        return 1

    calculated_df, errors = result
    if errors:
        sys.stdout.write(f"Engine encountered {len(errors)} errors:" + "\n")
        for error in errors[:5]:  # Show first 5 errors
            sys.stdout.write(f"  {error}" + "\n")
        if len(errors) > ERROR_PREVIEW_LIMIT:
            sys.stdout.write(f"  ... and {len(errors) - 5} more errors" + "\n")
        return 1

    discrepancies = _sheet_discrepancies(
        ground_truth_df,
        calculated_df,
        engine,
        sheet_name,
        sheet_manager.sheet_configs.get(sheet_name, {}).get("data_starts_at", 2),
    )

    if discrepancies:
        sys.stdout.write("Discrepancies found:" + "\n")
        for d in discrepancies:
            sys.stdout.write(str(d) + "\n")
    else:
        sys.stdout.write(
            f"Success! No discrepancies found for sheet: {sheet_name}" + "\n",
        )
    return int(bool(discrepancies))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default="Labour - Usage - VCGS")
    options = parser.parse_args()
    raise SystemExit(validate_sheet(options.sheet, options.workbook))
