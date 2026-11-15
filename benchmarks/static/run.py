"""Run the synthetic protocol and save complete, source-bound observations.

Existing output directories are never replaced. Failed checks are retained in a
failed bundle and cannot yield a timing summary. This module is unexecuted at the
initial draft handoff; consult the track record before claiming qualification.
"""

import argparse
import fractions
import json
import os
import platform
import statistics
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .build import REPO, git, runtime_identity
from .cache import Incremental, NativeCli, Result, WorkItem, full
from .common import Failure, canonical, decode, digest, file_digest, load, require
from .oracle import check
from .suite import PROTOCOL, mutations, portfolio, scenario


class Archive:
    """Content-addressed input/output bytes, without lossy JSON normalisation."""

    def __init__(self):
        self.inputs = {}
        self.reports = {}

    def inputs_for(self, items: dict[str, WorkItem]) -> dict:
        refs = {}
        for key, item in items.items():
            ref = digest(canonical([item.command, item.payload.decode("utf-8")]))
            value = {"command": item.command, "payload_utf8": item.payload.decode("utf-8")}
            require(ref not in self.inputs or self.inputs[ref] == value, "Input archive collision")
            self.inputs[ref] = value
            refs[key] = ref
        return refs

    def reports_for(self, result: Result) -> dict:
        refs = {}
        for key, raw in result.reports.items():
            ref = digest(raw)
            value = raw.decode("utf-8")
            require(
                ref not in self.reports or self.reports[ref] == value, "Report archive collision"
            )
            self.reports[ref] = value
            refs[key] = ref
        return refs


def _encoded(objects: dict) -> dict[str, WorkItem]:
    return {key: WorkItem(command, canonical(value)) for key, (command, value) in objects.items()}


def _measure(operation, objects: dict) -> tuple[Result, int]:
    started = time.perf_counter_ns()
    result = operation(_encoded(objects))
    return result, time.perf_counter_ns() - started


def _metrics(result: Result, elapsed_ns: int) -> dict:
    return {key: value for key, value in asdict(result).items() if key != "reports"} | {
        "wall_ns": elapsed_ns
    }


def comparison(runner: NativeCli, count: int, name: str, protocol: dict, archive: Archive) -> dict:
    baseline = portfolio(count)
    target, expected_calls = scenario(baseline, name)
    base_objects = {key: (work.command, decode(work.payload)) for key, work in baseline.items()}
    target_objects = {key: (work.command, decode(work.payload)) for key, work in target.items()}
    observation = {
        "portfolio_size_before": count,
        "portfolio_size_after": len(target),
        "scenario": name,
        "baseline_inputs": archive.inputs_for(baseline),
        "target_inputs": archive.inputs_for(target),
        "expected_incremental_calls": expected_calls,
        "pairs": [],
        "passed": False,
        "summary": None,
    }
    for index in range(-protocol["warmup_pairs"], protocol["measured_pairs"]):
        cache = Incremental(runner)
        pair = {"index": index, "warmup": index < 0, "passed": False, "seed": None}
        observation["pairs"].append(pair)
        try:
            if name != "cold":
                seeded, seed_ns = _measure(cache.evaluate, base_objects)
                pair["seed"] = _metrics(seeded, seed_ns)
                pair["seed_report_refs"] = archive.reports_for(seeded)
            order = ["full", "incremental"] if index % 2 == 0 else ["incremental", "full"]
            pair["order"] = order
            evaluated = {}
            for method in order:
                operation = (
                    cache.evaluate if method == "incremental" else lambda items: full(runner, items)
                )
                result, elapsed = _measure(operation, target_objects)
                evaluated[method] = result
                pair[method] = _metrics(result, elapsed)
                pair[method]["report_refs"] = archive.reports_for(result)
            reference, update = evaluated["full"], evaluated["incremental"]
            require(reference.native_calls == len(target), "Full call-count mismatch")
            require(update.native_calls == expected_calls, "Incremental invalidation mismatch")
            require(reference.reports == update.reports, "Complete native reports differ")
            coverage = {}
            for key, raw in reference.reports.items():
                work = target[key]
                coverage[key] = check(work.command, decode(work.payload), decode(raw))
            pair["oracle_checks"] = sum(len(fields) for fields in coverage.values())
            pair["complete_report_bytes_equal"] = True
            pair["passed"] = True
        except (Failure, KeyError, TypeError, OSError) as error:
            pair["failure"] = str(error)
            return observation
    observation["passed"] = True
    measured = [pair for pair in observation["pairs"] if not pair["warmup"]]
    full_median = statistics.median(pair["full"]["wall_ns"] for pair in measured)
    incremental_median = statistics.median(pair["incremental"]["wall_ns"] for pair in measured)
    observation["summary"] = {
        "measured_pairs": len(measured),
        "median_full_wall_ns": full_median,
        "median_incremental_wall_ns": incremental_median,
        "median_full_over_incremental_ratio": full_median / incremental_median,
        "interpretation": "Descriptive single-host result; no speed threshold or significance claim",
    }
    return observation


def _environment() -> dict:
    cpu = None
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith("model name"):
                    cpu = line.partition(":")[2].strip()
                    break
        except OSError:
            pass
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "python_executable_sha256": file_digest(Path(sys.executable).resolve()),
        "fractions_source_sha256": file_digest(Path(fractions.__file__)),
        "statistics_source_sha256": file_digest(Path(statistics.__file__)),
        "logical_cpus": os.cpu_count(),
        "cpu_model": cpu,
        "threads_used_by_harness": 1,
        "native_calls_concurrent": 1,
        "host_isolation": "uncontrolled shared execution host",
    }


def _memory() -> dict:
    if not sys.platform.startswith("linux"):
        return {
            "parent_peak_rss_kib": None,
            "max_child_rss_kib": None,
            "reason": "Only Linux resource RSS units qualified by this protocol",
        }
    import resource

    return {
        "parent_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "max_child_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "scope": "Entire run including metadata probes and CLI children; not per case or method",
        "per_method_peak_rss_kib": None,
    }


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Refusing to replace an existing result bundle")
    protocol = load(PROTOCOL)
    runner = NativeCli(args.cli)
    receipt = load(args.build_receipt)
    require(receipt["returncode"] == 0, "Build receipt is not successful")
    require(receipt["binary_sha256"] == runner.fingerprint(), "Build receipt binary mismatch")
    require(receipt["runtime_source_sha"] == protocol["runtime_base_sha"], "Runtime source pin")
    require(receipt["runtime_files"] == runtime_identity(), "Build receipt source mismatch")
    source_sha = git("rev-parse", "HEAD")
    require(
        not git("status", "--porcelain", "--untracked-files=normal"),
        "Commit source before qualification; clean checkout required",
    )
    source_files = [
        name
        for name in git("ls-files", "benchmarks/static").splitlines()
        if "/evidence/" not in name
    ]
    result = {
        "bundle_version": "1",
        "protocol": protocol,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "status": "running",
        "git_source_sha": source_sha,
        "git_dirty": False,
        "runtime_source_sha": protocol["runtime_base_sha"],
        "source_files": {name: file_digest(REPO / name) for name in source_files},
        "build_receipt": receipt,
        "environment": _environment(),
        "mutations": None,
        "comparisons": [],
        "unmeasured": {
            "analyst_effort_minutes": None,
            "diagnosis_and_repair_minutes": None,
            "external_validity": None,
            "transportability": None,
            "disclosure_risk": None,
            "reason": "No human study, external data, qualified provider or privacy experiment",
        },
    }
    archive = Archive()
    try:
        result["mutations"] = mutations(runner)
        require(result["mutations"]["passed"], "Mutation/oracle gate failed; timings not executed")
        for count in protocol["portfolio_sizes"]:
            for name in protocol["scenarios"]:
                observation = comparison(runner, count, name, protocol, archive)
                result["comparisons"].append(observation)
                require(observation["passed"], f"Comparison gate failed: {count}/{name}")
        require(receipt["binary_sha256"] == runner.fingerprint(), "CLI changed during run")
        require(runtime_identity() == receipt["runtime_files"], "Runtime changed during run")
        require(source_sha == git("rev-parse", "HEAD"), "Git source changed during run")
        require(
            result["source_files"] == {name: file_digest(REPO / name) for name in source_files},
            "Harness/protocol/fixtures changed during run",
        )
        result["status"] = "passed"
    except (Failure, KeyError, TypeError, OSError) as error:
        result.update(status="failed", failure=str(error))
    result["memory"] = _memory()
    result["finished_at_utc"] = datetime.now(UTC).isoformat()
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "results.json", result)
    write_json(args.output / "inputs.json", archive.inputs)
    write_json(args.output / "reports.json", archive.reports)
    checksums = {path.name: file_digest(path) for path in sorted(args.output.iterdir())}
    write_json(args.output / "checksums.json", checksums)
    print(
        json.dumps(
            {
                "status": result["status"],
                "source_sha": source_sha,
                "comparisons": len(result["comparisons"]),
                "output": str(args.output),
            }
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
