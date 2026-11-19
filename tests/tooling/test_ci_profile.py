"""Unit tests for scripts/ci_profile.py telemetry and reporting."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ci_profile", ROOT / "scripts/ci_profile.py")
ci_profile = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = ci_profile
SPEC.loader.exec_module(ci_profile)


class CiProfileTests(unittest.TestCase):
    def test_run_records_telemetry_and_propagates_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            prof = Path(td) / "prof.jsonl"
            rc_ok = ci_profile.main(
                [
                    "run",
                    "--name",
                    "ok-step",
                    "--profile-file",
                    str(prof),
                    "--",
                    sys.executable,
                    "-c",
                    "pass",
                ]
            )
            rc_fail = ci_profile.main(
                [
                    "run",
                    "--name",
                    "bad-step",
                    "--profile-file",
                    str(prof),
                    "--",
                    sys.executable,
                    "-c",
                    "raise SystemExit(3)",
                ]
            )
            self.assertEqual(rc_ok, 0)
            self.assertEqual(rc_fail, 3)
            entries = ci_profile.load_records(prof)
            self.assertEqual([e["name"] for e in entries], ["ok-step", "bad-step"])
            self.assertEqual(entries[0]["exit_code"], 0)
            self.assertEqual(entries[1]["exit_code"], 3)
            self.assertGreaterEqual(entries[0]["wall_seconds"], 0.0)
            self.assertGreaterEqual(entries[0]["max_rss_kib"], 0)

    def test_summarize_renders_markdown_compact_and_writes_summary_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            prof = Path(td) / "prof.jsonl"
            summary = Path(td) / "step_summary.md"
            ci_profile.append_record(
                prof,
                {
                    "name": "fast",
                    "wall_seconds": 0.25,
                    "child_cpu_seconds": 0.10,
                    "max_rss_kib": 10240,
                    "exit_code": 0,
                },
            )
            ci_profile.append_record(
                prof,
                {
                    "name": "slow",
                    "wall_seconds": 1.75,
                    "child_cpu_seconds": 1.20,
                    "max_rss_kib": 20480,
                    "exit_code": 0,
                },
            )
            compact = ci_profile.format_compact(ci_profile.load_records(prof), title="hook")
            self.assertIn("[hook] total=2.00s | fast=0.25s, slow=1.75s", compact)

            rc = ci_profile.main(
                [
                    "summarize",
                    "--profile-file",
                    str(prof),
                    "--title",
                    "Runtime Profile",
                    "--summary-file",
                    str(summary),
                ]
            )
            self.assertEqual(rc, 0)
            text = summary.read_text(encoding="utf-8")
            self.assertIn("### Runtime Profile", text)
            self.assertLess(text.index("`slow`"), text.index("`fast`"))
            self.assertIn("**2.000**", text)

    def test_summarize_roadmap_handles_flat_and_nested_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            flat = root / "flat"
            flat.mkdir()
            (flat / "qualification.json").write_text(
                json.dumps(
                    {
                        "lane": "decisions",
                        "status": "passed",
                        "commands": [
                            {"name": "decisions-tests", "status": "passed", "elapsed_seconds": 2.5},
                            {"name": "source-before", "status": "passed", "elapsed_seconds": 0.1},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            flat_md = ci_profile.render_roadmap_summary(flat, "Flat Receipt")
            self.assertIn("`decisions`", flat_md)
            self.assertIn("2.600", flat_md)

            nested = root / "nested"
            (nested / "lane-a").mkdir(parents=True)
            (nested / "lane-b").mkdir(parents=True)
            (nested / "lane-a/qualification.json").write_text(
                json.dumps(
                    {
                        "lane": "observed",
                        "status": "passed",
                        "commands": [
                            {"name": "observed-tests", "status": "passed", "elapsed_seconds": 1.0}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (nested / "lane-b/qualification.json").write_text(
                json.dumps(
                    {
                        "lane": "static",
                        "status": "passed",
                        "commands": [
                            {"name": "static-verify", "status": "passed", "elapsed_seconds": 3.0}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            nested_md = ci_profile.render_roadmap_summary(nested, "Nested Receipts")
            self.assertLess(nested_md.index("`static`"), nested_md.index("`observed`"))
