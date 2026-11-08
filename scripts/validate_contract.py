#!/usr/bin/env python3
"""Validate Dapane's schemas and independent synthetic contract fixtures.

Requires jsonschema==4.26.0. All schema references are resolved from this
repository, without network access. With --cli, also exercise the Rust public
CLI and check independent expected values, provenance, conservation and digests.
JSON Schema deliberately does not replace the kernel's semantic validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
SCHEMAS = ROOT / "schemas" / "0.1"
COLLECTIONS = ("quotes", "usage", "objects", "processes", "events", "allocations")
OPTIONAL_ARRAYS = ("objects", "processes", "events", "object_relations", "allocations")
CONTEXT_IDS = ("event_id", "process_id", "activity_id", "attribution_object_id")
MAX_INPUT_BYTES = 4 * 1024 * 1024


class ContractFailure(ValueError):
    """A schema, fixture or externally observable contract failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractFailure(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractFailure(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractFailure(f"Non-finite JSON literal: {value}")


def strict_loads(text: str) -> object:
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)


def read_json(path: Path) -> object:
    raw = path.read_bytes()
    require(len(raw) <= MAX_INPUT_BYTES, f"Fixture exceeds 4 MiB: {path}")
    return strict_loads(raw.decode("utf-8"))


def validators() -> dict[str, Draft202012Validator]:
    documents = {}
    registry = Registry()
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        document = read_json(path)
        Draft202012Validator.check_schema(document)
        documents[path.name.removesuffix(".schema.json")] = document
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
    require(
        set(documents) == {"common", "request", "report", "error"},
        "Expected common, request, report and error schemas",
    )
    return {
        name: Draft202012Validator(document, registry=registry, format_checker=FormatChecker())
        for name, document in documents.items()
    }


def validate(validator: Draft202012Validator, value: object, label: str) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda error: str(error.path))
    if errors:
        error = errors[0]
        path = "/" + "/".join(map(str, error.absolute_path))
        raise ContractFailure(f"{label}: schema failure at {path}: {error.message}")


def normalize_request(request: dict) -> dict:
    """Independent wire normalization from docs/contract-v0.1.md.

    This computes digest identity only; it does not calculate financial values.
    Decimal strings and rational input spellings remain unchanged.
    """
    result = deepcopy(request)
    for key in OPTIONAL_ARRAYS:
        result.setdefault(key, [])
    for quote in result["quotes"]:
        quote["components"].sort()
    for record in [*result["quotes"], *result["usage"]]:
        record["source"].setdefault("content_digest", None)
        record["source"].setdefault("locator", None)
    for usage in result["usage"]:
        for key in CONTEXT_IDS:
            usage.setdefault(key, None)
        usage.setdefault("object_ids", [])
        usage["object_ids"].sort()
    for event in result["events"]:
        event.setdefault("process_id", None)
        event.setdefault("activity_id", None)
        event.setdefault("object_ids", [])
        event["object_ids"].sort()
    for key in COLLECTIONS:
        result[key].sort(key=lambda record: record["id"])
    result["object_relations"].sort(
        key=lambda relation: (
            relation["from_object_id"],
            relation["to_object_id"],
            relation["relationship"],
        )
    )
    for allocation in result["allocations"]:
        allocation["source_line_ids"].sort()
        allocation["weights"].sort(key=lambda weight: weight["object_id"])
    return result


def canonical(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def digest(domain: str, value: object) -> str:
    return "sha256:" + hashlib.sha256((domain + canonical(value)).encode("utf-8")).hexdigest()


def fraction(value: dict | str) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def canonical_rationals(value: object) -> None:
    if isinstance(value, dict):
        if set(value) == {"numerator", "denominator"}:
            exact = fraction(value)
            require(
                value
                == {
                    "numerator": str(exact.numerator),
                    "denominator": str(exact.denominator),
                },
                f"Output rational is not reduced/canonical: {value}",
            )
        else:
            for item in value.values():
                canonical_rationals(item)
    elif isinstance(value, list):
        for item in value:
            canonical_rationals(item)


def compare_fields(actual: dict, expected: dict, label: str) -> None:
    for key, value in expected.items():
        require(actual.get(key) == value, f"{label}.{key}: {actual.get(key)!r} != {value!r}")


def keyed(records: list[dict], key: str, label: str) -> dict:
    result = {record[key]: record for record in records}
    require(len(result) == len(records), f"Duplicate {key} in {label}")
    return result


def check_report(report: dict, request: dict, expected: dict, label: str) -> None:
    normalized = normalize_request(request)
    require(report["run_id"] == request["run_id"], f"{label}: run identity changed")
    require(report["policy"] == request["policy"], f"{label}: policy changed")
    require(
        report["quote_snapshots"] == normalized["quotes"],
        f"{label}: supplied quote snapshot/provenance changed",
    )
    context = {key: normalized[key] for key in OPTIONAL_ARRAYS if key != "allocations"}
    require(report["context"] == context, f"{label}: event/process/object context changed")
    compare_fields(report["totals"], expected["totals"], f"{label}.totals")

    lines = keyed(report["lines"], "id", label + ".lines")
    require(set(lines) == set(expected["lines"]), f"{label}: unexpected source lines")
    uses = keyed(normalized["usage"], "id", label + ".usage")
    quotes = keyed(normalized["quotes"], "id", label + ".quotes")
    events = keyed(normalized["events"], "id", label + ".events")
    for line_id, expected_line in expected["lines"].items():
        actual = lines[line_id]
        compare_fields(actual, expected_line, f"{label}.lines[{line_id}]")
        supplied = {key: value for key, value in uses[line_id].items() if key != "quantity"}
        event = events.get(supplied["event_id"], {})
        for context_id in ("process_id", "activity_id"):
            if supplied[context_id] is None:
                supplied[context_id] = event.get(context_id)
        compare_fields(actual, supplied, f"{label}.lineage[{line_id}]")
        require(
            fraction(actual["quantity"]) == fraction(uses[line_id]["quantity"]),
            f"{label}: quantity changed for {line_id}",
        )
        require(
            actual["components"] == quotes[actual["quote_id"]]["components"],
            f"{label}: components changed for {line_id}",
        )

    objects = keyed(report["object_totals"], "object_id", label + ".objects")
    require(set(objects) == set(expected["object_totals"]), f"{label}: object set changed")
    for object_id, expected_total in expected["object_totals"].items():
        compare_fields(objects[object_id], expected_total, f"{label}.objects[{object_id}]")

    allocations = keyed(report["allocations"], "id", label + ".allocations")
    supplied_allocations = keyed(normalized["allocations"], "id", label + ".input-pools")
    require(set(allocations) == set(expected["allocations"]), f"{label}: pool set changed")
    for pool_id, expected_pool in expected["allocations"].items():
        pool = allocations[pool_id]
        compare_fields(
            pool,
            {key: value for key, value in expected_pool.items() if key != "shares"},
            f"{label}.pools[{pool_id}]",
        )
        require(
            pool["source_line_ids"] == supplied_allocations[pool_id]["source_line_ids"],
            f"{label}: pool source lineage changed",
        )
        shares = keyed(pool["shares"], "object_id", label + ".shares")
        require(set(shares) == set(expected_pool["shares"]), f"{label}: recipient set changed")
        for object_id, expected_share in expected_pool["shares"].items():
            compare_fields(shares[object_id], expected_share, f"{label}.shares[{object_id}]")
        require(
            sum((Fraction(share["rounded"]) for share in pool["shares"]), Fraction())
            + Fraction(pool["residual"])
            == Fraction(pool["pool_rounded"]),
            f"{label}: allocation does not conserve its rounded pool",
        )

    rounded = Fraction(report["totals"]["rounded"])
    require(
        sum((Fraction(line["rounded"]) for line in report["lines"]), Fraction()) == rounded,
        f"{label}: source ledger does not conserve the reported total",
    )
    require(
        sum((Fraction(obj["total"]) for obj in report["object_totals"]), Fraction())
        + Fraction(report["totals"]["unattributed"])
        == rounded,
        f"{label}: object view does not conserve the source ledger",
    )
    require(
        sum(
            (
                Fraction(report["totals"][key])
                for key in ("directly_attributed", "allocated", "unattributed")
            ),
            Fraction(),
        )
        == rounded,
        f"{label}: direct, pooled and unattributed balances do not conserve",
    )
    # Quote snapshots retain input spellings; only calculated output rationals
    # are required to be reduced. Remove them before this canonicality check.
    calculated = {key: value for key, value in report.items() if key != "quote_snapshots"}
    canonical_rationals(calculated)
    require(
        report["input_digest"] == digest("dapane:input:0.1\n", normalized),
        f"{label}: input digest differs from independent canonical normalization",
    )
    without_digest = {key: value for key, value in report.items() if key != "output_digest"}
    require(
        report["output_digest"] == digest("dapane:output:0.1\n", without_digest),
        f"{label}: output digest does not cover the report",
    )


def set_path(document: dict, path: tuple, value: object) -> dict:
    result = deepcopy(document)
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return result


def structural_cases(workforce: dict) -> list[tuple[str, dict]]:
    cases = []
    values = [
        ("numeric quantity", ("usage", 0, "quantity"), 0.5),
        ("negative quantity", ("usage", 0, "quantity"), "-1"),
        ("exponent quantity", ("usage", 0, "quantity"), "1e2"),
        ("spaced quantity", ("usage", 0, "quantity"), "1 "),
        ("zero denominator", ("usage", 0, "quantity"), {"numerator": "1", "denominator": "0"}),
        (
            "rational unknown field",
            ("usage", 0, "quantity"),
            {"numerator": "1", "denominator": "3", "unit": "hour"},
        ),
        ("numeric precision limit", ("usage", 0, "quantity"), "1" * 97),
        ("decimal scale limit", ("usage", 0, "quantity"), "0." + "1" * 37),
        ("zero price denominator", ("quotes", 0, "per_quantity"), "0.00"),
        ("invalid Gregorian date", ("usage", 0, "service_date"), "2026-02-30"),
        ("year zero", ("knowledge_cutoff",), "0000-01-01"),
        ("lowercase currency", ("policy", "currency"), "aud"),
        ("invalid price year", ("policy", "price_year"), 0),
        ("unsupported rounding", ("policy", "rounding", "mode"), "half_up"),
        ("rounding scale limit", ("policy", "rounding", "scale"), 13),
        ("empty identifier", ("run_id",), ""),
        ("spaced identifier", ("run_id",), " run"),
        ("control identifier", ("run_id",), "run\nname"),
        ("unknown evidence", ("usage", 0, "source", "evidence"), "certified"),
        ("invalid source digest", ("quotes", 0, "source", "content_digest"), "sha256:not-a-hash"),
        ("empty components", ("quotes", 0, "components"), []),
        ("duplicate components", ("quotes", 0, "components"), ["salary", "salary"]),
        ("unknown root field", ("execute_bpmn",), True),
        ("unknown nested field", ("usage", 0, "source", "certified"), True),
        ("record limit", ("objects",), [{"id": "a", "kind": "object"}] * 10001),
    ]
    for label, path, value in values:
        cases.append((label, set_path(workforce, path, value)))
    missing = deepcopy(workforce)
    del missing["usage"][0]["source"]["evidence"]
    cases.append(("missing provenance", missing))
    return cases


def report_shape_example(workforce: dict, expected: dict) -> dict:
    """An authored schema example, not a captured or qualified engine output."""
    normalized = normalize_request(workforce)
    line = deepcopy(normalized["usage"][0])
    line.update(expected["lines"][line["id"]])
    line["components"] = ["salary"]
    return {
        "schema_version": "0.1",
        "run_id": workforce["run_id"],
        "status": "complete",
        "engine_version": "0.1.0",
        "method_version": "dapane-exact-v0.1.0",
        "input_digest": "sha256:" + "0" * 64,
        "output_digest": "sha256:" + "0" * 64,
        "policy": workforce["policy"],
        "lines": [line],
        "quote_snapshots": normalized["quotes"],
        "context": {key: [] for key in ("objects", "processes", "events", "object_relations")},
        "totals": expected["totals"],
        "allocations": [],
        "object_totals": [],
    }


def schema_negative_tests(checkers: dict, requests: dict, expected: dict) -> int:
    count = 0
    for label, case in structural_cases(requests["workforce.json"]):
        require(not checkers["request"].is_valid(case), f"Schema accepted {label}")
        count += 1
    for text in ('{"a":1,"a":2}', '{"nested":{"a":1,"a":2}}', '{"a":NaN}', '{"a":Infinity}'):
        try:
            strict_loads(text)
        except ContractFailure:
            count += 1
        else:
            raise ContractFailure("Strict JSON reader accepted a duplicate/non-finite value")

    report = report_shape_example(requests["workforce.json"], expected["workforce.json"])
    validate(checkers["report"], report, "authored report shape example")
    for label, path, value in [
        ("partial report", ("status",), "partial"),
        ("numeric monetary output", ("totals", "rounded"), 30),
        ("negative output denominator", ("totals", "exact", "denominator"), "-1"),
        ("unknown report field", ("debug",), True),
    ]:
        require(
            not checkers["report"].is_valid(set_path(report, path, value)),
            f"Report schema accepted {label}",
        )
        count += 1
    error = {
        "code": "invalid_request",
        "message": "Synthetic schema example",
        "path": "/usage/0/quantity",
    }
    validate(checkers["error"], error, "authored error shape example")
    for label, path, value in [
        ("numeric error code", ("code",), 1),
        ("partial error total", ("total",), "30.00"),
        ("non-pointer error path", ("path",), "usage"),
    ]:
        require(
            not checkers["error"].is_valid(set_path(error, path, value)),
            f"Error schema accepted {label}",
        )
        count += 1
    return count


def cli_call(cli: Path, request: dict | str) -> subprocess.CompletedProcess:
    text = request if isinstance(request, str) else canonical(request)
    return subprocess.run(
        [str(cli), "evaluate", "-"],
        input=text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        cwd=ROOT,
        check=False,
    )


def successful_report(cli: Path, request: dict, checkers: dict, label: str) -> dict:
    result = cli_call(cli, request)
    require(result.returncode == 0, f"{label}: CLI failed: {result.stderr[:1000]}")
    require(not result.stderr.strip(), f"{label}: successful CLI wrote stderr")
    report = strict_loads(result.stdout)
    validate(checkers["report"], report, label)
    return report


def semantic_cases(requests: dict) -> list[tuple[str, dict]]:
    workforce = requests["workforce.json"]
    newborn = requests["newborn-screening.json"]
    cases = [
        ("expired quote", set_path(workforce, ("usage", 0, "service_date"), "2027-01-01")),
        ("not-yet-known quote", set_path(workforce, ("quotes", 0, "known_from"), "2027-01-01")),
        ("unit mismatch", set_path(workforce, ("usage", 0, "unit"), "minute")),
        ("target mismatch", set_path(workforce, ("usage", 0, "target"), "equipment")),
        (
            "activity/resource mismatch",
            set_path(workforce, ("usage", 0, "kind"), "activity_measure"),
        ),
        ("valuation basis mismatch", set_path(workforce, ("quotes", 0, "basis"), "funding")),
        (
            "unknown object reference",
            set_path(newborn, ("usage", 0, "object_ids"), ["unknown-object"]),
        ),
        (
            "event/process disagreement",
            set_path(newborn, ("usage", 0, "activity_id"), "other-activity"),
        ),
        ("UTF-8 byte limit", set_path(workforce, ("run_id",), "é" * 65)),
    ]
    overlap = deepcopy(workforce)
    duplicate = deepcopy(overlap["usage"][0])
    duplicate["id"] = "second-line-same-use"
    overlap["usage"].append(duplicate)
    cases.append(("overlapping use components", overlap))
    twice = deepcopy(newborn)
    second = deepcopy(twice["allocations"][0])
    second["id"] = "second-pool-same-source"
    twice["allocations"].append(second)
    cases.append(("double allocation", twice))
    both = deepcopy(newborn)
    both["allocations"][0]["source_line_ids"].append("collection-a")
    cases.append(("direct and pooled attribution", both))
    zero_weights = deepcopy(newborn)
    for recipient in zero_weights["allocations"][0]["weights"]:
        recipient["weight"] = "0"
    cases.append(("all-zero recipient weights", zero_weights))
    return cases


def cli_negative_tests(cli: Path, requests: dict, checkers: dict) -> int:
    cases = semantic_cases(requests)
    for label, request in cases:
        # These cases intentionally pass JSON Schema. Their rejection therefore
        # demonstrates semantic runtime validation, not structural validation.
        validate(checkers["request"], request, label + " structural precondition")
        result = cli_call(cli, request)
        require(result.returncode != 0, f"Rust accepted semantic failure: {label}")
        require(not result.stdout.strip(), f"{label}: invalid request produced a partial report")
        validate(checkers["error"], strict_loads(result.stderr), label + " error")
    raw = canonical(requests["workforce.json"])
    duplicate_key = raw[:-1] + ',"schema_version":"0.1"}'
    result = cli_call(cli, duplicate_key)
    require(
        result.returncode != 0 and not result.stdout.strip(), "Rust accepted duplicate JSON keys"
    )
    validate(checkers["error"], strict_loads(result.stderr), "duplicate JSON key error")
    return len(cases) + 1


def determinism_tests(
    cli: Path, requests: dict, reports: dict, checkers: dict, expected: dict
) -> None:
    reordered = deepcopy(requests["newborn-screening.json"])
    for key in (*COLLECTIONS, "object_relations"):
        reordered.get(key, []).reverse()
    for usage in reordered["usage"]:
        usage.get("object_ids", []).reverse()
    for event in reordered.get("events", []):
        event.get("object_ids", []).reverse()
    for allocation in reordered.get("allocations", []):
        allocation["source_line_ids"].reverse()
        allocation["weights"].reverse()
    rerun = successful_report(cli, reordered, checkers, "reordered newborn request")
    require(
        rerun == reports["newborn-screening.json"], "Collection reordering changed report identity"
    )

    respelled = deepcopy(requests["workforce.json"])
    respelled["quotes"][0]["amount"] = "90.0"
    changed = successful_report(cli, respelled, checkers, "respelled quote")
    original = reports["workforce.json"]
    require(
        changed["totals"] == original["totals"],
        "Equivalent decimal spelling changed financial values",
    )
    require(
        changed["input_digest"] != original["input_digest"],
        "Input digest lost supplied decimal spelling",
    )
    require(
        changed["output_digest"] != original["output_digest"],
        "Output digest lost quotation/input provenance",
    )

    inherited = deepcopy(requests["newborn-screening.json"])
    for usage in inherited["usage"]:
        usage.pop("process_id", None)
        usage.pop("activity_id", None)
    inherited_report = successful_report(cli, inherited, checkers, "inherited event context")
    check_report(
        inherited_report,
        inherited,
        expected["newborn-screening.json"],
        "inherited event context",
    )
    require(
        inherited_report["lines"] == reports["newborn-screening.json"]["lines"],
        "Omitted line process/activity did not inherit the declared event context",
    )
    require(
        inherited_report["input_digest"] != reports["newborn-screening.json"]["input_digest"],
        "Input digest lost the distinction between explicit and inherited context",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cli", type=Path, help="Also validate a built dapane CLI, e.g. target/release/dapane"
    )
    args = parser.parse_args()
    checkers = validators()
    reference = read_json(FIXTURES / "expected.json")
    expected = reference["fixtures"]
    requests = {}
    require(reference["schema_version"] == "0.1", "Expected fixtures have wrong schema version")
    names = {path.name for path in FIXTURES.glob("*.json") if path.name != "expected.json"}
    require(names == set(expected), "Request fixture files differ from independent expected cases")
    for name in sorted(expected):
        request = read_json(FIXTURES / name)
        validate(checkers["request"], request, name)
        for record in [*request["quotes"], *request["usage"]]:
            compare_fields(
                record["source"],
                {"evidence": "synthetic", "access": "public", "validation": "unvalidated"},
                name + ".source",
            )
        requests[name] = request
    structural_count = schema_negative_tests(checkers, requests, expected)
    print(
        f"Validated four JSON Schema 2020-12 documents, {len(requests)} synthetic request fixtures and {structural_count} negative schema/parser cases."
    )
    if args.cli is not None:
        cli = args.cli.resolve()
        require(cli.is_file(), f"CLI does not exist: {cli}")
        reports = {}
        for name, request in requests.items():
            report = successful_report(cli, request, checkers, name)
            require(
                report["method_version"] == reference["method_version"],
                "Reference method version changed",
            )
            check_report(report, request, expected[name], name)
            reports[name] = report
        semantic_count = cli_negative_tests(cli, requests, checkers)
        determinism_tests(cli, requests, reports, checkers, expected)
        print(
            f"Validated {len(reports)} CLI reports against independent exact values, allocations, provenance, conservation and digests; {semantic_count} runtime rejection cases and three identity/context cases passed."
        )
    else:
        print(
            "Runtime semantic validation, executable results and digests were not evaluated; use --cli with a built Rust CLI."
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        ContractFailure,
        json.JSONDecodeError,
        UnicodeDecodeError,
        OSError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"Contract validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
