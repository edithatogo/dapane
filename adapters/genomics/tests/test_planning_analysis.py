# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify the planning command's analytical handoffs against known results."""

import json
import sys
from hashlib import sha256

import polars as pl
import pytest

from dapane_genomics.reporting import main


def test_planning_report_joins_the_declared_source_analyses(tmp_path, monkeypatch):
    table = tmp_path / "components.parquet"
    pl.DataFrame(
        {
            "Test": ["Panel", "Panel", "Other"],
            "Category": ["Labour", "Equipment", "Labour"],
            "Sub-Category": ["Bench", "Compute", "Bench"],
            "cost": [8, 12, 1000],
        }
    ).write_parquet(table)
    request = tmp_path / "request.json"
    inputs = {
        "assay": "Panel",
        "cost_table": table.name,
        "cost_column": "cost",
        "currency": "AUD",
        "price_year": 2026,
        "low_cost": 16,
        "high_cost": 25,
        "cost_draws": [20, 28],
        "volumes": [10, 20],
        "fixed_cost": 120,
        "price_per_test": 26,
        "reference_cost": 25,
        "reference_source": "synthetic comparator",
        "diagnostic_yield": 0.25,
    }
    request.write_text(json.dumps(inputs), encoding="utf-8")
    output = tmp_path / "report"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "genomics-report",
            "--planning",
            str(request),
            "--output-dir",
            str(output),
        ],
    )
    assert main() == 0
    path = output / "planning-analysis.json"
    receipt = json.loads(path.read_text())
    assert receipt["component_table_sha256"] == sha256(table.read_bytes()).hexdigest()
    assert receipt["request_sha256"] == sha256(request.read_bytes()).hexdigest()
    assert [driver["Absolute_Value"] for driver in receipt["cost_drivers"]] == [12, 8]
    assert receipt["dsa"]["baseline"] == 20
    assert receipt["dsa"]["low_change_pct"] == -20
    assert receipt["dsa"]["high_change_pct"] == 25
    assert receipt["psa"]["percentiles"]["50%"] == 24
    assert receipt["voi"]["evpi"] == 2
    assert [volume["Total_Cost"] for volume in receipt["budget_impact"]] == [200, 400]
    assert receipt["break_even_volume"] == 20
    assert receipt["benchmark"][0]["Ratio"] == 0.8
    assert receipt["benchmark"][0]["Source"] == "synthetic comparator"
    assert receipt["cost_per_diagnosis"] == 80

    request.write_text(json.dumps({**inputs, "low_cost": 21}), encoding="utf-8")
    with pytest.raises(SystemExit) as invalid:
        main()
    assert invalid.value.code == 2
    assert json.loads(path.read_text()) == receipt
