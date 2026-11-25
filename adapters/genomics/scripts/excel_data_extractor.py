#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Extract calculated model rows from the workbook."""

from dapane_genomics.legacy_models import extract_main


def main() -> int:
    """Run this legacy source entry point."""
    return extract_main("data/corrected", "corrected")


if __name__ == "__main__":
    raise SystemExit(main())
