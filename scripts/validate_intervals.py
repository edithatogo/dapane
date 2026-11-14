#!/usr/bin/env python3
"""Check the 0.3 interval schema and independent synthetic references.

Resolve every schema locally. With --cli, check the actual Rust evaluator;
this script is a verification oracle, never an alternative valuation engine.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from validate_contract import (
    CONTEXT_IDS,
    ContractFailure,
    canonical_rationals,
    cli_call,
    compare_fields,
    digest,
    fraction,
    keyed,
    normalize_request,
    read_json,
    require,
    strict_loads,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "intervals"


def validators() -> dict[str, Draft202012Validator]:
    """Use an explicitly populated registry with no network retriever."""
    registry = Registry()
    documents = {}
    for version in ("0.1", "0.2", "0.3"):
        for path in sorted((ROOT / "schemas" / version).glob("*.schema.json")):
            document = read_json(path)
            Draft202012Validator.check_schema(document)
            registry = registry.with_resource(document["$id"], Resource.from_contents(document))
            documents[f"{version}/{path.name}"] = document
    return {
        name: Draft202012Validator(
            documents[key], registry=registry, format_checker=FormatChecker()
        )
        for name, key in (
            ("request", "0.3/request.schema.json"),
            ("report", "0.3/report.schema.json"),
            ("error", "0.1/error.schema.json"),
        )
    }


def normalized_interval_request(request: dict) -> dict:
    """Normalize transport identity only; retain supplied exact-number spelling."""
    result = normalize_request(request)
    intervals = result.get("interval_usage", [])
    if not intervals:
        result.pop("interval_usage", None)
    for usage in intervals:
        usage["source"].setdefault("content_digest", None)
        usage["source"].setdefault("locator", None)
        for key in CONTEXT_IDS:
            usage.setdefault(key, None)
        usage.setdefault("object_ids", [])
        usage["object_ids"].sort()
        usage["quote_ids"].sort()
    intervals.sort(key=lambda usage: usage["id"])
    capacities = result.get("capacity_allocations", [])
    if not capacities:
        result.pop("capacity_allocations", None)
    for capacity in capacities:
        capacity["source"].setdefault("content_digest", None)
        capacity["source"].setdefault("locator", None)
        capacity["source_line_ids"].sort()
        capacity["use_records"].sort(key=lambda record: record["object_id"])
    capacities.sort(key=lambda capacity: capacity["id"])
    return result


def successful_report(cli: Path, request: dict, checkers: dict, label: str) -> tuple[dict, str]:
    result = cli_call(cli, request)
    require(result.returncode == 0, f"{label}: CLI rejected request: {result.stderr}")
    require(result.stderr == "", f"{label}: successful CLI wrote stderr")
    report = strict_loads(result.stdout)
    validate(checkers["report"], report, label)
    return report, result.stdout


def check_report(report: dict, request: dict, expected: dict, label: str) -> None:
    normalized = normalized_interval_request(request)
    require(report["status"] == "complete", f"{label}: unexpected completion status")
    require(report["run_id"] == request["run_id"], f"{label}: changed run identity")
    require(report["policy"] == request["policy"], f"{label}: changed valuation policy")
    require(report["lines"] == [], f"{label}: manufactured point-date usage")
    require(report["quote_snapshots"] == normalized["quotes"], f"{label}: changed quotes")
    compare_fields(report["totals"], expected["totals"], label + ".totals")
    expected_context = {
        key: normalized[key]
        for key in ("objects", "processes", "events", "object_relations")
    }
    require(report["context"] == expected_context, f"{label}: changed context")
    actual_lines = keyed(report["interval_lines"], "id", label)
    require(set(actual_lines) == set(expected["interval_lines"]), f"{label}: changed line IDs")
    events = keyed(normalized["events"], "id", label)
    for usage in normalized["interval_usage"]:
        line = actual_lines[usage["id"]]
        compare_fields(line, expected["interval_lines"][usage["id"]], label)
        lineage = {key: value for key, value in usage.items() if key not in ("quantity", "quote_ids")}
        event = events.get(usage["event_id"], {})
        for key in ("process_id", "activity_id"):
            if lineage[key] is None:
                lineage[key] = event.get(key)
        compare_fields(line, lineage, label + ".lineage")
        require(fraction(line["quantity"]) == fraction(usage["quantity"]), f"{label}: quantity")
        require(
            sum(fraction(segment["quantity"]) for segment in line["segments"])
            == fraction(line["quantity"]),
            f"{label}: segment quantities do not conserve original quantity",
        )
        require(
            sum(fraction(segment["exact"]) for segment in line["segments"])
            == fraction(line["exact"]),
            f"{label}: segment exact amounts do not reconcile",
        )
    if "allocation_shares" in expected:
        require(len(report["allocations"]) == 1, f"{label}: allocation count")
        pool = report["allocations"][0]
        require(
            {share["object_id"]: share["rounded"] for share in pool["shares"]}
            == expected["allocation_shares"],
            f"{label}: allocation differs from independent one-cent oracle",
        )
        require(
            sum(fraction(share["rounded"]) for share in pool["shares"])
            + fraction(pool["residual"])
            == fraction(pool["pool_rounded"]),
            f"{label}: allocation did not conserve the parent pool",
        )
    require(
        report["input_digest"] == digest("dapane:input:0.3\n", normalized),
        f"{label}: input digest differs from independent wire normalization",
    )
    undigested = {key: value for key, value in report.items() if key != "output_digest"}
    require(
        report["output_digest"] == digest("dapane:output:0.3\n", undigested),
        f"{label}: output digest differs from independent canonicalization",
    )
    canonical_rationals(report)


def structural_negatives(checker: Draft202012Validator, request: dict) -> int:
    cases = []
    for field, value in (
        ("exposure", "business_days"),
        ("quantity", 10),
        ("quote_ids", []),
        ("quote_ids", ["rate-first", "rate-first"]),
        ("start_date", "2026-02-30"),
        ("unexpected", True),
    ):
        case = deepcopy(request)
        case["interval_usage"][0][field] = value
        cases.append(case)
    case = deepcopy(request)
    del case["interval_usage"][0]["exposure"]
    cases.append(case)
    for index, case in enumerate(cases):
        require(not checker.is_valid(case), f"Schema accepted negative interval case {index}")
    return len(cases)


def semantic_negatives(cli: Path, checkers: dict, request: dict) -> int:
    changes = (
        ("valid_to", "2026-01-04", 0, "interval_gap"),
        ("valid_to", "2026-01-06", 0, "interval_overlap"),
        ("unit", "minute", 1, "quote_mismatch"),
        ("known_from", "2027-01-01", 1, "quote_not_known"),
        ("components", ["salary", "overhead"], 1, "inconsistent_components"),
    )
    for field, value, index, code in changes:
        case = deepcopy(request)
        case["quotes"][index][field] = value
        result = cli_call(cli, case)
        require(result.returncode != 0, f"CLI accepted semantic negative {code}")
        require(result.stdout == "", f"{code}: error exposed a partial financial report")
        diagnostic = strict_loads(result.stderr)
        validate(checkers["error"], diagnostic, code)
        require(diagnostic["code"] == code, f"Expected {code}, received {diagnostic}")
    return len(changes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, help="Qualified native dapane executable")
    args = parser.parse_args()
    checkers = validators()
    reference = read_json(FIXTURES / "expected.json")
    require(reference["schema_version"] == "0.3", "Incorrect reference schema identity")
    require(reference["evidence"] == "synthetic", "References must be labelled synthetic")
    requests = {name: read_json(FIXTURES / name) for name in reference["cases"]}
    for name, request in requests.items():
        validate(checkers["request"], request, name)
    count = structural_negatives(checkers["request"], requests["rate-boundary.json"])
    print(f"Validated 0.3 schemas, {len(requests)} synthetic requests and {count} schema negatives.")
    if args.cli is None:
        print("Native numerical, semantic and determinism checks were not run; supply --cli.")
        return 0
    cli = args.cli.resolve()
    for name, request in requests.items():
        report, raw = successful_report(cli, request, checkers, name)
        check_report(report, request, reference["cases"][name], name)
        _, replay = successful_report(cli, request, checkers, name + " replay")
        require(raw == replay, f"{name}: repeated CLI output changed")
        permuted = deepcopy(request)
        permuted["quotes"].reverse()
        permuted["interval_usage"].reverse()
        for usage in permuted["interval_usage"]:
            usage["quote_ids"].reverse()
        _, reordered = successful_report(cli, permuted, checkers, name + " reordered")
        require(raw == reordered, f"{name}: quote/schedule ordering changed canonical output")
    unchanged = deepcopy(requests["rounding.json"])
    unchanged["quotes"][0]["valid_to"] = unchanged["quotes"][1]["valid_to"]
    unchanged["quotes"] = unchanged["quotes"][:1]
    unchanged["interval_usage"][0]["quote_ids"] = [unchanged["quotes"][0]["id"]]
    single, _ = successful_report(cli, unchanged, checkers, "uninterrupted equal rate")
    split, _ = successful_report(cli, requests["rounding.json"], checkers, "split equal rate")
    for key in ("totals", "allocations", "object_totals"):
        require(single[key] == split[key], f"Equal-rate segmentation changed {key}")
    negative_count = semantic_negatives(cli, checkers, requests["rate-boundary.json"])
    print(
        f"Verified {len(requests)} independent Rust/CLI results, canonical digests, replay/order "
        f"invariance, parent rounding/pool conservation and {negative_count} semantic rejections."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractFailure, OSError, json.JSONDecodeError) as error:
        print(f"Interval contract verification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
