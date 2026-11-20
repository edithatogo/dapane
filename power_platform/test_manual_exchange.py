"""Manual file transport and replay, including partial coverage and immutable retries."""

import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import manual_exchange as exchange
import pytest

FIXTURE = Path(__file__).parent / "fixtures/manual-input.json"
LIBRARY = "https://example.sharepoint.com/sites/synthetic-costing/Run%20Bundles"


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
    native_fields = tmp_path / "fields.json"
    assert (
        exchange.import_result(source, archive, native_fields, sharepoint_library=LIBRARY)
        == "incomplete"
    )
    fields = json.loads(native_fields.read_bytes())
    assert fields["JobState"] == "incomplete" and fields["Total"] is None
    assert fields["ExcludedInputCount"] == 1
    assert fields["IncompleteCapacityPoolCount"] == 0
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
    native_fields = tmp_path / "fields.json"
    assert (
        exchange.import_result(source, archive, native_fields, sharepoint_library=LIBRARY)
        == "incomplete"
    )
    fields = json.loads(native_fields.read_bytes())
    assert fields["IncompleteCapacityPoolCount"] == 1 and fields["Total"] is None


def test_sharepoint_handoff_from_downloaded_files(tmp_path, cli):
    script = [sys.executable, str(Path(exchange.__file__))]
    source = tmp_path / "export.json"
    library = tmp_path / "document-library"
    out = tmp_path / "list-fields.json"
    plan = json.loads(
        subprocess.check_output(
            [
                *script,
                "export",
                "--input",
                str(FIXTURE),
                "--out",
                str(source),
                "--sharepoint-plan",
            ]
        )
    )
    in_library = library / plan["InputPath"]
    in_library.parent.mkdir(parents=True)
    shutil.copyfile(source, in_library)
    downloaded = tmp_path / "download.json"
    shutil.copyfile(in_library, downloaded)
    prepared = tmp_path / "prepared"
    installed_bundle = exchange.execute(downloaded, cli, prepared)
    uploaded = library / plan["ResultFolder"]
    shutil.copytree(prepared, uploaded)
    retrieved = tmp_path / "retrieved"
    shutil.copytree(uploaded, retrieved)
    result = subprocess.check_output(
        [
            *script,
            "import",
            "--input",
            str(source),
            "--archive",
            str(retrieved),
            "--out",
            str(out),
            "--sharepoint-library",
            LIBRARY,
        ],
        text=True,
    )
    assert result.strip() == "completed"
    fields = json.loads(out.read_bytes())
    contract = json.loads(
        (Path(exchange.__file__).parent / "sharepoint-contract.json").read_bytes()
    )
    columns = contract["results_list"]["columns"]
    assert set(fields) == set(columns)
    assert contract["version"] == fields["ExchangeVersion"] == plan["ExchangeVersion"]
    assert plan["InputPath"] == contract["library"]["input_path"].format(**plan)
    assert plan["ResultFolder"] == contract["library"]["result_folder"].format(**plan)
    assert {p.name for p in retrieved.iterdir()} == set(contract["library"]["result_files"])
    for name, column in columns.items():
        if column["type"] == "Number":
            assert type(fields[name]) is int
        else:
            assert isinstance(fields[name], str) and 0 < len(fields[name]) <= 255
        if column["type"] == "Choice":
            assert fields[name] in column["choices"]
    assert fields["ExchangeKey"] == plan["ExchangeKey"]
    assert (
        fields["InputContentHash"] == plan["InputContentHash"] == exchange.sha(source.read_bytes())
    )
    assert fields["OutputContentHash"] == exchange.sha((retrieved / "bundle.json").read_bytes())
    assert fields["BundleDigest"] == installed_bundle
    assert fields["OutputLink"] == f"{LIBRARY}/{plan['ResultFolder']}/bundle.json"
    assert (fields["Total"], fields["Currency"], fields["PriceYear"]) == ("150.00", "AUD", 2026)


def test_sharepoint_key_tracks_project_scenario_revision(tmp_path):
    original = tmp_path / "export.json"
    edited = tmp_path / "edited.json"
    raw = FIXTURE.read_bytes()
    source = tmp_path / "input.json"
    source.write_bytes(raw)
    base = exchange.export_file(source, original, sharepoint=True)
    source.write_bytes(raw + b" ")
    changed = exchange.export_file(source, edited, sharepoint=True)
    assert changed["ExchangeKey"] == base["ExchangeKey"]
    assert changed["InputContentHash"] != base["InputContentHash"]
    assert changed["ResultFolder"] == base["ResultFolder"]
    for key in exchange.IDENTITY:
        packet = json.loads(raw)
        packet[key] += "-changed"
        source.write_text(json.dumps(packet))
        plan = exchange.export_file(source, tmp_path / f"{key}.json", sharepoint=True)
        assert plan["ExchangeKey"] != base["ExchangeKey"]
        assert plan["ResultFolder"] != base["ResultFolder"]


@pytest.mark.parametrize(
    "library",
    (
        "https://example.invalid/library",
        "http://example.sharepoint.com/library",
        "https://example.sharepoint.com/library/Forms/AllItems.aspx",
    ),
)
def test_sharepoint_link_requires_a_direct_library_url(library):
    with pytest.raises(ValueError, match="direct HTTPS SharePoint Online library"):
        exchange.archive_link(library, "row/result")


def test_import_rejects_an_unfinished_archive(tmp_path, cli):
    archive = tmp_path / "archive"
    exchange.execute(FIXTURE, cli, archive)
    (archive / "receipt.json").rename(tmp_path / "not-yet-downloaded")
    output = tmp_path / "row.json"
    with pytest.raises(ValueError, match="result directory must contain"):
        exchange.import_result(FIXTURE, archive, output)
    assert not output.exists()


def test_export_requires_the_recording_date(tmp_path):
    packet = json.loads(FIXTURE.read_bytes())
    del packet["bundle"]["recorded_on"]
    source, output = tmp_path / "input.json", tmp_path / "exported.json"
    source.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="recorded_on"):
        exchange.export_file(source, output)
    assert not output.exists()
