#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Standardize model labels and preserve the source values."""

from dapane_genomics.legacy_models import standardize_main


def main() -> int:
    """Run this legacy source entry point."""
    return standardize_main("docs/automated_standardization.md")


if __name__ == "__main__":
    raise SystemExit(main())
