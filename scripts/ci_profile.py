#!/usr/bin/env python3
"""Profile local checks, CI workflow steps, and roadmap qualification receipts."""

from __future__ import annotations

import argparse
import json
import resource
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _max_rss_kib() -> int:
    raw = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    # macOS reports ru_maxrss in bytes whereas Linux reports KiB.
    return int(raw // 1024) if sys.platform == "darwin" else int(raw)


def append_record(profile_file: Path, record: dict[str, Any]) -> None:
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    with profile_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, separators=(",", ":")) + "\n")


def load_records(profile_file: Path) -> list[dict[str, Any]]:
    if not profile_file.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for raw in profile_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def cmd_run(args: argparse.Namespace) -> int:
    cmd = list(args.cmd)
    if cmd[:1] == ["--"]:
        cmd = cmd[1:]
    if not cmd:
        print("ci_profile run: missing command after --", file=sys.stderr)
        return 2

    started_at = datetime.now(UTC).isoformat()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=args.cwd, check=False)
        exit_code = int(proc.returncode)
    except OSError as exc:
        print(f"ci_profile run: {exc}", file=sys.stderr)
        exit_code = 127
    wall = round(time.perf_counter() - t0, 6)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 6)

    record = {
        "name": args.name,
        "command": cmd,
        "started_at": started_at,
        "wall_seconds": wall,
        "child_cpu_seconds": max(0.0, cpu),
        "max_rss_kib": _max_rss_kib(),
        "exit_code": exit_code,
    }
    append_record(args.profile_file, record)
    return exit_code


def format_compact(entries: list[dict[str, Any]], title: str = "profile") -> str:
    if not entries:
        return f"[{title}] total=0.00s (no steps recorded)"
    total = sum(float(e.get("wall_seconds", 0.0)) for e in entries)
    parts = []
    for entry in entries:
        name = entry["name"]
        wall = float(entry.get("wall_seconds", 0.0))
        suffix = "" if entry.get("exit_code", 0) == 0 else "!"
        parts.append(f"{name}={wall:.2f}s{suffix}")
    return f"[{title}] total={total:.2f}s | " + ", ".join(parts)


def render_summary(entries: list[dict[str, Any]], title: str) -> str:
    if not entries:
        return f"### {title}\n\nNo profiled steps recorded.\n"
    total_wall = sum(float(e.get("wall_seconds", 0.0)) for e in entries)
    total_cpu = sum(float(e.get("child_cpu_seconds", 0.0)) for e in entries)
    peak_kib = max(int(e.get("max_rss_kib", 0)) for e in entries)
    lines = [
        f"### {title}",
        "",
        "| Step | Status | Wall (s) | CPU (s) | Share | Peak RSS (MiB) |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for entry in sorted(
        entries, key=lambda item: float(item.get("wall_seconds", 0.0)), reverse=True
    ):
        wall = float(entry.get("wall_seconds", 0.0))
        cpu = float(entry.get("child_cpu_seconds", 0.0))
        share = (100.0 * wall / total_wall) if total_wall > 0 else 0.0
        rss_mib = int(entry.get("max_rss_kib", 0)) / 1024.0
        status = "pass" if entry.get("exit_code", 1) == 0 else f"fail ({entry.get('exit_code')})"
        lines.append(
            f"| `{entry['name']}` | {status} | {wall:.3f} | {cpu:.3f} | {share:.1f}% | {rss_mib:.1f} |"
        )
    overall = "pass" if all(e.get("exit_code", 1) == 0 for e in entries) else "fail"
    lines.append(
        f"| **Total** | {overall} | **{total_wall:.3f}** | **{total_cpu:.3f}** | 100.0% | {peak_kib / 1024.0:.1f} |"
    )
    lines.append("")
    return "\n".join(lines)


def _find_roadmap_receipts(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    flat = directory / "qualification.json"
    if flat.is_file():
        return [flat]
    return sorted(
        p / "qualification.json"
        for p in directory.iterdir()
        if p.is_dir() and (p / "qualification.json").is_file()
    )


def render_roadmap_summary(directory: Path, title: str) -> str:
    receipt_paths = _find_roadmap_receipts(directory)
    if not receipt_paths:
        return f"### {title}\n\nNo roadmap qualification receipts found in `{directory}`.\n"

    lane_rows: list[tuple[str, str, int, float]] = []
    step_rows: list[tuple[str, str, str, float]] = []
    for path in receipt_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        lane = str(data.get("lane", path.parent.name))
        status = str(data.get("status", "unknown"))
        commands = data.get("commands", [])
        lane_elapsed = sum(float(cmd.get("elapsed_seconds") or 0.0) for cmd in commands)
        lane_rows.append((lane, status, len(commands), lane_elapsed))
        for cmd in commands:
            elapsed = cmd.get("elapsed_seconds")
            if isinstance(elapsed, (int, float)):
                step_rows.append(
                    (lane, str(cmd.get("name", "?")), str(cmd.get("status", "?")), float(elapsed))
                )

    lines = [
        f"### {title}",
        "",
        "| Lane | Status | Steps | Summed Step Time (s) |",
        "| --- | --- | ---: | ---: |",
    ]
    for lane, status, count, elapsed in sorted(lane_rows, key=lambda r: r[3], reverse=True):
        lines.append(f"| `{lane}` | {status} | {count} | {elapsed:.3f} |")

    if step_rows:
        lines.extend(
            [
                "",
                "| Lane | Slowest Steps (Top 15) | Status | Elapsed (s) |",
                "| --- | --- | --- | ---: |",
            ]
        )
        for lane, name, status, elapsed in sorted(step_rows, key=lambda r: r[3], reverse=True)[:15]:
            lines.append(f"| `{lane}` | `{name}` | {status} | {elapsed:.3f} |")
    lines.append("")
    return "\n".join(lines)


def _write_summary_file(summary_file: Path | None, markdown: str) -> None:
    if summary_file is None or not str(summary_file).strip():
        return
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with summary_file.open("a", encoding="utf-8") as stream:
        stream.write(markdown + "\n")


def cmd_summarize(args: argparse.Namespace) -> int:
    entries = load_records(args.profile_file)
    if args.compact:
        output = format_compact(entries, title=args.title)
        print(output)
        _write_summary_file(args.summary_file, output)
        return 0
    markdown = render_summary(entries, title=args.title)
    print(markdown)
    _write_summary_file(args.summary_file, markdown)
    return 0


def cmd_summarize_roadmap(args: argparse.Namespace) -> int:
    markdown = render_roadmap_summary(args.directory, title=args.title)
    print(markdown)
    _write_summary_file(args.summary_file, markdown)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_p = subparsers.add_parser("run", help="Execute a command and append timing/RSS telemetry.")
    run_p.add_argument("--name", required=True)
    run_p.add_argument("--profile-file", type=Path, required=True)
    run_p.add_argument("--cwd", type=Path)
    run_p.add_argument("cmd", nargs=argparse.REMAINDER)

    sum_p = subparsers.add_parser(
        "summarize", help="Render a profile summary from JSONL telemetry."
    )
    sum_p.add_argument("--profile-file", type=Path, required=True)
    sum_p.add_argument("--title", default="CI Execution Profile")
    sum_p.add_argument("--summary-file", type=Path)
    sum_p.add_argument("--compact", action="store_true")

    rm_p = subparsers.add_parser(
        "summarize-roadmap", help="Summarize elapsed times from roadmap qualification receipts."
    )
    rm_p.add_argument("--directory", type=Path, required=True)
    rm_p.add_argument("--title", default="Roadmap Lane Profile")
    rm_p.add_argument("--summary-file", type=Path)

    args = parser.parse_args(argv)
    if args.subcommand == "run":
        return cmd_run(args)
    if args.subcommand == "summarize":
        return cmd_summarize(args)
    return cmd_summarize_roadmap(args)


if __name__ == "__main__":
    raise SystemExit(main())
