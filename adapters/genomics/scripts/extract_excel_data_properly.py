#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Export the original labour-usage rows by model."""

from dapane_genomics.legacy_models import LABOUR_SHEET, extract_main


def main() -> int:
    """Run this legacy source entry point."""
    return extract_main("data/extracted_correct", "extracted", sheet=LABOUR_SHEET)


if __name__ == "__main__":
    raise SystemExit(main())
