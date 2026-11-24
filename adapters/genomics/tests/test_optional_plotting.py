# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Retain installed data routes when plotting is unavailable."""

import polars as pl

from genomics_microcosting import visualization
from genomics_microcosting.web import create_app


def test_web_without_optional_plotter(tmp_path, monkeypatch):
    table = pl.DataFrame({"category": ["equipment"], "cost": [12.5]})
    table.write_parquet(tmp_path / "detailed_table.parquet")
    monkeypatch.setattr(visualization, "plt", None)
    client = create_app(tmp_path).test_client()

    assert client.get("/api/tables").status_code == 200
    assert client.get("/api/table/detailed_table").status_code == 200
    health = client.get("/health").json["checks"]["data_availability"]
    assert health["status"] == "healthy"
    assert health["result"]["file_count"] == 1
    for route in (
        "/api/generate_viz/detailed_table?column=cost",
        "/api/dashboard/cost-distribution",
        "/api/dashboard/top-categories",
    ):
        response = client.get(route)
        assert response.status_code == 503
        assert "genomics-microcosting[visualization]" in response.json["error"]
