"""Manual exchange of synthetic point-valuation bundles using the installed CLI and wheel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_run_bundle as bundles  # noqa: E402

VERSION = "dapane-file-exchange/0.1"
IDENTITY = ("ProjectKey", "ScenarioId", "InputRevision")
FILES = {"report.json", "bundle.json", "receipt.json"}


def sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_bytes(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("file exceeds the exchange byte limit")
    return raw


def decode(raw):
    return json.loads(
        raw.decode("utf-8"), object_pairs_hook=bundles._pairs, parse_constant=bundles._constant
    )


def input_file(path):
    raw = read_bytes(path, bundles.MAX_HISTORY_BYTES)
    packet = decode(raw)
    if (
        not isinstance(packet, dict)
        or set(packet) != {"schema_version", *IDENTITY, "bundle", "history"}
        or packet["schema_version"] != VERSION
    ):
        raise ValueError("unknown manual request contract")
    for key in IDENTITY:
        value = packet[key]
        if (
            not isinstance(value, str)
            or not 1 <= len(value.encode("utf-8")) <= 128
            or value.strip() != value
            or not value.isprintable()
        ):
            raise ValueError(f"invalid {key}")
    template = packet["bundle"]
    if (
        not isinstance(template, dict)
        or template.get("change") not in ("create", "replace")
        or template.get("qualification") != "synthetic_candidate"
        or "report" in template
        or "bundle_digest" in template
    ):
        raise ValueError("supply a synthetic create or replacement request without a result")
    if (
        not isinstance(template.get("request"), dict)
        or not isinstance(packet["history"], list)
        or len(packet["history"]) >= bundles.MAX_REVISIONS
    ):
        raise ValueError("invalid request or history")
    return raw, packet


def publish_file(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        try:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
            try:
                os.link(temp, path)
            except FileExistsError:
                if path.is_symlink() or not path.is_file() or read_bytes(path, len(raw)) != raw:
                    raise ValueError("destination already holds a different revision") from None
        finally:
            temp.unlink(missing_ok=True)


def export_file(source, output):
    raw, _ = input_file(source)
    publish_file(output, raw)
    return sha(raw)


def assemble(packet, report):
    bundle = {**packet["bundle"], "report": report}
    bundle["bundle_digest"] = bundles.bundle_digest(bundle)
    result = bundles.verify_history(
        [*packet["history"], bundle],
        expected_head_digest=bundle["bundle_digest"],
        as_of=bundle["recorded_on"],
    )
    if result["status"] != "active":
        raise ValueError("the submitted revision is inactive")
    return bundle


def encode(value):
    return bundles.canonical(value) + b"\n"


def receipt(raw, packet, report, archive):
    return {
        "schema_version": VERSION,
        **{key: packet[key] for key in IDENTITY},
        "input_sha256": sha(raw),
        "report_sha256": sha(report),
        "bundle_sha256": sha(archive),
    }


def execute(source, cli, directory):
    raw, packet = input_file(source)
    result = subprocess.run(
        [str(cli), "evaluate", "-"],
        input=bundles.canonical(packet["bundle"]["request"]),
        capture_output=True,
        timeout=60,
    )
    if result.returncode:
        raise ValueError(
            "native evaluation failed: " + result.stderr[:500].decode("utf-8", errors="replace")
        )
    if len(result.stdout) > bundles.MAX_BUNDLE_BYTES:
        raise ValueError("native result exceeds bundle size limit")
    resolved = assemble(packet, decode(result.stdout))
    archive = encode(resolved)
    manifest = encode(receipt(raw, packet, result.stdout, archive))
    content = {"report.json": result.stdout, "bundle.json": archive, "receipt.json": manifest}
    directory.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=directory.parent) as staging:
        fresh = Path(staging) / "ready"
        fresh.mkdir()
        for name, data in content.items():
            (fresh / name).write_bytes(data)
        try:
            # An existing nonempty archive is immutable; identical retries share it.
            if directory.exists() or directory.is_symlink():
                raise FileExistsError
            fresh.rename(directory)
        except OSError:
            if (
                directory.is_symlink()
                or not directory.is_dir()
                or {p.name for p in directory.iterdir()} != FILES
            ):
                raise
            if any(
                (directory / name).is_symlink() or read_bytes(directory / name, len(data)) != data
                for name, data in content.items()
            ):
                raise ValueError("archive location already holds different bytes") from None
    return resolved["bundle_digest"]


def import_result(source, directory, output):
    raw, packet = input_file(source)
    report = read_bytes(directory / "report.json", bundles.MAX_BUNDLE_BYTES)
    archive = read_bytes(directory / "bundle.json", bundles.MAX_BUNDLE_BYTES + 1)
    manifest = decode(read_bytes(directory / "receipt.json", 4096))
    if manifest != receipt(raw, packet, report, archive):
        raise ValueError("receipt does not match the submitted source and downloaded files")
    result = decode(report)
    bundle = assemble(packet, result)
    if archive != encode(bundle):
        raise ValueError("archive differs from native replay and submitted identity")
    excluded = bundle["excluded_inputs"]
    partial_pools = [
        pool["id"]
        for pool in result.get("capacity_allocations", [])
        if pool["observation_coverage"] != "complete"
        or pool["available_capacity"]["status"] != "known"
    ]
    status = result["status"]
    incomplete = status != "complete" or bool(excluded) or bool(partial_pools)
    row = {
        **{key: packet[key] for key in IDENTITY},
        "RunId": result["run_id"],
        "BundleId": bundle["bundle_id"],
        "SeriesId": bundle["series_id"],
        "BundleDigest": bundle["bundle_digest"],
        "OutputContentHash": sha(archive),
        "CalculationContractVersion": result["method_version"],
        "JobState": "incomplete" if incomplete else "completed",
        "NativeStatus": status,
        "ExcludedInputs": excluded,
        "IncompleteCapacityPools": partial_pools,
        "OutputFile": "bundle.json",
        "Total": None if incomplete else result["totals"]["rounded"],
        "Currency": result["policy"]["currency"],
    }
    publish_file(output, encode(row))
    return row["JobState"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("export", "run", "import"):
        sub = commands.add_parser(command)
        sub.add_argument("--input", type=Path, required=True)
        if command in ("run", "import"):
            sub.add_argument("--archive", type=Path, required=True)
        if command in ("export", "import"):
            sub.add_argument("--out", type=Path, required=True)
        if command == "run":
            sub.add_argument("--cli", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "export":
            outcome = export_file(args.input, args.out)
        elif args.command == "run":
            outcome = execute(args.input, args.cli, args.archive)
        else:
            outcome = import_result(args.input, args.archive, args.out)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"{exc}\n")
    print(outcome)


if __name__ == "__main__":
    main()
