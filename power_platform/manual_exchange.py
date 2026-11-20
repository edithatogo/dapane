"""Manual exchange of synthetic point-valuation bundles using the installed CLI and wheel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_run_bundle as bundles  # noqa: E402

VERSION = "dapane-file-exchange/0.1"
SHAREPOINT_VERSION = "dapane-sharepoint-exchange/1.0"
IDENTITY = ("ProjectKey", "ScenarioId", "InputRevision")
FILES = {"report.json", "bundle.json", "receipt.json"}


def sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_bytes(path, limit):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{path.name} must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("file exceeds the exchange byte limit")
    return raw


def matches_bytes(path, expected):
    return (
        not path.is_symlink()
        and path.is_file()
        and path.stat().st_size == len(expected)
        and read_bytes(path, len(expected)) == expected
    )


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
    bundles._date(template.get("recorded_on"), "/bundle/recorded_on")
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
                if not matches_bytes(path, raw):
                    raise ValueError("destination already holds a different revision") from None
        finally:
            temp.unlink(missing_ok=True)


def sharepoint_plan(raw, packet):
    identity = {key: packet[key] for key in IDENTITY}
    revision = hashlib.sha256(encode(identity)).hexdigest()
    return {
        "ExchangeVersion": SHAREPOINT_VERSION,
        "ExchangeKey": revision,
        "InputContentHash": sha(raw),
        "InputPath": f"{revision}/input.json",
        "ResultFolder": f"{revision}/result",
    }


def export_file(source, output, *, sharepoint=False):
    raw, packet = input_file(source)
    publish_file(output, raw)
    return sharepoint_plan(raw, packet) if sharepoint else sha(raw)


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


def archive_files(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("expected a regular result directory")
    files = {path.name: path for path in directory.iterdir()}
    if files.keys() != FILES:
        raise ValueError("result directory must contain report.json, bundle.json and receipt.json")
    return files


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
            if not directory.exists() and not directory.is_symlink():
                raise
            saved = archive_files(directory)
            if any(not matches_bytes(saved[name], data) for name, data in content.items()):
                raise ValueError("archive location already holds different bytes") from None
    return resolved["bundle_digest"]


def archive_link(library, folder):
    url = urlsplit(library)
    parts = [unquote(part, errors="strict") for part in url.path.strip("/").split("/")]
    if (
        not library.isprintable()
        or library.strip() != library
        or url.scheme != "https"
        or re.fullmatch(r"[a-z0-9-]+\.sharepoint\.com", url.hostname or "") is None
        or url.netloc.casefold() != url.hostname
        or url.query
        or url.fragment
        or parts[-1].casefold().endswith(".aspx")
        or any(
            part in {"", ".", ".."}
            or not part.isprintable()
            or any(char in '/\\:*?"<>|' for char in part)
            for part in parts
        )
    ):
        raise ValueError("supply a direct HTTPS SharePoint Online library URL")
    path = "/".join(quote(part, safe="") for part in parts)
    link = f"https://{url.hostname}/{path}/{folder}/bundle.json"
    if len(link) > 255:
        raise ValueError("use a shorter library URL for the result hyperlink")
    return link


def sharepoint_summary(raw, packet, row, policy, library):
    plan = sharepoint_plan(raw, packet)
    return {
        "Title": row["ScenarioId"],
        **{key: plan[key] for key in ("ExchangeVersion", "ExchangeKey", "InputContentHash")},
        **{key: row[key] for key in IDENTITY},
        "BundleDigest": row["BundleDigest"],
        "OutputContentHash": row["OutputContentHash"],
        "CalculationContractVersion": row["CalculationContractVersion"],
        "JobState": row["JobState"],
        "NativeStatus": row["NativeStatus"],
        "ExcludedInputCount": len(row["ExcludedInputs"]),
        "IncompleteCapacityPoolCount": len(row["IncompleteCapacityPools"]),
        "OutputLink": archive_link(library, plan["ResultFolder"]),
        "Total": row["Total"],
        "Currency": row["Currency"],
        "PriceYear": policy["price_year"],
        "Perspective": policy["perspective"],
        "ValuationBasis": policy["basis"],
    }


def import_result(source, directory, output, *, sharepoint_library=None):
    raw, packet = input_file(source)
    files = archive_files(directory)
    report = read_bytes(files["report.json"], bundles.MAX_BUNDLE_BYTES)
    archive = read_bytes(files["bundle.json"], bundles.MAX_BUNDLE_BYTES + 1)
    manifest = decode(read_bytes(files["receipt.json"], 4096))
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
    fields = (
        row
        if sharepoint_library is None
        else sharepoint_summary(raw, packet, row, result["policy"], sharepoint_library)
    )
    publish_file(output, encode(fields))
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
        if command == "export":
            metadata = sub.add_mutually_exclusive_group()
            metadata.add_argument("--sharepoint-plan", type=Path, help="save upload paths as JSON")
            metadata.add_argument("--digest-out", type=Path, help="save the input SHA-256 digest")
        if command == "import":
            sub.add_argument("--sharepoint-library", help="produce SharePoint list fields")
    args = parser.parse_args()
    try:
        if args.command == "export":
            if args.sharepoint_plan is not None:
                plan = export_file(args.input, args.out, sharepoint=True)
                publish_file(args.sharepoint_plan, encode(plan))
            else:
                digest = export_file(args.input, args.out)
                if args.digest_out is not None:
                    publish_file(args.digest_out, (digest + "\n").encode("ascii"))
            print("exported")
        elif args.command == "run":
            execute(args.input, args.cli, args.archive)
            print("archived")
        else:
            status = import_result(
                args.input, args.archive, args.out, sharepoint_library=args.sharepoint_library
            )
            if status == "incomplete":
                print("incomplete")
            else:
                print("completed")
    except ValueError:
        # Parser and replay errors can include values from the input or native stderr.
        parser.exit(1, "Exchange rejected. Check the input, replay, and destination revision.\n")
    except OSError:
        parser.exit(1, "Exchange could not access the requested files or CLI.\n")
    except subprocess.TimeoutExpired:
        parser.exit(1, "Native evaluation timed out.\n")


if __name__ == "__main__":
    main()
