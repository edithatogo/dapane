# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Replicate detailed worksheet costs from the original formula inputs."""

import argparse
import sys
from pathlib import Path

import polars as pl

from dapane_genomics.legacy_workbooks import (
    DETAILED_SHEET,
    evaluate_sheet,
    replicate_cost_rows,
)


def main() -> int:
    """Calculate all reference rows and save the cost columns to Parquet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=DETAILED_SHEET)
    parser.add_argument("--first-row", type=int)
    parser.add_argument("--column", default="N")
    parser.add_argument(
        "--reference", type=Path, default=Path("data/ground_truth/ground_truth.parquet")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/calculated_costs_tidy.parquet")
    )
    args = parser.parse_args()
    reference = pl.read_parquet(args.reference)
    _, evaluated, start = evaluate_sheet(args.workbook, args.sheet, args.first_row)
    result = replicate_cost_rows(reference, evaluated, start, args.column)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.write_parquet(args.output)
    sys.stdout.write(f"Calculated {result.height} detailed-table rows\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
