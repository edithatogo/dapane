# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify the native model calibration, taxonomy and bundled template contract."""

from decimal import Decimal

import polars as pl
from openpyxl import load_workbook

from dapane_genomics.model_tables import (
    model_template,
    standardize_models,
    write_model_template,
)


def test_standardization_preserves_costs_and_checks_cross_model_coverage():
    frame = pl.DataFrame(
        {
            "Test": ["Panel", "Panel", "WGS (T)", "WGS (T)"],
            "Category": ["Labor", "Equipment", "Labour", "Equipment"],
            "Sub-Category": [
                "Specimen Receipt",
                "Computation",
                "Specimen Receipt",
                "Processing",
            ],
            "cost": [
                Decimal("0.10"),
                Decimal("0.20"),
                Decimal("0.20"),
                Decimal("0.30"),
            ],
        }
    )
    normalized, report = standardize_models(frame)
    assert normalized["Category"].to_list() == [
        "Labour",
        "Equipment",
        "Labour",
        "Equipment",
    ]
    assert normalized["Sub-Category"].to_list()[1] == "Compute"
    assert normalized["cost"].equals(frame["cost"])
    assert report["category_overlap"] == {"common": 2, "total": 2}
    assert report["subcategory_overlap"] == {"common": 1, "total": 3}
    assert report["models"][1]["missing_categories"] == ["Consumables"]
    assert report["models"][1]["unknown_subcategories"] == {}


def test_templates_are_available_as_installed_resources():
    for name in ("base", "panel", "wes_p", "wes_t", "wgs", "wgs_t"):
        template = model_template(name)
        assert {"Test", "Category", "Sub-Category"} <= set(template["column_order"])


def test_editable_template_keeps_input_columns_and_leaves_cost_blank(tmp_path):
    target = tmp_path / "panel.xlsx"
    write_model_template("panel", target)
    with target.open("rb") as artifact:
        workbook = load_workbook(artifact, read_only=True, data_only=True)
        try:
            labels, first, *_ = workbook.active.values
        finally:
            workbook.close()
    assert list(labels) == model_template("panel")["column_order"]
    assert first[labels.index("Category")] == "Labour"
    assert first[labels.index("Unit Cost (AUD $/unit)")] is None
