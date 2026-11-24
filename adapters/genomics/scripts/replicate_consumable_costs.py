# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Replicate the consumable cost calculations from the extracted CSV."""

import argparse
import sys
from pathlib import Path

import polars as pl

COLUMNS = [
    "Stage",
    "Step",
    "Details",
    "Consumables",
    "Unit Cost",
    "Units per",
    "50x (WES)",
    "80x (WES)",
    "30x (WGS)",
    "Other",
    "50x",
    "80x",
    "30x",
    "Comments",
    "Source",
    "Reagent Discounts (30%)",
    "Reagent Discounts (70%)",
]
NUMERIC_COLUMNS = [
    "Unit Cost",
    "Units per",
    "50x (WES)",
    "80x (WES)",
    "30x (WGS)",
    "Other",
    "50x",
    "80x",
    "30x",
]


def replicate_costs(source: Path) -> pl.DataFrame:
    """Read the legacy extracted table and reproduce its calculated columns."""
    df = pl.read_csv(source, skip_rows=2, infer_schema=False)
    if df.width < len(COLUMNS):
        raise ValueError(
            "The extracted table has fewer columns than its published layout"
        )
    df = df.rename(dict(zip(df.columns[: len(COLUMNS)], COLUMNS, strict=True)))
    df = df.filter(pl.any_horizontal(pl.all().is_not_null()))

    df = df.with_columns(
        pl.col(column).str.replace_all(r"[^0-9.\-]", "").cast(pl.Float64, strict=False)
        for column in NUMERIC_COLUMNS
    )

    df = df.with_columns(
        (pl.col("Unit Cost") * pl.col("Units per")).alias("Calculated Other")
    )
    df = df.with_columns(
        (pl.col("Unit Cost") * pl.col("Units per") * pl.col("50x (WES)")).alias(
            "Calculated 50x"
        )
    )
    df = df.with_columns(
        (pl.col("Unit Cost") * pl.col("Units per") * pl.col("80x (WES)")).alias(
            "Calculated 80x"
        )
    )
    df = df.with_columns(
        (pl.col("Unit Cost") * pl.col("Units per") * pl.col("30x (WGS)")).alias(
            "Calculated 30x"
        )
    )

    return df


def main() -> int:
    """Run this workbook compatibility check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/extracted/Cons -  Costs and Util - VCGS_values.csv"),
    )
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    result = replicate_costs(options.input)
    if options.output is not None:
        result.write_csv(options.output)
    sys.stdout.write(f"Calculated rows: {result.height}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
