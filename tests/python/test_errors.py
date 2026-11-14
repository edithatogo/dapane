"""Installed-boundary diagnostics and rejection of ambiguous exact values."""

import copy
import json
import pickle
from decimal import Decimal

import pytest

import dapane
from dapane import _native


@pytest.mark.parametrize(
    "quantity, code",
    [
        (None, "invalid_request"),
        (True, "invalid_request"),
        (1, "invalid_request"),
        ("-1", "invalid_number"),
        ({"numerator": "1", "denominator": "0"}, "zero_denominator"),
        ("1" * 97, "precision_limit"),
    ],
)
def test_invalid_exact_values_keep_native_diagnostics(quantity, code, load_request):
    request = load_request("workforce.json")
    request["usage"][0]["quantity"] = quantity
    encoded = json.dumps(request)
    with pytest.raises(_native.CoreError) as native:
        _native.evaluate_json(encoded)
    with pytest.raises(dapane.DapaneError) as public:
        dapane.evaluate_json(encoded)
    assert public.value.code == code
    assert public.value.as_dict() == json.loads(str(native.value))
    assert public.value.path.startswith("/")
    assert public.value.message


@pytest.mark.parametrize("quantity", [0.1, float("nan"), float("inf"), float("-inf")])
def test_python_float_values_are_never_silently_coerced(quantity, load_request):
    request = load_request("workforce.json")
    request["usage"][0]["quantity"] = quantity
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "invalid_transport"
    assert caught.value.path == "/usage/0/quantity"


@pytest.mark.parametrize("quantity", [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity")])
def test_nonfinite_decimal_values_fail_at_transport(quantity, load_request):
    request = load_request("workforce.json")
    request["usage"][0]["quantity"] = quantity
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "invalid_transport"
    assert caught.value.path == "/usage/0/quantity"


def test_decimal_exponent_cannot_force_unbounded_string_expansion(load_request):
    request = load_request("workforce.json")
    request["usage"][0]["quantity"] = Decimal("1E+999999999")
    with pytest.raises(dapane.DapaneError, match="transport limit"):
        dapane.evaluate(request)


def test_missing_quantity_differs_from_explicit_zero(load_request):
    request = load_request("workforce.json")
    del request["usage"][0]["quantity"]
    with pytest.raises(dapane.DapaneError) as missing:
        dapane.evaluate(request)
    assert missing.value.code == "invalid_request"
    request["usage"][0]["quantity"] = "0"
    report = dapane.evaluate(request)
    assert report["totals"]["rounded"] == "0.00"
    assert len(report["lines"]) == 1


@pytest.mark.parametrize(
    "section, field, value, code",
    [
        ("usage", "unit", "minute", "quote_mismatch"),
        ("usage", "service_date", "2027-01-01", "quote_not_effective"),
        ("usage", "quote_id", "absent-quote", "missing_quote"),
        ("quotes", "known_from", "2027-01-01", "quote_not_known"),
        ("quotes", "basis", "funding", "valuation_mismatch"),
    ],
)
def test_policy_unit_and_date_errors_remain_structured(section, field, value, code, load_request):
    request = load_request("workforce.json")
    request[section][0][field] = value
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == code
    assert caught.value.path.startswith("/")


def test_duplicate_use_components_are_not_charged_twice(load_request):
    request = load_request("workforce.json")
    duplicate = copy.deepcopy(request["usage"][0])
    duplicate["id"] = "a-second-valuation-line"
    request["usage"].append(duplicate)
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "component_overlap"


def test_unresolved_object_context_is_an_error(load_request):
    request = load_request("newborn-screening.json")
    request["usage"][0]["object_ids"].append("unknown-infant")
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "unknown_reference"


def test_duplicate_pool_source_cannot_double_allocation(load_request):
    request = load_request("newborn-screening.json")
    duplicate = copy.deepcopy(request["allocations"][0])
    duplicate["id"] = "second-pool"
    request["allocations"].append(duplicate)
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "allocation_overlap"


def test_unknown_fields_and_unsupported_schema_are_rejected(load_request):
    request = load_request("workforce.json")
    request["schema_version"] = "999"
    with pytest.raises(dapane.DapaneError) as version:
        dapane.evaluate(request)
    assert version.value.code == "unsupported_schema"
    request["schema_version"] = "0.1"
    request["execute_bpmn"] = True
    with pytest.raises(dapane.DapaneError) as field:
        dapane.evaluate(request)
    assert field.value.code == "invalid_request"


def test_duplicate_json_keys_are_not_overwritten(load_request):
    encoded = json.dumps(load_request("workforce.json"))
    encoded = encoded.replace(
        '"schema_version": "0.1"',
        '"schema_version": "0.1", "schema_version": "0.1"',
        1,
    )
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate_json(encoded)
    assert caught.value.code == "invalid_json"
    assert "duplicate" in caught.value.message.lower()


@pytest.mark.parametrize("payload", [[], "{}", None])
def test_dictionary_entry_requires_a_dictionary(payload):
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(payload)
    assert caught.value.code == "invalid_transport"


@pytest.mark.parametrize("value", [{1: "ambiguous-key"}, {"unsupported": {"set-value"}}])
def test_unrepresentable_python_containers_fail_cleanly(value):
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(value)
    assert caught.value.code == "invalid_transport"


def test_cyclic_container_fails_without_recursion_crash():
    request = {}
    request["cycle"] = request
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate(request)
    assert caught.value.code == "invalid_transport"
    assert caught.value.path == "/cycle"


def test_invalid_unicode_in_raw_json_has_a_transport_diagnostic():
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate_json('"\ud800"')
    assert caught.value.code == "invalid_transport"


def test_structured_errors_survive_pickle_and_do_not_poison_later_calls(load_request):
    with pytest.raises(dapane.DapaneError) as caught:
        dapane.evaluate_json("{not-json}")
    restored = pickle.loads(pickle.dumps(caught.value))
    assert restored.as_dict() == caught.value.as_dict()
    assert dapane.evaluate(load_request("workforce.json"))["totals"]["rounded"] == "30.00"
