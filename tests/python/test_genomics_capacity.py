"""Synthetic candidate scenarios through an installed wheel; no provider data."""

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

import dapane

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures" / "genomics-capacity"
CASES = json.loads((FIXTURES / "expected.json").read_text())["cases"]


def load(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(scope="module")
def schemas():
    documents = {}
    registry = Registry()
    # Local resources only; schema $ids are identifiers, not network fetches.
    for path in (ROOT / "schemas").rglob("*.schema.json"):
        value = json.loads(path.read_text())
        Draft202012Validator.check_schema(value)
        documents[str(path.relative_to(ROOT / "schemas"))] = value
        registry = registry.with_resource(value["$id"], Resource.from_contents(value))
    return {
        name: Draft202012Validator(value, registry=registry, format_checker=FormatChecker())
        for name, value in documents.items()
    }


def exact(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


@pytest.mark.parametrize("name", CASES)
def test_installed_genomics_cases_match_independent_results_and_schemas(name, schemas):
    request, expected = load(name), CASES[name]
    version = request["schema_version"]
    schemas[f"{version}/request.schema.json"].validate(request)
    report = dapane.evaluate(request)
    schemas[f"{version}/report.schema.json"].validate(report)
    assert report == json.loads(dapane.evaluate_json(json.dumps(request)))
    assert report["totals"]["rounded"] == expected["total"]
    assert report["totals"]["allocated"] == expected["allocated"]
    assert report["totals"]["unattributed"] == expected["unattributed"]
    pool = report["capacity_allocations" if version == "0.2" else "allocations"][0]
    assert pool["pool_rounded"] == expected["pool"]
    shares = {share["object_id"]: share["rounded"] for share in pool["shares"]}
    assert shares == expected["shares"]
    remaining = pool["unallocated" if version == "0.2" else "residual"]
    assert remaining == expected["unallocated"]
    assert sum(Fraction(value) for value in shares.values() if value is not None) + Fraction(
        remaining
    ) == Fraction(pool["pool_rounded"])
    assert sum(Fraction(obj["total"]) for obj in report["object_totals"]) + Fraction(
        report["totals"]["unattributed"]
    ) == Fraction(report["totals"]["rounded"])
    # Independent digest check; this is transport verification, not a value oracle.
    payload = {key: value for key, value in report.items() if key != "output_digest"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(f"dapane:output:{version}\n{encoded}".encode()).hexdigest()
    assert report["output_digest"] == f"sha256:{digest}"
    assert all(
        quote["source"]["evidence"] == "synthetic"
        and quote["source"]["validation"] == "unvalidated"
        for quote in report["quote_snapshots"]
    )


def test_candidate_preparation_separates_useful_life_contract_term_and_recurrence(schemas):
    scenario = load("scenario.json")
    schemas["scenarios/genomics-candidate-v0.1.schema.json"].validate(scenario)
    assert set(scenario["requests"]) == set(CASES)
    device, maintenance = scenario["device"], scenario["maintenance"]
    # Independent candidate arithmetic in tests only. The runtime accepts prepared
    # quotes; it does not implement these economic preparation methods.
    device_month = Fraction(device["purchase_amount"]) / Fraction(device["useful_life_months"])
    maintenance_month = Fraction(maintenance["contract_amount"]) / Fraction(
        maintenance["contract_duration_months"]
    )
    assert device_month == Fraction(device["candidate_monthly_charge"]) == 200
    assert maintenance_month == Fraction(maintenance["candidate_monthly_charge"]) == 100
    assert Fraction(maintenance["contract_amount"]) / Fraction(device["useful_life_months"]) == 40
    assert scenario["implementation"]["recurrence"] == "one_time"
    assert not scenario["implementation"]["included_in_recurring_pool"]
    for name in CASES:
        request = load(name)
        quotes = {quote["id"]: quote for quote in request["quotes"]}
        assert Fraction(quotes["device-period-quote"]["amount"]) == device_month
        assert Fraction(quotes["maintenance-period-quote"]["amount"]) == maintenance_month
        if name == "sample-full-recurring.json":
            assert "implementation-quote" not in quotes
            assert {line["id"] for line in request["usage"]} == {
                "device-period",
                "maintenance-period",
            }
        else:
            assert quotes["implementation-quote"]["amount"] == scenario["implementation"]["amount"]
        for pool in request.get("allocations", []) + request.get("capacity_allocations", []):
            assert set(pool["source_line_ids"]) == {"device-period", "maintenance-period"}
    # A preparation manifest cannot accidentally be evaluated as a valuation request.
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(scenario)


def test_missing_observation_is_not_zero_and_does_not_establish_idle_capacity():
    request = load("time-missing-use.json")
    report = dapane.evaluate(request)
    pool = report["capacity_allocations"][0]
    assert pool["observation_coverage"] == "incomplete"
    assert exact(pool["accounted_quantity"]) == 10
    assert exact(pool["unaccounted_quantity"]) == 90
    assert pool["shares"][1]["quantity"] == {
        "status": "unknown",
        "reason": "instrument-duration-not-recorded",
    }
    assert pool["shares"][1]["exact_share"] is None
    assert pool["shares"][1]["rounded"] is None
    assert "utilization" not in pool
    assert "idle_hours" not in pool
    # Object totals are assigned ledger values only, not estimates of true cost.
    assert report["object_totals"][1]["total"] == "0.00"


def test_capacity_denominator_is_independent_of_observed_weights():
    request = load("time-known.json")
    request["capacity_allocations"][0]["available_capacity"]["quantity"] = Fraction(200)
    report = dapane.evaluate(request)
    pool = report["capacity_allocations"][0]
    assert [share["rounded"] for share in pool["shares"]] == ["15.00", "30.00"]
    assert pool["unallocated"] == "255.00"
    samples = load("sample-full-first.json")
    before = dapane.evaluate(samples)
    samples["allocations"][0]["weights"][0]["weight"] = "200"
    samples["allocations"][0]["weights"][1]["weight"] = "300"
    after = dapane.evaluate(samples)
    assert before["object_totals"] == after["object_totals"]
    assert after["allocations"][0]["residual"] == "0.00"


@pytest.mark.parametrize(
    "mutation",
    [
        {"unit": "sample"},
        {"unit": "hour"},
        {"observation_coverage": "complete"},
        {"available_capacity": None},
        {"available_capacity": {"status": "known", "quantity": 100}},
        {"available_capacity": {"status": "unknown", "reason": "missing", "quantity": "100"}},
        {"available_capacity": {"status": "known", "quantity": "0"}},
        {"sample_throughput": "50"},
        {"utilization": "0.3"},
        {"mode": "normalize_to_observed"},
    ],
)
def test_unsupported_capacity_structure_is_rejected_by_schema_and_native(mutation, schemas):
    request = load("time-known.json")
    request["capacity_allocations"][0].update(copy.deepcopy(mutation))
    assert not schemas["0.2/request.schema.json"].is_valid(request)
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(request)


def test_capacity_extension_cannot_be_silently_downgraded(schemas):
    request = load("time-known.json")
    request["schema_version"] = "0.1"
    assert not schemas["0.1/request.schema.json"].is_valid(request)
    with pytest.raises(dapane.DapaneError) as error:
        dapane.evaluate(request)
    assert error.value.code == "invalid_request"


def test_v02_keeps_explicit_full_pool_allocations_compatible():
    request = load("sample-full-first.json")
    v01 = dapane.evaluate(request)
    request["schema_version"] = "0.2"
    v02 = dapane.evaluate(request)
    assert v02["method_version"] == "dapane-exact-v0.2.0"
    assert v02["allocations"] == v01["allocations"]
    assert v02["totals"] == v01["totals"]
    assert v02["input_digest"] != v01["input_digest"]
    assert v02["output_digest"] != v01["output_digest"]
