# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Replicate the labour cost calculations using the extracted CSV data."""

import argparse
import sys
from pathlib import Path

import polars as pl

COLUMNS = [
    "Jurisdiction",
    "Personnel type",
    "Label",
    "Award",
    "Grade(s)",
    "Distribution desc",
    "References",
    "Rate of Pay (weekly, 38h) desc",
    "Year",
    "Superannuation Rate (%)",
    "Hours per week",
    "Average productive time (%)",
    "Average Penalties %",
    "Public Holiday Penalty Percentage",
    "Private Practice Loading",
    "Attraction and Retention Allowance",
    "Sick Leave Percentage",
    "Professional Development Allowance",
    "Annual Leave Entitlement (Weeks)",
    "Annual Leave Loading (%)",
    "Indexation per annum (%)",
    "Base Salary LL",
    "Base Salary Mid-point",
    "Base Salary UL",
    "Base Salary + Costs LL",
    "Base Salary + Costs Mid-point",
    "Base Salary + Costs UL",
    "Base Salary + Costs (hourly) LL",
    "Base Salary + Costs (hourly) Mid-point",
    "Base Salary + Costs (hourly) UL",
]
NUMERIC_COLUMNS = [
    "Base Salary LL",
    "Base Salary Mid-point",
    "Base Salary UL",
    "Base Salary + Costs LL",
    "Superannuation Rate (%)",
    "Average Penalties %",
    "Public Holiday Penalty Percentage",
    "Private Practice Loading",
    "Attraction and Retention Allowance",
    "Sick Leave Percentage",
    "Professional Development Allowance",
    "Annual Leave Entitlement (Weeks)",
    "Annual Leave Loading (%)",
    "Average productive time (%)",
    "Hours per week",
    "Base Salary + Costs (hourly) LL",
]

RATE_COLUMNS = {
    "Superannuation Rate (%)",
    "Average Penalties %",
    "Public Holiday Penalty Percentage",
    "Private Practice Loading",
    "Attraction and Retention Allowance",
    "Sick Leave Percentage",
    "Annual Leave Loading (%)",
    "Average productive time (%)",
}


def replicate_costs(source: Path) -> pl.DataFrame:
    """Read the legacy extracted table and reproduce its calculated columns."""
    df = pl.read_csv(source, skip_rows=1, infer_schema=False)
    if df.width < len(COLUMNS):
        raise ValueError(
            "The extracted table has fewer columns than its published layout"
        )
    df = df.rename(dict(zip(df.columns[: len(COLUMNS)], COLUMNS, strict=True)))
    df = df.filter(pl.any_horizontal(pl.all().is_not_null()))

    for column in NUMERIC_COLUMNS:
        source = pl.col(column).str.strip_chars()
        amount = source.str.replace_all(r"[^0-9.\-]", "").cast(pl.Float64, strict=False)
        if column in RATE_COLUMNS:
            amount = (
                pl.when(source.str.ends_with("%")).then(amount / 100).otherwise(amount)
            )
        df = df.with_columns(amount.alias(column))

    df = df.with_columns(
        (
            pl.col("Base Salary LL")
            + (pl.col("Base Salary UL") - pl.col("Base Salary LL")) / 2
        ).alias("Calculated Base Salary Mid-point")
    )
    df = df.with_columns(
        (
            (
                pl.col("Base Salary LL")
                + pl.col("Base Salary LL") * pl.col("Superannuation Rate (%)")
                + pl.col("Base Salary LL") * pl.col("Average Penalties %")
                + pl.col("Base Salary LL") * pl.col("Public Holiday Penalty Percentage")
                + pl.col("Base Salary LL") * pl.col("Private Practice Loading")
                + pl.col("Base Salary LL")
                * pl.col("Attraction and Retention Allowance")
                + pl.col("Base Salary LL") * pl.col("Sick Leave Percentage")
                + pl.col("Professional Development Allowance")
                + pl.col("Base Salary LL")
                * ((52 + pl.col("Annual Leave Entitlement (Weeks)")) / 52)
                * (1 + pl.col("Annual Leave Loading (%)"))
            )
            * (1 / pl.col("Average productive time (%)"))
        ).alias("Calculated Base Salary + Costs LL")
    )
    df = df.with_columns(
        (
            pl.col("Calculated Base Salary + Costs LL") / 52 / pl.col("Hours per week")
        ).alias("Calculated Base Salary + Costs (hourly) LL")
    )

    return df


def main() -> int:
    """Run this workbook compatibility check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/extracted/Labour - Costs - VCGS_values.csv"),
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
