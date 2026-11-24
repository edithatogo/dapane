#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Rebuild the detailed worksheet from formula dependencies and validate its values."""

import argparse
import sys
from pathlib import Path

from dapane_genomics.legacy_workbooks import (
    DETAILED_SHEET,
    compare_sheet,
    csv_ready,
    evaluate_sheet,
)


def main() -> int:
    """Export the evaluated table only when the workbook comparison agrees."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=DETAILED_SHEET)
    parser.add_argument(
        "--output", type=Path, default=Path("reports/replicated_detailed_table.csv")
    )
    parser.add_argument("--publication-output", type=Path)
    args = parser.parse_args()
    expected, actual, start = evaluate_sheet(args.workbook, args.sheet)
    compared, differences = compare_sheet(expected, actual, start)
    sys.stdout.write(
        f"Compared {compared} workbook cells, {len(differences)} differences\n"
    )
    if differences or not compared:
        sys.stderr.write("Disagreeing cells: " + ", ".join(differences[:20]) + "\n")
        return 1
    exported = csv_ready(actual)
    for output in (args.output, args.publication_output):
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            exported.write_csv(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
