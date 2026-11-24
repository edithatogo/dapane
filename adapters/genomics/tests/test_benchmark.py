# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify cost-driver workload measurement and strict comparison."""

import pytest

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
