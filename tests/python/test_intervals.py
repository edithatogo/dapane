"""Exercise interval profile 0.3 through the installed native Python wheel."""

from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

import dapane

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
INTERVALS = FIXTURES / "intervals"
EXPECTED = json.loads((INTERVALS / "expected.json").read_text(encoding="utf-8"))["cases"]


def request(name: str) -> dict:
    return json.loads((INTERVALS / name).read_text(encoding="utf-8"))


def check_reference(report: dict, expected: dict) -> None:
    assert report["schema_version"] == "0.3"
    assert report["method_version"] == "dapane-exact-v0.3.0"
    assert report["status"] == "complete"
    assert report["lines"] == []
    assert report["totals"] == expected["totals"]
    lines = {line["id"]: line for line in report["interval_lines"]}
    assert set(lines) == set(expected["interval_lines"])
    for line_id, fields in expected["interval_lines"].items():
        for name, value in fields.items():
            assert lines[line_id][name] == value
    if "allocation_shares" in expected:
        assert {
            share["object_id"]: share["rounded"]
            for share in report["allocations"][0]["shares"]
        } == expected["allocation_shares"]


@pytest.mark.parametrize("name", ["rate-boundary.json", "rational.json", "rounding.json"])
def test_interval_references_through_both_installed_entrypoints(name: str) -> None:
    supplied = request(name)
    original = deepcopy(supplied)
    report = dapane.evaluate(supplied)
    check_reference(report, EXPECTED[name])
    assert json.loads(dapane.evaluate_json(json.dumps(supplied))) == report
    assert supplied == original


def test_fraction_and_decimal_interval_quantities_remain_exact() -> None:
    for name, quantity in (
        ("rational.json", Fraction(1, 3)),
        ("rate-boundary.json", Decimal("10.00")),
    ):
        supplied = request(name)
        supplied["interval_usage"][0]["quantity"] = quantity
        report = dapane.evaluate(supplied)
        check_reference(report, EXPECTED[name])
        assert supplied["interval_usage"][0]["quantity"] == quantity


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("missing_exposure", "invalid_request"),
        ("unsupported_exposure", "invalid_request"),
        ("gap", "interval_gap"),
    ],
)
def test_interval_errors_preserve_native_structured_diagnostics(mutation: str, code: str) -> None:
    supplied = request("rate-boundary.json")
    if mutation == "missing_exposure":
        del supplied["interval_usage"][0]["exposure"]
    elif mutation == "unsupported_exposure":
        supplied["interval_usage"][0]["exposure"] = "business_days"
    else:
        supplied["quotes"][0]["valid_to"] = "2026-01-04"
    for evaluate, argument in (
        (dapane.evaluate, supplied),
        (dapane.evaluate_json, json.dumps(supplied)),
    ):
        with pytest.raises(dapane.DapaneError) as caught:
            evaluate(argument)
        diagnostic = caught.value
        assert diagnostic.code == code
        assert diagnostic.message
        assert diagnostic.path.startswith("/")
        assert diagnostic.as_dict() == {
            "code": diagnostic.code,
            "message": diagnostic.message,
            "path": diagnostic.path,
        }


def test_old_profiles_reject_even_empty_interval_transport() -> None:
    for version in ("0.1", "0.2"):
        supplied = json.loads((FIXTURES / "workforce.json").read_text(encoding="utf-8"))
        supplied["schema_version"] = version
        supplied["interval_usage"] = []
        for evaluate, argument in (
            (dapane.evaluate, supplied),
            (dapane.evaluate_json, json.dumps(supplied)),
        ):
            with pytest.raises(dapane.DapaneError) as caught:
                evaluate(argument)
            assert caught.value.code == "invalid_request"
            assert caught.value.path == "/interval_usage"
