"""Synthetic mutation inventory and deterministic complete-request workloads."""

from copy import deepcopy
from pathlib import Path

from .cache import NativeCli, NativeRejection, WorkItem
from .common import Failure, canonical, decode, digest, load, require
from .oracle import check, number, wire

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
PROTOCOL = ROOT / "protocol.json"


def mutations(runner: NativeCli) -> dict:
    inventory = load(FIXTURES / "cases.json")
    protocol = load(PROTOCOL)
    require(inventory["protocol_id"] == protocol["protocol_id"], "Mutation protocol")
    require(len(inventory["cases"]) == 24, "Frozen mutation inventory is incomplete")
    cases = []
    for case in inventory["cases"]:
        work = WorkItem(case["command"], (FIXTURES / case["file"]).read_bytes())
        observation = {
            **case,
            "input_digest": digest(work.payload),
            "input_utf8": work.payload.decode("utf-8"),
            "passed": False,
            "outcome": None,
            "coverage": None,
        }
        expected = case["expected"]
        try:
            raw = runner.invoke(work)
            observation.update(
                outcome="accept", stdout_utf8=raw.decode(), output_digest=digest(raw)
            )
            require(expected["outcome"] == "accept", "Expected native rejection")
            request, report = decode(work.payload), decode(raw)
            observation["coverage"] = check(work.command, request, report)
            financial = report if work.command == "evaluate" else report["report"]
            require(financial["totals"]["rounded"] == expected["rounded"], "Literal rounded total")
            require(
                financial["totals"]["exact"] == wire(number(expected["exact"])),
                "Literal exact total",
            )
            if "object_totals" in expected:
                require(
                    {obj["object_id"]: obj["total"] for obj in financial["object_totals"]}
                    == expected["object_totals"],
                    "Literal object totals",
                )
            observation["passed"] = True
        except NativeRejection as error:
            observation.update(outcome="reject", diagnostic=error.diagnostic, stdout_utf8="")
            observation["passed"] = (
                expected["outcome"] == "reject" and expected["code"] == error.diagnostic["code"]
            )
            if not observation["passed"]:
                observation["failure"] = "Unexpected native rejection/code"
        except (Failure, KeyError, TypeError) as error:
            observation["failure"] = str(error)
        cases.append(observation)
    summary = {}
    for group in ("control", "contract", "source_truth"):
        selected = [case for case in cases if case["stratum"] == group]
        rejected = sum(case["outcome"] == "reject" for case in selected)
        summary[group] = {
            "count": len(selected),
            "rejected": rejected,
            "rejection_fraction": rejected / len(selected) if selected else None,
        }
    defects = [case for case in cases if case["defect"]]
    summary["all_defects"] = {
        "count": len(defects),
        "rejected": sum(case["outcome"] == "reject" for case in defects),
        "sensitivity": sum(case["outcome"] == "reject" for case in defects) / len(defects),
    }
    summary["interpretation"] = "Native rejection only; authored truth is not an engine capability"
    return {
        "protocol_id": protocol["protocol_id"],
        "passed": all(case["passed"] for case in cases),
        "cases": cases,
        "summary": summary,
    }


def portfolio(count: int) -> dict[str, WorkItem]:
    require(type(count) is int and count >= 2, "At least two requests cover both commands")
    result = {}
    for index in range(count):
        command = "evaluate" if index % 2 == 0 else "evaluate-intervals"
        request = load(FIXTURES / ("point.json" if index % 2 == 0 else "interval.json"))
        inner = request if command == "evaluate" else request["request"]
        inner["run_id"] = f"synthetic-static-{index:04d}"
        result[f"request-{index:04d}"] = WorkItem(command, canonical(request))
    return result


def scenario(base: dict[str, WorkItem], name: str) -> tuple[dict[str, WorkItem], int]:
    """Fresh target and preregistered number of native update calls."""
    result = dict(base)
    keys = sorted(base)
    require(len(keys) >= 2, "Two commands required")
    point_key, interval_key = keys[:2]
    if name in {"cold", "unchanged"}:
        return result, len(base) if name == "cold" else 0
    if name == "remove":
        del result[keys[-1]]
        return result, 0
    if name == "insert":
        request = decode(base[point_key].payload)
        request["run_id"] = "synthetic-static-inserted"
        require("request-inserted" not in result, "Insertion identity already present")
        result["request-inserted"] = WorkItem("evaluate", canonical(request))
        return result, 1
    changed_keys = (
        keys
        if name == "all_rates"
        else [interval_key if name == "one_interval_rate" else point_key]
    )
    for key in changed_keys:
        work = base[key]
        request = decode(work.payload)
        inner = request if work.command == "evaluate" else request["request"]
        if name in {"one_rate", "all_rates", "one_interval_rate"}:
            for quote in inner["quotes"]:
                if work.command == "evaluate-intervals":
                    quote["amount"] = "0.03"
                elif quote["id"] == "labour-rate":
                    quote["amount"] = "120"
        elif name == "one_policy":
            inner["policy"]["version"] = "2"
        elif name == "one_source":
            inner["quotes"][0]["source"]["version"] = "2"
        elif name == "one_allocation":
            inner["allocations"][0]["weights"][0]["weight"] = "2"
        elif name == "one_unused_quote":
            unused = deepcopy(inner["quotes"][0])
            unused["id"] = "unused-quote"
            unused["source"]["id"] = "synthetic-unused-quote"
            inner["quotes"].append(unused)
        elif name == "one_reorder":
            for field in ("usage", "quotes", "objects"):
                inner[field].reverse()
        else:
            raise Failure(f"Unregistered scenario: {name}")
        result[key] = WorkItem(work.command, canonical(request))
    return result, len(changed_keys)
