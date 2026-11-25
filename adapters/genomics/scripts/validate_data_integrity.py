#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify that corrected exports preserve their original values."""

from dapane_genomics.legacy_models import compare_models_main


def main() -> int:
    """Run this legacy source entry point."""
    return compare_models_main("data/corrected", "corrected")


if __name__ == "__main__":
    raise SystemExit(main())
