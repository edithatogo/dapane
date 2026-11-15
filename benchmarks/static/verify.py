"""Check saved bytes, complete report equality and arithmetic without execution.

Internal consistency is not proof of authorship, external truth or timing accuracy.
"""

import argparse
import json
import statistics
from pathlib import Path

from .common import canonical, decode, digest, file_digest, load, require
from .oracle import check, number, wire


def verify(directory: Path) -> dict:
    checksums = load(directory / "checksums.json")
    require(set(checksums) == {"results.json", "inputs.json", "reports.json"}, "Bundle membership")
    for name, expected in checksums.items():
        require(file_digest(directory / name) == expected, f"Companion checksum: {name}")
    result = load(directory / "results.json")
    inputs = load(directory / "inputs.json")
    reports = load(directory / "reports.json")
    require(result["status"] == "passed", "Bundle is not a passing run")
    protocol = result["protocol"]
    for ref, record in inputs.items():
        require(
            ref == digest(canonical([record["command"], record["payload_utf8"]])),
            "Input reference",
        )
    for ref, raw in reports.items():
        require(ref == digest(raw.encode("utf-8")), "Report reference")
    expected_scenarios = {
        (count, name) for count in protocol["portfolio_sizes"] for name in protocol["scenarios"]
    }
    observed_scenarios = {
        (row["portfolio_size_before"], row["scenario"]) for row in result["comparisons"]
    }
    require(
        observed_scenarios == expected_scenarios
        and len(result["comparisons"]) == len(expected_scenarios),
        "Missing/duplicate scenarios",
    )
    checked, pairs = set(), 0
    for comparison in result["comparisons"]:
        require(comparison["passed"] and comparison["summary"] is not None, "Comparison gate")
        target, baseline = comparison["target_inputs"], comparison["baseline_inputs"]
        require(len(target) == comparison["portfolio_size_after"], "Target size")
        require(len(baseline) == comparison["portfolio_size_before"], "Baseline size")
        baseline_values = set() if comparison["scenario"] == "cold" else set(baseline.values())
        expected_calls = len(set(target.values()) - baseline_values)
        require(expected_calls == comparison["expected_incremental_calls"], "Invalidation rule")
        expected_indices = set(range(-protocol["warmup_pairs"], protocol["measured_pairs"]))
        require(
            {pair["index"] for pair in comparison["pairs"]} == expected_indices
            and len(comparison["pairs"]) == len(expected_indices),
            "Missing/duplicate pairs",
        )
        for pair in comparison["pairs"]:
            require(pair["passed"] and pair["complete_report_bytes_equal"], "Pair gate")
            require(pair["warmup"] == (pair["index"] < 0), "Warmup marker")
            require(pair["full"]["native_calls"] == len(target), "Full native count")
            require(
                pair["incremental"]["native_calls"] == expected_calls, "Incremental native count"
            )
            require(pair["incremental"]["hits"] == len(target) - expected_calls, "Cache hit count")
            left, right = pair["full"]["report_refs"], pair["incremental"]["report_refs"]
            require(set(left) == set(right) == set(target), "Portfolio inventory")
            for name in target:
                require(reports[left[name]] == reports[right[name]], "Complete reports differ")
                identity = target[name], left[name]
                if identity not in checked:
                    work = inputs[target[name]]
                    check(
                        work["command"],
                        decode(work["payload_utf8"].encode()),
                        decode(reports[left[name]].encode()),
                    )
                    checked.add(identity)
            for method in ("full", "incremental"):
                require(
                    type(pair[method]["wall_ns"]) is int and pair[method]["wall_ns"] > 0,
                    "Invalid elapsed time",
                )
            pairs += 1
        measured = [pair for pair in comparison["pairs"] if not pair["warmup"]]
        full_median = statistics.median(pair["full"]["wall_ns"] for pair in measured)
        inc_median = statistics.median(pair["incremental"]["wall_ns"] for pair in measured)
        summary = comparison["summary"]
        require(summary["measured_pairs"] == len(measured), "Summary pair count")
        require(summary["median_full_wall_ns"] == full_median, "Full median")
        require(summary["median_incremental_wall_ns"] == inc_median, "Incremental median")
        require(
            summary["median_full_over_incremental_ratio"] == full_median / inc_median,
            "Descriptive ratio",
        )
    require(result["mutations"]["passed"], "Mutation gate")
    require(len(result["mutations"]["cases"]) == 24, "Mutation inventory")
    for case in result["mutations"]["cases"]:
        require(case["passed"], "Mutation expectation")
        raw = case["input_utf8"].encode("utf-8")
        require(digest(raw) == case["input_digest"], "Mutation input digest")
        require(case["outcome"] == case["expected"]["outcome"], "Mutation outcome")
        if case["outcome"] == "accept":
            output = case["stdout_utf8"].encode("utf-8")
            require(digest(output) == case["output_digest"], "Mutation report digest")
            report = decode(output)
            check(case["command"], decode(raw), report)
            financial = report if case["command"] == "evaluate" else report["report"]
            require(financial["totals"]["rounded"] == case["expected"]["rounded"], "Literal total")
            require(
                financial["totals"]["exact"] == wire(number(case["expected"]["exact"])),
                "Literal exact total",
            )
            if "object_totals" in case["expected"]:
                require(
                    {obj["object_id"]: obj["total"] for obj in financial["object_totals"]}
                    == case["expected"]["object_totals"],
                    "Literal object totals",
                )
        else:
            require(case["outcome"] == "reject" and case["stdout_utf8"] == "", "Rejection output")
            require(case["diagnostic"]["code"] == case["expected"]["code"], "Error code")
    return {
        "verified_pairs_including_warmups": pairs,
        "distinct_request_report_checks": len(checked),
        "mutation_cases": len(result["mutations"]["cases"]),
        "scope": "Offline consistency and independent arithmetic; no execution/timing attestation",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
