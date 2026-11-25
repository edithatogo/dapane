#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Validate prepared data and report on its CSV and Parquet consistency."""

import argparse
import sys
from pathlib import Path

from genomics_microcosting.data_consistency_validator import DataConsistencyValidator
from genomics_microcosting.data_manager import DataManager


def main() -> int:
    """Write every table's result and fail when any validation fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument(
        "--output", type=Path, default=Path("reports/data_consistency_validation.md")
    )
    args = parser.parse_args()
    validator = DataConsistencyValidator(DataManager(args.data_dir))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _, passed = validator.write_validation_report(str(args.output))
    sys.stdout.write(f"Validation report saved to {args.output}\n")
    return int(not passed)


if __name__ == "__main__":
    raise SystemExit(main())
