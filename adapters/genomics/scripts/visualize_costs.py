#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Write a dashboard of charts from installed prepared data."""

import argparse
import sys
from pathlib import Path

from genomics_microcosting.visualization import create_summary_dashboard


def main() -> int:
    """Render the dashboard to the selected output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/prepared"))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("reports/visualizations")
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures = create_summary_dashboard(args.data_dir, args.output_dir)
    sys.stdout.write(f"Created {len(figures)} charts in {args.output_dir}\n")
    return int(not figures)


if __name__ == "__main__":
    raise SystemExit(main())
