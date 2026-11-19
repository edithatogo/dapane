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
CASE_NAMES = [
    "composed-two-infant",
    "repeat-collection",
    "failed-assay-repeat",
    "unresolved-failure",
    "reflex-assay",
    "partial-batch",
    "added-panel",
    "family-perspective",
    "capacity-below",
    "capacity-at",
    "capacity-above",
    "capacity-missing-use",
    "capacity-unknown",
]


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
        documents[path.relative_to(ROOT / "schemas").as_posix()] = document
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


@pytest.mark.parametrize("name", CASE_NAMES)
def test_recipe_identities_states_scope_and_explicit_denominators(name):
    recipe, sources = load("recipe.json"), load("sources.json")
    scenario = load("scenarios.json")["cases"][name]
    request, expected = load(f"{name}.json"), load("expected.json")["cases"][name]
    assert scenario["branch"] in recipe["branches"]
    assert scenario["perspective"] == request["policy"]["perspective"]
    assert scenario["population_id"] == sources["population"]["id"]
    assert scenario["window_id"] == sources["window"]["id"]
    kinds = {obj["id"]: obj["kind"] for obj in request["objects"]}
    assert len(kinds) == len(request["objects"])
    assert set(kinds.values()) <= set(recipe["object_kinds"] + recipe["optional_object_kinds"])
    assert {event["activity_id"] for event in request["events"]} <= set(recipe["stages"])
    valid_relations = {
        (item["from_kind"], item["relationship"], item["to_kind"])
        for item in recipe["relationships"]
    }
    relations = request["object_relations"]
    for relation in relations:
        assert (
            kinds[relation["from_object_id"]],
            relation["relationship"],
            kinds[relation["to_object_id"]],
        ) in valid_relations
    results = {item["result_id"]: item for item in scenario["assay_results"]}
    assert len(results) == len(scenario["assay_results"])
    for rid, item in results.items():
        assert kinds[rid] == "result" and kinds[item["assay_id"]] == "assay"
        assert item["status"] in recipe["result_states"]
        assert {
            "from_object_id": rid,
            "to_object_id": item["assay_id"],
            "relationship": "reports",
        } in relations
    for specimen in scenario["specimen_states"]:
        assert kinds[specimen["specimen_id"]] == "specimen"
        assert specimen["status"] in recipe["specimen_states"]
    episodes = scenario["episodes"]
    assert len({episode["infant_id"] for episode in episodes}) == len(episodes)
    assert len({episode["episode_id"] for episode in episodes}) == len(episodes)
    for episode in episodes:
        assert (
            kinds[episode["infant_id"]] == "infant"
            and kinds[episode["episode_id"]] == "screening_episode"
        )
        assert {
            "from_object_id": episode["episode_id"],
            "to_object_id": episode["infant_id"],
            "relationship": "screens",
        } in relations
        required = episode["required_final_result_ids"]
        assert required and len(set(required)) == len(required)
        assert all(result in results for result in required)
        for result in required:
            specimens = [
                rel["to_object_id"]
                for rel in relations
                if rel["relationship"] == "uses_specimen"
                and rel["from_object_id"] == results[result]["assay_id"]
            ]
            assert len(specimens) == 1
            donors = [
                rel["to_object_id"]
                for rel in relations
                if rel["relationship"] == "collected_from" and rel["from_object_id"] == specimens[0]
            ]
            assert donors == [episode["infant_id"]]
        assert (episode["valid_screen_date"] is not None) == all(
            results[result]["status"] == "valid" for result in required
        )
        assert episode["completion_date"] is None or episode["valid_screen_date"] is not None
    start, end = sources["window"]["start"], sources["window"]["end_exclusive"]
    members = {
        "eligible_birth": {
            member["infant_id"]
            for member in sources["population"]["members"]
            if start <= member["birth_date"] < end
        }
    }
    for key, definition in recipe["denominators"].items():
        if key != "eligible_birth":
            date_key = definition["membership_date"]
            members[key] = {
                e["infant_id"]
                for e in episodes
                if e[date_key] is not None and start <= e[date_key] < end
            }
    assert members["eligible_birth"] == {"infant-a", "infant-b", "infant-c"}
    assert "infant-window-end" not in members["eligible_birth"]
    assert members["participating_infant"] <= members["eligible_birth"]
    assert members["valid_screen"] <= members["participating_infant"]
    assert members["completed_pathway"] <= members["valid_screen"]
    assert members["confirmed_diagnosis"] <= members["completed_pathway"]
    assert {key: len(value) for key, value in members.items()} == expected["denominators"]
    total = Fraction(dapane.evaluate(request)["totals"]["rounded"])
    for key, value in members.items():
        ratio = expected["cost_per_denominator"][key]
        if value:
            assert total / len(value) == Fraction(ratio)
        else:
            assert ratio is None  # Undefined is not zero; this is no new native API.


def test_catalogues_cover_exactly_the_delivered_cases_and_keep_sources_synthetic():
    assert set(load("scenarios.json")["cases"]) == set(CASE_NAMES)
    assert set(load("expected.json")["cases"]) == set(CASE_NAMES)
    assert {p.stem for p in FIXTURES.glob("*.json")} == set(CASE_NAMES) | {
        "recipe",
        "sources",
        "scenarios",
        "expected",
    }
    source = load("sources.json")["source"]
    assert source["evidence"] == "synthetic" and source["access"] == "public"
    assert source["validation"] == "unvalidated"


def test_inadequate_specimen_recollection_retains_infant_and_episode():
    request = load("repeat-collection.json")
    scenario = load("scenarios.json")["cases"]["repeat-collection"]
    assert {item["infant_id"] for item in scenario["episodes"]} == {"infant-a", "infant-b"}
    assert {item["specimen_id"]: item["status"] for item in scenario["specimen_states"]} == {
        "specimen-a-1": "inadequate",
        "specimen-a-2": "adequate",
        "specimen-b-1": "adequate",
    }
    assert {
        line["use_id"]
        for line in request["usage"]
        if line["activity_id"] in {"collection", "repeat_collection"}
    } == {"collection-a-1", "collection-a-2", "collection-b-1"}
    assert not any(
        rel["relationship"] == "uses_specimen" and rel["to_object_id"] == "specimen-a-1"
        for rel in request["object_relations"]
    )
    report = dapane.evaluate(request)
    assert Fraction(report["totals"]["rounded"]) == 150 + 10 + 5 + 5 == 170
    assert len(report["allocations"]) == 1 and report["allocations"][0]["pool_rounded"] == "100.00"


def test_failed_attempt_keeps_cost_and_history_and_only_successful_repeat_finishes_screen():
    failed, repeated = load("unresolved-failure.json"), load("failed-assay-repeat.json")
    cases = load("scenarios.json")["cases"]
    for name in ("unresolved-failure", "failed-assay-repeat"):
        results = {item["result_id"]: item["status"] for item in cases[name]["assay_results"]}
        assert results["result-a-primary-1"] == "failed"
    assert set(cases["failed-assay-repeat"]["episodes"][0]["required_final_result_ids"]) == {
        "result-a-repeat-1",
        "result-a-primary-2",
    }
    assert cases["unresolved-failure"]["episodes"][0]["valid_screen_date"] is None
    assert cases["unresolved-failure"]["episodes"][0]["completion_date"] is None
    before, after = dapane.evaluate(failed), dapane.evaluate(repeated)
    assert before["totals"]["rounded"] == "150.00"
    assert Fraction(after["totals"]["rounded"]) - Fraction(before["totals"]["rounded"]) == 20
    assert {line["id"] for line in failed["usage"]} < {line["id"] for line in repeated["usage"]}
    assert {
        "from_object_id": "assay-a-repeat-1",
        "to_object_id": "assay-a-primary-1",
        "relationship": "repeats",
    } in repeated["object_relations"]


def test_reflex_assay_uses_same_specimen_and_prices_only_extra_resources():
    request = load("reflex-assay.json")
    assert {
        "from_object_id": "result-b-primary-2",
        "to_object_id": "assay-b-reflex-1",
        "relationship": "triggers",
    } in request["object_relations"]
    assert {
        "from_object_id": "assay-b-reflex-1",
        "to_object_id": "specimen-b-1",
        "relationship": "uses_specimen",
    } in request["object_relations"]
    extra = [
        line for line in dapane.evaluate(request)["lines"] if line["activity_id"] == "reflex_assay"
    ]
    assert len(extra) == 3 and sum(Fraction(line["rounded"]) for line in extra) == 3 * 2 + 14 == 20


def test_partial_batch_conserves_full_cost_without_inventing_a_capacity_denominator():
    report = dapane.evaluate(load("partial-batch.json"))
    pool = report["allocations"][0]
    assert report["totals"]["rounded"] == "110.00" and pool["pool_rounded"] == "100.00"
    assert [(s["object_id"], s["rounded"]) for s in pool["shares"]] == [("infant-a", "100.00")]
    assert "capacity_allocations" not in report
    assert (
        load("expected.json")["cases"]["partial-batch"]["cost_per_denominator"][
            "confirmed_diagnosis"
        ]
        is None
    )


def test_added_panel_marginal_cost_is_distinct_from_programme_average():
    before, after = [
        dapane.evaluate(load(f"{name}.json")) for name in ("composed-two-infant", "added-panel")
    ]
    assert before["allocations"] == after["allocations"]
    assert Fraction(after["totals"]["rounded"]) == 170
    assert Fraction(after["totals"]["rounded"]) / 2 == 85
    assert (Fraction(after["totals"]["rounded"]) - Fraction(before["totals"]["rounded"])) / 2 == 10


def test_family_time_is_explicit_and_only_in_declared_family_perspective():
    before, after = load("composed-two-infant.json"), load("family-perspective.json")
    assert before["policy"]["perspective"] == "provider"
    assert after["policy"]["perspective"] == "provider_plus_family"
    assert not any(line["target"] == "family_time" for line in before["usage"])
    family = [line for line in after["usage"] if line["target"] == "family_time"]
    assert len(family) == 2 and {line["quantity"] for line in family} == {"30"}
    assert [line for line in after["usage"] if line["target"] != "family_time"] == before["usage"]
    assert (
        Fraction(dapane.evaluate(after)["totals"]["rounded"])
        == 150 + 2 * 30 * Fraction("0.50")
        == 180
    )


def test_explicit_capacity_step_changes_source_expense_and_retains_unallocated_pool():
    reports = {
        name: dapane.evaluate(load(f"capacity-{name}.json")) for name in ("below", "at", "above")
    }
    assert [reports[n]["totals"]["rounded"] for n in ("below", "at", "above")] == [
        "110.00",
        "120.00",
        "230.00",
    ]
    assert [
        reports[n]["capacity_allocations"][0]["unallocated"] for n in ("below", "at", "above")
    ] == ["50.00", "0.00", "50.00"]
    assert (
        Fraction(reports["at"]["totals"]["rounded"])
        - Fraction(reports["below"]["totals"]["rounded"])
        == 10
    )
    assert (
        Fraction(reports["above"]["totals"]["rounded"])
        - Fraction(reports["at"]["totals"]["rounded"])
        == 110
    )
    assert Fraction(reports["above"]["totals"]["rounded"]) / 3 == Fraction(230, 3)
    declared = load("sources.json")["capacity_scenarios"]
    for name in ("below", "at", "above"):
        request, supplied = load(f"capacity-{name}.json"), declared[f"capacity-{name}"]
        pool = request["capacity_allocations"][0]
        assert pool["available_capacity"] == {
            "status": "known",
            "quantity": supplied["available_instrument_hours"],
        }
        assert (
            next(line for line in request["usage"] if line["id"] == "instrument-blocks")["quantity"]
            == supplied["blocks"]
        )
        assert pool["observation_coverage"] == "incomplete"
        assert all(
            record["quantity"] == {"status": "known", "quantity": "1"}
            for record in pool["use_records"]
        )
        assert all(
            key not in reports[name]["capacity_allocations"][0]
            for key in ("utilization", "idle_cost", "savings")
        )


def test_unknown_capacity_and_missing_use_never_become_zero_or_sample_weights():
    missing = load("capacity-missing-use.json")
    report = dapane.evaluate(missing)
    pool = report["capacity_allocations"][0]
    assert [s["rounded"] for s in pool["shares"]] == ["50.00", None]
    assert pool["unallocated"] == "50.00"
    missing["capacity_allocations"][0]["use_records"][1]["quantity"] = {
        "status": "known",
        "quantity": "0",
    }
    zero = dapane.evaluate(missing)
    assert zero["capacity_allocations"][0]["shares"][1]["rounded"] == "0.00"
    assert report["totals"] == zero["totals"] and report["input_digest"] != zero["input_digest"]
    unknown = dapane.evaluate(load("capacity-unknown.json"))["capacity_allocations"][0]
    assert unknown["unallocated"] == "100.00" and unknown["unaccounted_quantity"] is None
    assert all(s["rounded"] is None for s in unknown["shares"])
    assert exact(unknown["accounted_quantity"]) == 2


@pytest.mark.parametrize("name", CASE_NAMES)
def test_fixture_results_are_invariant_to_record_order(name):
    request = load(f"{name}.json")
    report = dapane.evaluate(request)
    for value in request.values():
        if isinstance(value, list):
            value.reverse()
            for item in value:
                for nested in item.values():
                    if isinstance(nested, list):
                        nested.reverse()
    assert dapane.evaluate(request) == report


@pytest.mark.parametrize(
    "case",
    [
        "duplicate_use",
        "overlapping_components",
        "duplicate_pool",
        "direct_and_pooled",
        "missing_quote",
        "unknown_field",
        "over_capacity",
        "zero_capacity",
        "downgrade_capacity",
        "missing_quantity",
        "unsupported_capacity_unit",
    ],
)
def test_invalid_compositions_fail_in_native_without_a_financial_report(case):
    request = load("composed-two-infant.json")
    if case == "duplicate_use":
        extra = copy.deepcopy(request["usage"][0])
        extra["id"] = "duplicate-underlying-use"
        request["usage"].append(extra)
        expected_code = "component_overlap"
    elif case == "overlapping_components":
        next(q for q in request["quotes"] if q["id"] == "oncost-quote")["components"] = ["salary"]
        expected_code = "component_overlap"
    elif case == "duplicate_pool":
        extra = copy.deepcopy(request["allocations"][0])
        extra["id"] = "second-batch-allocation"
        request["allocations"].append(extra)
        expected_code = "allocation_overlap"
    elif case == "direct_and_pooled":
        next(line for line in request["usage"] if line["id"] == "setup-batch-1")[
            "attribution_object_id"
        ] = "infant-a"
        expected_code = "allocation_overlap"
    elif case == "missing_quote":
        request["quotes"] = [q for q in request["quotes"] if q["id"] != "salary-quote"]
        expected_code = "missing_quote"
    elif case == "unknown_field":
        request["automatic_repeat_probability"] = "0.1"
        expected_code = "invalid_request"
    else:
        request = load("capacity-at.json")
        pool = request["capacity_allocations"][0]
        expected_code = "invalid_request"
        if case == "over_capacity":
            pool["use_records"].append(
                {"object_id": "infant-c", "quantity": {"status": "known", "quantity": "1"}}
            )
            expected_code = "capacity_exceeded"
        elif case == "zero_capacity":
            pool["available_capacity"]["quantity"] = "0"
            expected_code = "invalid_capacity"
        elif case == "downgrade_capacity":
            request["schema_version"] = "0.1"
        elif case == "missing_quantity":
            del pool["use_records"][0]["quantity"]
        elif case == "unsupported_capacity_unit":
            pool["unit"] = "sample"
    with pytest.raises(dapane.DapaneError) as error:
        dapane.evaluate(request)
    assert error.value.code == expected_code and error.value.path.startswith("/")


def test_newborn_source_line_rounding_is_half_even_before_summing():
    request = load("composed-two-infant.json")
    request["usage"] = [
        line
        for line in request["usage"]
        if line["quote_id"] == "salary-quote" and line["activity_id"] == "collection"
    ]
    request["quotes"] = [q for q in request["quotes"] if q["id"] == "salary-quote"]
    request["quotes"][0]["amount"] = "0.001"
    request["allocations"] = []
    report = dapane.evaluate(request)
    assert [exact(line["exact"]) for line in report["lines"]] == [
        Fraction(1, 200),
        Fraction(1, 200),
    ]
    assert [line["rounded"] for line in report["lines"]] == ["0.00", "0.00"]
    assert exact(report["totals"]["exact"]) == Fraction(1, 100)
    assert report["totals"]["rounded"] == "0.00"
