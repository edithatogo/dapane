# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Validate calculated detailed-table costs with the installed engine."""

import sys

import polars as pl

from genomics_microcosting.validate_engine import (
    load_ground_truth,
)
from genomics_microcosting.validate_engine import (
    validate_engine as run_validation,
)


def establish_ground_truth() -> pl.DataFrame | None:
    """Load the configured source-backed prepared table."""
    return load_ground_truth()


def validate_engine() -> bool:
    """Run the maintained comparison with explicit status."""
    return run_validation() == 0


def main() -> int:
    """Pass the report and version options to the installed command."""
    return int(not validate_engine())


if __name__ == "__main__":
    sys.exit(main())
