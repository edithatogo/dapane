# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Connect the installed legacy analyses to declared inputs for a single assay."""

from __future__ import annotations

import math
from hashlib import sha256
from pathlib import Path
from typing import Annotated

import numpy as np
import polars as pl
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from genomics_microcosting.benchmarking_analysis import BenchmarkingAnalyzer
from genomics_microcosting.break_even_analysis import BreakEvenAnalyzer
from genomics_microcosting.budget_impact_analysis import BudgetImpactAnalyzer
from genomics_microcosting.cost_driver_tables import summarise_cost_drivers
from genomics_microcosting.cost_effectiveness_analysis import CostEffectivenessAnalyzer
from genomics_microcosting.data_manager import DataManager
from genomics_microcosting.dsa_analysis import DSAAnalyzer
from genomics_microcosting.psa_analysis import PSAAnalyzer
from genomics_microcosting.voi_analysis import VOIAnalyzer

Amount = Annotated[FiniteFloat, Field(ge=0)]
PositiveAmount = Annotated[FiniteFloat, Field(gt=0)]


class PlanningInputs(BaseModel):
    """Source identity, independent simulated costs and declared planning assumptions."""

    model_config = ConfigDict(extra="forbid", strict=True)

    assay: str = Field(min_length=1)
    cost_table: Path
    cost_column: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    price_year: int = Field(ge=1900, le=9999)
    low_cost: Amount
    high_cost: Amount
    cost_draws: list[Amount] = Field(min_length=2, max_length=100_000)
    volumes: list[Annotated[int, Field(gt=0)]] = Field(min_length=1, max_length=200)
    fixed_cost: Amount
    price_per_test: PositiveAmount
    reference_cost: PositiveAmount
    reference_source: str = Field(min_length=1)
    diagnostic_yield: Annotated[FiniteFloat, Field(gt=0, le=1)]


def planning_analysis(request: Path) -> dict[str, object]:
    """Read the declared component table and return a source-linked analysis report.

    The table must contain component rows for one test per assay and omit
    subtotals. Amounts and draws use the declared currency and price year.
    The legacy cost-only VOI approximation describes simulated cost variation.
    """
    encoded = request.read_bytes()
    inputs = PlanningInputs.model_validate_json(encoded)
    source = request.parent / inputs.cost_table
    source_bytes = source.read_bytes()
    components = pl.read_parquet(source_bytes).filter(pl.col("Test") == inputs.assay)
    costs = components[inputs.cost_column].cast(pl.Float64)
    if costs.is_empty() or costs.null_count() or (costs < 0).any():
        raise ValueError("The selected assay requires fully priced component rows")
    drivers = summarise_cost_drivers(components, cost_column=inputs.cost_column)
    baseline = float(drivers["Absolute_Value"].sum())
    if (
        not math.isfinite(baseline)
        or not 0 < baseline
        or not (inputs.low_cost <= baseline <= inputs.high_cost)
    ):
        raise ValueError("The supplied bounds must bracket the positive baseline cost")

    draws = np.asarray(inputs.cost_draws, dtype=np.float64)
    if not np.isfinite(draws.mean()) or draws.mean() <= 0:
        raise ValueError("Simulation draws require a positive finite mean cost")

    data = DataManager(request.parent, create_directories=False)
    break_even = BreakEvenAnalyzer(data).calculate_break_even_volume(
        inputs.fixed_cost,
        inputs.price_per_test,
        baseline,
    )
    benchmark = BenchmarkingAnalyzer(data).compare_against_benchmarks(
        {inputs.assay: {"cost_per_test": baseline}},
        {
            inputs.assay: {
                "cost_per_test": inputs.reference_cost,
                "source": inputs.reference_source,
            },
        },
    )
    return {
        "report_version": 1,
        "assay": inputs.assay,
        "currency": inputs.currency,
        "price_year": inputs.price_year,
        "request_sha256": sha256(encoded).hexdigest(),
        "component_table_sha256": sha256(source_bytes).hexdigest(),
        "cost_drivers": drivers.to_dicts(),
        "dsa": DSAAnalyzer(data).perform_one_way_sensitivity(
            baseline,
            inputs.low_cost,
            inputs.high_cost,
            "Variable cost per test",
        ),
        "psa": {
            "draws": len(draws),
            "percentiles": PSAAnalyzer(data).calculate_confidence_intervals(draws),
        },
        "voi": {
            "method": "legacy cost-only approximation",
            **VOIAnalyzer(data).calculate_evpi(draws),
        },
        "budget_impact": BudgetImpactAnalyzer(data)
        .perform_volume_sensitivity_analysis(
            base_volume=inputs.volumes[0],
            volume_range=inputs.volumes,
            cost_per_test=baseline,
        )
        .to_dicts(),
        "break_even_volume": break_even if math.isfinite(break_even) else None,
        "benchmark": benchmark.filter(pl.col("Metric") == "Cost per Test").to_dicts(),
        "cost_per_diagnosis": CostEffectivenessAnalyzer(
            data,
        ).calculate_cost_per_diagnostic_yield(baseline, inputs.diagnostic_yield),
    }
