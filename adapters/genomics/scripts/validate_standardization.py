#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Validate the installed model-template requirements."""

from dapane_genomics.legacy_models import quality_main


def main() -> int:
    """Run this legacy source entry point."""
    return quality_main("docs/standardization_validation.md")


if __name__ == "__main__":
    raise SystemExit(main())
