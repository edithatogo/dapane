# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compare the process worksheet with the calculated results."""

import argparse
import sys
from pathlib import Path

from dapane_genomics.legacy_workbooks import compare_sheet, evaluate_sheet


def validate_process_sheet(workbook: Path | None = None) -> int:
    """Compare calculated process data with the reference at its original cells."""
    expected, calculated, start = evaluate_sheet(workbook, "Process")
    checked, differences = compare_sheet(expected, calculated, start)
    sys.stdout.write(
        f"Compared {checked} process worksheet cells, {len(differences)} differences\n"
    )
    if differences:
        sys.stderr.write("Disagreeing cells: " + ", ".join(differences[:20]) + "\n")
    return int(not checked or bool(differences))


def main() -> int:
    """Read either the caller's workbook or the configured default."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    return validate_process_sheet(parser.parse_args().workbook)


if __name__ == "__main__":
    raise SystemExit(main())
