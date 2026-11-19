"""Unit tests for scripts/run_local_ci.py."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("run_local_ci", ROOT / "scripts/run_local_ci.py")
local_ci = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = local_ci
SPEC.loader.exec_module(local_ci)


class RunLocalCiTests(unittest.TestCase):
    def test_runner_resolution_without_docker_daemon(self) -> None:
        with (
            mock.patch.object(local_ci.shutil, "which", return_value="/usr/local/bin/act"),
            mock.patch.object(local_ci, "find_docker_socket", return_value=None),
        ):
            runner, _, note = local_ci.resolve_runner("auto")
            self.assertEqual(runner, "native")
            self.assertIn("falling back", note)
            with self.assertRaisesRegex(RuntimeError, "Docker daemon"):
                local_ci.resolve_runner("act")

    def test_runner_resolution_uses_act_when_socket_available(self) -> None:
        with (
            mock.patch.object(local_ci.shutil, "which", return_value="/usr/local/bin/act"),
            mock.patch.object(
                local_ci, "find_docker_socket", return_value="unix:///tmp/colima.sock"
            ),
        ):
            runner, host, _ = local_ci.resolve_runner("auto")
            self.assertEqual(runner, "act")
            self.assertEqual(host, "unix:///tmp/colima.sock")

    def test_dry_run_selects_only_d2_steps_when_only_d2_changed(self) -> None:
        fake_sel = local_ci.ci_select.select_changes(
            ROOT,
            [local_ci.ci_select.ChangeRecord("adapters/decision_provider_d2/README.md", "M")],
            mode="pr",
        )
        with (
            mock.patch.object(
                local_ci,
                "compute_selection",
                return_value=(fake_sel, "range", "abc", "def"),
            ),
            mock.patch.object(local_ci, "find_docker_socket", return_value=None),
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = local_ci.main(["--dry-run"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["workflows"], [".github/workflows/decision-provider-d2.yml"])
            step_names = [s["name"] for s in payload["native_steps"]]
            self.assertIn("decision-d2-tests", step_names)
            self.assertNotIn("rust-clippy", step_names)
            self.assertNotIn("release-tests", step_names)

    def test_native_execution_runs_selected_d2_and_writes_profile(self) -> None:
        fake_sel = local_ci.ci_select.select_changes(
            ROOT,
            [local_ci.ci_select.ChangeRecord("adapters/decision_provider_d2/README.md", "M")],
            mode="pr",
        )
        with (
            tempfile.TemporaryDirectory() as td,
            mock.patch.object(
                local_ci,
                "compute_selection",
                return_value=(fake_sel, "range", "HEAD", "HEAD"),
            ),
            mock.patch.object(local_ci, "resolve_default_base", return_value="HEAD"),
            mock.patch.object(local_ci.shutil, "which", return_value=None),
        ):
            prof = Path(td) / "prof.jsonl"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = local_ci.main(["--runner", "native", "--profile-output", str(prof)])
            self.assertEqual(rc, 0)
            self.assertTrue(prof.is_file())
            self.assertIn("### Local CI Profile", buf.getvalue())
            entries = local_ci.ci_profile.load_records(prof)
            self.assertEqual(
                [e["name"] for e in entries], ["decision-d2-tests", "decision-d2-compile"]
            )
