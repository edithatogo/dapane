#!/usr/bin/env python3
"""Bounded synthetic CLI measurements; not a cross-machine benchmark claim."""

import argparse
import copy
import itertools
import json
import platform
import resource
import statistics
import subprocess
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=Path)
    parser.add_argument("--counts", nargs="+", type=int, default=[10, 1000, 5000])
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=["valuation", "allocation"],
        default=["valuation", "allocation"],
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeats < 1 or any(count < 1 or count > 9998 for count in args.counts):
        parser.error("positive repeats and counts from 1 to 9998 are required")
    cli = args.cli.resolve(strict=True)
    root = Path(__file__).resolve().parents[1]
    base = json.loads((root / "fixtures/workforce.json").read_text())
    measurements = []
    engine_version = None
    for mode, count in itertools.product(args.modes, args.counts):
        request = copy.deepcopy(base)
        request["run_id"] = f"synthetic-benchmark-{mode}-{count}"
        request["usage"] = []
        for index in range(count):
            usage = copy.deepcopy(base["usage"][0])
            usage["id"] = f"line-{index:05d}"
            usage["use_id"] = f"use-{index:05d}"
            usage["source"]["id"] = f"synthetic-observation-{index:05d}"
            request["usage"].append(usage)
        if mode == "allocation":
            request["objects"] = [
                {"id": f"object-{index:05d}", "kind": "synthetic_recipient"}
                for index in range(count)
            ]
            request["allocations"] = [
                {
                    "id": "shared-pool",
                    "source_line_ids": [usage["id"] for usage in request["usage"]],
                    "weights": [
                        {"object_id": item["id"], "weight": "1"} for item in request["objects"]
                    ],
                }
            ]
        encoded = json.dumps(request, separators=(",", ":")).encode()
        times = []
        cpu_times = []
        digest = None
        output_bytes = None
        for _ in range(args.repeats):
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            start = time.perf_counter()
            result = subprocess.run(
                [str(cli), "evaluate", "-"],
                input=encoded,
                capture_output=True,
                check=True,
                timeout=60,
            )
            times.append(time.perf_counter() - start)
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu_times.append(after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime)
            report = json.loads(result.stdout)
            # Independent hand-derived reference: every row is (1/3)*90 = 30.
            assert report["totals"]["rounded"] == f"{count * 30}.00"
            assert report["totals"]["exact"] == {"numerator": str(count * 30), "denominator": "1"}
            assert len(report["lines"]) == count
            if mode == "allocation":
                assert len(report["object_totals"]) == count
                assert all(item["total"] == "30.00" for item in report["object_totals"])
                assert report["allocations"][0]["residual"] == "0.00"
                assert report["totals"]["unattributed"] == "0.00"
            if digest is not None:
                assert digest == report["output_digest"]
            digest = report["output_digest"]
            engine_version = report["engine_version"]
            output_bytes = len(result.stdout)
        measurements.append(
            {
                "mode": mode,
                "usage_rows": count,
                "quotes": 1,
                "input_bytes": len(encoded),
                "output_bytes": output_bytes,
                "repeats": args.repeats,
                "wall_seconds": times,
                "median_wall_seconds": statistics.median(times),
                "child_cpu_seconds": cpu_times,
                "output_digest": digest,
            }
        )
    summary = {
        "scope": "synthetic CLI valuation and shared-pool allocation, including process startup and JSON IO",
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "engine_version": engine_version,
        "measurements": measurements,
        "max_child_rss_kib_across_run": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "limits": "Linux ru_maxrss is peak child RSS across this run, not per-workload memory. No concurrency, provider or cross-machine comparison is implied.",
    }
    text = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
