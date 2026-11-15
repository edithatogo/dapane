"""Independent small-case references; never a production evaluator.

Python Fraction/round are separate from Rust's numeric implementation. Literal
expectations were authored before comparison. Only the declared point/interval
subset is covered; this is not an economic or source-truth validator.
"""

import re
from copy import deepcopy
from datetime import date
from fractions import Fraction

from .common import canonical, digest, require


def number(value: object) -> Fraction:
    if isinstance(value, str):
        require(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value) is not None, "Invalid exact string")
        return Fraction(value)
    require(isinstance(value, dict), "Reference accepts exact strings or rational pairs only")
    require(set(value) == {"numerator", "denominator"}, "Invalid rational pair")
    for part in value.values():
        require(
            isinstance(part, str) and re.fullmatch(r"[0-9]+", part),
            "Unsigned integers only",
        )
    require(int(value["denominator"]) > 0, "Zero denominator")
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def wire(value: Fraction) -> dict:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def money(units: int, scale: int) -> str:
    require(units >= 0, "Negative financial view outside this reference scope")
    if scale == 0:
        return str(units)
    factor = 10**scale
    return f"{units // factor}.{units % factor:0{scale}d}"


def keyed(records: list[dict], key: str) -> dict:
    result = {record[key]: record for record in records}
    require(len(result) == len(records), f"Repeated identity in {key}")
    return result


def point_reference(request: dict) -> dict:
    """Financial projection from small, valid point inputs, without calling Rust."""
    require(request["schema_version"] == "0.1", "Only point 0.1 oracle is qualified")
    for field in ("capacity_allocations", "processes", "events", "object_relations"):
        require(not request.get(field), f"Unqualified oracle scope: {field}")
    require(request["policy"]["rounding"]["mode"] == "half_even", "Only half_even is qualified")
    scale = request["policy"]["rounding"]["scale"]
    require(type(scale) is int and 0 <= scale <= 12, "Invalid rounding scale")
    factor = 10**scale
    quotes = keyed(request["quotes"], "id")
    uses = keyed(request["usage"], "id")
    exacts, units, lines = {}, {}, {}
    objects = {obj["id"]: {"direct": 0, "allocated": 0} for obj in request.get("objects", [])}
    for name, row in uses.items():
        quotation = quotes[row["quote_id"]]
        quantity = number(row["quantity"])
        denominator = number(quotation["per_quantity"])
        require(denominator > 0, "Zero quotation denominator")
        exact = quantity * number(quotation["amount"]) / denominator
        rounded = round(exact * factor)
        exacts[name], units[name] = exact, rounded
        lines[name] = {
            "quantity": wire(quantity),
            "exact": wire(exact),
            "rounded": money(rounded, scale),
            "rounding_adjustment": wire(Fraction(rounded, factor) - exact),
        }
        if row.get("attribution_object_id") is not None:
            objects[row["attribution_object_id"]]["direct"] += rounded

    allocations = {}
    for pool in request.get("allocations", []):
        pool_units = sum(units[line] for line in pool["source_line_ids"])
        weights = {row["object_id"]: number(row["weight"]) for row in pool["weights"]}
        total_weight = sum(weights.values(), Fraction())
        require(total_weight > 0, "Zero allocation weights")
        ideal = {name: pool_units * weight / total_weight for name, weight in weights.items()}
        portions = {name: share.numerator // share.denominator for name, share in ideal.items()}
        order = sorted(ideal, key=lambda name: (-(ideal[name] - portions[name]), name))
        for name in order[: pool_units - sum(portions.values())]:
            portions[name] += 1
        shares = {}
        for name, portion in portions.items():
            objects[name]["allocated"] += portion
            shares[name] = {
                "weight": wire(weights[name]),
                "exact_share": wire(ideal[name] / factor),
                "rounded": money(portion, scale),
            }
        allocations[pool["id"]] = {
            "source_line_ids": sorted(pool["source_line_ids"]),
            "pool_exact": wire(sum((exacts[line] for line in pool["source_line_ids"]), Fraction())),
            "pool_rounded": money(pool_units, scale),
            "shares": shares,
            "residual": money(0, scale),
        }
    exact = sum(exacts.values(), Fraction())
    rounded = sum(units.values())
    direct = sum(obj["direct"] for obj in objects.values())
    allocated = sum(obj["allocated"] for obj in objects.values())
    return {
        "lines": lines,
        "allocations": allocations,
        "objects": {
            name: {
                "direct": money(obj["direct"], scale),
                "allocated": money(obj["allocated"], scale),
                "total": money(obj["direct"] + obj["allocated"], scale),
            }
            for name, obj in objects.items()
        },
        "totals": {
            "exact": wire(exact),
            "rounded": money(rounded, scale),
            "rounding_adjustment": wire(Fraction(rounded, factor) - exact),
            "directly_attributed": money(direct, scale),
            "allocated": money(allocated, scale),
            "unattributed": money(rounded - direct - allocated, scale),
        },
    }


def _source(source: dict) -> dict:
    return {"content_digest": None, "locator": None, **source}


def _normalized_point(request: dict) -> dict:
    """Wire identity for the deliberately small subset, not financial logic."""
    result = deepcopy(request)
    for field in ("objects", "processes", "events", "object_relations", "allocations"):
        result.setdefault(field, [])
    for quote in result["quotes"]:
        quote["source"] = _source(quote["source"])
        quote["components"].sort()
    for row in result["usage"]:
        row["source"] = _source(row["source"])
        row.setdefault("object_ids", [])
        row["object_ids"].sort()
        for field in ("event_id", "process_id", "activity_id", "attribution_object_id"):
            row.setdefault(field, None)
    for field in ("quotes", "usage", "objects", "allocations"):
        result[field].sort(key=lambda row: row["id"])
    for pool in result["allocations"]:
        pool["source_line_ids"].sort()
        pool["weights"].sort(key=lambda row: row["object_id"])
    return result


def _output_digest(report: dict, domain: str) -> None:
    body = {key: value for key, value in report.items() if key != "output_digest"}
    require(report["output_digest"] == digest(domain.encode() + canonical(body)), "Output digest")


def _check_point(request: dict, report: dict) -> dict[str, bool]:
    expected = point_reference(request)
    normalized = _normalized_point(request)
    require(report["status"] == "complete", "Report completion")
    require(report["schema_version"] == "0.1", "Report schema")
    require(report["method_version"] == "dapane-exact-v0.1.0", "Method identity")
    require(
        isinstance(report["engine_version"], str) and report["engine_version"],
        "Engine identity",
    )
    require(report["run_id"] == request["run_id"], "Run identity")
    require(report["policy"] == request["policy"], "Policy identity")
    require(report["quote_snapshots"] == normalized["quotes"], "Quote/source snapshots")
    require(
        report["context"]
        == {key: normalized[key] for key in ("objects", "processes", "events", "object_relations")},
        "Context identity",
    )
    require(
        report["input_digest"] == digest(b"dapane:input:0.1\n" + canonical(normalized)),
        "Input digest",
    )
    _output_digest(report, "dapane:output:0.1\n")
    actual_lines = keyed(report["lines"], "id")
    require(set(actual_lines) == set(expected["lines"]), "Line inventory")
    for row in normalized["usage"]:
        actual = actual_lines[row["id"]]
        for key, value in row.items():
            if key != "quantity":
                require(actual[key] == value, f"Line source/context: {row['id']}.{key}")
        quote = next(q for q in normalized["quotes"] if q["id"] == row["quote_id"])
        require(actual["components"] == quote["components"], "Line components")
        for key, value in expected["lines"][row["id"]].items():
            require(actual[key] == value, f"Line oracle: {row['id']}.{key}")
    actual_pools = keyed(report["allocations"], "id")
    require(set(actual_pools) == set(expected["allocations"]), "Pool inventory")
    for name, expected_pool in expected["allocations"].items():
        actual = dict(actual_pools[name])
        del actual["id"]
        actual["shares"] = {
            obj: {k: v for k, v in share.items() if k != "object_id"}
            for obj, share in keyed(actual["shares"], "object_id").items()
        }
        require(actual == expected_pool, f"Pool oracle: {name}")
    actual_objects = {
        name: {k: v for k, v in obj.items() if k != "object_id"}
        for name, obj in keyed(report["object_totals"], "object_id").items()
    }
    require(actual_objects == expected["objects"], "Object oracle/conservation")
    require(report["totals"] == expected["totals"], "Total oracle/conservation")
    return dict.fromkeys(
        (
            "identity", "input_digest", "output_digest", "policy", "quotes_and_sources",
            "context", "line_inventory", "line_sources", "line_arithmetic",
            "allocations", "object_totals", "totals",
        ),
        True,
    )


def _check_interval(request: dict, report: dict) -> dict[str, bool]:
    require(request["schema_version"] == "0.1", "Only interval 0.1 oracle is qualified")
    template = request["request"]
    require(
        not template["usage"] and not template.get("allocations"),
        "Only standalone interval oracle",
    )
    require(len(request["intervals"]) == 1, "Only single-interval oracle is qualified")
    original = request["intervals"][0]
    require(original["exposure"] == "uniform_calendar_day", "Explicit uniform exposure")
    require(not original.get("attribution_object_id"), "Unqualified interval attribution")
    start, end = date.fromisoformat(original["start"]), date.fromisoformat(original["end"])
    total_days = (end - start).days
    require(total_days > 0, "Interval duration")
    quotes = keyed(template["quotes"], "id")
    expected_segments = []
    for quote_id in original["quote_ids"]:
        quote = quotes[quote_id]
        left = max(start, date.fromisoformat(quote["valid_from"]))
        right = min(end, date.fromisoformat(quote["valid_to"]))
        require(left < right, "Selected interval overlap")
        quantity = number(original["quantity"]) * Fraction((right - left).days, total_days)
        expected_segments.append((left.isoformat(), right.isoformat(), quote_id, wire(quantity)))
    expected_segments.sort()
    require(expected_segments[0][0] == original["start"], "Interval coverage start")
    require(expected_segments[-1][1] == original["end"], "Interval coverage end")
    for previous, following in zip(expected_segments, expected_segments[1:]):
        require(previous[1] == following[0], "Interval coverage continuity")

    segments = sorted(
        report["segments"], key=lambda row: (row["start"], row["end"], row["quote_id"])
    )
    observed = [
        (row["start"], row["end"], row["quote_id"], row["quantity"]) for row in segments
    ]
    require(observed == expected_segments, "Independent segmentation/quantity oracle")
    expanded = report["expanded_request"]
    require(len(expanded["usage"]) == len(segments), "Expanded line count")
    uses = keyed(expanded["usage"], "id")
    require(set(uses) == {row["line_id"] for row in segments}, "Segment line identities")
    for segment in segments:
        require(segment["interval_id"] == original["id"], "Original interval identity")
        require(segment["use_id"] == original["use_id"], "Original use identity")
        row = uses[segment["line_id"]]
        for field in ("kind", "target", "unit"):
            require(row[field] == original[field], f"Interval {field} lineage")
        require(row["source"] == _source(original["source"]), "Interval source lineage")
        require(row["quote_id"] == segment["quote_id"], "Segment quote identity")
        require(row["quantity"] == segment["quantity"], "Segment exact quantity")
        require(row["service_date"] == segment["start"], "Segment effective date")
    normalized = _normalized_point(template)
    require(report["request_snapshot"] == normalized, "Original request snapshot")
    expected_original = deepcopy(original)
    expected_original["source"] = _source(original["source"])
    expected_original["quote_ids"].sort()
    expected_original.setdefault("object_ids", [])
    for field in ("event_id", "process_id", "activity_id", "attribution_object_id"):
        expected_original.setdefault(field, None)
    require(report["interval_snapshots"] == [expected_original], "Original interval snapshot")
    normalized_envelope = {
        "schema_version": "0.1", "request": normalized, "intervals": [expected_original],
    }
    require(
        report["input_digest"]
        == digest(b"dapane:interval-input:0.1\n" + canonical(normalized_envelope)),
        "Interval input digest",
    )
    require(report["method_version"] == "dapane-intervals-v0.1.0", "Interval method identity")
    _output_digest(report, "dapane:interval-output:0.1\n")
    for key in ("quotes", "policy", "run_id", "knowledge_cutoff"):
        require(expanded[key] == normalized[key], f"Expanded {key} identity")
    coverage = _check_point(expanded, report["report"])
    coverage.update(dict.fromkeys(
        ("interval_source", "interval_snapshots", "interval_segments",
         "interval_input_digest", "interval_output_digest"), True,
    ))
    return coverage


def check(command: str, request: dict, report: dict) -> dict[str, bool]:
    """Raise on mismatch; otherwise enumerate the applicable checks performed."""
    if command == "evaluate":
        return _check_point(request, report)
    require(command == "evaluate-intervals", "Unsupported oracle command")
    return _check_interval(request, report)
