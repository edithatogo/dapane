#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Script to prepare translated tables for publication with metadata."""

import argparse
import json
import logging
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from genomics_microcosting.config import load_config

logger = logging.getLogger(__name__)


def create_table_metadata(
    df: pl.DataFrame,
    table_name: str,
    description: str = "",
) -> dict[str, object]:
    """Create metadata for a table.

    Args:
        df (pl.DataFrame): The DataFrame containing the table data
        table_name (str): Name of the table
        description (str): Description of the table

    Returns:
        dict: Metadata dictionary

    """
    metadata = {
        "table_name": table_name,
        "description": description,
        "created_date": datetime.now(UTC).astimezone().isoformat(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": [],
    }

    for col, dtype in df.schema.items():
        series = df[col]
        if dtype.is_float():
            series = series.fill_nan(None)
        col_info = {
            "name": col,
            "dtype": str(dtype),
            "null_count": series.null_count(),
        }

        # Add unique count for categorical columns
        if dtype.base_type() in (pl.String, pl.Categorical, pl.Enum):
            col_info["unique_count"] = series.drop_nulls().n_unique()
            # Add sample values for context
            sample_values = (
                series.drop_nulls().unique(maintain_order=True).head(5).to_list()
            )
            col_info["sample_values"] = sample_values

        metadata["columns"].append(col_info)

    return metadata


def prepare_publication_tables(
    data_dir: Path | None = None,
    publication_dir: Path | None = None,
) -> int:
    """Prepare all tables for publication with metadata."""
    sys.stdout.write("Preparing tables for publication..." + "\n")

    try:
        # Load configuration
        load_config()
        sys.stdout.write("Configuration loaded successfully" + "\n")

        # Define paths
        root = Path(__file__).resolve().parents[1]
        data_dir = data_dir if data_dir is not None else root / "data/prepared"
        publication_dir = (
            publication_dir if publication_dir is not None else root / "publication"
        )
        publication_dir.mkdir(exist_ok=True, parents=True)

        sys.stdout.write(f"Looking for prepared data in {data_dir}" + "\n")

        # Process all parquet files
        parquet_files = sorted(data_dir.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError("No prepared Parquet tables were found")
        sys.stdout.write(f"Found {len(parquet_files)} parquet files" + "\n")

        processed_count = 0

        for parquet_file in parquet_files:
            table_name = parquet_file.stem
            sys.stdout.write(f"Processing {table_name}..." + "\n")

            try:
                # Load the data
                df = pl.read_parquet(parquet_file)
                sys.stdout.write(
                    f"  Loaded {len(df)} rows and {len(df.columns)} columns" + "\n",
                )

                # Save as CSV for publication
                csv_file = publication_dir / f"{table_name}.csv"
                df.write_csv(csv_file)
                sys.stdout.write(f"  Saved CSV to {csv_file}" + "\n")

                # Create metadata
                description = f"Translated table from Excel workbook: {table_name}"
                metadata = create_table_metadata(df, table_name, description)

                # Save metadata as JSON
                metadata_file = publication_dir / f"{table_name}_metadata.json"
                with Path(metadata_file).open("w") as f:
                    json.dump(metadata, f, indent=2)
                sys.stdout.write(f"  Saved metadata to {metadata_file}" + "\n")

                processed_count += 1

            except Exception as e:
                logger.exception("Could not complete prepare publication tables")
                sys.stdout.write(f"  Error processing {table_name}: {e}" + "\n")
                continue

        sys.stdout.write(
            f"\nSuccessfully prepared {processed_count} tables for publication" + "\n",
        )
        sys.stdout.write(f"Publication files saved to {publication_dir}" + "\n")

        # Create a README for the publication directory
        readme_content = f"""# Publication Tables

This directory holds the workbook tables prepared for publication.

## Contents

- CSV files: The translated tables in CSV format for easy use outside Excel
- JSON metadata files: Column names and data types for each table.

## Processing Information

- Processed on: {datetime.now(UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S")}
- Source data directory: {data_dir}
- Number of tables processed: {processed_count}

## Table Descriptions

"""

        # Add table descriptions to README
        for parquet_file in parquet_files:
            table_name = parquet_file.stem
            readme_content += f"- {table_name}.csv: Translated table from Excel\n"

        readme_content += (
            "\n## Usage\n\nThese tables can be used for research, analysis, and "
            "reporting on microcosting for rare disease genomics.\n"
        )

        readme_file = publication_dir / "README.md"
        with Path(readme_file).open("w") as f:
            f.write(readme_content)
        sys.stdout.write(f"Created README.md in {publication_dir}" + "\n")

    except Exception as e:
        logger.exception("Could not complete prepare publication tables")
        sys.stdout.write(f"Error preparing publication tables: {e}" + "\n")

        traceback.print_exc()
        return 1
    else:
        return int(processed_count != len(parquet_files))


def main() -> int:
    """Prepare the tables used in the publication."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    options = parser.parse_args()
    return prepare_publication_tables(options.data_dir, options.output_dir)


if __name__ == "__main__":
    sys.exit(main())
