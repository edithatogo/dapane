"""Adapt Innovate's cumulative monthly Bass forecast to the declared resource schedule."""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from bridge import (
    INNOVATE_PREDICTION,
    SUPPORTED,
    _bad,
    _closed_output,
    _digest,
    _f64,
    _fraction,
    _key,
    _object,
    _provider_executable,
    adoption_capacity,
    negotiate,
)

SCHEMA = "dapane-d2-innovate-prediction/0.1"
REVISION = "fd7e259bb9a685d620f80907c6815d4837da3e53"
DOMAIN = "dapane:d2-innovate-prediction:0.1\n"


def _verify_receipt(report, domain, expected, key):
    if not isinstance(report, dict) or report.get("key") != key:
        _bad("feedback_chain", "/key", "Prior report must identify the same decision cell")
    body = dict(report)
    digest = body.pop("output_digest", None)
    if not digest or digest != expected or _digest(domain, body) != digest:
        _bad("feedback_chain", "/output_digest", "Prior report differs from its declared digest")


def _prior_digest(request, previous, valuation):
    if request["iteration"] == 0:
        if previous is not None or valuation is not None:
            _bad("feedback_chain", "/iteration", "Initial forecast has no earlier reports")
        return None
    digest = request["previous_evaluation_digest"]
    _verify_receipt(previous, DOMAIN, digest, request["key"])
    if (
        previous.get("run_id") != request["run_id"]
        or previous.get("schema_version") != SCHEMA
        or previous.get("iteration") != request["iteration"] - 1
        or previous.get("provider", {}).get("artifact_digest")
        != request["provider"]["artifact_digest"]
    ):
        _bad("feedback_chain", "/previous_evaluation_digest", "Run, caller or iteration changed")
    domains = {
        "dapane-fiscal/0.1": "dapane:fiscal-output:0.1\n",
        "dapane-fiscal/0.2": "dapane:fiscal-output:0.2\n",
    }
    domain = domains.get(valuation.get("schema_version")) if isinstance(valuation, dict) else None
    if domain is None or valuation.get("status") != "complete":
        _bad("feedback_chain", "/feedback", "A complete fiscal valuation is required")
    feedback = _object(
        request["feedback"], "/feedback", {"mode", "valuation_digest", "price_affects_adoption"}
    )
    _verify_receipt(valuation, domain, feedback["valuation_digest"], request["key"])
    return digest


def _parameters(model):
    model = _object(model, "/model", {"model_key", "p", "q", "m", "count_policy"})
    if model["model_key"] != "bass" or model["count_policy"] != "floor_cumulative":
        _bad("unsupported_method", "/model", "Select Bass and cumulative whole-person flooring")
    market = model["m"]
    if type(market) is not int or not 1 <= market <= 10**9:
        _bad(
            "invalid_market",
            "/model/m",
            "Expected a positive integer population at most one billion",
        )
    result = {"m": market}
    for name in ("p", "q"):
        rate = _fraction(model[name], "/model/" + name, nonnegative=True)
        if rate > 1 or (name == "p" and not rate):
            _bad("invalid_rate", "/model/" + name, "Expected monthly p in (0,1] and q in [0,1]")
        result[name] = _f64(rate, "/model/" + name)
    return result


def _counts(binary, parameters, periods):
    request = {
        "schema_version": "2.0",
        "operation": "predict_model",
        "model_key": "bass",
        "payload": {"inputs": {"time": list(range(periods + 1))}, "parameters": parameters},
    }
    with TemporaryDirectory() as directory:
        src, dst = Path(directory) / "input.json", Path(directory) / "result.json"
        src.write_text(json.dumps(request), encoding="utf-8")
        result = subprocess.run(
            [binary, "predict", "--request", str(src), "--output", str(dst)],
            capture_output=True,
            timeout=60,
        )
        if result.returncode:
            _bad("native_provider_failed", "/", f"Innovate exited {result.returncode}")
        if not dst.is_file() or dst.stat().st_size > 1024 * 1024:
            _bad("native_provider_error", "/", "Forecast output missing or oversized")
        answer = json.loads(dst.read_text(encoding="utf-8"))
    if (
        not isinstance(answer, dict)
        or answer.get("schema_version") != "2.0"
        or answer.get("operation") != "predict_model"
    ):
        _bad("native_provider_error", "/", "Unexpected forecast response")
    meta, data = answer.get("metadata"), answer.get("result")
    if (
        not isinstance(meta, dict)
        or meta.get("model_key") != "bass"
        or meta.get("runtime") != "rust_native"
        or not isinstance(data, dict)
        or data.get("shape") != [periods + 1]
    ):
        _bad("native_provider_error", "/", "Unexpected model, runtime or output shape")
    values = data.get("values")
    if not isinstance(values, list) or len(values) != periods + 1:
        _bad("native_provider_error", "/", "Invalid cumulative series length")
    previous = 0
    incident = []
    for index, current in enumerate(values):
        if (
            type(current) not in (int, float)
            or not math.isfinite(current)
            or not previous <= current <= parameters["m"]
            or (index == 0 and current != 0)
        ):
            _bad(
                "invalid_trajectory",
                "/result/values",
                "Expected bounded nondecreasing cumulative adoption from zero",
            )
        if index:
            incident.append(math.floor(current) - math.floor(previous))
        previous = current
    return values, incident


def predict_capacity(payload, binary, previous, valuation):
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA:
        _bad(
            "unsupported_schema",
            "/schema_version",
            "Use the prediction schema for native forecasts and adoption_capacity for supplied observations",
        )
    request = _object(
        payload,
        "/",
        {
            "schema_version",
            "provider",
            "run_id",
            "iteration",
            "previous_evaluation_digest",
            "key",
            "resource",
            "feedback",
            "periods",
            "model",
        },
    )
    pin = negotiate(request["provider"])
    if (
        pin["provider"] != "edithatogo/innovate"
        or pin["revision"] != REVISION
        or pin["method"] != INNOVATE_PREDICTION[1]
    ):
        _bad("unsupported_provider", "/provider", "Use the qualified Innovate revision")
    parameters = _parameters(request["model"])
    _key(request["key"], "/key")
    periods = request["periods"]
    if not isinstance(periods, list) or not 1 <= len(periods) <= 120:
        _bad("invalid_period_sequence", "/periods", "Expected one to 120 consecutive months")
    if type(request["iteration"]) is not int or not 0 <= request["iteration"] <= 16:
        _bad("invalid_iteration", "/iteration", "Expected iteration 0..16")
    prior = _prior_digest(request, previous, valuation)
    setup = {k: v for k, v in request.items() if k not in {"periods", "model"}}
    setup.update(
        schema_version="dapane-d2-innovate/0.1",
        observations=[{"period": p, "new_adoptions": 0} for p in periods],
    )
    contract, method = SUPPORTED["edithatogo/innovate"]
    setup["provider"] = {**request["provider"], "contract": contract, "method": method}
    adoption_capacity(setup, expected_previous_digest=prior)
    months = [int(p[:4]) * 12 + int(p[5:]) for p in periods]
    if any(b != a + 1 for a, b in zip(months, months[1:])):
        _bad("invalid_period_sequence", "/periods", "Bass time steps must be contiguous months")
    executable = _provider_executable(binary, pin["artifact_digest"])
    cumulative, incident = _counts(executable, parameters, len(periods))
    for row, count in zip(setup["observations"], incident, strict=True):
        row["new_adoptions"] = count
    output = adoption_capacity(setup, expected_previous_digest=prior)
    del output["output_digest"]
    output.update(
        schema_version=SCHEMA,
        provider=pin,
        provider_execution="native_predict_model",
        model=request["model"],
        provider_operation="predict_model",
        cumulative_adoption=cumulative,
    )
    return _closed_output(DOMAIN, output)
