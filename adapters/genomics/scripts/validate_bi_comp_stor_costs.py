# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compare replicated compute and storage costs with the original CSV export."""

import argparse
import csv
import sys
from pathlib import Path

import polars as pl

from dapane_genomics.legacy_workbooks import COMPUTE_STORAGE_BLOCKS, same_value

SOURCE = Path("data/extracted/BI___CompStor_Costs___VCGS_values.csv")


def _scalar(value: str | None) -> float | str | None:
    if not value:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return value


def validate_bi_comp_stor_costs(
    source: Path = SOURCE,
    replicated_dir: Path = Path("data/replicated"),
) -> int:
    """Compare the named calculated fields at their original source rows."""
    with source.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    failures = []
    compared = 0
    for name, (indices, columns) in COMPUTE_STORAGE_BLOCKS.items():
        actual = pl.read_csv(replicated_dir / name, infer_schema=False)
        if actual.height != len(indices) or len(rows) < max(indices):
            raise ValueError(f"{name} has an unexpected source or result row count")
        for column_index, column_name in columns.items():
            for index, value in zip(indices, actual[column_name], strict=True):
                original = rows[index - 1]
                raw = (
                    original[column_index - 1] if column_index <= len(original) else ""
                )
                expected = _scalar(raw)
                observed = _scalar(value)
                if expected is not None or observed is not None:
                    compared += 1
                if not same_value(expected, observed):
                    failures.append(f"{name} field {column_name} at source row {index}")
    if failures:
        sys.stderr.write("\n".join(failures) + "\n")
    sys.stdout.write(f"{compared} cells compared, {len(failures)} mismatches\n")
    return int(not compared or bool(failures))


def main() -> int:
    """Validate a local historical export against calculated outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE)
    parser.add_argument("--replicated-dir", type=Path, default=Path("data/replicated"))
    options = parser.parse_args()
    return validate_bi_comp_stor_costs(options.input, options.replicated_dir)


if __name__ == "__main__":
    raise SystemExit(main())
