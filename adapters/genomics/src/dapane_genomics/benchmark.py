# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Measure and compare repeatable synthetic cost-driver workloads."""

from __future__ import annotations

import argparse
import json
import platform
from math import isfinite
from pathlib import Path
from statistics import median_low
from time import perf_counter_ns
from typing import Literal

import polars as pl
import psutil
from pydantic import BaseModel, ConfigDict, Field

from genomics_microcosting.cost_driver_tables import summarise_cost_drivers


class Measurement(BaseModel):
    """Measured elapsed time and sampled memory growth for one workload size."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rows: int = Field(gt=0)
    median_ns: int = Field(gt=0)
    max_sampled_rss_growth_bytes: int = Field(ge=0)


class BenchmarkReceipt(BaseModel):
    """Record the environment and the workload needed for comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    python: str
    polars: str
    platform: str
    threads: int = Field(gt=0)
    repeats: int = Field(ge=3)
    measurements: tuple[Measurement, ...] = Field(min_length=1)


def _workload(rows: int) -> pl.DataFrame:
    index = pl.Series("row", range(rows), dtype=pl.Int64)
    return pl.DataFrame(index).select(
        pl.lit("Synthetic assay").alias("Test"),
        pl.when(pl.col("row") % 2 == 0)
        .then(pl.lit("Labour"))
        .otherwise(pl.lit("Equipment"))
        .alias("Category"),
        pl.lit("Synthetic component").alias("Sub-Category"),
        pl.when(pl.col("row") % 2 == 0).then(8.0).otherwise(2.0).alias("cost"),
    )


def measure(rows: tuple[int, ...], repeats: int = 5) -> BenchmarkReceipt:
    """Run the real native contribution calculation on independently known totals."""
    if not rows or any(size < 1 for size in rows) or len(set(rows)) != len(rows):
        raise ValueError("Workload sizes must be distinct positive integers")
    if repeats < 3:
        raise ValueError("At least three samples are required")
    process = psutil.Process()
    results = []
    for size in sorted(rows):
        frame = _workload(size)
        expected_total = 8 * ((size + 1) // 2) + 2 * (size // 2)
        summarise_cost_drivers(frame, cost_column="cost")
        elapsed = []
        memory = []
        for _ in range(repeats):
            before = process.memory_info().rss
            start = perf_counter_ns()
            contributions = summarise_cost_drivers(frame, cost_column="cost")
            elapsed.append(max(1, perf_counter_ns() - start))
            memory.append(max(0, process.memory_info().rss - before))
            if (
                contributions["Absolute_Value"].sum() != expected_total
                or contributions["Source_Rows"].sum() != size
            ):
                raise RuntimeError("The evaluated workload differs from its reference")
        results.append(
            Measurement(
                rows=size,
                median_ns=median_low(elapsed),
                max_sampled_rss_growth_bytes=max(memory),
            )
        )
    return BenchmarkReceipt(
        python=platform.python_version(),
        polars=pl.__version__,
        platform=platform.platform(),
        threads=pl.thread_pool_size(),
        repeats=repeats,
        measurements=tuple(results),
    )


def compare(
    reference: BenchmarkReceipt,
    candidate: BenchmarkReceipt,
    time_ratio: float = 1.05,
) -> list[int]:
    """Return workload sizes that exceed the allowed runtime ratio."""
    if not isfinite(time_ratio) or time_ratio < 1:
        raise ValueError("The timing ratio must be finite and at least 1")
    if reference.model_dump(exclude={"measurements"}) != candidate.model_dump(
        exclude={"measurements"}
    ):
        raise ValueError(
            "Benchmark runtime, platform, threads and sample counts must match"
        )
    if tuple(item.rows for item in reference.measurements) != tuple(
        item.rows for item in candidate.measurements
    ):
        raise ValueError("Benchmark workload sizes must match")
    return [
        after.rows
        for before, after in zip(
            reference.measurements, candidate.measurements, strict=True
        )
        if after.median_ns > before.median_ns * time_ratio
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sample = commands.add_parser("measure")
    sample.add_argument("output", type=Path)
    sample.add_argument("--rows", nargs="+", type=int, default=[1000, 5000, 10000])
    sample.add_argument("--repeats", type=int, default=5)
    diff = commands.add_parser("compare")
    diff.add_argument("baseline", type=Path)
    diff.add_argument("candidate", type=Path)
    diff.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "measure":
        result = measure(tuple(args.rows), args.repeats)
        with args.output.open("xb") as output:
            output.write((result.model_dump_json(indent=2) + "\n").encode())
        return 0
    reference = BenchmarkReceipt.model_validate_json(args.baseline.read_bytes())
    candidate = BenchmarkReceipt.model_validate_json(args.candidate.read_bytes())
    regressions = compare(reference, candidate)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump({"timing_regression_rows": regressions}, output)
        output.write("\n")
    return int(bool(regressions))
