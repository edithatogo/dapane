# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Exercise source-distribution commands against synthetic reference values."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest
from openpyxl import Workbook

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run_command(cwd, script, *args):
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPTS / f"{script}.py"), *map(str, args)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout


@pytest.mark.parametrize(
    ("name", "headers", "width", "values", "expected"),
    [
        (
            "replicate_consumable_costs",
            2,
            17,
            {0: "Synthetic stage", 4: "5", 5: "2", 6: "3"},
            {"Calculated Other": 10, "Calculated 50x": 30},
        ),
        (
            "replicate_equipment_costs",
            3,
            34,
            {0: "Synthetic instrument", 4: "5", 7: "1,000"},
            {
                "Calculated Annualised cost": 200,
                "Calculated Present value": 1000 * 0.0452 / (1 - 1.0452**-5),
            },
        ),
        (
            "replicate_labour_costs",
            1,
            30,
            {
                0: "Synthetic jurisdiction",
                9: "0",
                10: "40",
                11: "80%",
                **dict.fromkeys(range(12, 20), "0"),
                21: "1000",
                23: "1200",
            },
            {
                "Calculated Base Salary Mid-point": 1100,
                "Calculated Base Salary + Costs LL": 2500,
                "Calculated Base Salary + Costs (hourly) LL": 2500 / 52 / 40,
            },
        ),
    ],
)
def test_replication_commands(tmp_path, name, headers, width, values, expected):
    source = tmp_path / "synthetic.csv"
    calculated = tmp_path / "calculated.csv"
    with source.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows([["skipped"] * width] * headers)
        writer.writerow([f"column_{i}" for i in range(width)])
        writer.writerow([values.get(i) for i in range(width)])
    run_command(tmp_path, name, "--input", source, "--output", calculated)
    rows = pl.read_csv(calculated)
    assert rows.height == 1
    for column, value in expected.items():
        assert rows[column][0] == pytest.approx(value)


def test_revision_demo_restores_first_revision(tmp_path):
    result = run_command(tmp_path, "demonstrate_excel_version_control")
    assert "Same checksum: False" in result
    assert "Integrity check passed: True" in result
    assert "Demonstration completed successfully!" in result


def test_publication_command_exports_data_and_metadata(tmp_path):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    output = tmp_path / "output"
    frame = pl.DataFrame({"component": ["Synthetic", None], "cost": [5.0, 2.0]})
    frame.write_parquet(prepared / "example.parquet")
    run_command(
        tmp_path,
        "prepare_publication_tables",
        "--data-dir",
        prepared,
        "--output-dir",
        output,
    )
    assert pl.read_csv(output / "example.csv").equals(frame)
    metadata = json.loads((output / "example_metadata.json").read_bytes())
    assert metadata["row_count"] == 2
    assert metadata["columns"][0]["null_count"] == 1
    assert metadata["columns"][0]["sample_values"] == ["Synthetic"]


def test_compute_storage_export_uses_source_formula_cells(tmp_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "BI - Comp+Stor Costs - VCGS"
    sheet["AB2"] = "Last header"
    sheet["D3"] = 2
    sheet["E3"] = 6
    sheet["G3"] = "=D3*E3"
    sheet["J8"] = 100
    sheet["M8"] = 10
    sheet["P8"] = "=J8/M8"
    sheet["D15"] = 20
    sheet["E15"] = 500
    sheet["H15"] = "=E15/D15"
    sheet["A20"] = "Last source row"
    path = tmp_path / "compute-source.xlsx"
    workbook.save(path)
    cached = [list(row) for row in sheet.values]
    cached[2][6] = 12
    cached[7][15] = 10
    cached[14][7] = 25
    source_csv = tmp_path / "reference.csv"
    with source_csv.open("w", newline="", encoding="utf-8") as output:
        csv.writer(output).writerows(cached)
    workbook.close()
    calculated = tmp_path / "replicated"
    run_command(
        tmp_path,
        "replicate_bi_comp_stor_costs",
        "--workbook",
        path,
        "--output-dir",
        calculated,
    )
    result = run_command(
        tmp_path,
        "validate_bi_comp_stor_costs",
        "--input",
        source_csv,
        "--replicated-dir",
        calculated,
    )
    assert "0 mismatches" in result
    assert pl.read_csv(calculated / "server_costs.csv")["Total Cores"][0] == 12
    assert (
        pl.read_csv(calculated / "equipment_costs.csv")[
            "Unit Cost ($/sample) - Initial"
        ][0]
        == 10
    )
    assert pl.read_csv(calculated / "storage_costs.csv")["Cost/GB"][0] == 25


def test_quality_history_reports_a_value_changed_after_model_export(tmp_path):
    source = tmp_path / "synthetic.csv"
    rows = {
        "Labour": ["Specimen Collection", "Specimen Receipt", "DNA Extraction"],
        "Equipment": ["DNA Extraction", "Library Preparation", "Sequencing"],
        "Consumables": ["DNA Extraction", "Sequencing"],
    }
    categories = [
        (category if index == 0 else None, item)
        for category, items in rows.items()
        for index, item in enumerate(items)
    ]
    with source.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "Test",
                "Category",
                "Sub-Category",
                "Step",
                "Unit Cost (AUD $/unit)",
                "Units",
            ]
        )
        for index, (category, item) in enumerate(categories):
            writer.writerow(
                [
                    "Panel" if index == 0 else None,
                    category,
                    item,
                    "Synthetic item",
                    3,
                    2,
                ]
            )
    data = tmp_path / "enhanced"
    report = tmp_path / "enhanced.md"
    run_command(
        tmp_path,
        "phase3_data_enhancement",
        "--source",
        source,
        "--output-dir",
        data,
        "--report",
        report,
    )
    history = tmp_path / "history.json"
    options = ("--data-dir", data, "--model", "Panel", "--history", history)
    run_command(tmp_path, "validation_pipeline", *options)
    model = data / "Panel_enhanced.csv"
    calculated = pl.read_csv(model)
    assert calculated["Total Cost (AUD)"].to_list() == [6.0] * len(categories)
    assert calculated["Source_Row"].to_list() == list(range(2, 2 + len(categories)))
    calculated.with_columns(
        pl.when(pl.col("Source_Row") == 2)
        .then(7.0)
        .otherwise(pl.col("Total Cost (AUD)"))
        .alias("Total Cost (AUD)")
    ).write_csv(model)
    with pytest.raises(subprocess.CalledProcessError) as raised:
        run_command(tmp_path, "validation_pipeline", *options)
    assert raised.value.returncode == 1
    receipts = json.loads(history.read_bytes())
    first, second = (receipt["models"][0] for receipt in receipts)
    assert first["valid"] is True
    assert first["data_quality_score"] == 1
    assert second["valid"] is False
    assert second["cost_issues"] == 1
    assert second["data_quality_score"] == 7 / 8
