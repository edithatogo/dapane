#!/usr/bin/env python3
"""Validate independent interval references, schemas and the installed Rust CLI.

Python checks evidence and exact reference values; the supported evaluator is Rust.
All schema references resolve locally. No source or schema URL is fetched.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from validate_contract import (
    CONTEXT_IDS,
    ContractFailure,
    canonical,
    digest,
    fraction,
    keyed,
    normalize_request,
    read_json,
    require,
    set_path,
    strict_loads,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "intervals"
SCHEMAS = ROOT / "schemas"


def validators() -> dict[str, Draft202012Validator]:
    registry = Registry()
    selected = {}
    for directory in ("0.1", "0.2", "intervals"):
        for path in sorted((SCHEMAS / directory).glob("*.schema.json")):
            document = read_json(path)
            Draft202012Validator.check_schema(document)
            registry = registry.with_resource(document["$id"], Resource.from_contents(document))
            if directory == "intervals":
                selected[path.stem.removesuffix(".schema")] = document
            elif directory == "0.1" and path.name == "error.schema.json":
                selected["error"] = document
    return {
        name: Draft202012Validator(value, registry=registry, format_checker=FormatChecker())
        for name, value in selected.items()
    }


def normalize(input_request: dict) -> dict:
    """Independent wire normalization, without financial evaluation."""
    result = deepcopy(input_request)
    result["request"] = normalize_request(result["request"])
    capacity = result["request"].get("capacity_allocations", [])
    if not capacity:
        result["request"].pop("capacity_allocations", None)
    else:
        capacity.sort(key=lambda item: item["id"])
        for allocation in capacity:
            allocation["source_line_ids"].sort()
            allocation["use_records"].sort(key=lambda item: item["object_id"])
            allocation["source"].setdefault("content_digest", None)
            allocation["source"].setdefault("locator", None)
    for interval in result["intervals"]:
        interval["quote_ids"].sort()
        interval.setdefault("object_ids", [])
        interval["object_ids"].sort()
        for key in CONTEXT_IDS:
            interval.setdefault(key, None)
        interval["source"].setdefault("content_digest", None)
        interval["source"].setdefault("locator", None)
    result["intervals"].sort(key=lambda item: item["id"])
    return result


def call(cli: Path, command: str, request: dict | str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(cli), command, "-"],
        input=request if isinstance(request, str) else canonical(request),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        cwd=ROOT,
        check=False,
    )


def successful(cli: Path, request: dict, checkers: dict) -> dict:
    result = call(cli, "evaluate-intervals", request)
    require(result.returncode == 0, f"Interval CLI failed: {result.stderr[:1000]}")
    require(not result.stderr.strip(), "Successful interval CLI wrote stderr")
    report = strict_loads(result.stdout)
    validate(checkers["report"], report, "interval report")
    return report


def verify_lineage(request: dict, report: dict) -> dict:
    """Check original-to-derived provenance without evaluating any monetary rule."""
    normalized = normalize(request)
    require(
        report["request_snapshot"] == normalized["request"],
        "Original normalized request template was not retained",
    )
    require(
        report["interval_snapshots"] == normalized["intervals"],
        "Original normalized interval snapshots were not retained",
    )
    original = normalized["request"]
    expanded = report["expanded_request"]
    scalar = report["report"]
    transformed = {"usage", "allocations", "capacity_allocations"}
    require(
        {key: value for key, value in expanded.items() if key not in transformed}
        == {key: value for key, value in original.items() if key not in transformed},
        "Expansion changed original quote, policy or context snapshots",
    )
    require(scalar["policy"] == original["policy"], "Scalar policy snapshot changed")
    require(scalar["quote_snapshots"] == original["quotes"], "Scalar quote snapshots changed")
    require(scalar["run_id"] == original["run_id"], "Scalar run identity changed")
    require(scalar["schema_version"] == original["schema_version"], "Scalar contract changed")
    require(
        scalar["context"]
        == {key: original[key] for key in ("objects", "processes", "events", "object_relations")},
        "Scalar context snapshots changed",
    )
    parents = keyed(normalized["intervals"], "id", "original intervals")
    points = keyed(original["usage"], "id", "original point rows")
    quotes = keyed(original["quotes"], "id", "original quotes")
    events = keyed(original["events"], "id", "original events")
    segments = keyed(report["segments"], "line_id", "interval segments")
    uses = keyed(expanded["usage"], "id", "expanded usage")
    lines = keyed(scalar["lines"], "id", "scalar lines")
    require(not set(points).intersection(segments), "Generated line collides with an original row")
    require(set(uses) == set(points) | set(segments), "Expansion has missing or unexplained rows")
    require(set(lines) == set(uses), "Scalar source ledger differs from prepared row identities")
    for point_id, point in points.items():
        require(uses[point_id] == point, "Expansion changed an original point row")
    children = {parent_id: [] for parent_id in parents}
    retained = ("kind", "target", "unit", "source", "object_ids", *CONTEXT_IDS)
    for line_id, segment in segments.items():
        require(segment["interval_id"] in parents, "Segment refers to an unknown parent")
        parent = parents[segment["interval_id"]]
        require(segment["use_id"] == parent["use_id"], "Segment lost the original use identity")
        require(segment["quote_id"] in parent["quote_ids"], "Segment uses an unselected quote")
        quote = quotes[segment["quote_id"]]
        require(
            segment["start"] == max(parent["start"], quote["valid_from"])
            and segment["end"] == min(parent["end"], quote["valid_to"]),
            "Segment dates differ from its original selected quote intersection",
        )
        expected_line_id = "il-" + digest(
            "dapane:interval-line:0.1\n", [parent["id"], segment["start"], segment["end"]]
        ).removeprefix("sha256:")
        expected_use_id = "iu-" + digest(
            "dapane:interval-use:0.1\n", [parent["use_id"], segment["start"], segment["end"]]
        ).removeprefix("sha256:")
        require(
            line_id == expected_line_id, "Generated line identity differs from its parent tuple"
        )
        require(
            uses[line_id]["use_id"] == expected_use_id,
            "Generated use identity differs from its parent tuple",
        )
        prepared = {key: parent[key] for key in retained}
        prepared.update(
            id=line_id,
            use_id=uses[line_id]["use_id"],
            service_date=segment["start"],
            quote_id=segment["quote_id"],
            quantity=segment["quantity"],
        )
        require(uses[line_id] == prepared, "Prepared segment changed parent source or context")
        children[parent["id"]].append(segment)
    for parent_id, records in children.items():
        parent = parents[parent_id]
        require(len(records) == len(parent["quote_ids"]), "Unexpected segment count for parent")
        require(
            {record["quote_id"] for record in records} == set(parent["quote_ids"]),
            "Segment selection differs from the parent's pinned quote series",
        )
        cursor = parent["start"]
        for segment in sorted(records, key=lambda item: (item["start"], item["end"])):
            require(segment["start"] == cursor, "Segments overlap or leave an interval gap")
            require(segment["start"] < segment["end"], "Segment is empty or reversed")
            cursor = segment["end"]
        require(cursor == parent["end"], "Segments do not cover the original interval")
    for field in ("allocations", "capacity_allocations"):
        expected_pools = deepcopy(original.get(field, []))
        for pool in expected_pools:
            pool["source_line_ids"] = sorted(
                child["line_id"]
                for source_id in pool["source_line_ids"]
                for child in children.get(source_id, [{"line_id": source_id}])
            )
        require(
            expanded.get(field, []) == expected_pools,
            f"Expansion changed {field} beyond replacing parent source references",
        )
    for line_id, prepared in uses.items():
        line = lines[line_id]
        for field in (
            "id",
            "use_id",
            "kind",
            "target",
            "unit",
            "quote_id",
            "service_date",
            "source",
            "event_id",
            "object_ids",
            "attribution_object_id",
        ):
            require(line[field] == prepared[field], f"Scalar line changed prepared {field}")
        require(
            fraction(line["quantity"]) == fraction(prepared["quantity"]),
            "Scalar line changed the exact prepared quantity",
        )
        require(
            line["components"] == quotes[prepared["quote_id"]]["components"],
            "Scalar line changed its selected quote components",
        )
        event = events.get(prepared["event_id"], {})
        for field in ("process_id", "activity_id"):
            expected_context = prepared[field]
            if expected_context is None:
                expected_context = event.get(field)
            require(line[field] == expected_context, f"Scalar line changed resolved {field}")
    return normalized


def lineage_rejections(request: dict, report: dict, checkers: dict) -> int:
    """Prove lineage controls reject structurally valid tampering of actual output.

    These checks deliberately call the pure lineage verifier without digest or
    financial checks, so a stale digest cannot conceal a missing lineage control.
    """
    cases = []
    for label, path in [
        ("duplicate segment", ("segments",)),
        ("duplicate prepared row", ("expanded_request", "usage")),
        ("duplicate scalar line", ("report", "lines")),
    ]:
        tampered = deepcopy(report)
        rows = tampered
        for key in path:
            rows = rows[key]
        rows.append(deepcopy(rows[0]))
        cases.append((label, tampered))
    for label, path, value in [
        (
            "duplicate segment identity",
            ("segments", 1, "line_id"),
            report["segments"][0]["line_id"],
        ),
        ("lost parent identity", ("segments", 0, "interval_id"), "unknown-parent"),
        ("altered quote snapshot", ("expanded_request", "quotes", 0, "amount"), "999"),
        (
            "altered scalar quote source",
            ("report", "quote_snapshots", 0, "source", "version"),
            "changed",
        ),
        (
            "altered prepared source",
            ("expanded_request", "usage", 0, "source", "version"),
            "changed",
        ),
        ("altered scalar source", ("report", "lines", 0, "source", "version"), "changed"),
        (
            "altered original source",
            ("request_snapshot", "quotes", 0, "source", "version"),
            "changed",
        ),
        ("altered interval source", ("interval_snapshots", 0, "source", "version"), "changed"),
        (
            "altered prepared context",
            ("expanded_request", "objects"),
            [{"id": "extra", "kind": "recipient"}],
        ),
        (
            "altered scalar context",
            ("report", "context", "objects"),
            [{"id": "extra", "kind": "recipient"}],
        ),
    ]:
        cases.append((label, set_path(report, path, value)))
    for field, replacement in [("id", "changed-line"), ("use_id", "changed-use")]:
        tampered = deepcopy(report)
        line_id = tampered["segments"][0]["line_id"]
        prepared = next(
            row for row in tampered["expanded_request"]["usage"] if row["id"] == line_id
        )
        scalar = next(row for row in tampered["report"]["lines"] if row["id"] == line_id)
        prepared[field] = replacement
        scalar[field] = replacement
        if field == "id":
            tampered["segments"][0]["line_id"] = replacement
        cases.append((f"consistently altered generated {field}", tampered))
    for label, tampered in cases:
        validate(checkers["report"], tampered, f"{label}: structural precondition")
        try:
            verify_lineage(request, tampered)
        except ContractFailure:
            pass
        else:
            raise ContractFailure(f"Lineage verifier accepted {label}")
    return len(cases)


def verify(cli: Path, request: dict, expected: dict, checkers: dict) -> int:
    report = successful(cli, request, checkers)
    normalized = verify_lineage(request, report)
    reconstructed = {
        "schema_version": report["schema_version"],
        "request": report["request_snapshot"],
        "intervals": report["interval_snapshots"],
    }
    require(reconstructed == normalized, "Report lost original input identities")
    require(
        report["input_digest"] == digest("dapane:interval-input:0.1\n", reconstructed),
        "Interval input digest differs from independent normalization",
    )
    unsigned = deepcopy(report)
    output_digest = unsigned.pop("output_digest")
    require(
        output_digest == digest("dapane:interval-output:0.1\n", unsigned),
        "Interval output digest differs from independently calculated digest",
    )
    scalar = report["report"]
    require(scalar["totals"]["rounded"] == expected["rounded"], "Independent total differs")
    require(scalar["totals"]["exact"] == expected["exact"], "Independent exact total differs")
    lines = keyed(scalar["lines"], "id", "reference scalar lines")
    segments = keyed(report["segments"], "start", "single-parent reference segments")
    require(len(report["segments"]) == len(expected["segments"]), "Unexpected segment count")
    quantity = Fraction(0)
    for reference in expected["segments"]:
        segment = segments[reference["start"]]
        for key in ("start", "end", "quote_id", "quantity"):
            require(segment[key] == reference[key], f"Segment {key} differs from reference")
        quantity += fraction(segment["quantity"])
        line = lines[segment["line_id"]]
        require(line["exact"] == reference["exact"], "Independent exact line differs")
        require(line["rounded"] == reference["rounded"], "Independent rounded line differs")
        require(line["quantity"] == reference["quantity"], "Line quantity differs from segment")
        require(segment["interval_id"] == request["intervals"][0]["id"], "Lost interval identity")
        require(segment["use_id"] == request["intervals"][0]["use_id"], "Lost parent use identity")
    require(quantity == fraction(request["intervals"][0]["quantity"]), "Quantity not conserved")
    replay = call(cli, "evaluate", report["expanded_request"])
    require(replay.returncode == 0 and not replay.stderr.strip(), "Scalar replay failed")
    require(strict_loads(replay.stdout) == scalar, "Expanded scalar request replay differs")
    require(successful(cli, request, checkers) == report, "Repeated run changed output identity")
    reordered = deepcopy(request)
    reordered["request"]["quotes"].reverse()
    reordered["intervals"][0]["quote_ids"].reverse()
    require(successful(cli, reordered, checkers) == report, "Input order changed report identity")
    return lineage_rejections(request, report, checkers)


def reject_cases(request: dict) -> list[dict | str]:
    cases = []
    for position, field, value in [
        ("interval", "end", "2026-01-31"),
        ("interval", "quote_ids", ["before"]),
        ("interval", "quote_ids", ["before", "before", "after"]),
        ("quote", "valid_from", "2026-02-02"),
        ("quote", "valid_from", "2026-01-31"),
        ("quote", "known_from", "2026-02-04"),
        ("quote", "components", ["different-component"]),
        ("quote", "unit", "minute"),
    ]:
        case = deepcopy(request)
        target = case["intervals"][0] if position == "interval" else case["request"]["quotes"][1]
        target[field] = value
        cases.append(case)
    duplicate = deepcopy(request)
    second = deepcopy(duplicate["intervals"][0])
    second["id"] = "other-line-same-use-and-components"
    duplicate["intervals"].append(second)
    cases.append(duplicate)
    nested = deepcopy(request)
    nested["request"]["schema_version"] = "0.1"
    nested["request"]["capacity_allocations"] = []
    cases.append(nested)
    raw = canonical(request)
    cases.append(raw[:-1] + ',"schema_version":"0.1"}')
    return cases


def schema_rejections(request: dict, checkers: dict) -> int:
    count = 0
    for key in ("exposure", "start", "end", "quote_ids"):
        missing = deepcopy(request)
        del missing["intervals"][0][key]
        require(not checkers["request"].is_valid(missing), f"Schema accepted missing {key}")
        count += 1
    for field, value in [
        ("quantity", 0.5),
        ("exposure", "infer_uniform"),
        ("start", "2026-02-30"),
    ]:
        invalid = deepcopy(request)
        invalid["intervals"][0][field] = value
        require(not checkers["request"].is_valid(invalid), f"Schema accepted invalid {field}")
        count += 1
    empty = deepcopy(request)
    empty["intervals"] = []
    require(not checkers["request"].is_valid(empty), "Schema accepted empty interval list")
    count += 1
    nested = deepcopy(request)
    nested["request"]["schema_version"] = "0.1"
    nested["request"]["capacity_allocations"] = []
    require(not checkers["request"].is_valid(nested), "Schema accepted 0.1 capacity field")
    return count + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, help="Validate an independently built or installed CLI")
    args = parser.parse_args()
    checkers = validators()
    references = read_json(FIXTURES / "expected.json")
    request = read_json(FIXTURES / "rate-boundary.json")
    validate(checkers["request"], request, "independent interval reference")
    count = schema_rejections(request, checkers)
    print(
        "Validated interval request/report schemas and synthetic reference; "
        f"{count} negative cases passed."
    )
    if args.cli is None:
        print("Rust interval evaluation and digests were not exercised; supply --cli.")
        return 0
    cli = args.cli.resolve()
    require(cli.is_file(), f"CLI does not exist: {cli}")
    lineage_count = verify(cli, request, references["fixtures"]["rate-boundary.json"], checkers)
    cases = reject_cases(request)
    for case in cases:
        result = call(cli, "evaluate-intervals", case)
        require(result.returncode != 0, "Invalid interval case produced a successful report")
        require(not result.stdout.strip(), "Invalid interval case produced financial stdout")
        validate(checkers["error"], strict_loads(result.stderr), "interval diagnostic")
    print(
        "Verified independent exact segment/reference values, parent lineage, conservation, "
        "immutable digests, scalar replay and ordering; "
        f"{len(cases)} runtime rejection cases and {lineage_count} tampered-report controls passed."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractFailure, json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Interval validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
