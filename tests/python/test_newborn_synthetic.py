"""Synthetic newborn qualification through an installed Rust wheel.

Exact arithmetic below is an independent test oracle, not a production engine.
The recipe is a fixture profile, not a new native request or reporting API.
"""

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
FIXTURES = ROOT / "fixtures" / "newborn-synthetic"
CASE_NAMES = ["composed-two-infant"]


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def exact(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


@pytest.fixture(scope="module")
def schemas():
    registry = Registry()
    documents = {}
    for path in (ROOT / "schemas").rglob("*.schema.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
        documents[str(path.relative_to(ROOT / "schemas"))] = document
    return {
        name: Draft202012Validator(document, registry=registry, format_checker=FormatChecker())
        for name, document in documents.items()
    }


def test_original_two_infant_fixture_and_shared_baseline_entry_are_unchanged():
    assert hashlib.sha256((ROOT / "fixtures/newborn-screening.json").read_bytes()).hexdigest() == (
        "48eb8649483a8ccb8a5fd2b44641c5f171ab892c152d475ac768553069e9601f"
    )
    # Only pin the historical newborn oracle, allowing unrelated shared additions.
    shared = json.loads((ROOT / "fixtures/expected.json").read_text())["fixtures"][
        "newborn-screening.json"
    ]
    canonical = json.dumps(shared, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == (
        "fa1a26326f9967360732d478507dd579b1f1f11b59a138336c4ebe3601b24636"
    )
    request = json.loads((ROOT / "fixtures/newborn-screening.json").read_text())
    report = dapane.evaluate(request)
    assert report["totals"] == shared["totals"]
    assert report["totals"]["rounded"] == "150.00"
    objects = {item["object_id"]: item["total"] for item in report["object_totals"]}
    assert objects["infant-a"] == "60.00" and objects["infant-b"] == "90.00"
    assert report["input_digest"] == (
        "sha256:1b5afba6fc193da9d1fb4debdb22d0f88f0430e4faadb0216f993f0fc0d33959"
    )
    assert report["output_digest"] == (
        "sha256:a38641e5373cb775f84fec290cb48e7e030a344bf86e44c0d1f76e1b44cd0d9c"
    )


@pytest.mark.parametrize("name", CASE_NAMES)
def test_prepared_requests_match_independent_values_and_schemas(name, schemas):
    request, expected = load(f"{name}.json"), load("expected.json")["cases"][name]
    before = copy.deepcopy(request)
    version = request["schema_version"]
    schemas[f"{version}/request.schema.json"].validate(request)
    report = dapane.evaluate(request)
    schemas[f"{version}/report.schema.json"].validate(report)
    assert request == before
    assert report == json.loads(dapane.evaluate_json(json.dumps(request)))
    assert report["totals"]["rounded"] == expected["total"]
    assert exact(report["totals"]["exact"]) == Fraction(expected["total"])
    assert report["totals"]["unattributed"] == expected["unattributed"]
    objects = {item["object_id"]: item for item in report["object_totals"]}
    assert {key: objects[key]["total"] for key in expected["infant_totals"]} == expected[
        "infant_totals"
    ]
    assert all(
        value["total"] == "0.00"
        for key, value in objects.items()
        if key not in expected["infant_totals"]
    )
    assert sum(Fraction(item["total"]) for item in objects.values()) + Fraction(
        report["totals"]["unattributed"]
    ) == Fraction(expected["total"])
    for pool in report["allocations"]:
        assert sum(Fraction(share["rounded"]) for share in pool["shares"]) == Fraction(
            pool["pool_rounded"]
        )
        assert pool["residual"] == "0.00"
    for pool in report.get("capacity_allocations", []):
        assert sum(
            Fraction(share["rounded"]) for share in pool["shares"] if share["rounded"] is not None
        ) + Fraction(pool["unallocated"]) == Fraction(pool["pool_rounded"])
    sources = load("sources.json")
    declared_source = sources["source"] | {
        "locator": "fixtures/newborn-synthetic/sources.json",
        "content_digest": "sha256:"
        + hashlib.sha256((FIXTURES / "sources.json").read_bytes()).hexdigest(),
    }
    for item in (
        report["quote_snapshots"] + report["lines"] + report.get("capacity_allocations", [])
    ):
        assert item["source"] == declared_source
    for quote in report["quote_snapshots"]:
        original = sources["quotes"][quote["id"]]
        assert {key: quote[key] for key in original} == original


def test_object_and_stage_vocabulary_matches_composed_request():
    recipe, request = load("recipe.json"), load("composed-two-infant.json")
    kinds = {item["id"]: item["kind"] for item in request["objects"]}
    assert set(kinds.values()) == set(recipe["object_kinds"])
    assert {event["activity_id"] for event in request["events"]} <= set(recipe["stages"])
    valid_relations = {
        (item["from_kind"], item["relationship"], item["to_kind"])
        for item in recipe["relationships"]
    }
    for relation in request["object_relations"]:
        assert (
            kinds[relation["from_object_id"]],
            relation["relationship"],
            kinds[relation["to_object_id"]],
        ) in valid_relations
    for suffix in ("a", "b"):
        assays = [
            relation["from_object_id"]
            for relation in request["object_relations"]
            if relation["relationship"] == "uses_specimen"
            and relation["to_object_id"] == f"specimen-{suffix}-1"
        ]
        assert len(assays) == 2 and all(kinds[assay] == "assay" for assay in assays)
    assert len([kind for kind in kinds.values() if kind == "assay_batch"]) == 1
    for name in ("recipe.json", "sources.json", "scenarios.json"):
        with pytest.raises(dapane.DapaneError):
            dapane.evaluate(load(name))


def test_composition_counts_shared_resources_once_and_splits_staff_components():
    request = load("composed-two-infant.json")
    report = dapane.evaluate(request)
    quotes = {quote["id"]: quote for quote in request["quotes"]}
    pool = report["allocations"][0]
    assert set(pool["source_line_ids"]) == {
        "transport-batch-1",
        "accession-qc-batch-1",
        "setup-batch-1",
        "controls-batch-1",
        "assay-material-batch-1",
        "programme-overhead-batch-1",
    }
    assert pool["pool_rounded"] == "100.00"
    for use_id, quantity, amount in (
        ("collection-a-1", "5", 10),
        ("collection-b-1", "5", 10),
        ("confirmation-b", "15", 30),
    ):
        lines = [line for line in request["usage"] if line["use_id"] == use_id]
        assert len(lines) == 2 and {line["quantity"] for line in lines} == {quantity}
        assert {tuple(quotes[line["quote_id"]]["components"]) for line in lines} == {
            ("salary",),
            ("oncost",),
        }
        assert Fraction(quantity) * (Fraction("1.50") + Fraction("0.50")) == amount
    assert len(request["usage"]) == 12
    assert Fraction("10") + 10 + 20 + 10 + 40 + 10 == 100
    assert report["totals"]["rounded"] == "150.00"
