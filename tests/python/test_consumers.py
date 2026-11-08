"""Independent arithmetic and installation checks, with synthetic inputs only."""

import copy
import importlib.machinery
import importlib.metadata
import json
from concurrent.futures import ThreadPoolExecutor
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction
from pathlib import Path

import pytest

import dapane
from dapane import _native

FIXTURES = [
    "workforce.json",
    "genomics.json",
    "activity-funding.json",
    "newborn-screening.json",
    "subcent-allocation.json",
]


def fraction(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def test_imports_resolve_to_an_installed_native_distribution():
    distribution = importlib.metadata.distribution("dapane")
    installation = Path(distribution.locate_file("")).resolve()
    assert Path(dapane.__file__).resolve().is_relative_to(installation)
    assert Path(_native.__file__).resolve().is_relative_to(installation)
    assert any(
        _native.__file__.endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES
    )
    assert distribution.version == dapane.__version__
    assert (Path(dapane.__file__).parent / "py.typed").is_file()


@pytest.mark.parametrize("name", FIXTURES)
def test_installed_consumers_match_independent_fixture_totals(name, load_request, expected_cases):
    request = load_request(name)
    before = copy.deepcopy(request)
    report = dapane.evaluate(request)
    assert report["totals"] == expected_cases[name]["totals"]
    assert report["status"] == "complete"
    assert report["engine_version"] == dapane.__version__
    assert report["policy"] == request["policy"]
    assert request == before
    assert report == json.loads(dapane.evaluate_json(json.dumps(request)))
    # Allocation/object views must reconcile with the source ledger, not augment it.
    object_sum = sum(Fraction(item["total"]) for item in report["object_totals"])
    assert object_sum + Fraction(report["totals"]["unattributed"]) == Fraction(
        report["totals"]["rounded"]
    )


def test_workforce_fractional_hours_are_exact(load_request):
    report = dapane.evaluate(load_request("workforce.json"))
    # Independent unit arithmetic: twenty minutes is one third of an hour.
    expected = Fraction(20, 60) * 90
    assert fraction(report["lines"][0]["quantity"]) == Fraction(1, 3)
    assert fraction(report["totals"]["exact"]) == expected == 30


def test_disjoint_components_share_resolved_event_context(load_request):
    request = load_request("workforce.json")
    request["processes"] = [{"id": "p", "model_id": "staff-work", "model_version": "1"}]
    request["events"] = [
        {"id": "e", "occurred_on": "2026-06-15", "process_id": "p", "activity_id": "work"}
    ]
    # Salary inherits its process/activity context from the event. The on-cost
    # component declares the same context explicitly for the same underlying use.
    request["usage"][0]["event_id"] = "e"
    oncost_quote = copy.deepcopy(request["quotes"][0])
    oncost_quote.update(id="oncost-rate", amount="9.00", components=["oncost"])
    request["quotes"].append(oncost_quote)
    oncost_line = copy.deepcopy(request["usage"][0])
    oncost_line.update(id="oncost-line", quote_id="oncost-rate", process_id="p", activity_id="work")
    request["usage"].append(oncost_line)
    report = dapane.evaluate(request)
    assert fraction(report["totals"]["exact"]) == Fraction(20, 60) * (90 + 9) == 33
    assert report["totals"]["rounded"] == "33.00"
    assert len(report["lines"]) == 2
    assert all(line["process_id"] == "p" for line in report["lines"])
    assert all(line["activity_id"] == "work" for line in report["lines"])
    assert all(line["event_id"] == "e" for line in report["lines"])


def test_genomics_shared_batch_is_charged_once(load_request):
    report = dapane.evaluate(load_request("genomics.json"))
    # One batch plus two collections, each attributable to a different specimen.
    assert fraction(report["totals"]["exact"]) == Fraction(100) + 2 * Fraction(10)
    objects = {item["object_id"]: item["total"] for item in report["object_totals"]}
    assert objects == {"specimen-a": "60.00", "specimen-b": "60.00", "batch-1": "0.00"}
    assert len(report["lines"]) == 3


def test_activity_funding_does_not_invent_physical_resources(load_request):
    report = dapane.evaluate(load_request("activity-funding.json"))
    assert fraction(report["totals"]["exact"]) == Fraction("2.50") * 17 == Fraction(85, 2)
    assert report["policy"]["basis"] == "funding"
    assert {line["kind"] for line in report["lines"]} == {"activity_measure"}
    assert report["context"]["objects"] == []
    assert report["object_totals"] == []


def test_newborn_event_process_and_object_views_preserve_one_ledger(load_request):
    request = load_request("newborn-screening.json")
    report = dapane.evaluate(request)
    assert fraction(report["totals"]["exact"]) == 2 * Fraction(10) + 100 + 30 == 150
    objects = {item["object_id"]: item["total"] for item in report["object_totals"]}
    assert objects["infant-a"] == "60.00"
    assert objects["infant-b"] == "90.00"
    assert all(value == "0.00" for key, value in objects.items() if not key.startswith("infant-"))
    assert {event["id"] for event in report["context"]["events"]} == {
        line["event_id"] for line in report["lines"]
    }
    assert {line["process_id"] for line in report["lines"]} == {"screening-process"}
    assert len(report["context"]["object_relations"]) == len(request["object_relations"])
    assert report["allocations"][0]["pool_rounded"] == "100.00"
    assert report["allocations"][0]["residual"] == "0.00"


def test_subcent_allocation_conserves_five_cents_with_stable_ties(load_request):
    request = load_request("subcent-allocation.json")
    report = dapane.evaluate(request)
    shares = report["allocations"][0]["shares"]
    assert {item["object_id"]: item["rounded"] for item in shares} == {
        "a": "0.02",
        "b": "0.02",
        "c": "0.01",
    }
    assert all(fraction(item["exact_share"]) == Fraction(1, 60) for item in shares)
    assert sum(Fraction(item["rounded"]) for item in shares) == Fraction(1, 20)
    request["allocations"][0]["weights"].reverse()
    assert dapane.evaluate(request) == report


@pytest.mark.parametrize("amount", ["0.005", "0.015", "0.025", "0.035"])
def test_rounding_matches_independent_decimal_half_even(amount, load_request):
    request = load_request("workforce.json")
    request["quotes"][0]["amount"] = amount
    request["usage"][0]["quantity"] = "1"
    report = dapane.evaluate(request)
    expected = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    assert report["totals"]["rounded"] == str(expected)
    assert fraction(report["totals"]["exact"]) == Fraction(amount)


def test_decimal_and_fraction_inputs_are_only_transport_conversions(load_request):
    request = load_request("workforce.json")
    baseline = dapane.evaluate(request)
    request["usage"][0]["quantity"] = Fraction(20, 60)
    request["quotes"][0]["amount"] = Decimal("90.00")
    before = copy.deepcopy(request)
    assert dapane.evaluate(request) == baseline
    assert request == before


def test_decimal_exponent_is_expanded_before_native_transport(load_request):
    request = load_request("workforce.json")
    request["quotes"][0]["amount"] = Decimal("9E+1")
    request["usage"][0]["quantity"] = Fraction(1, 3)
    report = dapane.evaluate(request)
    assert report["totals"]["rounded"] == "30.00"
    assert report["quote_snapshots"][0]["amount"] == "90"


def test_concurrent_calls_have_owned_inputs_and_deterministic_results(load_request):
    encoded = json.dumps(load_request("newborn-screening.json"))
    baseline = dapane.evaluate_json(encoded)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(dapane.evaluate_json, [encoded] * 16))
    assert all(result == baseline for result in results)


def test_canonical_result_ignores_key_and_collection_order(load_request):
    request = load_request("newborn-screening.json")
    baseline = dapane.evaluate_json(json.dumps(request))
    for key in ("quotes", "usage", "objects", "processes", "events", "object_relations"):
        request[key].reverse()
    assert dapane.evaluate_json(json.dumps(request, sort_keys=True)) == baseline


def test_valid_unicode_identifiers_round_trip(load_request):
    request = load_request("workforce.json")
    request["run_id"] = "laboratory-Δ"
    assert dapane.evaluate(request)["run_id"] == "laboratory-Δ"
