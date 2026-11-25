# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compare all calculated worksheet cells and write a validation report."""

import argparse
import sys
from pathlib import Path

from dapane_genomics.legacy_workbooks import (
    DETAILED_SHEET,
    compare_sheet,
    evaluate_sheet,
)


def main() -> int:
    """Validate source-backed calculated values across the specified sheet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--sheet", default=DETAILED_SHEET)
    parser.add_argument(
        "--output", type=Path, default=Path("reports/phase4_validation_report.txt")
    )
    args = parser.parse_args()
    expected, calculated, first = evaluate_sheet(args.workbook, args.sheet)
    checked, differences = compare_sheet(expected, calculated, first)
    rate = (checked - len(differences)) / checked if checked else 0.0
    report = (
        f"Worksheet: {args.sheet}\n"
        f"Compared cells: {checked}\n"
        f"Agreement: {rate:.2%}\n"
        f"Disagreeing cells: {', '.join(differences) or 'none'}\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return int(not checked or bool(differences))


if __name__ == "__main__":
    raise SystemExit(main())
