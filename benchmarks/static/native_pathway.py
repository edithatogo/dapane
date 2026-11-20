"""Compare explicit allocation with a deliberately duplicated case-centric representation."""

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def call(args, request=None):
    result = subprocess.run(
        args,
        input=None if request is None else json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise ValueError(result.stderr)
    return json.loads(result.stdout)


def flattened(request):
    result = copy.deepcopy(request)
    recipients = {}
    for pool in result["allocations"]:
        for line_id in pool["source_line_ids"]:
            recipients[line_id] = [w["object_id"] for w in pool["weights"]]
    for pool in result.get("capacity_allocations", []):
        for line_id in pool["source_line_ids"]:
            recipients[line_id] = [usage["object_id"] for usage in pool["use_records"]]
    usage = []
    for line in result["usage"]:
        if line["id"] not in recipients:
            usage.append(line)
            continue
        for recipient in recipients[line["id"]]:
            # This intentionally assigns the full shared consumption to each recipient.
            changed = {
                **line,
                "id": line["id"] + "-" + recipient,
                "use_id": line["use_id"] + "-" + recipient,
                "attribution_object_id": recipient,
            }
            usage.append(changed)
    result["usage"] = usage
    result["allocations"] = []
    if "capacity_allocations" in result:
        result["capacity_allocations"] = []
    return result


def compare(request, cli, archive=None):
    original = call([cli, "evaluate", "-"], request)
    flat_request = flattened(request)
    flat = call([cli, "evaluate", "-"], flat_request)
    if archive is not None:
        archive.update(
            object_request=request,
            object_report=original,
            flat_request=flat_request,
            flat_report=flat,
        )
    return {
        "object_total": original["totals"]["rounded"],
        "flat_total": flat["totals"]["rounded"],
        "object_unattributed": original["totals"]["unattributed"],
        "flat_unattributed": flat["totals"]["unattributed"],
        "object_lines": len(original["lines"]),
        "flat_lines": len(flat["lines"]),
        "object_digest": original["output_digest"],
        "flat_digest": flat["output_digest"],
    }


def run(cli, process_cli, archive=None):
    root = ROOT / "fixtures/newborn-synthetic"
    cases = {}
    for case in [
        "composed-two-infant",
        "failed-assay-repeat",
        "capacity-at",
        "capacity-above",
        "capacity-unknown",
    ]:
        case_archive = archive.setdefault(case, {}) if archive is not None else None
        cases[case] = compare(json.loads((root / (case + ".json")).read_text()), cli, case_archive)
    fixture = ROOT / "adapters/process_models/fixtures"
    trace = call(
        [
            process_cli,
            "execute-pnml",
            fixture / "pnml/shared-batch-parallel.pnml",
            fixture / "pnml/shared-batch-parallel.config.json",
        ]
    )
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "trace.json"
        path.write_text(json.dumps(trace))
        request = call(
            [process_cli, "project-dapane", path, fixture / "quotes-release-2026-v1.json"]
        )
    process_archive = (
        archive.setdefault("process-shared-batch", {"trace": trace})
        if archive is not None
        else None
    )
    cases["process-shared-batch"] = {
        **compare(request, cli, process_archive),
        "model_sha256": trace["model_sha256"],
        "trace_uses": len(trace["usages"]),
        "valued_uses": len(request["usage"]),
    }
    return cases
