# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Run bounded, reproducible diagnostics without invoking external commands."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from io import BytesIO
from time import perf_counter_ns
from typing import TYPE_CHECKING, Literal, TypedDict

import numpy as np
import polars as pl

from genomics_microcosting.cost_driver_tables import summarise_cost_drivers
from genomics_microcosting.dsa_analysis import DSAAnalyzer
from genomics_microcosting.psa_analysis import DistributionSpec, PSAAnalyzer
from genomics_microcosting.voi_analysis import VOIAnalyzer

from .model_tables import model_template_bytes

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from genomics_microcosting.data_manager import DataManager

Analysis = Literal["cost_driver", "dsa", "psa", "voi"]
Suite = Literal["integration", "end_to_end", "performance"]
ANALYSES: tuple[Analysis, ...] = ("cost_driver", "dsa", "psa", "voi")


class _Check(TypedDict):
    analysis_module: Analysis
    passed: bool
    elapsed_ns: int


def synthetic_psa(data: DataManager, iterations: int) -> NDArray[np.float64]:
    """Exercise both the seeded sampler and the historical PSA cost model."""
    parameters: dict[str, DistributionSpec] = {
        "labour_cost": {
            "distribution": "normal",
            "parameters": {"mean": 20.0, "std": 1.0},
        },
        "equipment_cost": {
            "distribution": "uniform",
            "parameters": {"low": 9.0, "high": 11.0},
        },
    }
    analyzer = PSAAnalyzer(data, rng=np.random.default_rng(314))
    return analyzer.calculate_cost_outcomes(
        analyzer.perform_monte_carlo_simulation(parameters, iterations)
    )


def diagnose(
    data: DataManager, suite: Suite, selected: list[Analysis]
) -> dict[str, object]:
    """Use independent checks for integration, pipeline and bounded load cases."""
    end_to_end = suite == "end_to_end"
    size = 512 if suite == "performance" else 4

    def cost_driver() -> bool:
        inputs = pl.DataFrame(
            {
                "Test": ["Synthetic assay"] * size,
                "Category": ["Labour"] * size,
                "Sub-Category": ["Bench time"] * size,
                "cost": [8] * size,
            }
        )
        if end_to_end:
            template = model_template_bytes("panel", "csv")
            if pl.read_csv(BytesIO(template)).is_empty():
                return False
            inputs = pl.read_csv(BytesIO(inputs.write_csv().encode()))
        result = summarise_cost_drivers(inputs, cost_column="cost")
        return (
            result["Absolute_Value"].sum() == 8 * size
            and result["Source_Rows"].sum() == size
        )

    def dsa() -> bool:
        result = DSAAnalyzer(data).perform_one_way_sensitivity(20, 16, 25, "Labour")
        return result["low_change_pct"] == -20 and result["high_change_pct"] == 25

    def psa() -> bool:
        draws = synthetic_psa(data, size)
        return (
            len(draws) == size
            and bool(np.isfinite(draws).all())
            and 526 < float(draws.mean()) < 534
        )

    def voi() -> bool:
        analyzer = VOIAnalyzer(data)
        fixed_costs = np.array([20.0, 28.0])
        if analyzer.calculate_evpi(fixed_costs)["evpi"] != 2.0:
            return False
        if end_to_end:
            draws = synthetic_psa(data, size)
            return 0 < float(analyzer.calculate_evpi(draws)["evpi"]) < 2
        return True

    checks: Mapping[Analysis, Callable[[], bool]] = {
        "cost_driver": cost_driver,
        "dsa": dsa,
        "psa": psa,
        "voi": voi,
    }
    outcomes: list[_Check] = []
    for analysis in selected:
        start = perf_counter_ns()
        passed = checks[analysis]()
        outcomes.append(
            {
                "analysis_module": analysis,
                "passed": passed,
                "elapsed_ns": max(1, perf_counter_ns() - start),
            }
        )
    return {
        "test_type": suite,
        "analysis_modules": selected,
        "checks": outcomes,
        "passed": all(outcome["passed"] for outcome in outcomes),
    }
