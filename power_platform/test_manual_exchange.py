"""Manual file transport and replay, including partial coverage and immutable retries."""

import copy
import json
import os
import subprocess
from pathlib import Path

import manual_exchange as exchange
import pytest

FIXTURE = Path(__file__).parent / "fixtures/manual-input.json"


@pytest.fixture
def cli():
    value = os.environ.get("DAPANE_CLI")
    if not value:
        pytest.skip("Set DAPANE_CLI to the built point-valuation CLI")
    return Path(value)


def test_exact_archive_and_idempotent_replay(tmp_path, cli):
    source, archive, summary = tmp_path / "input.json", tmp_path / "archive", tmp_path / "row.json"
    exchange.export_file(FIXTURE, source)
    assert source.read_bytes() == FIXTURE.read_bytes()
    first = exchange.execute(source, cli, archive)
    original = {path.name: path.read_bytes() for path in archive.iterdir()}
    direct = subprocess.check_output(
        [str(cli), "evaluate", "-"],
        input=exchange.bundles.canonical(json.loads(source.read_bytes())["bundle"]["request"]),
    )
    assert original["report.json"] == direct
    assert exchange.execute(source, cli, archive) == first
    assert {path.name: path.read_bytes() for path in archive.iterdir()} == original
    assert exchange.import_result(source, archive, summary) == "completed"
    row = json.loads(summary.read_bytes())
    assert (row["ProjectKey"], row["ScenarioId"], row["Currency"], row["Total"]) == (
        "SYN-01",
        "SYN-PATHWAY",
        "AUD",
        "150.00",
    )
    assert row["BundleDigest"] == first
    assert exchange.import_result(source, archive, summary) == "completed"
    source.write_bytes(source.read_bytes() + b" ")
    with pytest.raises(ValueError, match="receipt"):
        exchange.import_result(source, archive, summary)
    with pytest.raises(ValueError, match="different bytes"):
        exchange.execute(source, cli, archive)
    assert {path.name: path.read_bytes() for path in archive.iterdir()} == original


def test_missing_inputs_and_changed_result(tmp_path, cli):
    packet = json.loads(FIXTURE.read_bytes())
    source = tmp_path / "input.json"
    archive = tmp_path / "archive"
    out = tmp_path / "row.json"
    missing = {
        "id": "optional-input",
        "state": "missing",
        "reason": "No observation in the synthetic extract",
    }
    packet["bundle"]["excluded_inputs"] = [missing]
    source.write_text(json.dumps(packet))
    exchange.execute(source, cli, archive)
    assert exchange.import_result(source, archive, out) == "incomplete"
    row = json.loads(out.read_bytes())
    assert (
        row["NativeStatus"] == "complete"
        and row["Total"] is None
        and row["ExcludedInputs"] == [missing]
    )
    report = archive / "report.json"
    report.write_bytes(report.read_bytes() + b" ")
    with pytest.raises(ValueError, match="receipt"):
        exchange.import_result(source, archive, tmp_path / "rejected.json")
    assert not (tmp_path / "rejected.json").exists()


def test_replacement_needs_verified_predecessor(tmp_path, cli):
    source = tmp_path / "input.json"
    archive = tmp_path / "original"
    exchange.export_file(FIXTURE, source)
    exchange.execute(source, cli, archive)
    parent = json.loads((archive / "bundle.json").read_bytes())
    packet = json.loads(source.read_bytes())
    packet["history"] = [parent]
    packet["InputRevision"] = "2"
    packet["bundle"].update(
        change="replace",
        bundle_id="replacement",
        previous_digest=parent["bundle_digest"],
        reason="Synthetic correction",
    )
    source.write_text(json.dumps(packet))
    exchange.execute(source, cli, tmp_path / "replacement")
    wrong = copy.deepcopy(packet)
    wrong["history"] = []
    source.write_text(json.dumps(wrong))
    with pytest.raises(ValueError, match="missing_origin"):
        exchange.execute(source, cli, tmp_path / "bad")
    assert not (tmp_path / "bad").exists()


def test_native_capacity_gap_is_visible(tmp_path, cli):
    packet = json.loads(FIXTURE.read_bytes())
    template = packet["bundle"]
    req = json.loads(
        (exchange.ROOT / "fixtures/newborn-synthetic/capacity-unknown.json").read_bytes()
    )
    template["request"] = req
    source_record = req["quotes"][0]["source"]
    template["rate_releases"] = [
        {
            "source_id": source_record["id"],
            "version": source_record["version"],
            "quote_ids": [q["id"] for q in req["quotes"]],
            "published_on": "2026-01-01",
            "retrieved_on": "2026-11-15",
        }
    ]
    source = tmp_path / "input.json"
    archive = tmp_path / "archive"
    out = tmp_path / "row.json"
    source.write_text(json.dumps(packet))
    exchange.execute(source, cli, archive)
    assert exchange.import_result(source, archive, out) == "incomplete"
    row = json.loads(out.read_bytes())
    assert row["IncompleteCapacityPools"] == ["instrument-capacity-pool"] and row["Total"] is None
