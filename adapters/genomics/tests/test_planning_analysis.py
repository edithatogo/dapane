# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify the planning command's analytical handoffs against known results."""

import json
import sys
from hashlib import sha256

import polars as pl
import pytest

from dapane_genomics.reporting import main
from dapane_genomics.v15_pathways import WORKBOOK_SHA256
from genomics_microcosting import visualization
from genomics_microcosting.cost_driver_tables import summarise_cost_drivers


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


def test_cost_driver_check_retains_unpriced_rows_and_rejects_nonfinite_values():
    ingredients = pl.DataFrame(
        {
            "Test": ["Panel", "Panel"],
            "Category": ["Labour", "Equipment"],
            "Sub-Category": ["Bench", "Compute"],
            "cost": [5.0, None],
        }
    )
    contributions = summarise_cost_drivers(ingredients, cost_column="cost")
    assert contributions["Absolute_Value"].to_list() == [5, None]
    assert contributions["Unpriced_Rows"].to_list() == [0, 1]
    assert contributions["Percentage_of_Priced_Cost"].to_list() == [100, None]

    nonfinite = ingredients.with_columns(pl.col("cost").fill_null(float("inf")))
    with pytest.raises(ValueError, match="Nonfinite source costs"):
        summarise_cost_drivers(nonfinite, cost_column="cost")


def test_pathway_report_reuses_exact_valued_lines_and_rejects_double_counting(
    tmp_path,
    monkeypatch,
):
    one = {"numerator": "1", "denominator": "1"}
    pathway = {
        "request": {"policy": {"currency": "AUD"}},
        "expected_total": one,
        "stages": {
            "a": {
                "stage": "Preparation",
                "source": "Synthetic",
                "lines": ["x", "y"],
                "exact": one,
            }
        },
        "report": {
            "status": "complete",
            "policy": {"currency": "AUD"},
            "totals": {"exact": one},
            "lines": [
                {
                    "id": "x",
                    "components": ["labour"],
                    "exact": {"numerator": "1", "denominator": "3"},
                },
                {
                    "id": "y",
                    "components": ["labour"],
                    "exact": {"numerator": "2", "denominator": "3"},
                },
            ],
        },
    }
    receipt = tmp_path / "synthetic-pathway-receipt.json"
    result = {"source_sha256": WORKBOOK_SHA256, "pathways": {"synthetic": pathway}}
    receipt.write_text(json.dumps(result), encoding="utf-8")
    output = tmp_path / "report"
    monkeypatch.setattr(visualization, "plt", None)
    argv = ["genomics-report", "--pathways", str(receipt), "--output-dir", str(output)]
    monkeypatch.setattr(sys, "argv", argv)
    assert main() == 0
    report = json.loads((output / "pathway-report.json").read_bytes())
    assert report["receipt_sha256"] == sha256(receipt.read_bytes()).hexdigest()
    view = report["pathways"]["synthetic"]
    assert view["currency"] == "AUD"
    assert view["by_component"] == [{"component": "labour", "exact": one}]
    assert view["by_stage"] == [
        {"stage": "Preparation", "source": "Synthetic", "exact": one}
    ]

    rejected = tmp_path / "rejected"
    monkeypatch.setattr(sys, "argv", [*argv[:-1], str(rejected)])
    pathway["request"]["policy"]["currency"] = "USD"
    receipt.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(SystemExit) as failure:
        main()
    assert failure.value.code == 2
    assert not rejected.exists()
    pathway["request"]["policy"]["currency"] = "AUD"
    pathway["stages"]["b"] = pathway["stages"]["a"]
    receipt.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(SystemExit) as failure:
        main()
    assert failure.value.code == 2
    assert not rejected.exists()
