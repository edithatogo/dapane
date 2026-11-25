#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Evaluate cross-sheet references and export model rows."""

from dapane_genomics.legacy_models import extract_main


def main() -> int:
    """Run this legacy source entry point."""
    return extract_main("data/extracted_proper", "extracted", calculate=True)


if __name__ == "__main__":
    raise SystemExit(main())
