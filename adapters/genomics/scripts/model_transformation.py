#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Normalize model labels and map them to their input templates."""

from dapane_genomics.legacy_models import standardize_main


def main() -> int:
    """Run this legacy source entry point."""
    return standardize_main("docs/model_transformation.md", template=True)


if __name__ == "__main__":
    raise SystemExit(main())
