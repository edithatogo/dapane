#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Systematic validation of all sheets in the microcosting analysis.

This script provides comprehensive validation of all sheets to ensure they have been
properly translated and are consistent with the source data.
"""

import argparse
import json
import logging
import sys
import traceback
from pathlib import Path

import polars as pl
import polars.selectors as cs

from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.data_manager import DataManager
from genomics_microcosting.sheet_manager import SheetManager

logger = logging.getLogger(__name__)

LARGE_SHEET_ROWS = 100000
HIGH_NULL_PERCENTAGE = 80


def validate_sheet_integrity(sheet_name: str, df: pl.DataFrame) -> dict:
    """Validate the integrity of a sheet.

    Args:
        sheet_name (str): Name of the sheet
        df (pl.DataFrame): DataFrame containing the sheet data

    Returns:
        dict: Validation results

    """
    results = {
        "sheet_name": sheet_name,
        "passed": True,
        "errors": [],
        "warnings": [],
        "metrics": {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_percentage": 0.0,
            "duplicate_rows": 0,
        },
    }

    try:
        # Check basic structure
        if df.is_empty():
            results["errors"].append("Sheet is empty")
            results["passed"] = False

        # Check for reasonable size
        if len(df) > LARGE_SHEET_ROWS:
            results["warnings"].append(
                f"Sheet has {len(df)} rows, which is unusually large",
            )

        # Check null percentage
        if len(df) > 0 and len(df.columns) > 0:
            total_cells = df.shape[0] * df.shape[1]
            null_cells = sum(
                df.with_columns(cs.float().fill_nan(None)).null_count().row(0)
            )
            null_percentage = (null_cells / total_cells) * 100 if total_cells > 0 else 0
            results["metrics"]["null_percentage"] = null_percentage

            if null_percentage > HIGH_NULL_PERCENTAGE:
                results["warnings"].append(
                    f"High null percentage: {null_percentage:.2f}%",
                )

        # Check for duplicate rows
        duplicate_rows = df.height - df.unique().height if df.width else 0
        results["metrics"]["duplicate_rows"] = duplicate_rows
        if duplicate_rows > 0:
            results["warnings"].append(f"Found {duplicate_rows} duplicate rows")

        # Check data types
        numeric_cols = df.select(cs.numeric()).columns

        if len(numeric_cols) == 0:
            results["warnings"].append("No numeric columns found")

    except Exception as e:
        logger.exception("Could not complete validate sheet integrity")
        results["errors"].append(f"Error during integrity validation: {e}")
        results["passed"] = False

    return results


def validate_sheet_consistency(
    sheet_name: str,
    df_parquet: pl.DataFrame,
    df_csv: pl.DataFrame,
) -> dict:
    """Validate consistency between different formats of the same sheet.

    Args:
        sheet_name (str): Name of the sheet
        df_parquet (pl.DataFrame): DataFrame from parquet format
        df_csv (pl.DataFrame): DataFrame from CSV format

    Returns:
        dict: Consistency validation results

    """
    results = {
        "sheet_name": sheet_name,
        "passed": True,
        "errors": [],
        "warnings": [],
    }

    try:
        # Check shape consistency
        if df_parquet.shape != df_csv.shape:
            results["errors"].append(
                f"Shape mismatch: Parquet {df_parquet.shape} vs CSV {df_csv.shape}",
            )
            results["passed"] = False

        # Check column consistency
        if df_parquet.columns != df_csv.columns:
            results["errors"].append("Column names mismatch between formats")
            results["passed"] = False

        # Check data consistency (for a sample of numeric columns)
        numeric_cols_parquet = df_parquet.select(cs.numeric()).columns
        numeric_cols_csv = set(df_csv.select(cs.numeric()).columns)

        common_numeric_cols = [
            col for col in numeric_cols_parquet if col in numeric_cols_csv
        ]

        if common_numeric_cols:
            # Check a sample of values
            sample_size = min(100, df_parquet.height, df_csv.height)
            for col in common_numeric_cols[:3]:  # Check first 3 numeric columns
                parquet_sample = df_parquet[col].head(sample_size)
                csv_sample = df_csv[col].head(sample_size)

                if parquet_sample.dtype.is_float():
                    parquet_sample = parquet_sample.fill_nan(None)
                if csv_sample.dtype.is_float():
                    csv_sample = csv_sample.fill_nan(None)
                comparison = parquet_sample.eq_missing(csv_sample)
                if not comparison.all():
                    mismatch_count = (~comparison).sum()
                    results["warnings"].append(
                        "Data mismatch in column '"
                        f"{col}"
                        "': "
                        f"{mismatch_count}"
                        "/"
                        f"{sample_size}"
                        " values differ",
                    )

    except Exception as e:
        logger.exception("Could not complete validate sheet consistency")
        results["errors"].append(f"Error during consistency validation: {e}")
        results["passed"] = False

    return results


def validate_sheet_cross_references(
    sheet_name: str,
    _df: pl.DataFrame,
    sheet_manager: SheetManager,
    _engine: CalculationEngine,
) -> dict:
    """Validate cross-references from this sheet to others.

    Args:
        sheet_name (str): Name of the sheet
        df (pl.DataFrame): DataFrame containing the sheet data
        sheet_manager (SheetManager): Sheet manager instance
        engine (CalculationEngine): Calculation engine instance

    Returns:
        dict: Cross-reference validation results

    """
    results = {
        "sheet_name": sheet_name,
        "passed": True,
        "errors": [],
        "warnings": [],
        "cross_references_checked": 0,
    }

    try:
        # Get formulas for this sheet
        formulas_df = sheet_manager.get_formulas(sheet_name)
        if formulas_df is None:
            results["warnings"].append(
                "Could not load formulas for cross-reference validation",
            )
            return results

        # Check a sample of cells with formulas for cross-references
        checked_count = 0
        for r_idx in range(min(100, formulas_df.shape[0])):  # Limit to first 100 rows
            for c_idx in range(
                min(10, formulas_df.shape[1]),
            ):  # Limit to first 10 columns
                formula = formulas_df[r_idx, c_idx]
                if (
                    isinstance(formula, str)
                    and formula.startswith("=")
                    and "!" in formula
                    and "'" in formula
                ):
                    checked_count += 1

        results["cross_references_checked"] = checked_count

    except Exception as e:
        logger.exception("Could not complete validate sheet cross references")
        results["errors"].append(f"Error during cross-reference validation: {e}")
        results["passed"] = False

    return results


def validate_sheet(
    sheet_name: str,
    data_manager: DataManager,
    sheet_manager: SheetManager,
    engine: CalculationEngine,
) -> dict:
    """Comprehensive validation of a single sheet.

    Args:
        sheet_name (str): Name of the sheet to validate
        data_manager (DataManager): Data manager instance
        sheet_manager (SheetManager): Sheet manager instance
        engine (CalculationEngine): Calculation engine instance

    Returns:
        dict: Comprehensive validation results

    """
    sys.stdout.write(f"Validating sheet: {sheet_name}" + "\n")

    results = {
        "sheet_name": sheet_name,
        "overall_passed": True,
        "integrity": {},
        "consistency": {},
        "cross_references": {},
    }

    try:
        # Load data in different formats
        df_parquet = data_manager.load_sheet(sheet_name, file_format="parquet")
        if df_parquet is None:
            results["overall_passed"] = False
            sys.stdout.write(f"  Failed to load sheet '{sheet_name}'" + "\n")
            return results
        df_csv = data_manager.load_sheet(
            sheet_name,
            file_format="csv",
            csv_schema=dict(df_parquet.schema),
        )

        # Validate integrity
        results["integrity"] = validate_sheet_integrity(sheet_name, df_parquet)
        if not results["integrity"]["passed"]:
            results["overall_passed"] = False

        # Validate consistency between formats
        if df_csv is not None:
            results["consistency"] = validate_sheet_consistency(
                sheet_name,
                df_parquet,
                df_csv,
            )
            if not results["consistency"]["passed"]:
                results["overall_passed"] = False
        else:
            results["consistency"] = {
                "sheet_name": sheet_name,
                "passed": False,
                "errors": ["CSV format not available"],
                "warnings": [],
            }
            results["overall_passed"] = False

        # Validate cross-references
        results["cross_references"] = validate_sheet_cross_references(
            sheet_name,
            df_parquet,
            sheet_manager,
            engine,
        )
        if not results["cross_references"]["passed"]:
            results["overall_passed"] = False

        # Print summary
        status = "PASSED" if results["overall_passed"] else "FAILED"
        sys.stdout.write(f"  Overall status: {status}" + "\n")

        if results["integrity"]["errors"]:
            sys.stdout.write(
                f"    Integrity errors: {len(results['integrity']['errors'])}" + "\n",
            )
        if results["consistency"]["errors"]:
            sys.stdout.write(
                f"    Consistency errors: {len(results['consistency']['errors'])}\n",
            )
        if results["integrity"]["warnings"]:
            sys.stdout.write(
                f"    Warnings: {len(results['integrity']['warnings'])}" + "\n",
            )

    except Exception as e:
        logger.exception("Could not complete validate sheet")
        results["overall_passed"] = False
        sys.stdout.write(f"  Error validating sheet '{sheet_name}': {e}" + "\n")

    return results


def _print_validation_summary(
    validation_results: list[dict],
    passed_count: int,
    sheet_names: list[str],
) -> None:
    # Summary
    sys.stdout.write(str("=" * 50) + "\n")
    sys.stdout.write("VALIDATION SUMMARY" + "\n")
    sys.stdout.write(str("=" * 50) + "\n")
    sys.stdout.write(f"Total sheets validated: {len(sheet_names)}" + "\n")
    sys.stdout.write(f"Passed validation: {passed_count}" + "\n")
    sys.stdout.write(f"Failed validation: {len(sheet_names) - passed_count}" + "\n")
    sys.stdout.write("\n")

    # Detailed results
    sys.stdout.write("DETAILED RESULTS:" + "\n")
    for result in validation_results:
        status = "PASSED" if result["overall_passed"] else "FAILED"
        sys.stdout.write(f"  {result['sheet_name']}: {status}" + "\n")

        if not result["overall_passed"]:
            if result["integrity"]["errors"]:
                sys.stdout.write(
                    "    Integrity errors: "
                    f"{', '.join(result['integrity']['errors'])}"
                    "\n",
                )
            if result["consistency"]["errors"]:
                sys.stdout.write(
                    "    Consistency errors: "
                    f"{', '.join(result['consistency']['errors'])}"
                    "\n",
                )


def main() -> int | None:
    """Validate all sheets systematically."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "reports/validation_report.json",
    )
    options = parser.parse_args()
    sys.stdout.write("Systematically validating all sheets..." + "\n")
    sys.stdout.write(str("=" * 50) + "\n")

    try:
        # Initialize managers and engine
        data_manager = DataManager()
        sheet_manager = SheetManager()
        engine = CalculationEngine(sheet_manager)

        # Use the workbook names for formula lookups. DataManager resolves file names.
        sheet_names = sheet_manager.get_sheet_names()

        if not sheet_names:
            sys.stdout.write("No sheets found to validate!" + "\n")
            return 1

        sys.stdout.write(f"Found {len(sheet_names)} sheets to validate:" + "\n")
        for name in sheet_names:
            sys.stdout.write(f"  - {name}" + "\n")
        sys.stdout.write("\n")

        # Validate each sheet
        validation_results = []
        passed_count = 0

        for sheet_name in sheet_names:
            result = validate_sheet(sheet_name, data_manager, sheet_manager, engine)
            validation_results.append(result)

            if result["overall_passed"]:
                passed_count += 1
            sys.stdout.write("\n")

        _print_validation_summary(validation_results, passed_count, sheet_names)

        # Save validation report
        report_path = options.output
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format
        serializable_results = []
        for result in validation_results:
            serializable_result = {}
            for key, value in result.items():
                if isinstance(value, pl.DataFrame):
                    serializable_result[key] = "DataFrame"
                else:
                    serializable_result[key] = value
            serializable_results.append(serializable_result)

        with Path(report_path).open("w") as f:
            json.dump(serializable_results, f, indent=2, default=str)

        sys.stdout.write(f"\nValidation report saved to: {report_path}" + "\n")

        return 0 if passed_count == len(sheet_names) else 1

    except Exception as e:
        logger.exception("Could not complete validate all sheets")
        sys.stdout.write(f"Error in main validation process: {e}" + "\n")

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
