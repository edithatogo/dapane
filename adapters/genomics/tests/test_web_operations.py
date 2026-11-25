# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify roles, diagnostics, benchmarks and retained quality receipts."""

import json
from datetime import UTC, datetime
from decimal import Decimal

import polars as pl
import pytest
from werkzeug.security import generate_password_hash

from dapane_genomics import web_access
from genomics_microcosting.web import create_app

PREFIX = "/api/microcosting"
VIEWER = ("read-only", "fictional viewer")
ANALYST = ("operator", "fictional analyst")


@pytest.fixture
def dashboard(tmp_path, monkeypatch):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    table = pl.DataFrame(
        {
            "id": ["001", "002", "003"],
            "cost": [Decimal("1.25"), Decimal("-2.00"), None],
        }
    )
    table.write_parquet(prepared / "assay.parquet")
    table.write_csv(prepared / "assay.csv")
    table.write_parquet(prepared / "unpaired.parquet")
    table.with_columns(pl.lit("001").alias("id")).write_csv(prepared / "unpaired.csv")
    table.write_parquet(prepared / "archive.parquet")
    audit = tmp_path / "audit.jsonl"
    access = tmp_path / "access.json"
    access.write_text(
        json.dumps(
            {
                "users": {
                    VIEWER[0]: {
                        "role": "viewer",
                        "password_hash": generate_password_hash(VIEWER[1]),
                    },
                    ANALYST[0]: {
                        "role": "analyst",
                        "password_hash": generate_password_hash(ANALYST[1]),
                    },
                },
                "audit_file": str(audit),
                "requests_per_minute": 12,
            },
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GENOMICS_WEB_ACCESS_FILE", str(access))
    monkeypatch.setenv("GENOMICS_OPERATIONS_STORE", str(tmp_path / "operations.sqlite"))
    return prepared, audit, access


def test_web_access_roles_and_request_audit(dashboard):
    prepared, audit, _ = dashboard
    client = create_app(prepared).test_client()
    missing = client.get("/api/tables")
    assert missing.status_code == 401
    assert "Basic" in missing.headers["WWW-Authenticate"]
    table = client.get("/api/tables", auth=VIEWER)
    assert set(table.json) == {"archive", "assay", "unpaired"}
    export_url = next(
        rule.rule
        for rule in client.application.url_map.iter_rules()
        if rule.endpoint == "export_all_zip"
    )
    assert client.get(export_url, auth=VIEWER).status_code == 403
    with client.get(export_url, auth=ANALYST) as exported:
        assert exported.status_code == 200
    assert client.post(f"{PREFIX}/tests/run", auth=VIEWER).status_code == 403
    assert client.get(f"{PREFIX}/tests/results").status_code == 401
    assert client.get(f"{PREFIX}/tests/results", auth=VIEWER).json == {"results": []}
    with client.get("/static/model_templates.js") as script:
        assert script.status_code == 200
        assert b"dragover" in script.data

    audit_text = audit.read_text(encoding="utf-8")
    assert all(password not in audit_text for _, password in (VIEWER, ANALYST))
    events = [json.loads(line) for line in audit_text.splitlines()]
    assert events[0]["user"] is None and events[0]["success"] is False
    assert events[1]["user"] == VIEWER[0]
    assert events[1]["details"] == f"{table.headers['X-Request-ID']} 200"


def test_rate_limit_recovers_for_each_configured_account(dashboard, monkeypatch):
    prepared, _, access = dashboard
    data = json.loads(access.read_text(encoding="utf-8"))
    data["requests_per_minute"] = 1
    access.write_text(json.dumps(data), encoding="utf-8")
    now = [100]
    monkeypatch.setattr(web_access, "monotonic", lambda: now[0])
    client = create_app(prepared).test_client()
    assert client.get("/api/tables", auth=VIEWER).status_code == 200
    limited = client.get("/api/tables", auth=VIEWER)
    assert limited.status_code == 429 and limited.headers["Retry-After"] == "60"
    assert client.get("/api/tables", auth=ANALYST).status_code == 200
    now[0] += 60
    assert client.get("/api/tables", auth=VIEWER).status_code == 200


@pytest.mark.parametrize("suite", ["integration", "end_to_end", "performance"])
def test_diagnostics_and_result_filters_through_installed_app(dashboard, suite):
    prepared, audit, _ = dashboard
    client = create_app(prepared).test_client()
    response = client.post(
        f"{PREFIX}/tests/run", json={"test_type": suite}, auth=ANALYST
    )
    assert response.status_code == 200
    result = response.json
    assert result["passed"] is True
    assert result["analysis_modules"] == ["cost_driver", "dsa", "psa", "voi"]
    assert all(
        check["passed"] and check["elapsed_ns"] > 0 for check in result["checks"]
    )
    request_id = response.headers["X-Request-ID"]
    assert result["request_id"] == request_id
    assert request_id in audit.read_text(encoding="utf-8")

    restarted = create_app(prepared).test_client()
    filtered = restarted.get(
        f"{PREFIX}/tests/results",
        query_string={"test_type": suite, "analysis_module": "voi"},
        auth=VIEWER,
    )
    assert filtered.json == {"results": [result]}
    assert restarted.get(
        f"{PREFIX}/tests/results",
        query_string={"date_range": '{"end":"1900-01-01"}'},
        auth=VIEWER,
    ).json == {"results": []}


def test_benchmark_and_health_metrics(dashboard):
    prepared, _, _ = dashboard
    client = create_app(prepared).test_client()
    benchmark = client.post(
        f"{PREFIX}/performance/benchmark",
        json={"data_set_size": 37, "iterations": 321},
        auth=ANALYST,
    )
    assert benchmark.status_code == 200
    receipt = benchmark.json
    assert receipt["cost_driver"]["measurements"][0]["rows"] == 37
    assert receipt["psa"]["iterations"] == 321
    analysis = client.get(
        f"{PREFIX}/performance/metrics",
        query_string={"analysis_type": "psa"},
        auth=VIEWER,
    )
    assert analysis.json == {"benchmarks": [receipt], "diagnostics": []}
    assert (
        client.get(
            f"{PREFIX}/performance/metrics",
            query_string={"analysis_type": "voi"},
            auth=VIEWER,
        ).json["benchmarks"]
        == []
    )
    health = client.get(f"{PREFIX}/monitoring/health", auth=VIEWER)
    assert health.status_code in {200, 503}
    assert "data_availability" in health.json["checks"]
    readiness = client.get("/health")
    assert readiness.status_code in {200, 503}
    assert set(readiness.json) == {"status"}
    for name in ("cpu", "memory", "execution_time"):
        response = client.get(
            f"{PREFIX}/monitoring/metrics",
            query_string={"metric_type": name},
            auth=VIEWER,
        )
        assert response.status_code == 200 and set(response.json) == {name}
        if name == "execution_time":
            assert response.json[name]["benchmark.execution_time"]["count"] == 1


def test_quality_metrics_distinguish_consistency_and_missing_inputs(dashboard):
    prepared, _, _ = dashboard
    client = create_app(prepared).test_client()
    result = client.post(
        f"{PREFIX}/data-quality/validate",
        json={
            "sheet_names": ["assay", "unpaired", "archive"],
            "validation_types": ["integrity", "consistency", "anomalies"],
        },
        auth=ANALYST,
    )
    assert result.status_code == 200
    payload = result.json
    assay, unpaired, archive = payload["sheets"]
    assert assay["integrity"]["errors"] == 1
    assert assay["integrity"]["passed"] is False
    assert assay["anomalies"] >= 1
    assert assay["consistency"]["passed"] is True
    assert unpaired["consistency"]["passed"] is False
    assert archive["consistency"] == {"available": False}
    readings = client.get(
        f"{PREFIX}/monitoring/data-quality",
        query_string={"sheet_name": "assay"},
        auth=VIEWER,
    )
    assert readings.json == {"results": [payload]}
    today = datetime.now(UTC).date().isoformat()
    history = client.get(
        f"{PREFIX}/data-quality/reports",
        query_string={"date_range": json.dumps({"start": today, "end": today})},
        auth=VIEWER,
    )
    assert history.json == {"results": [payload]}
    assert "-2.00" not in result.get_data(as_text=True)


def test_operation_inputs_are_bounded_and_disabled_without_access(
    dashboard, monkeypatch
):
    prepared, _, _ = dashboard
    client = create_app(prepared).test_client()
    invalid_cases = (
        ("tests/run", {"test_type": "arbitrary"}),
        ("tests/run", {"test_type": "integration", "analysis_modules": ["dsa", "dsa"]}),
        ("performance/benchmark", {"data_set_size": 10, "iterations": 10001}),
        ("performance/benchmark", {"data_set_size": "10", "iterations": 1}),
        (
            "data-quality/validate",
            {"sheet_names": ["unknown"], "validation_types": ["integrity"]},
        ),
    )
    for route, payload in invalid_cases:
        response = client.post(f"{PREFIX}/{route}", json=payload, auth=ANALYST)
        assert response.status_code == 400
    assert (
        client.get(
            f"{PREFIX}/tests/results",
            query_string={"date_range": '{"start":"2000-02-01","end":"2000-01-01"}'},
            auth=VIEWER,
        ).status_code
        == 400
    )
    assert (
        client.post(
            f"{PREFIX}/tests/run",
            data=b" " * 8193,
            content_type="application/json",
            auth=ANALYST,
        ).status_code
        == 413
    )
    monkeypatch.delenv("GENOMICS_WEB_ACCESS_FILE")
    unconfigured = create_app(prepared).test_client()
    assert unconfigured.get("/api/tables").status_code == 200
    assert unconfigured.get(f"{PREFIX}/tests/results").status_code == 404
