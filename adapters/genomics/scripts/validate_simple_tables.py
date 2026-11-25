# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Check calculated values for supporting workbook tables."""

import argparse
import sys
from math import isfinite
from pathlib import Path

import polars as pl

from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.config import load_config
from genomics_microcosting.sheet_manager import SheetManager

NUMERIC_COMPARISON_TOLERANCE = 1e-6


def validate_simple_tables(
    workbook: Path | None = None,
    data_dir: Path = Path("data/prepared"),
    *,
    labor_sheet: str = "2. Labor Prices",
    estimates_sheet: str = "3. Estimates",
) -> int:
    """Evaluate the sheets and compare numeric cells at their physical offsets."""
    if workbook is None:
        workbook = Path(load_config()["workbooks"]["main"]["path"])
    tables = (
        (labor_sheet, "2._labor_prices.parquet", 2, 3),
        (estimates_sheet, "3._estimates.parquet", 3, 5),
    )
    sheets = SheetManager(
        workbook,
        sheet_configs={
            sheet: {"header_rows": headers, "data_starts_at": first}
            for sheet, _, headers, first in tables
        },
    )
    status = 0
    try:
        engine = CalculationEngine(sheets)
        for sheet, filename, _, _ in tables:
            reference = pl.read_parquet(data_dir / filename)
            result, errors = engine.run_engine(sheet, fail_on_error=False)
            if errors or result is None or result.shape != reference.shape:
                sys.stderr.write(f"{sheet}: evaluation failed or table shape differs\n")
                status = 1
                continue
            differences = []
            missing = 0
            for expected, calculated in zip(reference, result, strict=True):
                for original, value in zip(expected, calculated, strict=True):
                    if type(original) not in (int, float) or not isfinite(original):
                        continue
                    if type(value) not in (int, float) or not isfinite(value):
                        missing += 1
                        continue
                    differences.append(abs(value - original))
            invalid = sum(diff > NUMERIC_COMPARISON_TOLERANCE for diff in differences)
            sys.stdout.write(
                f"{sheet}: {len(differences)} cells compared, {invalid} differences, "
                f"{missing} missing\n"
            )
            if not differences or missing or invalid:
                status = 1
    finally:
        sheets.close()
    return status


def main() -> int:
    """Compare the configured supplemental tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--data-dir", type=Path, default=Path("data/prepared"))
    parser.add_argument("--labor-sheet", default="2. Labor Prices")
    parser.add_argument("--estimates-sheet", default="3. Estimates")
    options = parser.parse_args()
    return validate_simple_tables(
        options.workbook,
        options.data_dir,
        labor_sheet=options.labor_sheet,
        estimates_sheet=options.estimates_sheet,
    )


if __name__ == "__main__":
    raise SystemExit(main())
