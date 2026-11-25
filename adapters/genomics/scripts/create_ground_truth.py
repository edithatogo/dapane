# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Export a cached detailed-table reference with Excel row identities."""

import argparse
import sys
from pathlib import Path

import polars as pl

from dapane_genomics.legacy_workbooks import ground_truth


def create_ground_truth_dataset(
    source: Path = Path("data/prepared/detailed_table.parquet"),
    output_dir: Path = Path("data/ground_truth"),
    first_row: int = 5,
) -> pl.DataFrame:
    """Retain all populated reference rows and their physical locations."""
    result = ground_truth(pl.read_parquet(source), first_row)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.write_parquet(output_dir / "ground_truth.parquet")
    result.write_csv(output_dir / "ground_truth.csv")
    return result


def main() -> int:
    """Write the selected reference dataset in both compatibility formats."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("data/prepared/detailed_table.parquet")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/ground_truth"))
    parser.add_argument("--first-row", type=int, default=5)
    args = parser.parse_args()
    result = create_ground_truth_dataset(args.input, args.output_dir, args.first_row)
    sys.stdout.write(f"Retained {result.height} source rows\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
