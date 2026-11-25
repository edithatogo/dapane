# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Recalculate the workbook's server, equipment and storage cost tables."""

import argparse
import sys
from pathlib import Path

from dapane_genomics.legacy_workbooks import (
    COMPUTE_STORAGE_BLOCKS,
    COMPUTE_STORAGE_SHEET,
    csv_ready,
    evaluate_sheet,
)


def replicate_bi_comp_stor_costs(
    workbook: Path | None = None,
    output: Path = Path("data/replicated"),
) -> None:
    """Read original workbook inputs and recalculate the three cost blocks."""
    _, evaluated, start = evaluate_sheet(workbook, COMPUTE_STORAGE_SHEET)
    frame = csv_ready(evaluated)
    tables = {}
    for filename, (rows, columns) in COMPUTE_STORAGE_BLOCKS.items():
        offsets = [row - start for row in rows]
        if (
            min(offsets) < 0
            or max(offsets) >= frame.height
            or max(columns) > frame.width
        ):
            raise ValueError(f"{COMPUTE_STORAGE_SHEET} lacks the {filename} block")
        tables[filename] = frame[offsets, [index - 1 for index in columns]].rename(
            dict(
                zip(
                    [frame.columns[index - 1] for index in columns],
                    columns.values(),
                    strict=True,
                )
            )
        )
    output.mkdir(parents=True, exist_ok=True)
    for filename, table in tables.items():
        table.write_csv(output / filename)


def main() -> int:
    """Recalculate and export each workbook cost block."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/replicated"))
    args = parser.parse_args()
    replicate_bi_comp_stor_costs(args.workbook, args.output_dir)
    sys.stdout.write("Recalculated server, equipment and storage tables\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
