#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Export workbook DSA, archived PSA and optional native cost scenarios."""

import argparse
import json
import sys
from pathlib import Path

import polars as pl

from genomics_microcosting.config import load_config
from genomics_microcosting.dapane_adapter import evaluate_native_request
from genomics_microcosting.sensitivity_evidence import archived_draws, scenario_costs


def save_analysis_results(
    results: pl.DataFrame, analysis_type: str, output_dir: Path
) -> None:
    """Write one JSON evidence output and its corresponding summary table."""
    prefix = analysis_type.lower()
    results.write_json(output_dir / f"{prefix}_results.json")
    results.write_csv(output_dir / f"{prefix}_summary.csv")


def main() -> int:
    """Run each analysis selected by the provided source artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument(
        "--draws", type=Path, help="Legacy notebook with retained PSA draws"
    )
    parser.add_argument(
        "--custom",
        type=Path,
        help="JSON object mapping scenario names to Dapane requests",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("reports/scenario_analysis")
    )
    args = parser.parse_args()
    if args.workbook is None and args.draws is None and args.custom is None:
        config = load_config()
        args.workbook = Path(config["workbooks"][config["default_workbook"]]["path"])

    analyses = {}
    if args.workbook is not None:
        analyses["DSA"] = scenario_costs(args.workbook)
    if args.draws is not None:
        analyses["PSA"] = archived_draws(args.draws)
    custom = None
    if args.custom is not None:
        requests = json.loads(args.custom.read_bytes())
        if not isinstance(requests, dict) or not requests:
            parser.error("--custom must contain at least one named Dapane request")
        custom = {
            name: evaluate_native_request(request) for name, request in requests.items()
        }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, result in analyses.items():
        save_analysis_results(result, name, args.output_dir)
        sys.stdout.write(f"{name}: {result.height} evidence records\n")
    if custom is not None:
        (args.output_dir / "custom_results.json").write_text(
            json.dumps(custom, indent=2) + "\n", encoding="utf-8"
        )
        pl.DataFrame(
            {
                "scenario": list(custom),
                "native_result": [json.dumps(v) for v in custom.values()],
            }
        ).write_csv(args.output_dir / "custom_summary.csv")
        sys.stdout.write(f"Custom: {len(custom)} native valuations\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
