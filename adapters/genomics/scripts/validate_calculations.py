# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Validate the tidy calculated output against original workbook cells."""

import argparse
import sys
from pathlib import Path

import polars as pl
from openpyxl.utils import column_index_from_string

from dapane_genomics.legacy_workbooks import (
    DETAILED_SHEET,
    UNIT_COST_COLUMNS,
    same_value,
)
from genomics_microcosting.sheet_manager import SheetManager


def validate_calculations(
    source: Path = Path("data/calculated_costs_tidy.parquet"),
    workbook: Path | None = None,
    sheet: str = DETAILED_SHEET,
    column: str = "N",
) -> int:
    """Compare numeric and marker outputs using retained one-based row IDs."""
    computed = pl.read_parquet(source)
    if computed.is_empty() or computed["Source_Row"].n_unique() != computed.height:
        raise ValueError("Expected distinct, nonempty calculated source rows")
    sheets = SheetManager(workbook)
    disagreements = []
    numeric_count = 0
    try:
        reference = sheets.get_ground_truth(sheet)
        first = sheets.sheet_configs[sheet].get("data_starts_at", 2)
        col = column_index_from_string(column) - 1
        for record in computed.select(
            "Source_Row", *UNIT_COST_COLUMNS, "Source_Marker"
        ).iter_rows(named=True):
            row = record["Source_Row"]
            if not 0 <= row - first < reference.height:
                raise ValueError(
                    f"Calculated source row {row} is outside the worksheet"
                )
            expected = reference[row - first, col]
            expected_numeric = type(expected) in (int, float)
            amounts = [record[key] for key in UNIT_COST_COLUMNS]
            numeric_count += expected_numeric
            if expected_numeric:
                agrees = all(amount is not None for amount in amounts) and same_value(
                    float(expected), sum(amounts)
                )
                agrees = agrees and record["Source_Marker"] is None
            else:
                agrees = (
                    amounts.count(None) == 1
                    and all(amount == 0 for amount in amounts if amount is not None)
                    and same_value(expected, record["Source_Marker"])
                )
            if not agrees:
                disagreements.append(str(row))
    finally:
        sheets.close()
    if disagreements:
        sys.stderr.write(
            "Mismatched worksheet rows: " + ", ".join(disagreements) + "\n"
        )
    sys.stdout.write(
        f"Compared {computed.height} retained rows ({numeric_count} numeric), "
        f"{len(disagreements)} differences\n"
    )
    return int(not numeric_count or bool(disagreements))


def main() -> int:
    """Validate the output produced by replicate_calculations.py."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=DETAILED_SHEET)
    parser.add_argument("--column", default="N")
    parser.add_argument(
        "--input", type=Path, default=Path("data/calculated_costs_tidy.parquet")
    )
    options = parser.parse_args()
    return validate_calculations(
        options.input, options.workbook, options.sheet, options.column
    )


if __name__ == "__main__":
    raise SystemExit(main())
