# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Exercise inherited analyst workflows against disposable local fixtures."""

import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import pytest
from openpyxl import Workbook

from dapane_genomics import reporting
from genomics_microcosting import validate_engine as engine_validation
from genomics_microcosting import visualization
from genomics_microcosting.advanced_scenario_modeling import (
    AdvancedScenario,
    AdvancedScenarioManager,
)
from genomics_microcosting.analysis_config import AnalysisConfigurationManager
from genomics_microcosting.calculation_engine import CalculationEngine
from genomics_microcosting.config_validation import (
    ConfigurationValidator,
    ConfigurationVersionManager,
    DynamicConfigurationUpdater,
)
from genomics_microcosting.data_manager import DataManager
from genomics_microcosting.enhanced_plugin_system import (
    EnhancedPlugin,
    EnhancedPluginManager,
    EnhancedVisualizationPlugin,
)
from genomics_microcosting.excel_version_control import WorkbookVersionControl
from genomics_microcosting.extensibility_framework import ExtensibilityFramework
from genomics_microcosting.formula_parser import parse_formula
from genomics_microcosting.sheet_manager import SheetManager


def test_legacy_averages_preserve_range_and_cell_behaviour(tmp_path):
    source = tmp_path / "synthetic.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Synthetic"
    worksheet.append(("Number", "Label"))
    worksheet.append((2, "text"))
    worksheet.append((8, None))
    worksheet.append((None, "row marker"))
    worksheet.append(("=A2*2", None))
    workbook.save(source)
    workbook.close()
    engine = CalculationEngine(
        SheetManager(
            source, sheet_configs={"Synthetic": {"header_rows": 1, "data_starts_at": 2}}
        )
    )

    cases = (
        ("=AVERAGE(A3:A2)", "average_range", 5.0),
        ("=AVERAGE(A2,A3)", "average_cells", 5.0),
        ("=AVERAGE(A3:A4)", "average_range", None),
        ("=AVERAGE(A3,A4)", "average_cells", None),
        ("=AVERAGE(A2:B2)", "average_range", None),
        ("=AVERAGE(A2,B2)", "average_cells", None),
        ("=AVERAGE(A5:A5)", "average_range", 4.0),
        ("=AVERAGE(A5,A3)", "average_cells", 6.0),
    )
    for row, (formula, kind, expected) in enumerate(cases, 2):
        parsed = parse_formula(formula)
        assert parsed is not None and parsed["type"] == kind
        assert engine.execute_formula(formula, "Synthetic", f"D{row}") == expected

    assert (
        engine.execute_formula(
            {"type": "average_cells", "cells": []}, "Synthetic", "D10"
        )
        is None
    )


def test_local_plugin_discovery_lifecycle_and_legacy_conversion(tmp_path):
    config = tmp_path / "plugin-settings.json"
    config.write_text('{"precision":2}', encoding="utf-8")
    manager = EnhancedPluginManager(tmp_path / "plugins", config)
    directory = manager.plugin_directory
    (directory / "estimate.py").write_text(
        """
from genomics_microcosting.enhanced_plugin_system import EnhancedPlugin

class Estimate(EnhancedPlugin):
    def __init__(self):
        super().__init__("estimate", "1", "Synthetic estimates", tags=["cost"])

    def calculate(self, quantity):
        return self.get_config()["unit_cost"] * quantity

    def cleanup(self):
        self.set_config({})
""",
        encoding="utf-8",
    )
    (directory / "legacy.py").write_text(
        """
from genomics_microcosting.plugin_system import Plugin

class LegacyEstimate(Plugin):
    def __init__(self):
        super().__init__("legacy", "2", "Synthetic legacy estimates")

    def calculate(self, quantity):
        return 2 * quantity
""",
        encoding="utf-8",
    )
    (directory / "empty.py").write_text("VALUE = 1\n", encoding="utf-8")
    (directory / "__init__.py").touch()

    assert manager.load_all_plugins() == {
        "loaded": list(manager.plugins),
        "failed": ["empty.py"],
    }
    assert set(manager.plugins) == {"estimate", "legacy"}
    assert manager.execute_plugin_method("legacy", "calculate", 5) == 10
    plugin = manager.plugins["estimate"]
    plugin.set_config({"unit_cost": 3})
    assert manager.execute_plugins_by_tag("cost", "calculate", 5) == {"estimate": 15}
    assert (
        "missing_operation"
        in manager.execute_plugins_by_tag("cost", "missing_operation", 5)["estimate"][
            "error"
        ]
    )
    assert [item["name"] for item in manager.list_plugins(["cost"])] == ["estimate"]
    counts = manager.get_plugin_statistics()
    assert counts["initialized_plugins"] == 2
    assert counts["tags"] == {"cost": 1}
    assert not manager.register_plugin(
        EnhancedPlugin("requires-rate", "1", "", dependencies=["rates"])
    )
    assert manager.register_plugin(EnhancedVisualizationPlugin())
    assert (
        manager.execute_plugin_method(
            "enhanced_visualization", "visualize", "sample", output_format="svg"
        )["format"]
        == "svg"
    )
    assert manager.disable_plugin("estimate")
    assert manager.execute_plugins_by_tag("cost", "calculate", 5) == {}
    with pytest.raises(ValueError, match="not enabled"):
        manager.execute_plugin_method("estimate", "calculate", 5)
    assert manager.enable_plugin("estimate")
    assert not manager.enable_plugin("unknown")
    assert not manager.disable_plugin("unknown")
    with pytest.raises(ValueError, match="not found"):
        manager.execute_plugin_method("unknown", "calculate", 5)
    assert manager.config == {"precision": 2}
    manager.config["precision"] = 3
    manager.save_config()
    assert EnhancedPluginManager(directory, config).config == {"precision": 3}
    manager.cleanup()
    assert plugin.get_config() == {}
    assert manager.get_plugin_statistics()["initialized_plugins"] == 0


def test_extension_uses_installed_data_manager_and_local_configuration(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "extension-settings.json"
    config.write_text('{"baseline":"synthetic"}', encoding="utf-8")
    framework = ExtensibilityFramework(tmp_path / "extensions", config)
    extension_file = framework.extension_directory / "summarize.py"
    extension_file.write_text(
        """
from genomics_microcosting.extensibility_framework import AnalysisExtension

class Summarize(AnalysisExtension):
    def __init__(self):
        super().__init__("summarize", "1", "Calculate a synthetic total")

    def analyze(self, sheet, **options):
        table = self.data_manager.load_sheet_polars(sheet)
        return table["units"].sum()
""",
        encoding="utf-8",
    )
    (extension_file.parent / "invalid.py").write_text("VALUE = 1\n", encoding="utf-8")
    manager = DataManager(tmp_path / "data")
    frame = pl.DataFrame({"sample_id": ["001", "002"], "units": [5, 6]})
    assert manager.save_sheet("01. Source table", frame)
    framework.set_data_manager(manager)
    framework.load_all_extensions()
    assert (
        framework.execute_extension_method("summarize", "analyze", "01. Source table")
        == 11
    )
    assert framework.list_extensions()[0]["name"] == "summarize"
    assert framework.get_extensions_by_type("analysis") == [
        framework.extensions["summarize"]
    ]
    assert framework.validate_extension_dependencies() == {}
    framework.config["baseline"] = "verified"
    framework.save_config()
    assert json.loads(config.read_bytes()) == {"baseline": "verified"}
    framework.cleanup()


def test_local_table_formats_and_publication_dictionary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manager = DataManager(tmp_path / "tables")
    title = "01. Synthetic costs"
    frame = pl.DataFrame({"case": ["001", None, "003"], "units": [2, 3, 4]})
    assert manager.save_sheet(title, frame)
    assert not manager.save_sheet(title, frame, formats=["xlsx"])
    assert set(manager.list_available_sheets()["sheet_01_synthetic_costs"]) == {
        "csv",
        "parquet",
    }
    assert manager.load_sheet(title, "unknown") is None
    assert manager.load_sheet("missing") is None
    with pytest.raises(ValueError, match="explicit field schema"):
        manager.load_sheet(title, "csv")
    for kind in ("csv", "parquet"):
        restored = manager.load_sheet(title, kind, csv_schema=frame.schema)
        assert restored is not None and restored.equals(frame)
    assert manager.save_for_publication(title, frame, {"edition": "synthetic"})
    path = manager.publication_dir / "sheet_01_synthetic_costs_dictionary.csv"
    dictionary = pl.read_csv(path).to_dicts()
    assert dictionary[0] == {
        "column_name": "case",
        "data_type": "String",
        "sample_values": "",
        "null_count": 1,
        "unique_count": 2,
    }
    assert dictionary[1]["unique_count"] is None
    assert manager.save_for_publication(title, frame, include_examples=True)
    assert "001" in path.read_text(encoding="utf-8")
    assert json.loads(
        path.with_name("sheet_01_synthetic_costs_metadata.json").read_bytes()
    ) == {
        "edition": "synthetic",
    }


def test_configuration_snapshot_and_failed_update_preserve_prior_values(tmp_path):
    manager = AnalysisConfigurationManager(tmp_path / "configs")
    versions = ConfigurationVersionManager(tmp_path)
    updater = DynamicConfigurationUpdater(manager, ConfigurationValidator())
    name = "psa_analysis"
    config = manager.get_configuration(name)
    assert config is not None
    parameter = config.parameters["monte_carlo_iterations"]
    initial = parameter.value
    digest = versions.create_version(config, "Synthetic baseline")
    (tmp_path / "versions" / "psa_analysis_invalid.json").write_text(
        "[]", encoding="utf-8"
    )
    assert [version["notes"] for version in versions.list_versions(name)] == [
        "Synthetic baseline"
    ]
    recorded = []

    def record_update(analysis, setting, value):
        recorded.append((analysis, setting, value))

    updater.register_update_listener(record_update)
    assert not updater.update_parameter("missing", parameter.name, 123)
    assert not updater.update_parameter(name, "missing", 123)
    assert not updater.update_parameter(name, parameter.name, "invalid")
    assert recorded == []
    assert parameter.value == initial
    assert updater.update_parameter(name, parameter.name, 1000)
    assert recorded == [(name, parameter.name, 1000)]
    before = versions.get_version(name, digest)
    assert before is not None and before.parameters[parameter.name].value == initial
    assert parameter.value == 1000
    assert versions.get_version(name, "invalid") is None


def test_advanced_scenario_replays_declared_changes_and_exports_results(tmp_path):
    source = pl.DataFrame({"cost": [4.0, 8.0], "count": [1, 2], "label": ["a", "b"]})
    seed = 109
    manager = AdvancedScenarioManager(
        {"costs": source, "context": source.select("label")},
        rng=np.random.default_rng(seed),
    )
    manager.add_advanced_scenario(
        AdvancedScenario(
            "base",
            "Synthetic scenario",
            {},
            {"cost": 2.0},
            probability_distributions={
                "cost": {"type": "normal", "mean": 2.0, "std": 0.001},
                "count": {"type": "uniform", "low": 3.0, "high": 4.0},
            },
        )
    )
    sweep = manager.run_sensitivity_analysis("base", "cost", 2.0, 4.0, steps=3)
    assert sweep["cost"] == [2.0, 3.0, 4.0]
    assert sweep["results"] == {"costs": [24.0, 36.0, 48.0], "context": [0, 0, 0]}
    no_scenario = "missing"
    with pytest.raises(ValueError, match="not found"):
        manager.run_sensitivity_analysis(no_scenario, "cost", 2.0, 4.0)
    with pytest.raises(ValueError, match="not found"):
        manager.run_probabilistic_analysis(no_scenario, 2)
    with pytest.raises(ValueError, match="not found"):
        manager.compare_scenarios_detailed([no_scenario], "costs")
    with pytest.raises(ValueError, match="Run analysis first"):
        manager.export_scenario_results("base", str(tmp_path))
    draws = manager.run_probabilistic_analysis("base", iterations=2)
    oracle = np.random.default_rng(seed)
    for result in draws:
        assert result["costs"]["cost"].to_list() == pytest.approx(
            source["cost"].to_numpy() * oracle.normal(2.0, 0.001)
        )
        assert result["costs"]["count"].to_list() == pytest.approx(
            source["count"].to_numpy() * oracle.uniform(3.0, 4.0)
        )
    comparison = manager.compare_scenarios_detailed(["base"], "costs")["cost"]
    assert comparison.row(0) == ("Mean", 6.0, 12.0)
    assert comparison.row(-1) == ("75th Percentile", 7.0, 14.0)
    figure = manager.generate_tornado_chart(
        "base", "costs", {"cost": (2.0, 3.0)}, "cost"
    )
    try:
        assert figure.axes[0].patches[0].get_width() == 24
    finally:
        plt.close(figure)
    manager.export_scenario_results(
        "base", str(tmp_path), formats=("csv", "json", "parquet")
    )
    for kind, read in (
        ("csv", pl.read_csv),
        ("json", pl.read_json),
        ("parquet", pl.read_parquet),
    ):
        assert read(tmp_path / kind / f"base_costs.{kind}")["cost"].to_list() == [
            8.0,
            16.0,
        ]
    assert source["cost"].to_list() == [4.0, 8.0]


def test_workbook_version_readback_and_damage_detection(tmp_path):
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet["A1"] = 9
    path = tmp_path / "costs.xlsx"
    workbook.save(path)
    store = WorkbookVersionControl(tmp_path / "archive")
    first = store.commit_workbook(path, {"basis": "synthetic"})
    assert store.commit_workbook(path) == first
    sheet["A1"] = 10
    workbook.save(path)
    workbook.close()
    second = store.commit_workbook(path)
    assert first != second
    reopened = WorkbookVersionControl(store.repository_directory)
    assert reopened.verify_integrity("costs", first)
    latest = reopened.get_latest_version("costs")
    assert latest is not None and latest.version_id == second
    assert reopened.verify_integrity("costs")
    assert (
        reopened.checkout_workbook(
            "costs", second, tmp_path / "restored.xlsx"
        ).read_bytes()
        == path.read_bytes()
    )
    assert "differences" in reopened.compare_versions("costs", first, second)
    latest.file_path.write_bytes(b"damaged synthetic archive")
    assert not reopened.verify_integrity("costs")
    latest.file_path.unlink()
    assert not reopened.verify_integrity("costs", second)
    with pytest.raises(FileNotFoundError, match="Stored workbook file not found"):
        reopened.checkout_workbook("costs", second, tmp_path / "damaged.xlsx")
    with pytest.raises(ValueError, match="not found"):
        reopened.verify_integrity("costs", "unknown")


def test_static_chart_and_report_outputs_preserve_cost_order_and_totals(
    tmp_path, monkeypatch
):
    table = pl.DataFrame(
        {
            "Category": ["Equipment", "Labour", "Labour"],
            "unit_cost": [7, 10, 12],
            "hours": [1, 2, 2],
        }
    )
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    with pytest.raises(ValueError, match="Detailed table not found"):
        visualization.create_summary_dashboard(prepared, tmp_path)
    (prepared / "damaged.parquet").write_bytes(b"damaged synthetic table")
    table.write_parquet(prepared / "detailed_table.parquet")
    charts = visualization.create_summary_dashboard(prepared, tmp_path)
    assert len(charts) == 3
    assert sum(bar.get_height() for bar in charts[0].axes[0].patches) == 3
    assert [bar.get_height() for bar in charts[1].axes[0].patches] == [22, 7]
    assert [bar.get_height() for bar in charts[2].axes[0].patches] == [12, 10, 7]
    assert (
        visualization.plot_top_costs(table.select("unit_cost"), "unit_cost")
        .axes[0]
        .get_xticklabels()[0]
        .get_text()
        == "Item 1"
    )
    plt.close("all")
    figures = tmp_path / "figures"
    figures.mkdir()
    assert (
        reporting.create_cost_analysis_plots(
            {"detailed_table": table.select("Category")}, figures
        )
        == []
    )
    assert set(
        reporting.create_cost_analysis_plots({"detailed_table": table}, figures)
    ) == {
        "cost_distribution.png",
        "top_costs.png",
        "category_costs.png",
    }
    report = tmp_path / "report.md"
    reporting.generate_markdown_report({"detailed_table": table}, report, figures)
    assert "figures/category_costs.png" in report.read_text(encoding="utf-8")
    reporting.generate_markdown_report({"detailed_table": table}, report)
    assert "![Cost analysis chart]" not in report.read_text(encoding="utf-8")
    for operation in (
        lambda: visualization.plot_cost_distribution(table, "unknown"),
        lambda: visualization.plot_top_costs(table, "unknown"),
        lambda: visualization.plot_category_costs(table, "unknown", "unit_cost"),
        lambda: visualization.plot_category_costs(table, "Category", "unknown"),
        lambda: visualization.plot_cost_breakdown(table, "unknown", ["unit_cost"]),
        lambda: visualization.plot_cost_breakdown(table, "Category", ["unknown"]),
    ):
        with pytest.raises(ValueError, match="not found"):
            operation()
    monkeypatch.setattr(visualization, "plt", None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "genomics-report",
            "--data-dir",
            str(prepared),
            "--output-dir",
            str(tmp_path / "fallback"),
        ],
    )
    assert reporting.main() == 0
    assert (tmp_path / "fallback" / "enhanced_microcosting_report.json").exists()


def test_engine_validation_reports_missing_inputs_and_matches_shifted_headers(
    monkeypatch,
):
    assert engine_validation.match_columns(
        [
            "Unit Cost (AUD) Midpoint",
            "Unit Price (USD)",
            "Expected Quantity",
            "Unrelated",
        ],
        ["Unit Price (USD)", "Reported Unit Cost (AUD)", "Estimated Quantity"],
    ) == {
        "Unit Cost (AUD) Midpoint": "Reported Unit Cost (AUD)",
        "Unit Price (USD)": "Unit Price (USD)",
        "Expected Quantity": "Estimated Quantity",
    }
    monkeypatch.setitem(engine_validation.VALIDATION_CONFIG, "export_results", False)
    monkeypatch.setattr(engine_validation, "load_ground_truth", lambda: None)
    unavailable = engine_validation.validate_calculation_engine()
    assert unavailable["errors"] == ["Cannot proceed without ground truth data"]
    assert not unavailable["ground_truth_loaded"] and not unavailable["engine_run"]
    monkeypatch.setattr(
        engine_validation, "load_ground_truth", lambda: pl.DataFrame({"unknown": [1]})
    )
    unknown = engine_validation.validate_calculation_engine()
    assert unknown["errors"] == ["No unit cost columns found in ground truth data"]
    assert unknown["ground_truth_loaded"] and not unknown["engine_run"]
