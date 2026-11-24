#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Validate model tables and record the result in the local history."""

from dapane_genomics.legacy_models import quality_main


def main() -> int:
    """Run this legacy source entry point."""
    return quality_main(
        "docs/validation_pipeline.md", history="data/validation_history.json"
    )


if __name__ == "__main__":
    raise SystemExit(main())
