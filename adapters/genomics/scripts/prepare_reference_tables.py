# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Prepare supplemental reference tables from workbook sheets."""

import argparse
from pathlib import Path

from genomics_microcosting.config import load_config
from genomics_microcosting.prepare_data import parse_reference_sheet

LABOR = "2. Labor Prices"
ESTIMATES = "3. Estimates"
REFERENCE_TABLES = (
    ("2._labor_prices.parquet", 2, 0),
    ("3._estimates.parquet", 3, 1),
)


def main() -> int:
    """Prepare and save the two supplemental reference tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--labor-sheet", default=LABOR)
    parser.add_argument("--estimates-sheet", default=ESTIMATES)
    parser.add_argument("--output-dir", type=Path, default=Path("data/prepared"))
    args = parser.parse_args()
    workbook = args.workbook
    if workbook is None:
        workbook = Path(load_config()["workbooks"]["main"]["path"])
    names = args.labor_sheet, args.estimates_sheet
    tables = {
        filename: parse_reference_sheet(workbook, name, header, skip)
        for (filename, header, skip), name in zip(REFERENCE_TABLES, names, strict=True)
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, frame in tables.items():
        frame.write_parquet(args.output_dir / filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
