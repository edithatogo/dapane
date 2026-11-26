# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify the native model calibration, taxonomy and bundled template contract."""

import io
import json
import sys
from decimal import Decimal

import polars as pl
import pytest
from openpyxl import load_workbook
from pydantic import ValidationError

from dapane_genomics.model_tables import (
    LabProfile,
    load_lab_profile,
    main,
    model_template,
    model_template_bytes,
    standardize_models,
    write_model_template,
)
from genomics_microcosting.web import create_app


@pytest.mark.parametrize("multiplier", ["0", "1/0", "NaN", "1e129", "invalid"])
def test_lab_profile_requires_a_positive_exact_multiplier(multiplier):
    with pytest.raises(ValidationError, match="positive exact number"):
        LabProfile.model_validate(
            {"cost_adjustments": {"labor_multiplier": multiplier}}
        )


@pytest.mark.parametrize(
    ("categories", "error"),
    [
        ({"Other": []}, "requires 1 to 25"),
        ({"Other": ["Repeat", "Repeat "]}, "duplicate subcategories"),
    ],
)
def test_lab_profile_requires_distinct_subcategories(categories, error):
    with pytest.raises(ValidationError, match=error):
        LabProfile(custom_categories=categories)


def test_profile_formats_and_template_command(tmp_path, monkeypatch):
    json_profile = tmp_path / "lab.json"
    json_profile.write_text('{"lab_name":" Synthetic lab "}', encoding="utf-8")
    yaml_profile = tmp_path / "lab.yml"
    yaml_profile.write_text(
        "user_customizations:\n  lab_name: Synthetic lab\n", encoding="utf-8"
    )
    assert load_lab_profile(json_profile) == load_lab_profile(yaml_profile)
    destination = tmp_path / "template.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "genomics-model",
            "template",
            "panel",
            str(destination),
            "--profile",
            str(json_profile),
        ],
    )
    assert main() == 0
    assert (
        json.loads(destination.read_bytes())["lab_profile"]["lab_name"]
        == "Synthetic lab"
    )
    yaml_profile.write_text("user_customizations: []\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="valid dictionary"):
        load_lab_profile(yaml_profile)
    yaml_profile.write_text("[]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_lab_profile(yaml_profile)
    yaml_profile.write_text(
        "custom_categories:\n"
        "- {name: Local, subcategories: [One]}\n"
        "- {name: Local, subcategories: [Two]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="repeats a custom category"):
        load_lab_profile(yaml_profile)
    with pytest.raises(ValueError, match="Unknown genomics model"):
        model_template("unknown")
    with pytest.raises(ValueError, match="support JSON, CSV and Excel"):
        model_template_bytes("panel", "doc")


def test_model_standardization_requires_complete_typed_inputs(tmp_path, monkeypatch):
    complete = pl.DataFrame(
        {"Test": ["Panel"], "Category": ["Labour"], "Sub-Category": ["Sequencing"]}
    )
    with pytest.raises(ValueError, match="require string Test"):
        standardize_models(complete.with_columns(pl.lit(1).alias("Test")))
    with pytest.raises(ValueError, match="identifiers must be present"):
        standardize_models(complete.with_columns(pl.lit(None, pl.String).alias("Test")))
    _, audit = standardize_models(complete.clear())
    assert audit["category_overlap"] == {"common": 0, "total": 0}
    source = tmp_path / "models.parquet"
    complete.write_parquet(source)
    output = tmp_path / "result"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "genomics-model",
            "standardize",
            str(source),
            str(output),
            "--cost-column",
            "unknown",
        ],
    )
    with pytest.raises(ValueError, match="requires rows and a numeric cost"):
        main()
    assert not output.exists()


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


def test_distribution_audit_accounts_for_every_input_row(tmp_path, monkeypatch):
    frame = pl.DataFrame(
        {
            "Test": ["Panel"] * 4 + ["WGS (T)"] * 4,
            "Category": ["Labour"] * 8,
            "Sub-Category": ["Specimen Receipt"] * 8,
            "cost": [2.0, 8.0, None, float("inf"), 4.0, 16.0, -1.0, 0.0],
        }
    )
    source = tmp_path / "models.parquet"
    frame.write_parquet(source)
    output = tmp_path / "audit"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "genomics-model",
            "standardize",
            str(source),
            str(output),
            "--cost-column",
            "cost",
        ],
    )
    assert main() == 0
    audit = json.loads((output / "taxonomy-audit.json").read_text())[
        "cost_distribution"
    ]
    assert audit["rows"] == 8
    assert audit["valid_rows"] == 5
    assert audit["valid_percentage"] == 62.5
    assert not audit["above_99_5_percent"]
    panel, wgs = audit["models"]
    assert (panel["median"], panel["missing"], panel["nonfinite"]) == (5, 1, 1)
    assert (wgs["quartile_1"], wgs["median"], wgs["quartile_3"], wgs["negative"]) == (
        2,
        4,
        10,
        1,
    )
    assert pl.read_parquet(output / "standardized.parquet").equals(frame)


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
