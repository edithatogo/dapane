# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Replicate equipment cost calculations using the extracted CSV data."""

import argparse
import sys
from pathlib import Path

import numpy_financial as npf
import polars as pl

COLUMNS = [
    "Equipment",
    "Description",
    "Brand",
    "Model",
    "Useful Life",
    "List Price (USD)",
    "List Price (EUR)",
    "List Price (AUD)",
    "Date Accessed",
    "Source",
    "Annualised cost",
    "Present value",
    "Workflows WES/Panel",
    "Workflows WGS",
    "Initial Estimate Total Samples per Year",
    "Initial Estimate 0.7",
    "Initial Estimate Max",
    "Theoretical 50x WES",
    "Theoretical 0.8",
    "Theoretical 0.4",
    "Theoretical Comment",
    "50x WES Max",
    "50x WES 0.7",
    "50x WES Comment",
    "80x WES Max",
    "80x WES 0.7",
    "30x Genomes Estimate",
    "30x Genomes Source",
    "30x Genomes Comment",
    "30x Genomes Max",
    "30x Genomes 70%",
    "Cost per sample LL",
    "Cost per sample MP",
    "Cost per sample UL",
]
NUMERIC_COLUMNS = [
    "Useful Life",
    "List Price (AUD)",
    "Annualised cost",
    "Present value",
]


def replicate_costs(source: Path) -> pl.DataFrame:
    """Read the legacy extracted table and reproduce its calculated columns."""
    df = pl.read_csv(source, skip_rows=3, infer_schema=False)
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
        (pl.col("List Price (AUD)") / pl.col("Useful Life")).alias(
            "Calculated Annualised cost"
        )
    )
    df = df.with_columns(
        pl.struct("Useful Life", "List Price (AUD)")
        .map_elements(
            lambda row: (
                float(npf.pmt(0.0452, row["Useful Life"], -row["List Price (AUD)"]))
                if row["Useful Life"] and row["List Price (AUD)"] is not None
                else None
            ),
            return_dtype=pl.Float64,
        )
        .alias("Calculated Present value")
    )

    return df


def main() -> int:
    """Run this workbook compatibility check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/extracted/Eq - Costs and Usage - VCGS_values.csv"),
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
