# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify cost-driver workload measurement and strict comparison."""

import pytest

from dapane_genomics import benchmark
from dapane_genomics.benchmark import compare, measure


def test_benchmark_measures_the_workload_and_detects_a_regression():
    result = measure((6, 5), repeats=3)
    assert [row.rows for row in result.measurements] == [5, 6]
    assert compare(result, result) == []
    first, second = result.measurements
    changed = result.model_copy(
        update={
            "measurements": (
                first.model_copy(update={"median_ns": first.median_ns * 2}),
                second,
            )
        }
    )
    assert compare(result, changed) == [5]
    with pytest.raises(ValueError, match="platform"):
        compare(result, changed.model_copy(update={"platform": "other"}))


def test_benchmark_rejects_unsupported_workloads_and_failed_reference(monkeypatch):
    with pytest.raises(ValueError, match="distinct positive integers"):
        measure((10, 10))
    with pytest.raises(ValueError, match="three samples"):
        measure((10,), repeats=2)
    reference = measure((10,), repeats=3)
    with pytest.raises(ValueError, match="timing ratio"):
        compare(reference, reference, time_ratio=0.9)
    with pytest.raises(ValueError, match="sizes must match"):
        compare(reference, measure((20,), repeats=3))
    measured = benchmark.summarise_cost_drivers

    def remove_contributions(*args, **kwargs):
        return measured(*args, **kwargs).clear()

    monkeypatch.setattr(benchmark, "summarise_cost_drivers", remove_contributions)
    with pytest.raises(RuntimeError, match="differs from its reference"):
        measure((10,), repeats=3)
