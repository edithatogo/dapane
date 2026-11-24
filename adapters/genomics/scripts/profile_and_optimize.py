#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Script to profile and optimize the performance of microcosting analysis."""

__lazy_modules__ = (
    "collections.abc",
    "numpy",
)

import argparse
import json
import logging
import sys
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

import polars as pl
import polars.selectors as cs

from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.performance import (
    CachingOptimizer,
    DataOptimizer,
    ParallelProcessor,
    PerformanceProfiler,
)
from genomics_microcosting.sheet_manager import SheetManager
from genomics_microcosting.visualization import load_prepared_data

logger = logging.getLogger(__name__)

CACHE_TEST_SAMPLE_ROWS = 100


def profile_data_loading(
    profiler: PerformanceProfiler,
    data_dir: Path,
) -> dict[str, Any]:
    """Profile data loading performance.

    Args:
        profiler: PerformanceProfiler instance
        data_dir: Directory containing prepared data

    Returns:
        Dictionary with profiling results

    """
    sys.stdout.write("Profiling data loading performance..." + "\n")

    @profiler.profile("load_prepared_data")
    def load_data() -> dict[str, pl.DataFrame]:
        return load_prepared_data(data_dir)

    try:
        data_dict = load_data()
        sys.stdout.write(f"Loaded {len(data_dict)} data tables" + "\n")
        return {
            "status": "success" if data_dict else "error",
            "table_count": len(data_dict),
            "data": data_dict,
        }
    except Exception as e:
        logger.exception("Could not complete profile data loading")
        sys.stdout.write(f"Error loading data: {e}" + "\n")
        return {"status": "error", "error": str(e)}


def profile_calculation_engine(
    profiler: PerformanceProfiler,
    _data_dict: dict[str, pl.DataFrame],
    workbook: Path | None = None,
) -> dict[str, Any]:
    """Profile calculation engine performance.

    Args:
        profiler: PerformanceProfiler instance
        data_dict: Dictionary of loaded data tables

    Returns:
        Dictionary with profiling results

    """
    sys.stdout.write("Profiling calculation engine performance..." + "\n")

    @profiler.profile("initialize_engine")
    def init_engine() -> CalculationEngine:
        sheet_manager = SheetManager(workbook)
        return CalculationEngine(sheet_manager)

    @profiler.profile("run_engine")
    def run_engine(engine: CalculationEngine) -> object:
        return engine.run_engine(
            engine.sheet_manager.default_sheet_names["detailed_table"]
        )

    engine = None
    try:
        engine = init_engine()
        results_df, errors = run_engine(engine)

        sys.stdout.write(
            f"Calculation engine completed with {len(errors) if errors else 0} errors"
            "\n",
        )
        return {
            "status": "success",
            "result_shape": results_df.shape if results_df is not None else None,
            "error_count": len(errors) if errors else 0,
        }
    except Exception as e:
        logger.exception("Could not complete profile calculation engine")
        sys.stdout.write(f"Error running calculation engine: {e}" + "\n")
        return {"status": "error", "error": str(e)}
    finally:
        if engine is not None:
            engine.sheet_manager.close()


def optimize_dataframes(
    data_dict: dict[str, pl.DataFrame],
    output_dir: Path,
) -> dict[str, pl.DataFrame]:
    """Optimize DataFrames for better memory usage.

    Args:
        data_dict: Dictionary of DataFrames to optimize
        output_dir: Directory to save optimized data

    Returns:
        Dictionary of optimized DataFrames

    """
    sys.stdout.write("Optimizing DataFrames..." + "\n")
    optimizer = DataOptimizer()

    optimized_data = {}
    optimization_stats = []

    for table_name, df in data_dict.items():
        sys.stdout.write(f"  Optimizing {table_name} ({df.shape})..." + "\n")
        start_time = time.time()

        original_memory = df.estimated_size("mb")
        optimized_df = optimizer.optimize_dataframe(df)
        if not optimized_df.cast(df.schema).equals(df):
            raise ValueError(f"Optimization changed values in {table_name}")
        optimized_memory = optimized_df.estimated_size("mb")

        end_time = time.time()

        savings = original_memory - optimized_memory
        savings_percent = (
            (savings / original_memory) * 100 if original_memory > 0 else 0
        )

        optimization_stats.append(
            {
                "table": table_name,
                "original_memory_mb": original_memory,
                "optimized_memory_mb": optimized_memory,
                "savings_mb": savings,
                "savings_percent": savings_percent,
                "processing_time_seconds": end_time - start_time,
            },
        )

        optimized_data[table_name] = optimized_df

        # Save optimized DataFrame
        optimized_file = output_dir / f"optimized_{table_name}.parquet"
        optimized_df.write_parquet(optimized_file)
        sys.stdout.write(f"    Saved optimized data to {optimized_file}" + "\n")

    # Save optimization statistics
    stats_file = output_dir / "optimization_stats.json"
    with Path(stats_file).open("w") as f:
        json.dump(optimization_stats, f, indent=2)
    sys.stdout.write(f"  Saved optimization statistics to {stats_file}" + "\n")

    return optimized_data


def _profile_column_processing(
    df: pl.DataFrame,
    largest_table: str,
    profiler: PerformanceProfiler,
) -> tuple[Callable[[], pl.Series | None], Callable[[], pl.Series | None]]:
    # Create a test function to apply
    def test_function(series_chunk: pl.Series) -> pl.Series:
        # Simulate some computation
        return series_chunk * 1.1

    column = next(
        (name for name, dtype in df.schema.items() if dtype.is_numeric()),
        None,
    )

    @profiler.profile(f"sequential_processing_{largest_table}")
    def sequential_processing() -> pl.Series | None:
        return test_function(df[column]) if column is not None else None

    @profiler.profile(f"parallel_processing_{largest_table}")
    def parallel_processing() -> pl.Series | None:
        if column is None:
            return None
        return ParallelProcessor().parallel_apply(df, test_function, column, n_cores=4)

    return sequential_processing, parallel_processing


def benchmark_parallel_processing(
    data_dict: dict[str, pl.DataFrame],
    profiler: PerformanceProfiler,
) -> dict[str, Any]:
    """Benchmark parallel processing capabilities.

    Args:
        data_dict: Dictionary of DataFrames
        profiler: PerformanceProfiler instance

    Returns:
        Dictionary with benchmark results

    """
    sys.stdout.write("Benchmarking parallel processing..." + "\n")

    # Find the largest table for benchmarking
    largest_table = (
        max(data_dict.items(), key=lambda x: len(x[1]))[0] if data_dict else None
    )

    if not largest_table:
        return {"status": "skipped", "reason": "No data available"}

    df = data_dict[largest_table]
    sys.stdout.write(
        f"  Using {largest_table} with {len(df)} rows for benchmarking" + "\n",
    )

    sequential_processing, parallel_processing = _profile_column_processing(
        df,
        largest_table,
        profiler,
    )

    try:
        sys.stdout.write("    Running sequential processing..." + "\n")
        sequential_result = sequential_processing()

        sys.stdout.write("    Running parallel processing..." + "\n")
        parallel_result = parallel_processing()

        if sequential_result is None or parallel_result is None:
            return {"status": "skipped", "reason": "No numeric columns"}
        if not sequential_result.equals(parallel_result):
            return {"status": "error", "reason": "Parallel result changed values"}
        return {
            "status": "success",
            "table": largest_table,
            "rows_processed": len(df),
            "sequential_result_shape": sequential_result.shape
            if sequential_result is not None
            else None,
            "parallel_result_shape": parallel_result.shape
            if parallel_result is not None
            else None,
        }
    except Exception as e:
        logger.exception("Could not complete benchmark parallel processing")
        sys.stdout.write(f"  Error in parallel processing benchmark: {e}" + "\n")
        return {"status": "error", "error": str(e)}


def test_caching_performance(
    data_dict: dict[str, pl.DataFrame],
    profiler: PerformanceProfiler,
) -> dict[str, Any]:
    """Test caching performance improvements.

    Args:
        data_dict: Dictionary of DataFrames
        profiler: PerformanceProfiler instance

    Returns:
        Dictionary with caching test results

    """
    sys.stdout.write("Testing caching performance..." + "\n")
    cache = CachingOptimizer()

    # Test caching with a sample operation
    @profiler.profile("cache_test_operation")
    def expensive_operation(data: pl.DataFrame) -> float | int:
        result = data.select(cs.numeric().sum())
        return (
            sum(value for value in result.row(0) if value is not None)
            if result.width
            else 0
        )

    # Find a reasonably sized table
    test_table = None
    for name, df in data_dict.items():
        if len(df) > CACHE_TEST_SAMPLE_ROWS:  # At least 100 rows
            test_table = name
            break

    if not test_table:
        return {
            "status": "skipped",
            "reason": "No suitable table found for caching test",
        }

    df = data_dict[test_table]
    sys.stdout.write(f"  Testing caching with {test_table}" + "\n")

    # Run operation without caching first
    sys.stdout.write("    Running operation without caching..." + "\n")
    result1 = expensive_operation(df)

    # Cache the result
    cache.set(f"expensive_op_{test_table}", result1)

    # Run operation with caching
    @profiler.profile("cached_operation")
    def cached_operation() -> float | int:
        cached_result = cache.get(f"expensive_op_{test_table}")
        if cached_result is not None:
            return cached_result
        result = expensive_operation(df)
        cache.set(f"expensive_op_{test_table}", result)
        return result

    sys.stdout.write("    Running operation with caching..." + "\n")
    result2 = cached_operation()

    # Get cache statistics
    cache_stats = cache.get_stats()

    return {
        "status": "success",
        "table": test_table,
        "original_result": result1,
        "cached_result": result2,
        "results_match": result1 == result2,
        "cache_stats": cache_stats,
    }


def generate_performance_report(
    profiler: PerformanceProfiler,
    _optimization_stats: dict[str, Any],
    output_dir: Path,
) -> None:
    """Generate a comprehensive performance report.

    Args:
        profiler: PerformanceProfiler instance
        optimization_stats: Data optimization statistics
        output_dir: Directory to save report

    """
    sys.stdout.write("Generating performance report..." + "\n")

    report = []
    report.append("# Performance Analysis Report")
    report.append(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Add profiling results
    report.append("## Performance Profiling Results")
    report.append("")

    metrics = profiler.get_report()
    if metrics:
        report.append(
            "| Operation | Calls | Avg Time (s) | Max Time (s) | Memory "
            "(MB) | Errors |",
        )
        report.append(
            "|-----------|-------|--------------|--------------|-------------|--------|",
        )

        for operation, data in metrics.items():
            report.append(
                f"| {operation} | {data['call_count']} | {data['avg_time']:.4f} | "
                f"{data['max_time']:.4f} | {data['avg_memory']:.2f} | "
                f"{data['errors']} |",
            )
    else:
        report.append("No profiling data available.")

    report.append("")

    # Add optimization statistics
    report.append("## Data Optimization Results")
    report.append("")

    if "optimization_stats.json" in [
        f.name for f in output_dir.iterdir() if f.is_file()
    ]:
        try:
            with Path(output_dir / "optimization_stats.json").open() as f:
                opt_stats = json.load(f)

            report.append(
                "| Table | Original (MB) | Optimized (MB) | Savings (MB) | "
                "Savings (%) | Time (s) |",
            )
            report.append(
                "|-------|---------------|----------------|--------------|-------------|----------|",
            )

            total_original = 0
            total_optimized = 0
            total_time = 0

            for stat in opt_stats:
                report.append(
                    f"| {stat['table']} | {stat['original_memory_mb']:.2f} | "
                    f"{stat['optimized_memory_mb']:.2f} | {stat['savings_mb']:.2f} | "
                    f"{stat['savings_percent']:.1f} | "
                    f"{stat['processing_time_seconds']:.3f} |",
                )
                total_original += stat["original_memory_mb"]
                total_optimized += stat["optimized_memory_mb"]
                total_time += stat["processing_time_seconds"]

            total_savings = total_original - total_optimized
            total_savings_percent = (
                (total_savings / total_original) * 100 if total_original > 0 else 0
            )

            report.append(
                f"| **TOTAL** | **{total_original:.2f}** | **"
                f"{total_optimized:.2f}** | **{total_savings:.2f}** | **"
                f"{total_savings_percent:.1f}** | **{total_time:.3f}** |",
            )
        except Exception as e:
            logger.exception("Could not complete generate performance report")
            report.append(f"Error loading optimization statistics: {e}")
    else:
        report.append("No optimization statistics available.")

    report.append("")

    # Save report
    report_file = output_dir / "performance_report.md"
    with Path(report_file).open("w") as f:
        f.write("\n".join(report))

    sys.stdout.write(f"Performance report saved to {report_file}" + "\n")


def main() -> int:
    """Profile and optimize performance."""
    parser = argparse.ArgumentParser(
        description="Profile and optimize microcosting analysis performance",
    )
    parser.add_argument("--data-dir", help="Path to prepared data directory")
    parser.add_argument(
        "--workbook", type=Path, help="Workbook used for the formula benchmark"
    )
    parser.add_argument("--output-dir", help="Path to output directory for results")
    parser.add_argument(
        "--optimize-data",
        action="store_true",
        help="Optimize DataFrames for memory usage",
    )
    parser.add_argument(
        "--benchmark-parallel",
        action="store_true",
        help="Benchmark parallel processing",
    )
    parser.add_argument(
        "--test-cache",
        action="store_true",
        help="Test caching performance",
    )

    args = parser.parse_args()

    sys.stdout.write("Performance Profiling and Optimization" + "\n")
    sys.stdout.write(str("=" * 50) + "\n")

    try:
        # Set up directories
        if args.data_dir:
            data_dir = Path(args.data_dir)
        else:
            data_dir = Path(__file__).resolve().parents[1] / "data" / "prepared"

        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = Path(__file__).resolve().parents[1] / "reports" / "performance"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create performance profiler
        profiler = PerformanceProfiler()

        # Profile data loading
        data_results = profile_data_loading(profiler, data_dir)
        if data_results["status"] != "success":
            sys.stdout.write(
                "Failed to load data, cannot continue with performance analysis" + "\n",
            )
            return 1

        data_dict = data_results["data"]

        # Profile calculation engine
        engine_results = profile_calculation_engine(profiler, data_dict, args.workbook)
        if engine_results["status"] != "success" or engine_results["error_count"]:
            return 1

        # Optimize DataFrames if requested
        if args.optimize_data:
            optimize_dataframes(data_dict, output_dir)

        # Benchmark parallel processing if requested
        parallel_results = None
        if args.benchmark_parallel:
            parallel_results = benchmark_parallel_processing(data_dict, profiler)
            sys.stdout.write(f"Parallel processing results: {parallel_results}" + "\n")
            if parallel_results["status"] != "success":
                return 1

        # Test caching performance if requested
        cache_results = None
        if args.test_cache:
            cache_results = test_caching_performance(data_dict, profiler)
            sys.stdout.write(f"Caching test results: {cache_results}" + "\n")
            if (
                cache_results["status"] != "success"
                or not cache_results["results_match"]
            ):
                return 1

        # Generate performance report
        generate_performance_report(profiler, {"optimization_stats": []}, output_dir)

        # Print performance summary
        sys.stdout.write("\nPerformance Profiling Summary:" + "\n")
        sys.stdout.write(str("-" * 30) + "\n")
        profiler.print_report()

        sys.stdout.write("\nPerformance analysis complete!" + "\n")
        sys.stdout.write(f"Results saved to {output_dir}" + "\n")

        # List generated files
        sys.stdout.write("\nGenerated files:" + "\n")
        for item in output_dir.iterdir():
            if item.is_file():
                sys.stdout.write(f"  {item.name}" + "\n")

    except Exception as e:
        logger.exception("Could not complete profile and optimize")
        sys.stdout.write(f"Error during performance profiling: {e}" + "\n")

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
