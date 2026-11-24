# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify the native model calibration, taxonomy and bundled template contract."""

import io
from decimal import Decimal

import polars as pl
from openpyxl import load_workbook

from dapane_genomics.model_tables import (
    LabProfile,
    model_template,
    standardize_models,
    write_model_template,
)
from genomics_microcosting.web import create_app


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


def test_lab_profile_extends_audit_and_local_template_download(tmp_path):
    profile = LabProfile(
        lab_name="Example lab", custom_categories={"Consumables": ["Local shipping"]}
    )
    source = pl.DataFrame(
        {
            "Test": ["Panel"],
            "Category": ["Consumables"],
            "Sub-Category": ["Local shipping"],
        }
    )
    _, plain_audit = standardize_models(source)
    _, custom_audit = standardize_models(source, profile)
    assert plain_audit["models"][0]["unknown_subcategories"] == {
        "Consumables": ["Local shipping"]
    }
    assert custom_audit["models"][0]["unknown_subcategories"] == {}

    client = create_app(tmp_path).test_client()
    assert b"Optional lab profile" in client.get("/models").data
    response = client.post(
        "/models/template",
        data={
            "model": "panel",
            "format": "xlsx",
            "profile_file": (
                io.BytesIO(profile.model_dump_json().encode()),
                "profile.json",
            ),
        },
    )
    assert response.status_code == 200
    assert "attachment; filename=panel.xlsx" in response.headers["Content-Disposition"]
    workbook = load_workbook(io.BytesIO(response.data), data_only=True, read_only=True)
    try:
        assert any("Local shipping" in row for row in workbook.active.values)
    finally:
        workbook.close()

    response = client.post(
        "/models/template",
        data={
            "model": "panel",
            "format": "xlsx",
            "profile": '{"lab_name": "Example", "custom_categories": {"Local": ["@directive"]}}',
        },
    )
    assert response.status_code == 400
