# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Exercise source-distribution commands against synthetic reference values."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest

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
