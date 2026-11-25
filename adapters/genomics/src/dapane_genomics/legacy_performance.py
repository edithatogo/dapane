# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Expose the maintained native benchmark in the legacy reporting commands."""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from .benchmark import BenchmarkReceipt, compare, measure

_SIZES = (1000, 5000, 10000)


def establish_performance_baselines() -> dict:
    """Measure the verified contribution workloads and retain machine identity."""
    return measure(_SIZES).model_dump(mode="json")


def save_baselines(baselines: dict, output_file: str | None = None) -> str:
    """Write a new baseline JSON receipt."""
    if output_file is None:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        output_file = f"performance_baselines_{timestamp}.json"
    with Path(output_file).open("x", encoding="utf-8") as output:
        json.dump(baselines, output, indent=2)
        output.write("\n")
    return output_file


def print_baseline_summary(baselines: dict) -> None:
    """Print timings and sampled memory for each workload."""
    result = BenchmarkReceipt.model_validate(baselines)
    for item in result.measurements:
        sys.stdout.write(
            f"{item.rows} rows: {item.median_ns / 1e6:.3f} ms median, "
            f"{item.max_sampled_rss_growth_bytes} bytes sampled RSS growth\n"
        )


def load_baselines(input_file: str) -> dict:
    """Load a benchmark receipt with the required comparison identity."""
    return BenchmarkReceipt.model_validate_json(
        Path(input_file).read_bytes()
    ).model_dump(mode="json")


def compare_baselines(current_baselines: dict, reference_baselines: dict) -> dict:
    """Compare matching runtimes and flag any workload over the 5% threshold."""
    current = BenchmarkReceipt.model_validate(current_baselines)
    reference = BenchmarkReceipt.model_validate(reference_baselines)
    regressions = compare(reference, current)
    candidate_seconds = sum(item.median_ns for item in current.measurements) / 1e9
    reference_seconds = sum(item.median_ns for item in reference.measurements) / 1e9
    return {
        "processing_time": {
            "current": candidate_seconds,
            "reference": reference_seconds,
            "change_percentage": 100 * (candidate_seconds / reference_seconds - 1),
            "timing_regression_rows": regressions,
            "performance_regression": bool(regressions),
        }
    }


def main() -> int:
    """Establish a real cost-contribution baseline and save its results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    args = parser.parse_args()
    baselines = establish_performance_baselines()
    print_baseline_summary(baselines)
    sys.stdout.write(save_baselines(baselines, args.output) + "\n")
    return 0
