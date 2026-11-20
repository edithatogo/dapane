"""Unit tests for scripts/ci_select.py selective CI routing."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ci_select", ROOT / "scripts/ci_select.py")
ci_select = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = ci_select
SPEC.loader.exec_module(ci_select)


class CiSelectTests(unittest.TestCase):
    def test_project_interpreter_changes_select_all_consumers(self) -> None:
        for path in (".python-version", ".github/actions/project-python/action.yml"):
            with self.subTest(path=path):
                selected = ci_select.select_changes(
                    ROOT, [ci_select.ChangeRecord(path, "M")], mode="pr"
                )
                self.assertTrue(selected.run_release_heavy)
                self.assertTrue(selected.run_provider_consumers)
                self.assertEqual(selected.lanes, ci_select.present_lanes(ROOT))
                self.assertEqual(
                    selected.python_versions, [(ROOT / ".python-version").read_text().strip()]
                )

    def test_dot_prefixed_workflow_path_selects_its_checks(self) -> None:
        change = ci_select.ChangeRecord("./.github/workflows/runtime.yml")
        selected = ci_select.select_changes(ROOT, [change])
        self.assertTrue(selected.run_native)
        self.assertTrue(selected.run_python)
        self.assertEqual(selected.changed_files, [".github/workflows/runtime.yml"])

    def test_docs_only_change_only_runs_conductor(self) -> None:
        for path in ("conductor/tracks.md", "docs/quickstart.md"):
            with self.subTest(path=path):
                sel = ci_select.select_changes(ROOT, [ci_select.ChangeRecord(path, "M")], mode="pr")
                self.assertTrue(sel.run_conductor)
                self.assertFalse(sel.run_native)
                self.assertFalse(sel.run_python)
                self.assertFalse(sel.run_process_models)
                self.assertFalse(sel.run_decision_provider_d2)
                self.assertFalse(sel.run_provider_consumers)
                self.assertFalse(sel.run_release_heavy)
                self.assertEqual(sel.lanes, [])
                self.assertEqual(sel.workflows, [".github/workflows/conductor.yml"])

    def test_single_adapter_d2_only_selects_d2_workflow(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("adapters/decision_provider_d2/study.py", "M")], mode="pr"
        )
        self.assertTrue(sel.run_decision_provider_d2)
        self.assertFalse(sel.run_native)
        self.assertFalse(sel.run_python)
        self.assertFalse(sel.run_process_models)
        self.assertEqual(sel.lanes, [])
        self.assertEqual(sel.workflows, [".github/workflows/decision-provider-d2.yml"])

    def test_observed_events_adapter_is_standalone_from_core(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("adapters/observed_events/src/lib.rs", "M")], mode="pr"
        )
        self.assertEqual(sel.lanes, ["observed"])
        self.assertEqual(sel.rust_adapters, ["adapters/observed_events/Cargo.toml"])
        self.assertFalse(sel.run_native)
        self.assertFalse(sel.run_python)
        self.assertEqual(sel.workflows, [".github/workflows/roadmap-lanes.yml"])

    def test_dapane_core_fans_out_to_dependants_and_pr_python_versions(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("crates/dapane-core/src/lib.rs", "M")], mode="pr"
        )
        self.assertTrue(sel.run_native)
        self.assertTrue(sel.run_python)
        self.assertEqual(sel.python_versions, ["3.15.1"])
        self.assertEqual(sel.pytest_targets, ["tests/python"])
        self.assertTrue(sel.run_process_models)
        self.assertTrue(sel.run_provider_consumers)
        self.assertTrue(sel.run_release_heavy)
        self.assertIn("decisions", sel.lanes)
        self.assertNotIn("observed", sel.lanes)
        self.assertEqual(sel.rust_adapters, ["adapters/decision_draws/Cargo.toml"])

    def test_pyproject_expands_full_python_matrix_and_wheel_lanes(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("pyproject.toml", "M")], mode="pr"
        )
        self.assertTrue(sel.run_python)
        self.assertTrue(sel.full_python_matrix)
        self.assertEqual(sel.python_versions, ["3.15.1"])
        self.assertEqual(sel.lanes, ["newborn", "mchs", "reporting"])
        self.assertTrue(sel.run_release_validate)
        self.assertTrue(sel.run_release_heavy)

    def test_narrow_python_test_change_narrows_pytest_targets(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("tests/python/test_errors.py", "M")], mode="pr"
        )
        self.assertTrue(sel.run_python)
        self.assertEqual(sel.python_versions, ["3.15.1"])
        self.assertEqual(sel.pytest_targets, ["tests/python/test_errors.py"])
        self.assertTrue(sel.run_provider_consumers)

    def test_roadmap_script_change_selects_all_present_lanes(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("scripts/qualify_roadmap.py", "M")], mode="pr"
        )
        self.assertTrue(sel.run_tooling)
        self.assertEqual(sel.lanes, ci_select.present_lanes(ROOT))

    def test_added_or_deleted_file_anywhere_triggers_conductor(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("adapters/decision_provider_d2/new.py", "A")], mode="pr"
        )
        self.assertTrue(sel.run_conductor)
        self.assertTrue(sel.run_decision_provider_d2)

    def test_full_mode_enables_everything_regardless_of_changes(self) -> None:
        sel = ci_select.select_changes(
            ROOT, [ci_select.ChangeRecord("conductor/tracks.md", "M")], mode="full"
        )
        self.assertTrue(sel.run_native)
        self.assertTrue(sel.run_python)
        self.assertEqual(sel.python_versions, ["3.15.1"])
        self.assertEqual(sel.lanes, ci_select.present_lanes(ROOT))
        self.assertTrue(sel.run_release_heavy)

    def test_github_output_and_fail_closed_when_base_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "github_output.txt"
            rc = ci_select.main(
                ["--base", "deadbeef" * 5, "--head", "HEAD", "--github-output", str(out)]
            )
            self.assertEqual(rc, 0)
            content = dict(line.split("=", 1) for line in out.read_text().splitlines())
            self.assertEqual(content["run_native"], "true")
            self.assertEqual(content["run_release_heavy"], "true")
            self.assertEqual(json.loads(content["python_versions"]), ["3.15.1"])
            self.assertEqual(json.loads(content["lanes"]), ci_select.present_lanes(ROOT))
