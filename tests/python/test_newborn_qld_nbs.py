"""Bounded Queensland / Australian NBS labour-pack tests through an installed Rust wheel.

Exact arithmetic below is an independent test oracle cross-checked against the
pinned workforce and manual-extraction provider records. Only manual DNA
extraction labour is priced; missing stages are explicit source gaps.
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
FIXTURES = ROOT / "fixtures" / "newborn-qld-nbs"
CASE_NAMES = [
    "qld-nbs-full-batch-6",
    "qld-nbs-partial-batch-3",
    "qld-nbs-failed-batch-repeat-3",
    "qld-nbs-inadequate-card-recollection-3",
    "qld-nbs-unresolved-failed-screen-3",
]


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def exact(value: dict) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


@pytest.fixture(scope="module")
def schemas() -> dict[str, Draft202012Validator]:
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


@pytest.mark.parametrize("name", CASE_NAMES)
def test_qld_nbs_cases_match_schemas_exact_arithmetic_and_locked_provenance(
    name: str, schemas: dict[str, Draft202012Validator]
) -> None:
    programme = load("programme.json")
    request = load(f"{name}.json")
    expected = load("expected.json")["cases"][name]
    before = copy.deepcopy(request)

    schemas["0.1/request.schema.json"].validate(request)
    report = dapane.evaluate(request)
    schemas["0.1/report.schema.json"].validate(report)
    assert request == before
    assert report == json.loads(dapane.evaluate_json(json.dumps(request)))

    assert exact(report["totals"]["exact"]) == Fraction(expected["exact_total"])
    assert report["totals"]["rounded"] == expected["rounded_total"]
    assert report["totals"]["unattributed"] == expected["unattributed"] == "0.00"

    for line in report["lines"]:
        step = line["id"].split(":")[-1]
        assert exact(line["exact"]) == Fraction(expected["batch_line_exact"][step])
        assert line["rounded"] == expected["batch_line_rounded"][step]
        assert line["components"] == ["base_salary"]

    for pool in report["allocations"]:
        assert pool["pool_rounded"] == "26.87"
        assert pool["residual"] == "0.00"
        assert sum(Fraction(share["rounded"]) for share in pool["shares"]) == Fraction("26.87")

    objects = {item["object_id"]: item for item in report["object_totals"]}
    assert {k: objects[k]["total"] for k in expected["infant_totals"]} == expected["infant_totals"]
    assert all(
        item["total"] == "0.00"
        for key, item in objects.items()
        if key not in expected["infant_totals"]
    )
    assert sum(Fraction(item["total"]) for item in objects.values()) == Fraction(
        expected["rounded_total"]
    )

    pinned_quote = programme["qualified_provider_inputs"]["workforce"]["quote"]
    assert report["quote_snapshots"] == [pinned_quote]
    workbook_sha = programme["qualified_provider_inputs"]["genomics_extraction_recipe"][
        "workbook_sha256"
    ]
    for line in report["lines"]:
        assert line["source"]["id"] == "manual-extraction-v15"
        assert line["source"]["version"] == "manual-dna-extraction-v1"
        assert line["source"]["content_digest"] == f"sha256:{workbook_sha}"


def test_programme_pack_locks_perspective_source_gaps_and_pending_reporting() -> None:
    programme = load("programme.json")
    locks = json.loads((ROOT / "docs/provider-consumers.lock.json").read_text(encoding="utf-8"))
    wf = programme["qualified_provider_inputs"]["workforce"]
    gen = programme["qualified_provider_inputs"]["genomics_extraction_recipe"]

    assert wf["repository"] == locks["workforce"]["repository"]
    assert wf["commit"] == locks["workforce"]["commit"]
    assert wf["python"] == locks["workforce"]["python"]
    assert wf["exported_artifact_sha256"] == locks["workforce"]["artifact_sha256"]
    assert gen["repository"] == locks["genomics"]["repository"]
    assert gen["commit"] == locks["genomics"]["commit"]
    assert gen["python"] == locks["genomics"]["python"]

    assert programme["perspective"] == "provider"
    assert programme["reporting_profile"]["status"] == "pending"
    assert programme["reporting_profile"]["required_track"] == "reporting_profiles_20261108"

    gaps = {item["id"]: item["status"] for item in programme["source_gaps"]}
    expected_gap_ids = {
        "collection_workforce_and_consumables",
        "specimen_transport",
        "accession_and_qc",
        "biochemical_msms_and_immunoassay",
        "molecular_reagents_and_instruments",
        "workforce_oncosts_and_loadings",
        "reporting_recall_and_clinical_confirmation",
        "programme_overhead",
        "epidemiological_probabilities_and_timing",
        "family_time_and_downstream_care",
        "uogto_reporting_profiles",
    }
    assert set(gaps) == expected_gap_ids
    assert gaps["family_time_and_downstream_care"] == "excluded_by_perspective"
    assert gaps["uogto_reporting_profiles"] == "pending_optional_track"
    assert sum(1 for status in gaps.values() if status == "unqualified_source_gap") == 9

    for pop in programme["populations"].values():
        assert pop["evidence"] == "illustrative_cohort_not_clinical_epidemiology"


@pytest.mark.parametrize("name", CASE_NAMES)
def test_object_graph_lineage_denominators_and_branch_semantics(name: str) -> None:
    programme = load("programme.json")
    scenario = load("scenarios.json")["cases"][name]
    request = load(f"{name}.json")
    expected = load("expected.json")["cases"][name]

    assert scenario["perspective"] == request["policy"]["perspective"] == "provider"
    kinds = {obj["id"]: obj["kind"] for obj in request["objects"]}
    assert len(kinds) == len(request["objects"])
    assert set(kinds.values()) <= set(programme["object_kinds"])
    assert {ev["activity_id"] for ev in request["events"]} <= set(programme["stages"])

    valid_relations = {
        (item["from_kind"], item["relationship"], item["to_kind"])
        for item in programme["relationships"]
    }
    relations = request["object_relations"]
    for rel in relations:
        assert (
            kinds[rel["from_object_id"]],
            rel["relationship"],
            kinds[rel["to_object_id"]],
        ) in valid_relations

    results = {item["result_id"]: item for item in scenario["assay_results"]}
    for episode in scenario["episodes"]:
        assert {
            "from_object_id": episode["episode_id"],
            "to_object_id": episode["infant_id"],
            "relationship": "screens",
        } in relations
        for rid in episode["required_final_result_ids"]:
            specimens = [
                rel["to_object_id"]
                for rel in relations
                if rel["relationship"] == "uses_specimen"
                and rel["from_object_id"] == results[rid]["assay_id"]
            ]
            assert len(specimens) == 1
            donors = [
                rel["to_object_id"]
                for rel in relations
                if rel["relationship"] == "collected_from" and rel["from_object_id"] == specimens[0]
            ]
            assert donors == [episode["infant_id"]]
        assert (episode["valid_screen_date"] is not None) == all(
            results[rid]["status"] == "valid" for rid in episode["required_final_result_ids"]
        )

    if name == "qld-nbs-inadequate-card-recollection-3":
        states = {s["specimen_id"]: s["status"] for s in scenario["specimen_states"]}
        assert states["specimen-01-1"] == "inadequate"
        assert states["specimen-01-2"] == "adequate"
        assert not any(
            rel["relationship"] == "uses_specimen" and rel["to_object_id"] == "specimen-01-1"
            for rel in relations
        )
    elif name == "qld-nbs-failed-batch-repeat-3":
        assert len(scenario["batches"]) == 2
        assert scenario["batches"][0]["outcome"] == "failed"
        assert scenario["batches"][1]["repeat_of"] == "batch-1"
        assert len({ep["infant_id"] for ep in scenario["episodes"]}) == 3
    elif name == "qld-nbs-unresolved-failed-screen-3":
        assert results["result-01-1"]["status"] == "failed"
        assert scenario["episodes"][0]["valid_screen_date"] is None
        assert scenario["episodes"][0]["completion_date"] is None

    window = programme["window"]
    start, end = window["start"], window["end_exclusive"]
    pop_members = programme["populations"][scenario["population_id"]]["members"]
    members = {
        "eligible_birth": {m["infant_id"] for m in pop_members if start <= m["birth_date"] < end}
    }
    for key, definition in programme["denominators"].items():
        if key != "eligible_birth":
            date_key = definition["membership_date"]
            members[key] = {
                ep["infant_id"]
                for ep in scenario["episodes"]
                if ep[date_key] is not None and start <= ep[date_key] < end
            }

    assert all(not key.endswith("window-end") for key in members["eligible_birth"])
    assert {k: len(v) for k, v in members.items()} == expected["denominators"]

    report = dapane.evaluate(request)
    rounded_total = Fraction(report["totals"]["rounded"])
    exact_total = exact(report["totals"]["exact"])
    for key, infants in members.items():
        r_ratio = expected["cost_per_denominator_rounded_ledger"][key]
        e_ratio = expected["cost_per_denominator_exact_ledger"][key]
        if infants:
            assert rounded_total / len(infants) == Fraction(r_ratio)
            assert exact_total / len(infants) == Fraction(e_ratio)
        else:
            assert r_ratio is None and e_ratio is None


@pytest.mark.parametrize("name", CASE_NAMES)
def test_input_order_invariance_and_context_only_collection_events(name: str) -> None:
    request = load(f"{name}.json")
    baseline = dapane.evaluate(request)

    reordered = copy.deepcopy(request)
    for key in ("usage", "objects", "events", "object_relations", "allocations"):
        reordered[key].reverse()
    for alloc in reordered["allocations"]:
        alloc["source_line_ids"].reverse()
        alloc["weights"].reverse()

    again = dapane.evaluate(reordered)
    assert again["input_digest"] == baseline["input_digest"]
    assert again["output_digest"] == baseline["output_digest"]
    assert again["totals"] == baseline["totals"]

    context_only_events = {
        ev["id"]
        for ev in request["events"]
        if ev["activity_id"] in {"collection", "repeat_collection", "confirmation"}
    }
    assert context_only_events
    assert not any(line["event_id"] in context_only_events for line in request["usage"])


def test_independent_provider_reference_crosscheck() -> None:
    full = dapane.evaluate(load("qld-nbs-full-batch-6.json"))
    partial = dapane.evaluate(load("qld-nbs-partial-batch-3.json"))
    repeated = dapane.evaluate(load("qld-nbs-failed-batch-repeat-3.json"))
    inadequate = dapane.evaluate(load("qld-nbs-inadequate-card-recollection-3.json"))

    assert exact(full["totals"]["exact"]) == Fraction(1612303, 60000)
    assert full["totals"]["rounded"] == "26.87"
    assert [s["rounded"] for s in full["allocations"][0]["shares"]] == [
        "4.48",
        "4.48",
        "4.48",
        "4.48",
        "4.48",
        "4.47",
    ]
    assert [s["rounded"] for s in partial["allocations"][0]["shares"]] == [
        "8.96",
        "8.96",
        "8.95",
    ]
    assert exact(repeated["totals"]["exact"]) == Fraction(1612303, 30000)
    assert repeated["totals"]["rounded"] == "53.74"
    rep_totals = {
        item["object_id"]: item["total"]
        for item in repeated["object_totals"]
        if item["object_id"] in {"infant-01", "infant-02", "infant-03"}
    }
    assert rep_totals == {"infant-01": "17.92", "infant-02": "17.92", "infant-03": "17.90"}
    inad_totals = {
        item["object_id"]: item["total"]
        for item in inadequate["object_totals"]
        if item["object_id"] in {"infant-01", "infant-02", "infant-03"}
    }
    assert inad_totals == {"infant-01": "26.87", "infant-02": "13.44", "infant-03": "13.43"}


def test_fail_closed_negative_controls_and_nominal_batch_bound() -> None:
    base = load("qld-nbs-partial-batch-3.json")

    stale = copy.deepcopy(base)
    stale["usage"][0]["service_date"] = "2026-11-16"
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(stale)

    early_cutoff = copy.deepcopy(base)
    early_cutoff["knowledge_cutoff"] = "2026-11-14"
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(early_cutoff)

    unquoted_gap = copy.deepcopy(base)
    gap_line = copy.deepcopy(unquoted_gap["usage"][0])
    gap_line["id"] = "collection-gap-1"
    gap_line["use_id"] = "collection-gap-1"
    gap_line["quote_id"] = "missing-collection-quote"
    unquoted_gap["usage"].append(gap_line)
    with pytest.raises(dapane.DapaneError) as exc_info:
        dapane.evaluate(unquoted_gap)
    assert exc_info.value.code == "missing_quote"

    overlap = copy.deepcopy(base)
    dup_line = copy.deepcopy(overlap["usage"][0])
    dup_line["id"] = "batch-1:labwork-duplicate"
    overlap["usage"].append(dup_line)
    with pytest.raises(dapane.DapaneError) as exc_info:
        dapane.evaluate(overlap)
    assert exc_info.value.code == "component_overlap"

    wrong_basis = copy.deepcopy(base)
    wrong_basis["policy"]["basis"] = "economic_cost"
    with pytest.raises(dapane.DapaneError):
        dapane.evaluate(wrong_basis)

    programme = load("programme.json")
    max_specimens = programme["qualified_provider_inputs"]["genomics_extraction_recipe"][
        "nominal_batch_specimens"
    ]
    assert max_specimens == 6
    for name in CASE_NAMES:
        for batch in load("scenarios.json")["cases"][name]["batches"]:
            assert 1 <= len(batch["specimen_ids"]) <= max_specimens


def test_qld_nbs_catalogue_exact_and_synthetic_baseline_preserved() -> None:
    expected_json = set(CASE_NAMES) | {"programme", "scenarios", "expected"}
    assert {path.stem for path in FIXTURES.glob("*.json")} == expected_json
    assert (FIXTURES / "README.md").is_file()

    assert len(list((ROOT / "fixtures" / "newborn-synthetic").glob("*.json"))) == 17
    assert (
        hashlib.sha256((ROOT / "fixtures/newborn-screening.json").read_bytes()).hexdigest()
        == "48eb8649483a8ccb8a5fd2b44641c5f171ab892c152d475ac768553069e9601f"
    )
