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
    normalize_request,
    read_json,
    require,
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


def verify(cli: Path, request: dict, expected: dict, checkers: dict) -> None:
    report = successful(cli, request, checkers)
    normalized = normalize(request)
    require(
        report["request_snapshot"] == normalized["request"],
        "Original normalized request template was not retained",
    )
    require(
        report["interval_snapshots"] == normalized["intervals"],
        "Original normalized interval snapshots were not retained",
    )
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
    lines = {line["id"]: line for line in scalar["lines"]}
    segments = {segment["start"]: segment for segment in report["segments"]}
    require(len(segments) == len(expected["segments"]), "Unexpected segment count")
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
    verify(cli, request, references["fixtures"]["rate-boundary.json"], checkers)
    cases = reject_cases(request)
    for case in cases:
        result = call(cli, "evaluate-intervals", case)
        require(result.returncode != 0, "Invalid interval case produced a successful report")
        require(not result.stdout.strip(), "Invalid interval case produced financial stdout")
        validate(checkers["error"], strict_loads(result.stderr), "interval diagnostic")
    print(
        "Verified independent exact segment/reference values, parent lineage, conservation, "
        "immutable digests, scalar replay and ordering; "
        f"{len(cases)} runtime rejection cases passed."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractFailure, json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Interval validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
