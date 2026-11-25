# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Exercise the installed preparation command and exact API table ingestion."""

from decimal import Decimal

import polars as pl
import pytest
from openpyxl import Workbook

from genomics_microcosting import prepare_data
from genomics_microcosting.data_pipeline import DataPipeline
from genomics_microcosting.extractors import APIExtractor
from genomics_microcosting.loaders import ParquetLoader


def test_prepare_command_preserves_configured_and_supporting_sheet_names(
    tmp_path,
    monkeypatch,
):
    workbook = Workbook()
    configured = workbook.active
    configured.title = "Local (Sheet)"
    configured.append(["Ignored", "Ignored"])
    configured.append(["Test", "Cost"])
    configured.append(["Synthetic", 1.25])
    supporting = workbook.create_sheet("DSA - Summary")
    supporting.append(["Test", "Other"])
    supporting.append(["Synthetic", 2.5])
    workbook.create_sheet("Sheet1")
    source = tmp_path / "input.xlsx"
    workbook.save(source)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MICROCOSTING_OUTPUT_DIR", str(tmp_path / "prepared"))
    monkeypatch.setattr(
        prepare_data,
        "load_config",
        lambda: {
            "workbooks": {
                "main": {
                    "path": str(source),
                    "sheets": {"Local (Sheet)": {"skip_rows": 1}, "Absent": {}},
                },
            },
        },
    )

    prepare_data.main()

    prepared = tmp_path / "prepared"
    assert sorted(file.name for file in prepared.iterdir()) == [
        "dsa___summary.csv",
        "dsa___summary.parquet",
        "local_sheet.csv",
        "local_sheet.parquet",
    ]
    assert pl.read_parquet(prepared / "local_sheet.parquet").to_dicts() == [
        {"Test": "Synthetic", "Cost": 1.25},
    ]
    assert pl.read_csv(prepared / "dsa___summary.csv").to_dicts() == [
        {"Test": "Synthetic", "Other": 2.5},
    ]


def test_api_extractor_round_trips_exact_numeric_response(tmp_path):
    payload = (
        b'{"schema_version":"0.1","records":[{"item":"synthetic","rate":'
        b"1234567890123456.0123}]}"
    )
    schema = pl.Schema({"item": pl.String, "rate": pl.Decimal(24, 4)})
    extractor = APIExtractor("rates", "synthetic-release", lambda: payload, schema)
    target = tmp_path / "rates.parquet"
    pipeline = DataPipeline("api-table")
    pipeline.add_extractor(extractor)
    pipeline.add_loader(ParquetLoader("rates", target))

    pipeline.run()

    assert pl.read_parquet(target).schema == schema
    assert pl.read_parquet(target)["rate"].to_list() == [
        Decimal("1234567890123456.0123"),
    ]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b'{"schema_version":"1.0","records":[]}', "Unknown API"),
        (b'{"schema_version":"0.1","records":[{}]}', "declared table columns"),
        (b'{"schema_version":"0.1","records":[{"rate":NaN}]}', "nonfinite"),
        (b'{"schema_version":"0.1","records":[{"rate":1,"rate":2}]}', "Duplicate"),
        (
            b'{"schema_version":"0.1","records":[{"rate":1.23456}]}',
            "precision or scale",
        ),
    ],
)
def test_api_extractor_rejects_ambiguous_or_inexact_records(payload, message):
    schema = pl.Schema({"rate": pl.Decimal(10, 4)})
    with pytest.raises(ValueError, match=message):
        APIExtractor("rates", "invalid-release", lambda: payload, schema).extract()
