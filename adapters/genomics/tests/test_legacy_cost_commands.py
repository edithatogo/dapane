# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Exercise source-distribution commands against synthetic reference values."""

import csv
import json
import os
import runpy
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock

import polars as pl
import pytest
from flask import Flask
from openpyxl import Workbook

from dapane_genomics import legacy_models
from dapane_genomics.legacy_models import (
    MODEL_KEYS,
    model_rows,
    read_model_source,
    verify_model,
)
from dapane_genomics.legacy_performance import (
    compare_baselines,
    load_baselines,
    save_baselines,
)
from dapane_genomics.legacy_performance import (
    main as measure_performance,
)
from dapane_genomics.legacy_workbooks import (
    compare_sheet,
    evaluate_sheet,
    ground_truth,
    replicate_cost_rows,
)
from genomics_microcosting import data_management

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


def test_enhanced_reporting_source_alias_emits_the_installed_formats(tmp_path):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    destination = tmp_path / "reports"
    pl.DataFrame({"component": ["Synthetic cost"], "price": [10]}).write_parquet(
        prepared / "synthetic.parquet"
    )
    run_command(
        tmp_path,
        "enhanced_reporting",
        "--data-dir",
        prepared,
        "--output-dir",
        destination,
    )
    report = destination / "enhanced_microcosting_report"
    assert report.with_suffix(".html").is_file()
    assert report.with_suffix(".md").is_file()
    assert "synthetic" in report.with_suffix(".json").read_text(encoding="utf-8")


def test_manage_data_restores_version_and_exports_both_formats(tmp_path):
    original = pl.DataFrame({"Assay": ["Synthetic panel"], "Cost": [10.5]})
    source = tmp_path / "costs.parquet"
    original.write_parquet(source)
    options = ("--data-dir", tmp_path / "data", "--metadata-dir", tmp_path / "metadata")
    run_command(
        tmp_path, "manage_data", *options, "--action", "register", "--file", source
    )
    run_command(
        tmp_path, "manage_data", *options, "--action", "verify", "--dataset", "costs"
    )
    for file_format, read in (("csv", pl.read_csv), ("parquet", pl.read_parquet)):
        target = tmp_path / f"restored.{file_format}"
        run_command(
            tmp_path,
            "manage_data",
            *options,
            "--action",
            "load",
            "--dataset",
            "costs",
            "--output",
            target,
        )
        assert read(target).equals(original)


def test_same_second_dataset_versions_reopen_with_distinct_values(
    tmp_path, monkeypatch
):
    clock = Mock(wraps=datetime)
    clock.now.return_value = datetime(2026, 11, 26, tzinfo=UTC)
    monkeypatch.setattr(data_management, "datetime", clock)
    manager = data_management.DataManager(tmp_path)
    versions = []
    for folder, amount in (("first", 4), ("second", 7)):
        source = tmp_path / folder / "costs.parquet"
        source.parent.mkdir()
        pl.DataFrame({"amount": [amount]}).write_parquet(source)
        versions.append(manager.register_dataset(source))

    assert versions[0] != versions[1]
    reopened = data_management.DataManager(tmp_path)
    for version, amount in zip(versions, (4, 7), strict=True):
        assert reopened.verify_integrity("costs", version)
        assert reopened.load_dataset("costs", version)["amount"].item() == amount
    assert reopened.load_dataset("costs")["amount"].item() == 7


def test_governed_dataset_registration_rejects_a_changed_source(tmp_path):
    sources = [tmp_path / edition / "costs.parquet" for edition in ("first", "second")]
    managers = [data_management.DataManager(tmp_path) for _ in sources]
    labels = {"owner": "synthetic laboratory", "access": "restricted"}
    for path, amount in zip(sources, (4, 7), strict=True):
        path.parent.mkdir()
        pl.DataFrame({"amount": [amount]}).write_parquet(path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        writes = [
            pool.submit(manager.register_dataset, path, labels)
            for manager, path in zip(managers, sources, strict=True)
        ]
        ids = [write.result(timeout=15) for write in writes]

    reader = data_management.DataManager(tmp_path)
    assert {
        version.version_id for version in reader.get_dataset_versions("costs")
    } == set(ids)
    assert all(
        version.metadata["access"] == "restricted"
        for version in reader.get_dataset_versions("costs")
    )
    if os.name == "posix":
        assert (tmp_path / "metadata" / "datasets.json").stat().st_mode & 0o777 == 0o600
    assert reader.load_dataset("costs", ids[0])["amount"].item() == 4
    pl.DataFrame({"amount": [99]}).write_parquet(sources[0])
    with pytest.raises(ValueError, match="registered checksum"):
        reader.load_dataset("costs", ids[0])
    assert reader.load_dataset("costs", ids[1])["amount"].item() == 7


def test_legacy_web_launcher_loads_consumer_prepared_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GENOMICS_WEB_ACCESS_FILE", raising=False)
    prepared = tmp_path / "data" / "prepared"
    prepared.mkdir(parents=True)
    pl.DataFrame({"Cost": [10]}).write_parquet(prepared / "synthetic.parquet")

    def run(app, **options):
        assert options == {
            "host": "127.0.0.1",
            "port": 5000,
            "debug": False,
            "use_debugger": False,
            "use_reloader": False,
        }
        with app.test_client() as client:
            assert client.get("/health").status_code == 200
            assert client.get("/api/tables").json == ["synthetic"]

    monkeypatch.setattr(Flask, "run", run)
    with pytest.raises(SystemExit) as result:
        runpy.run_path(str(SCRIPTS / "run_web.py"), run_name="__main__")
    assert result.value.code == 0


@pytest.mark.parametrize(
    ("script", "scenario"),
    [
        ("run_scenario_analysis", "inflation_5"),
        ("run_advanced_scenario_analysis", "advanced_inflation"),
    ],
)
def test_scenario_command_exports_the_expected_price_increase(
    tmp_path, script, scenario
):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    pl.DataFrame({"unit_cost_aud_per_unit": [100.0, 200.0]}).write_parquet(
        prepared / "detailed_table.parquet"
    )
    destination = tmp_path / "scenarios"
    run_command(
        tmp_path,
        script,
        "--data-dir",
        prepared,
        "--output-dir",
        destination,
        "--scenario",
        scenario,
        "--compare",
        scenario,
    )
    if script == "run_scenario_analysis":
        output = pl.read_csv(destination / "scenario_comparison.csv")
        assert output["Base Case"][0] == pytest.approx(300)
        assert output[scenario][0] == pytest.approx(315)
    else:
        path = (
            destination
            / "detailed_comparisons/detailed_comparison_unit_cost_aud_per_unit"
        )
        output = pl.read_csv(path.with_suffix(".csv"))
        assert output["Base Case"][0] == pytest.approx(150)
        assert output[scenario][0] == pytest.approx(157.5)
        receipt = json.loads(path.with_suffix(".json").read_bytes())
        assert receipt[scenario]["0"] == pytest.approx(157.5)


def test_process_sheet_validator_compares_cached_source_cells(tmp_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Process"
    sheet.append(["Stage", "Amount"])
    sheet.append(["Synthetic stage", 8])
    source = tmp_path / "process.xlsx"
    workbook.save(source)
    workbook.close()
    result = run_command(tmp_path, "validate_process_sheet", "--workbook", source)
    assert "Compared 2 process worksheet cells, 0 differences" in result


def test_consistency_report_retains_other_sheets_when_one_csv_disagrees(tmp_path):
    data = tmp_path / "data"
    prepared = data / "prepared"
    prepared.mkdir(parents=True)
    frame = pl.DataFrame({"cost": [5.5, 7.0]})
    for name in ("matched", "mismatched"):
        frame.write_parquet(prepared / f"{name}.parquet")
        frame.write_csv(prepared / f"{name}.csv")
    report = tmp_path / "consistency.md"
    options = ("--data-dir", data, "--output", report)
    run_command(tmp_path, "validate_data_consistency", *options)
    frame.with_columns(pl.lit("Unrecognized column").alias("extra")).write_csv(
        prepared / "mismatched.csv"
    )
    with pytest.raises(subprocess.CalledProcessError) as raised:
        run_command(tmp_path, "validate_data_consistency", *options)
    assert raised.value.returncode == 1
    output = report.read_text(encoding="utf-8")
    assert "### matched" in output
    assert "### mismatched" in output
    assert "CSV could not be read using the Parquet schema" in output


def test_visualization_command_writes_pngs_in_the_requested_directory(tmp_path):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    pl.DataFrame(
        {
            "Category": ["Synthetic labour", "Synthetic equipment"],
            "Unrelated quantity": [100, 200],
            "Unit Cost (AUD $/unit)": [5.0, 10.0],
        }
    ).write_parquet(prepared / "detailed_table.parquet")
    output = tmp_path / "plots"
    run_command(
        tmp_path, "visualize_costs", "--data-dir", prepared, "--output-dir", output
    )
    charts = sorted(output.glob("*.png"))
    assert len(charts) == 3
    assert (output / "cost_distribution_Unit Cost (AUD $_unit).png").is_file()
    assert all(chart.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for chart in charts)


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
    assert second["cost_issue_counts"] == {
        "missing_or_nonfinite_cost": 0,
        "outside_editable_bounds": 0,
        "extended_cost_disagrees": 1,
    }


def test_workbook_validation_keeps_source_cost_bases_and_rejects_changed_rows(tmp_path):
    source = tmp_path / "historical-source.csv"
    pl.DataFrame(
        {
            "Test": ["Panel", "Panel", "Panel"],
            "Category": ["Labour", "Equipment", "Equipment"],
            "Sub-Category": ["Sequencing"] * 3,
            "Step": ["Minutes of labour", "Annualized equipment", "Workflow total"],
            "Estimates Price (AUD $/unit) Estimate": [60.0, 24000.0, None],
            "Estimates Quantity of Use per Test Estimate": [2, 100, None],
            "Estimates Unit Cost (AUD $/unit) Estimate": [2.0, 24.0, 26.0],
        }
    ).write_csv(source)
    output = tmp_path / "enhanced"
    profile = tmp_path / "profile.json"
    profile.write_text('{"lab_name":"Synthetic Historical Lab"}', encoding="utf-8")
    run_command(
        tmp_path,
        "phase3_data_enhancement",
        "--source",
        source,
        "--output-dir",
        output,
        "--profile",
        profile,
    )
    history = tmp_path / "history.json"
    options = ("--data-dir", output, "--model", "Panel", "--history", history)
    workbook_options = (*options, "--workbook", source, "--profile", profile)
    run_command(tmp_path, "validation_pipeline", *workbook_options)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validation_pipeline", *options)
    receipts = json.loads(history.read_bytes())
    assert receipts[0]["workbook_sha256"] == sha256(source.read_bytes()).hexdigest()
    assert receipts[0]["profile_sha256"] == sha256(profile.read_bytes()).hexdigest()
    record = receipts[0]["models"][0]
    assert record["matching_rows"] == record["expected_rows"] == 3
    assert record["different_cells"] == 0
    assert receipts[1]["models"][0]["cost_issue_counts"] == {
        "missing_or_nonfinite_cost": 1,
        "outside_editable_bounds": 1,
        "extended_cost_disagrees": 2,
    }

    export = output / "Panel_enhanced.csv"
    tables = pl.read_csv(export)
    tables.with_columns(pl.col("Total Cost (AUD)") + 1).write_csv(export)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validation_pipeline", *workbook_options)
    tables.head(2).write_csv(export)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validation_pipeline", *workbook_options)
    export.unlink()
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validation_pipeline", *workbook_options)

    changed, incomplete, missing = json.loads(history.read_bytes())[2:]
    assert changed["models"][0]["different_cells"] == 3
    assert incomplete["models"][0]["schema_and_count_match"] is False
    assert missing["models"][0]["missing_file"] == export.name


def test_strict_quality_checks_five_complete_editable_models_at_workbook_size(tmp_path):
    rows = (
        ("Labour", "Specimen Collection"),
        ("Labour", "Specimen Receipt"),
        ("Labour", "DNA Extraction"),
        ("Equipment", "DNA Extraction"),
        ("Equipment", "Library Preparation"),
        ("Equipment", "Sequencing"),
        ("Consumables", "DNA Extraction"),
        ("Consumables", "Sequencing"),
    )
    counts = (214, 221, 250, 200, 206)
    source = tmp_path / "synthetic-validated-models.csv"
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
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
        for name, count in zip(MODEL_KEYS, counts, strict=True):
            for index in range(count):
                category, stage = rows[index % len(rows)]
                writer.writerow(
                    [name, category, stage, f"Synthetic item {index}", 3 + index % 4, 2]
                )
    exports = tmp_path / "enhanced"
    run_command(
        tmp_path, "phase3_data_enhancement", "--source", source, "--output-dir", exports
    )
    history = tmp_path / "quality.json"
    options = ("--data-dir", exports, "--history", history)
    run_command(tmp_path, "validation_pipeline", *options)
    models = json.loads(history.read_bytes())[0]["models"]
    assert [item["rows"] for item in models] == list(counts)
    assert all(item["valid"] and item["data_quality_score"] == 1 for item in models)
    path = exports / "WGS_P_enhanced.csv"
    frame = pl.read_csv(path)
    assert frame.height == 200
    frame.with_columns(
        pl.when(pl.col("Source_Row") == frame["Source_Row"][0])
        .then(None)
        .otherwise(pl.col("Unit Cost (AUD $/unit)"))
        .alias("Unit Cost (AUD $/unit)")
    ).write_csv(path)
    with pytest.raises(subprocess.CalledProcessError) as failed:
        run_command(tmp_path, "validation_pipeline", *options)
    assert failed.value.returncode == 1
    model = json.loads(history.read_bytes())[-1]["models"][3]
    assert model["data_quality_score"] == 0.995
    assert model["data_quality_target_passed"] is False


def test_reference_extraction_preserves_row_addresses_and_detects_missing_inputs():
    row_labels = pl.DataFrame(
        {
            "Test": ["Panel", None, None],
            "Category": ["Labour", "Labour", "Equipment"],
            "Sub-Category": ["Library", None, "Equipment"],
            "Step": ["Synthetic row", None, "Synthetic fallback"],
        }
    )
    reference = row_labels.with_columns(
        pl.Series("Unit Cost (AUD $/unit) LL", [8.0, None, 2.0])
    )
    retained = ground_truth(reference, 5)
    evaluated = pl.DataFrame({"price": [8.0, None, 2.0]})
    output = replicate_cost_rows(retained, evaluated, 5, "A")
    assert output["Source_Row"].to_list() == [5, 7]
    assert output["unit_cost_labour"].to_list() == [8, 0]
    assert output["unit_cost_equipment"].to_list() == [0, 2]
    assert compare_sheet(evaluated, pl.DataFrame({"price": [8.0, None, 3.0]}), 5) == (
        2,
        ["A7"],
    )
    with pytest.raises(ValueError, match="same nonzero shape"):
        compare_sheet(evaluated, evaluated.head(2), 5)
    with pytest.raises(ValueError, match="Cost_Step"):
        ground_truth(reference.drop("Step"), 5)
    with pytest.raises(ValueError, match="reference cost columns"):
        ground_truth(row_labels, 5)
    with pytest.raises(ValueError, match="No populated source rows"):
        ground_truth(reference.slice(1, 1), 6)
    with pytest.raises(ValueError, match="distinct physical source rows"):
        replicate_cost_rows(pl.concat([retained, retained]), evaluated, 5, "A")
    with pytest.raises(ValueError, match="cost column is outside"):
        replicate_cost_rows(retained, evaluated, 5, "AA")
    with pytest.raises(ValueError, match="outside the worksheet"):
        replicate_cost_rows(retained, evaluated.head(2), 5, "A")


def test_explicit_sheet_offset_preserves_formulas_and_rejects_unknown_functions(
    tmp_path,
):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Synthetic Costs"
    sheet["A2"] = "Price"
    sheet["A3"] = 5
    sheet["A4"] = "=A3*3"
    path = tmp_path / "offset.xlsx"
    workbook.save(path)
    _, result, start = evaluate_sheet(path, sheet.title, first_row=3)
    assert start == 3
    assert result.to_series().to_list() == [5, 15]
    sheet["A4"] = "=UNKNOWN_COST_FUNCTION(1)"
    workbook.save(path)
    workbook.close()
    with pytest.raises(ValueError, match="evaluation failures"):
        evaluate_sheet(path, "Synthetic Costs", first_row=3)


def test_model_checks_reject_a_missing_field_and_an_unidentified_source(tmp_path):
    unknown = pl.DataFrame(
        {
            "Test": ["Synthetic Unknown"],
            "Category": ["Labour"],
            "Sub-Category": ["No known model"],
        }
    )
    source = tmp_path / "unknown.parquet"
    unknown.write_parquet(source)
    loaded = read_model_source(source)
    assert loaded["Source_Row"].to_list() == [5]
    with pytest.raises(ValueError, match="No identified model"):
        model_rows(loaded)
    finding = verify_model(unknown, "Panel")
    assert finding["valid"] is False
    assert "Item" in finding["missing_columns"]
    invalid = tmp_path / "missing-header.csv"
    invalid.write_text("cost,units\n3,2\n")
    with pytest.raises(ValueError, match="No identifiable detailed-table header"):
        read_model_source(invalid)


def test_model_comparison_fails_if_an_expected_export_changes(tmp_path):
    source = tmp_path / "source.csv"
    pl.DataFrame(
        {
            "Test": ["Panel"],
            "Category": ["Labour"],
            "Sub-Category": ["DNA Extraction"],
            "Step": ["Synthetic item"],
            "Unit Cost (AUD $/unit)": [3],
            "Units": [2],
        }
    ).write_csv(source)
    data = tmp_path / "enhanced"
    report = tmp_path / "comparison.md"
    options = ("--workbook", source, "--data-dir", data, "--report", report)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validate_excel_comparison", *options)
    assert "missing Panel_enhanced.csv" in report.read_text()
    run_command(
        tmp_path,
        "phase3_data_enhancement",
        "--source",
        source,
        "--output-dir",
        data,
        "--report",
        tmp_path / "enhance.md",
    )
    run_command(tmp_path, "validate_excel_comparison", *options)
    assert "0 differences" in report.read_text()
    output = data / "Panel_enhanced.csv"
    pl.read_csv(output).drop("Units").write_csv(output)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(tmp_path, "validate_excel_comparison", *options)
    assert "schema or row count mismatch" in report.read_text()


def test_workbook_quality_rejects_a_model_absent_from_selected_reference(
    tmp_path, monkeypatch
):
    source = tmp_path / "panel.csv"
    tables = pl.DataFrame(
        {
            "Source_Row": [5],
            "Test": ["Panel"],
            "Category": ["Labour"],
            "Sub-Category": ["DNA Extraction"],
            "Item": ["Synthetic row"],
            "Unit Cost (AUD $/unit)": [4],
            "Units": [2],
        }
    )
    tables.write_csv(source)
    assert read_model_source(source)["Source_Row"].to_list() == [5]
    parquet = source.with_suffix(".parquet")
    tables.write_parquet(parquet)
    assert read_model_source(parquet).equals(tables)
    output = tmp_path / "model-exports"
    output.mkdir()
    tables.with_columns(pl.lit("WES (P)").alias("Test")).write_csv(
        output / "WES_P_enhanced.csv"
    )
    report = tmp_path / "historical.md"
    args = ["--report", str(report), "--data-dir", str(output), "--model", "WES (P)"]
    monkeypatch.setattr(
        sys, "argv", ["validate_standardization", *args, "--workbook", str(source)]
    )
    assert legacy_models.quality_main(str(report)) == 1
    assert '"missing_reference": true' in report.read_text(encoding="utf-8")
    for invalid in (
        ["--profile", "profile.json"],
        ["--workbook", str(source), "--suffix", "standardized"],
    ):
        monkeypatch.setattr(sys, "argv", ["validate_standardization", *args, *invalid])
        with pytest.raises(SystemExit, match="2"):
            legacy_models.quality_main(str(report))


def test_labour_workbook_export_preserves_shared_model_labels(tmp_path, monkeypatch):
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = legacy_models.LABOUR_SHEET
    sheet.append([None, None, "Hours"])
    sheet.append([None, None, "Input"])
    sheet.append(["Test", "Stage", "Midpoint"])
    sheet.append(["WES (S)", "Fixture stage", 7])
    source = tmp_path / "labour.xlsx"
    workbook.save(source)
    monkeypatch.setattr(
        legacy_models,
        "load_config",
        lambda: {
            "default_workbook": "historical",
            "workbooks": {"historical": {"path": str(source)}},
        },
    )
    output = tmp_path / "labour-lines"
    monkeypatch.setattr(sys, "argv", ["extract_labour", "--output-dir", str(output)])
    assert legacy_models.extract_main(str(output), "labour", sheet=sheet.title) == 0
    extracted = pl.read_csv(output / "WES_S_labour.csv")
    assert extracted["Test"].to_list() == ["WES (S)"]
    assert extracted["Source_Row"].to_list() == [4]
    assert extracted["Category"].to_list() == ["Labour"]
    sheet["A4"] = "Unknown"
    workbook.save(source)
    workbook.close()
    with pytest.raises(ValueError, match="No identified labour-use rows"):
        legacy_models.extract_main(str(output), "labour", sheet=sheet.title)


def test_legacy_performance_receipt_flags_a_six_percent_regression(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    baseline = {
        "schema_version": 1,
        "python": "3.15.1",
        "polars": "synthetic",
        "platform": "synthetic",
        "threads": 1,
        "repeats": 5,
        "measurements": [
            {"rows": 10000, "median_ns": 100, "max_sampled_rss_growth_bytes": 0},
        ],
    }
    stored = save_baselines(baseline)
    current = load_baselines(stored)
    current["measurements"][0]["median_ns"] = 106
    comparison = compare_baselines(current, baseline)["processing_time"]
    assert comparison["performance_regression"] is True
    assert comparison["timing_regression_rows"] == [10000]
    current["threads"] = 2
    with pytest.raises(ValueError, match="threads"):
        compare_baselines(current, baseline)


def test_performance_command_records_every_default_workload(
    tmp_path, monkeypatch, capsys
):
    receipt = tmp_path / "baseline.json"
    monkeypatch.setattr(
        sys, "argv", ["establish_performance_baselines", "--output", str(receipt)]
    )
    assert measure_performance() == 0
    assert [item["rows"] for item in load_baselines(str(receipt))["measurements"]] == [
        1000,
        5000,
        10000,
    ]
    assert "10000 rows:" in capsys.readouterr().out
