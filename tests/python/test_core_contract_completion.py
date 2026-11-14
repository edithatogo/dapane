"""Synthetic core-contract acceptance against the installed Rust wheel."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE_REVISION = "ae00b2e37802a43d29c58729875aff961ff3ae54"
REFERENCES = ROOT / "fixtures/core-contracts/references.json"


def interval_request():
    """Authored oracle: 1/3 h * 90 + 2/3 h * 120 = 110, not legacy output."""
    return json.loads(REFERENCES.read_text())["request"]


def seal(bundle):
    """Independent transport oracle, not the verifier's digest implementation."""
    payload = {key: value for key, value in bundle.items() if key != "bundle_digest"}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(("dapane:run-bundle:0.1\n" + encoded).encode("utf-8")).hexdigest()
    bundle["bundle_digest"] = "sha256:" + digest
    return bundle


def bundle_for(request=None):
    import dapane

    request = interval_request() if request is None else copy.deepcopy(request)
    return seal(
        {
            "bundle_version": "0.1",
            "bundle_id": "original",
            "series_id": "synthetic-series",
            "recorded_on": "2026-02-02",
            "change": "create",
            "previous_digest": None,
            "reason": None,
            "source_revision": SOURCE_REVISION,
            "qualification": "synthetic_candidate",
            "observation_window": {"from": "2026-01-31", "to": "2026-02-02"},
            "rate_releases": [
                {
                    "source_id": quote["source"]["id"],
                    "version": quote["source"]["version"],
                    "quote_ids": [quote["id"]],
                    "published_on": "2026-01-01",
                    "retrieved_on": "2026-02-02",
                }
                for quote in request["quotes"]
            ],
            "capital_treatments": [],
            "excluded_inputs": [
                {"id": "family-time", "state": "excluded", "reason": "provider perspective"},
            ],
            "request": request,
            "report": dapane.evaluate(request),
        }
    )


def history():
    import dapane

    first = bundle_for()
    second = copy.deepcopy(first)
    second.update(
        bundle_id="replacement",
        change="replace",
        recorded_on="2026-02-10",
        previous_digest=first["bundle_digest"],
        reason="correct recorded duration",
    )
    second["request"]["run_id"] = "corrected-interval"
    second["request"]["knowledge_cutoff"] = "2026-02-10"
    second["request"]["usage"][0]["quantity"] = {"numerator": "1", "denominator": "2"}
    second["report"] = dapane.evaluate(second["request"])
    seal(second)
    third = copy.deepcopy(second)
    third.update(
        bundle_id="withdrawn",
        change="retract",
        recorded_on="2026-02-12",
        previous_digest=second["bundle_digest"],
        reason="withdraw synthetic candidate",
        request=None,
        report=None,
        observation_window=None,
        rate_releases=[],
        capital_treatments=[],
        excluded_inputs=[],
    )
    seal(third)
    return [first, second, third]


@pytest.fixture
def contract():
    path = ROOT / "scripts/verify_run_bundle.py"
    assert path.is_file(), "C2.3: immutable bundle verifier is not implemented"
    spec = importlib.util.spec_from_file_location("dapane_bundle_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bundle_contract_artifacts_exist():
    assert (ROOT / "schemas/bundles/0.1.schema.json").is_file(), "C2.3 bundle schema missing"
    assert (ROOT / "scripts/verify_run_bundle.py").is_file(), "C2.3 bundle verifier missing"


def test_presegmented_rate_boundary_has_independent_exact_result():
    import dapane

    request = interval_request()
    expected = json.loads(REFERENCES.read_text())["expected"]
    report = dapane.evaluate(request)
    assert report["totals"]["rounded"] == expected["original"] == "110.00"
    assert report["totals"]["exact"] == {"numerator": "110", "denominator": "1"}
    assert {line["id"]: line["rounded"] for line in report["lines"]} == {
        "before": "30.00",
        "after": "80.00",
    }
    request["usage"][0]["service_date"] = "2026-02-01"
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(request)


def test_bundle_replays_native_report_and_preserves_excluded_states(contract):
    bundle = bundle_for()
    bundle["excluded_inputs"].extend(
        [
            {"id": "missing-time", "state": "missing", "reason": "not recorded"},
            {"id": "inflation", "state": "unsupported", "reason": "no escalation method"},
        ]
    )
    seal(bundle)
    before = copy.deepcopy(bundle)
    assert contract.verify_bundle(bundle) == bundle["bundle_digest"]
    assert bundle == before
    assert bundle["report"]["totals"]["rounded"] == "110.00"


def test_replace_and_retract_preserve_history_without_summing(contract):
    records = history()
    expected = json.loads(REFERENCES.read_text())["expected"]
    assert records[0]["report"]["totals"]["rounded"] == expected["original"] == "110.00"
    assert records[1]["report"]["totals"]["rounded"] == expected["corrected"] == "125.00"
    checkpoint = records[-1]["bundle_digest"]
    for as_of, status, total in [
        ("2026-02-01", "not_yet_known", None),
        ("2026-02-02", "active", "110.00"),
        ("2026-02-10", "active", "125.00"),
        ("2026-02-12", "retracted", None),
    ]:
        selected = contract.verify_history(records, expected_head_digest=checkpoint, as_of=as_of)
        assert selected["status"] == status
        report = selected["report"]
        assert (report["totals"]["rounded"] if report else None) == total


@pytest.mark.parametrize(
    "mutation",
    [
        "digest",
        "report",
        "request",
        "release",
        "window",
        "future",
        "excluded",
        "version",
        "unknown_field",
    ],
)
def test_invalid_manifest_is_rejected(contract, mutation):
    bundle = bundle_for()
    if mutation == "digest":
        bundle["bundle_digest"] = "sha256:" + "0" * 64
    elif mutation == "report":
        bundle["report"]["totals"]["rounded"] = "999.00"
    elif mutation == "request":
        bundle["request"]["usage"][0]["quantity"] = "0"
    elif mutation == "release":
        bundle["rate_releases"][0]["version"] = "wrong-release"
    elif mutation == "window":
        bundle["observation_window"]["to"] = "2026-02-01"
    elif mutation == "future":
        bundle["recorded_on"] = "2026-02-01"
    elif mutation == "excluded":
        bundle["excluded_inputs"][0]["id"] = "before"
    elif mutation == "version":
        bundle["bundle_version"] = "0.9"
    else:
        bundle["quietly_ignore"] = True
    if mutation != "digest":
        seal(bundle)
    with pytest.raises(contract.BundleError):
        contract.verify_bundle(bundle)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_predecessor",
        "reordered",
        "wrong_series",
        "backdated",
        "duplicate_id",
        "after_retract",
        "truncated",
    ],
)
def test_invalid_revision_history_is_rejected(contract, mutation):
    records = history()
    checkpoint = records[-1]["bundle_digest"]
    if mutation == "missing_predecessor":
        records = records[1:]
    elif mutation == "reordered":
        records[0], records[1] = records[1], records[0]
    elif mutation == "wrong_series":
        records[1]["series_id"] = "another-series"
        seal(records[1])
    elif mutation == "backdated":
        records[1]["recorded_on"] = "2026-02-01"
        seal(records[1])
    elif mutation == "duplicate_id":
        records[1]["bundle_id"] = "original"
        seal(records[1])
    elif mutation == "after_retract":
        extra = copy.deepcopy(records[1])
        extra.update(
            bundle_id="resurrected", recorded_on="2026-02-13", previous_digest=checkpoint
        )
        records.append(seal(extra))
        checkpoint = records[-1]["bundle_digest"]
    else:
        records = records[:-1]
    with pytest.raises(contract.BundleError):
        contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-20")


def test_capital_treatments_are_alternative_not_additive(contract):
    import dapane

    reference = json.loads(REFERENCES.read_text())
    request = interval_request()
    request["quotes"] = [request["quotes"][0]]
    request["usage"] = [request["usage"][0]]
    request["quotes"][0].update(
        target="instrument", unit="asset", amount="12000", components=["acquisition"]
    )
    request["usage"][0].update(target="instrument", unit="asset", quantity="1")
    acquisition = bundle_for(request)
    acquisition["capital_treatments"] = [
        {
            "asset_id": "instrument-1",
            "treatment": "acquisition_expenditure",
            "source_line_ids": ["before"],
            "assumption": "synthetic purchase only",
        },
    ]
    seal(acquisition)
    assert contract.verify_bundle(acquisition)
    assert acquisition["report"]["totals"]["rounded"] == reference["expected"]["acquisition"]
    charge = copy.deepcopy(acquisition)
    charge["request"]["quotes"][0].update(amount="200", components=["prepared-charge"])
    charge["capital_treatments"][0].update(
        treatment="prepared_accounting_charge",
        assumption="candidate 12000 / 60 months; not a validated formula",
    )
    charge["report"] = dapane.evaluate(charge["request"])
    seal(charge)
    assert contract.verify_bundle(charge)
    assert charge["report"]["totals"]["rounded"] == reference["expected"]["accounting_charge"]
    mixed = copy.deepcopy(acquisition)
    second_quote = copy.deepcopy(charge["request"]["quotes"][0])
    second_quote["id"] = "monthly"
    second_line = copy.deepcopy(charge["request"]["usage"][0])
    second_line.update(id="monthly", quote_id="monthly")
    mixed["request"]["quotes"].append(second_quote)
    mixed["request"]["usage"].append(second_line)
    mixed["report"] = dapane.evaluate(mixed["request"])
    mixed["rate_releases"][0]["quote_ids"].append("monthly")
    mixed["capital_treatments"].append(
        {
            "asset_id": "instrument-1",
            "treatment": "prepared_accounting_charge",
            "source_line_ids": ["monthly"],
            "assumption": "alternative, not additional cost",
        }
    )
    assert mixed["report"]["totals"]["rounded"] == "12200.00"
    seal(mixed)
    with pytest.raises(contract.BundleError):
        contract.verify_bundle(mixed)


@pytest.mark.parametrize(
    "field,value",
    [
        ("retraction", "before"),
        ("duration_interval", {"from": "2026-01-31", "to": "2026-02-02"}),
        ("capital_method", "annuity"),
    ],
)
def test_unimplemented_line_methods_remain_errors(field, value):
    import dapane

    request = interval_request()
    request["usage"][0][field] = value
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(request)


def test_source_states_remain_declarations_not_certification():
    import dapane

    request = interval_request()
    request["usage"][0]["source"].update(
        evidence="observed", access="restricted", validation="source_verified"
    )
    report = dapane.evaluate(request)
    line = next(line for line in report["lines"] if line["id"] == "before")
    assert line["source"]["evidence"] == "observed"
    assert line["source"]["access"] == "restricted"
    assert line["source"]["validation"] == "source_verified"
    # Fabricated values exercise label transport; no observed data is used.
    assert report["totals"]["rounded"] == "110.00"
