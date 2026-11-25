# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Authenticated operations for the installed genomics dashboard."""

from __future__ import annotations

import json
from contextlib import closing
from datetime import UTC, date, datetime
from sqlite3 import connect
from threading import Lock
from time import perf_counter_ns
from typing import TYPE_CHECKING, Literal, cast
from uuid import uuid4

import polars as pl
import psutil
from flask import Blueprint, Response, abort, g, jsonify, request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from werkzeug.exceptions import BadRequest

from genomics_microcosting.data_consistency_validator import DataConsistencyValidator
from genomics_microcosting.data_manager import DataManager
from genomics_microcosting.data_quality_assurance import (
    DataAnomalyDetector,
    DataIntegrityVerifier,
)

from .benchmark import measure
from .operational_checks import ANALYSES, Analysis, Suite, diagnose, synthetic_psa

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from genomics_microcosting.monitoring import PerformanceMetricsCollector

Kind = Literal["test", "benchmark", "quality"]
QualityCheck = Literal["integrity", "consistency", "anomalies"]


class _Request(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class _TestRequest(_Request):
    test_type: Suite
    analysis_modules: list[Analysis] = Field(
        default_factory=lambda: list(ANALYSES), min_length=1, max_length=4
    )


class _BenchmarkRequest(_Request):
    data_set_size: int = Field(ge=1, le=10000)
    iterations: int = Field(ge=1, le=10000)


class _QualityRequest(_Request):
    sheet_names: list[str] = Field(min_length=1, max_length=16)
    validation_types: list[QualityCheck] = Field(min_length=1, max_length=3)


class _DateRange(_Request):
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def check_order(self) -> _DateRange:
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("The start must be on or before the end")
        return self


def _json_body() -> bytes:
    request.max_content_length = 8192
    if not request.is_json:
        raise BadRequest("Send a JSON request")
    return request.get_data(cache=False)


def _date_range(name: str) -> _DateRange:
    try:
        return _DateRange.model_validate_json(request.args.get(name, "{}"))
    except ValidationError as error:
        raise BadRequest(f"Invalid {name}") from error


class _Receipts:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(connect(path)) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS operation_receipts ("
                "kind TEXT NOT NULL, date TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def record(self, kind: Kind, result: Mapping[str, object]) -> dict[str, object]:
        now = datetime.now(UTC)
        payload: dict[str, object] = {
            **result,
            "schema_version": 1,
            "kind": kind,
            "id": uuid4().hex,
            "timestamp": now.isoformat(),
            "request_id": cast("str", g.genomics_request_id),
        }
        with closing(connect(self.path)) as db, db:
            db.execute(
                "INSERT INTO operation_receipts VALUES (?, ?, ?)",
                (kind, now.date().isoformat(), json.dumps(payload, allow_nan=False)),
            )
        return payload

    def read(
        self,
        kind: Kind,
        dates: _DateRange,
        *,
        tag: str | None = None,
        value: str | None = None,
        suite: str | None = None,
    ) -> list[dict[str, object]]:
        with closing(connect(self.path)) as db:
            rows = db.execute(
                "SELECT payload FROM operation_receipts WHERE kind = ? "
                "AND date >= ? AND date <= ? "
                "AND (? IS NULL OR json_extract(payload, '$.test_type') = ?) "
                "AND (? IS NULL OR EXISTS (SELECT 1 FROM json_each(payload, ?) "
                "WHERE value = ?)) ORDER BY rowid DESC LIMIT 100",
                (
                    kind,
                    (dates.start or date.min).isoformat(),
                    (dates.end or date.max).isoformat(),
                    suite,
                    suite,
                    value,
                    tag,
                    value,
                ),
            )
            return [
                cast("dict[str, object]", json.loads(payload)) for (payload,) in rows
            ]


def _quality(
    data_manager: DataManager,
    prepared_dir: Path,
    name: str,
    table: pl.DataFrame,
    checks: list[QualityCheck],
) -> dict[str, object]:
    validator = DataConsistencyValidator(data_manager)
    columns = [name for name in table.columns if "cost" in name.casefold()]
    result: dict[str, object] = {"sheet_name": name}
    if "integrity" in checks:
        integrity = validator.validate_sheet_integrity(name, table)
        cost_issues = DataIntegrityVerifier().verify_cost_integrity(table, columns)
        result["integrity"] = {
            **integrity["metrics"],
            "passed": integrity["passed"] and not cost_issues,
            "errors": len(integrity["errors"]) + len(cost_issues),
            "warnings": len(integrity["warnings"]),
        }
    if "anomalies" in checks:
        detector = DataAnomalyDetector()
        result["anomalies"] = len(detector.detect_cost_anomalies(table, columns)) + len(
            detector.detect_pattern_anomalies(table)
        )
    if "consistency" in checks:
        csv_path = prepared_dir / (name + ".csv")
        consistency: dict[str, object] = {"available": csv_path.is_file()}
        if consistency["available"]:
            try:
                paired = pl.read_csv(csv_path, schema_overrides=table.schema)
                findings = validator.validate_sheet_consistency(name, table, paired)
                consistency.update(
                    passed=(
                        findings["passed"]
                        and not findings["warnings"]
                        and table.equals(paired)
                    ),
                    errors=len(findings["errors"]),
                    warnings=len(findings["warnings"]),
                )
            except OSError, pl.exceptions.PolarsError:
                consistency.update(passed=False, errors=1)
        result["consistency"] = consistency
    return result


def operations(
    store: Path,
    prepared_dir: Path,
    tables: Mapping[str, pl.DataFrame],
    health: Callable[[], Response | tuple[Response, int] | str],
    collector: PerformanceMetricsCollector | None,
) -> Blueprint:
    """Expose operator-enabled validation and readback with UTC date filters."""
    api = Blueprint("operations", __name__, url_prefix="/api/microcosting")
    receipts = _Receipts(store)
    work = Lock()
    data = DataManager(prepared_dir.parent, create_directories=False)

    def run(
        kind: Kind, operation: Callable[[DataManager], dict[str, object]]
    ) -> Response:
        if not work.acquire(blocking=False):
            abort(429)
        try:
            start = perf_counter_ns()
            payload = receipts.record(kind, operation(data))
            if collector is not None:
                collector.record_metric(
                    f"{kind}.execution_time",
                    (perf_counter_ns() - start) / 1_000_000_000,
                )
            return jsonify(payload)
        finally:
            work.release()

    @api.errorhandler(BadRequest)
    def invalid(error: BadRequest) -> tuple[Response, int]:
        return jsonify(error=error.description), 400

    @api.errorhandler(ValidationError)
    def invalid_parameters(_error: ValidationError) -> tuple[Response, int]:
        return jsonify(error="Check the documented request parameters"), 400

    @api.post("/tests/run")
    def run_tests() -> Response:
        payload = _TestRequest.model_validate_json(_json_body())
        if len(set(payload.analysis_modules)) != len(payload.analysis_modules):
            raise BadRequest("Select distinct analysis modules")
        return run(
            "test",
            lambda data: diagnose(data, payload.test_type, payload.analysis_modules),
        )

    @api.get("/tests/results")
    def test_results() -> Response:
        suite = request.args.get("test_type")
        analysis = request.args.get("analysis_module")
        if (suite and suite not in {"integration", "end_to_end", "performance"}) or (
            analysis and analysis not in ANALYSES
        ):
            raise BadRequest("Invalid suite or analysis module")
        dates = _date_range("date_range")
        return jsonify(
            results=receipts.read(
                "test", dates, tag="$.analysis_modules", value=analysis, suite=suite
            )
        )

    @api.post("/performance/benchmark")
    def benchmark() -> Response:
        payload = _BenchmarkRequest.model_validate_json(_json_body())

        def execute(data: DataManager) -> dict[str, object]:
            cost_driver = measure((payload.data_set_size,), repeats=3)
            start = perf_counter_ns()
            draws = synthetic_psa(data, payload.iterations)
            elapsed = max(1, perf_counter_ns() - start)
            if len(draws) != payload.iterations or not 526 < draws.mean() < 534:
                raise RuntimeError(
                    "The synthetic PSA workload differs from its reference"
                )
            return {
                "analysis_modules": ["cost_driver", "psa"],
                "cost_driver": cost_driver.model_dump(mode="json"),
                "psa": {"iterations": len(draws), "elapsed_ns": elapsed},
            }

        return run("benchmark", execute)

    @api.get("/performance/metrics")
    def performance_metrics() -> Response:
        analysis = request.args.get("analysis_type")
        if analysis and analysis not in ANALYSES:
            raise BadRequest("Invalid analysis type")
        dates = _date_range("time_range")
        return jsonify(
            benchmarks=receipts.read(
                "benchmark", dates, tag="$.analysis_modules", value=analysis
            ),
            diagnostics=receipts.read(
                "test", dates, tag="$.analysis_modules", value=analysis
            ),
        )

    api.add_url_rule("/monitoring/health", "health", health)

    @api.get("/monitoring/metrics")
    def monitoring_metrics() -> Response:
        selected = request.args.get("metric_type")
        if selected not in {None, "memory", "cpu", "execution_time"}:
            raise BadRequest("Invalid metric type")
        values: dict[str, object] = {}
        if selected in {None, "memory"}:
            values["memory"] = {"system_percent": psutil.virtual_memory().percent}
        if selected in {None, "cpu"}:
            values["cpu"] = {"system_percent": psutil.cpu_percent(interval=0.01)}
        if selected in {None, "execution_time"}:
            summary = collector.get_metrics_summary() if collector is not None else {}
            values["execution_time"] = {
                name: stats
                for name, stats in summary.items()
                if name.endswith(".execution_time")
            }
        return jsonify(values)

    @api.get("/monitoring/data-quality")
    def monitoring_quality() -> Response:
        name = request.args.get("sheet_name")
        if name is not None and name not in tables:
            abort(404)
        return jsonify(
            results=receipts.read(
                "quality", _DateRange(), tag="$.sheet_names", value=name
            )
        )

    @api.post("/data-quality/validate")
    def validate() -> Response:
        payload = _QualityRequest.model_validate_json(_json_body())
        names = list(dict.fromkeys(payload.sheet_names))
        types = list(dict.fromkeys(payload.validation_types))
        if any(name not in tables for name in names):
            raise BadRequest("Choose a listed prepared sheet")

        return run(
            "quality",
            lambda data: {
                "sheet_names": names,
                "validation_types": types,
                "sheets": [
                    _quality(data, prepared_dir, name, tables[name], types)
                    for name in names
                ],
            },
        )

    @api.get("/data-quality/reports")
    def quality_reports() -> Response:
        return jsonify(results=receipts.read("quality", _date_range("date_range")))

    return api
