"""Adversarial review cases for immutable candidate evidence, without economic mocks."""

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REFERENCE = load_module(
    "bundle_reference", Path(__file__).with_name("test_core_contract_completion.py")
)


@pytest.fixture
def contract():
    return load_module("bundle_review_subject", ROOT / "scripts/verify_run_bundle.py")


@pytest.mark.parametrize("location", ["bundle_id", "excluded", "asset"])
def test_new_identity_fields_enforce_utf8_byte_limit(contract, location):
    bundle = REFERENCE.bundle_for()
    oversized = "é" * 65
    if location == "bundle_id":
        bundle["bundle_id"] = oversized
    elif location == "excluded":
        bundle["excluded_inputs"][0]["id"] = oversized
    else:
        bundle["capital_treatments"] = [
            {
                "asset_id": oversized,
                "treatment": "prepared_accounting_charge",
                "source_line_ids": ["before"],
                "assumption": "only an identity-boundary negative fixture",
            }
        ]
    REFERENCE.seal(bundle)
    with pytest.raises(contract.BundleError):
        contract.verify_bundle(bundle)


@pytest.mark.parametrize("failure", ["missing", "malformed", "unregistered_reference"])
def test_unavailable_local_schemas_fail_structurally_without_network(
    contract, monkeypatch, tmp_path, failure
):
    bundle = REFERENCE.bundle_for()
    destination = tmp_path / "schemas/bundles"
    destination.mkdir(parents=True)
    if failure == "malformed":
        (destination / "0.1.schema.json").write_text("{", encoding="utf-8")
    elif failure == "unregistered_reference":
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://example.invalid/local-only",
            "$ref": "https://never-fetch.invalid/unregistered",
        }
        (destination / "0.1.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    monkeypatch.setattr(contract, "ROOT", tmp_path)
    contract._validator.cache_clear()
    with pytest.raises(contract.BundleError):
        contract.verify_bundle(bundle)


def test_resealed_report_numeric_type_change_is_not_equal_replay(contract):
    bundle = REFERENCE.bundle_for()
    bundle["report"]["policy"]["price_year"] = 2026.0
    REFERENCE.seal(bundle)
    with pytest.raises(contract.BundleError):
        contract.verify_bundle(bundle)


def test_v02_unknown_capacity_survives_bundle_replay(contract):
    import dapane

    request = json.loads((ROOT / "fixtures/genomics-capacity/time-missing-use.json").read_text())
    report = dapane.evaluate(request)
    bundle = REFERENCE.bundle_for()
    bundle.update(request=request, report=report, recorded_on="2026-12-31")
    bundle["observation_window"] = {"from": "2026-01-01", "to": "2027-01-01"}
    grouped = {}
    for quote in request["quotes"]:
        key = quote["source"]["id"], quote["source"]["version"]
        grouped.setdefault(
            key,
            {
                "source_id": key[0],
                "version": key[1],
                "quote_ids": [],
                "published_on": "2026-01-01",
                "retrieved_on": "2026-12-31",
            },
        )["quote_ids"].append(quote["id"])
    bundle["rate_releases"] = list(grouped.values())
    REFERENCE.seal(bundle)
    assert contract.verify_bundle(bundle)
    pool = bundle["report"]["capacity_allocations"][0]
    assert pool["unallocated"] == "270.00"
    assert any(share["rounded"] is None for share in pool["shares"])


def test_same_day_order_is_explicit_and_history_is_not_mutated(contract):
    records = REFERENCE.history()
    records[-1]["recorded_on"] = records[-2]["recorded_on"]
    REFERENCE.seal(records[-1])
    before = copy.deepcopy(records)
    result = contract.verify_history(
        records, expected_head_digest=records[-1]["bundle_digest"], as_of="2026-02-10"
    )
    assert result["status"] == "retracted"
    assert result["report"] is None
    assert records == before


@pytest.mark.parametrize("invalid", [[], [{}] * 101, {}, None])
def test_history_shape_and_revision_bound(contract, invalid):
    with pytest.raises(contract.BundleError):
        contract.verify_history(
            invalid, expected_head_digest="sha256:" + "0" * 64, as_of="2026-02-10"
        )


@pytest.mark.parametrize("raw", ['[{"id":1,"id":2}]', "[NaN]", "[Infinity]", "{}", "["])
def test_raw_history_parser_fails_closed(contract, tmp_path, raw):
    path = tmp_path / "history.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(contract.BundleError):
        contract.read_history(path)


def test_history_byte_limit_is_checked_before_parsing(contract, monkeypatch, tmp_path):
    monkeypatch.setattr(contract, "MAX_HISTORY_BYTES", 16)
    path = tmp_path / "history.json"
    path.write_bytes(b" " * 17)
    with pytest.raises(contract.BundleError) as failure:
        contract.read_history(path)
    assert failure.value.code == "limit_exceeded"


def test_cli_replay_and_rejection_have_separate_output_channels(tmp_path):
    records = REFERENCE.history()
    path = tmp_path / "history.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    command = [
        sys.executable,
        str(ROOT / "scripts/verify_run_bundle.py"),
        str(path),
        "--head",
        records[-1]["bundle_digest"],
        "--as-of",
        "2026-02-10",
    ]
    valid = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["report"]["totals"]["rounded"] == "125.00"
    assert not valid.stderr
    path.write_text('[{"duplicate":1,"duplicate":2}]', encoding="utf-8")
    invalid = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert invalid.returncode == 2
    assert not invalid.stdout
    assert json.loads(invalid.stderr)["error"]["code"] == "duplicate_key"


def reseal_records(records):
    """Rebuild legitimate native reports and links, keeping the history ordered."""
    import dapane

    for position, bundle in enumerate(records):
        if bundle["request"] is not None:
            bundle["report"] = dapane.evaluate(bundle["request"])
        if position:
            bundle["previous_digest"] = records[position - 1]["bundle_digest"]
        REFERENCE.seal(bundle)
    return records[-1]["bundle_digest"]


@pytest.mark.parametrize("intervening_subset", [False, True])
def test_quote_correction_requires_new_source_version(contract, intervening_subset):
    records = REFERENCE.history()[:2]
    records[-1]["request"]["quotes"][0]["amount"] = "100"
    if intervening_subset:
        subset = copy.deepcopy(records[0])
        subset.update(
            bundle_id="subset",
            change="replace",
            reason="only the second interval segment is in scope",
            recorded_on="2026-02-05",
        )
        subset["request"]["usage"] = subset["request"]["usage"][1:]
        subset["request"]["quotes"] = subset["request"]["quotes"][1:]
        subset["rate_releases"] = subset["rate_releases"][1:]
        records.insert(1, subset)
    checkpoint = reseal_records(records)
    assert records[-1]["report"]["totals"]["rounded"] == "130.00"
    for record in records:
        assert contract.verify_bundle(record)
    with pytest.raises(contract.BundleError) as failure:
        contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-10")
    assert failure.value.code == "release_conflict"


def test_corrected_quote_with_new_source_version_preserves_prior_report(contract):
    records = REFERENCE.history()[:2]
    original = copy.deepcopy(records[0])
    quote = records[1]["request"]["quotes"][0]
    quote.update(amount="100", known_from="2026-02-05")
    quote["source"]["version"] = "before-corrected"
    records[1]["rate_releases"][0].update(
        version="before-corrected", published_on="2026-02-05", retrieved_on="2026-02-10"
    )
    checkpoint = reseal_records(records)
    result = contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-10")
    expected = json.loads(REFERENCE.REFERENCES.read_text())["expected"]
    assert result["report"]["totals"]["rounded"] == expected["corrected_rate"] == "130.00"
    assert records[0] == original
    earlier = contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-02")
    assert earlier["report"]["totals"]["rounded"] == "110.00"


def test_release_publication_date_cannot_change_under_same_version(contract):
    records = REFERENCE.history()[:2]
    records[1]["rate_releases"][0]["published_on"] = "2025-12-31"
    checkpoint = reseal_records(records)
    with pytest.raises(contract.BundleError) as failure:
        contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-10")
    assert failure.value.code == "release_conflict"


def test_release_digest_conflict_is_rejected_across_different_quote_ids(contract):
    records = REFERENCE.history()[:2]
    records[0]["request"]["quotes"][0]["source"]["content_digest"] = "sha256:" + "a" * 64
    quote = records[1]["request"]["quotes"][0]
    quote["source"]["content_digest"] = "sha256:" + "b" * 64
    quote["id"] = "another-quote"
    records[1]["request"]["usage"][0]["quote_id"] = "another-quote"
    records[1]["rate_releases"][0]["quote_ids"] = ["another-quote"]
    checkpoint = reseal_records(records)
    with pytest.raises(contract.BundleError) as failure:
        contract.verify_history(records, expected_head_digest=checkpoint, as_of="2026-02-10")
    assert failure.value.code == "release_conflict"


def test_one_snapshot_cannot_declare_conflicting_release_digests(contract):
    bundle = REFERENCE.bundle_for()
    first, second = bundle["request"]["quotes"]
    first["source"]["content_digest"] = "sha256:" + "a" * 64
    second["source"].update(version=first["source"]["version"], content_digest="sha256:" + "b" * 64)
    bundle["rate_releases"][0]["quote_ids"].append(second["id"])
    bundle["rate_releases"] = bundle["rate_releases"][:1]
    reseal_records([bundle])
    with pytest.raises(contract.BundleError) as failure:
        contract.verify_bundle(bundle)
    assert failure.value.code == "release_conflict"


def test_release_retrieval_order_and_quote_subsets_can_change(contract):
    records = REFERENCE.history()[:2]
    second = records[1]
    second["request"]["quotes"].reverse()
    second["rate_releases"].reverse()
    for release in second["rate_releases"]:
        release["retrieved_on"] = "2026-02-10"
    subset = copy.deepcopy(second)
    subset.update(bundle_id="subset", recorded_on="2026-02-11", reason="second segment only")
    subset["request"]["usage"] = subset["request"]["usage"][1:]
    subset["request"]["quotes"] = subset["request"]["quotes"][:1]
    subset["rate_releases"] = subset["rate_releases"][:1]
    records.append(subset)
    restored = copy.deepcopy(second)
    restored.update(bundle_id="restored-scope", recorded_on="2026-02-12", reason="restore scope")
    records.append(restored)
    checkpoint = reseal_records(records)
    expected = {"2026-02-10": "125.00", "2026-02-11": "80.00", "2026-02-12": "125.00"}
    for as_of, total in expected.items():
        result = contract.verify_history(records, expected_head_digest=checkpoint, as_of=as_of)
        assert result["report"]["totals"]["rounded"] == total
