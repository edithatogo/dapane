"""Synthetic receipt and subprocess controls, never lane qualification evidence."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "qualify_roadmap", ROOT / "scripts/qualify_roadmap.py"
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class RoadmapControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="roadmap-controls-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repo = self.directory / "source"
        self.repo.mkdir()
        (self.repo / "adapters/observed_events").mkdir(parents=True)
        self.source_file = self.repo / "adapters/observed_events/source.txt"
        self.source_file.write_text("synthetic source\n")
        for args in (
            ["init", "-q"],
            ["add", "."],
            [
                "-c",
                "user.name=Qualification Test",
                "-c",
                "user.email=test@example.invalid",
                "-c",
                "core.hooksPath=/dev/null",
                "commit",
                "-qm",
                "Synthetic control",
            ],
        ):
            subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)
        self.sha = guard.git(self.repo, "rev-parse", "HEAD")
        self.source = guard.source_identity(self.repo, self.sha)

    def runner(self):
        run = guard.Runner(self.repo, self.directory / "execution", "observed", self.sha)
        run.step("source-before", action=lambda: self.source)
        run.report["source"] = self.source
        return run

    def receipt(self):
        root = self.directory / "download"
        artifact = root / "roadmap-lane-observed"
        artifact.mkdir(parents=True)
        (artifact / "fixture.log").write_text("Synthetic validator fixture; not test execution.\n")
        names = guard.required_checks("observed")
        order = [
            "source-before",
            *sorted(names - {"source-before", "source-after"}),
            "source-after",
        ]
        commands = [
            {
                "name": name,
                "status": "passed",
                "exit_code": 0,
                "prerequisites": [] if name == "source-before" else ["source-before"],
            }
            for name in order
        ]
        for command in commands:
            if command["name"] in guard.TEST_MINIMUM:
                command["test_count"] = guard.TEST_MINIMUM[command["name"]]
        record = {
            "format": "dapane-roadmap-qualification/1",
            "lane": "observed",
            "expected_source": self.sha,
            "source": self.source,
            "status": "passed",
            "commands": commands,
            "coverage": dict.fromkeys(guard.COVERAGE["observed"], "passed"),
            "required_checks": dict.fromkeys(names, "passed"),
            "artifacts": guard.artifact_inventory(artifact),
        }
        path = artifact / "qualification.json"
        guard.write_json(path, record)
        return root, path, record

    def test_style_failure_does_not_prevent_independent_test_execution(self):
        run = self.runner()
        run.step("style", [sys.executable, "-c", "raise SystemExit(7)"])
        run.step(
            "independent-tests",
            [
                sys.executable,
                "-c",
                "import unittest\nclass Case(unittest.TestCase):\n"
                " def test_execution(self): self.assertEqual(2+2,4)\nunittest.main()",
            ],
            coverage="unittest",
        )
        self.assertEqual(run.records["style"]["exit_code"], 7)
        self.assertTrue(run.passed("independent-tests"))
        self.assertEqual(run.records["independent-tests"]["test_count"], 1)
        self.assertFalse(run.finish())
        record = json.loads((run.retained / "qualification.json").read_text())
        self.assertEqual(record["status"], "failed")
        self.assertIn("logs/style.log", record["artifacts"])

    def test_failed_prerequisite_blocks_execution_and_never_becomes_pass(self):
        run = self.runner()
        marker = self.directory / "should-not-exist"
        run.step("build", [sys.executable, "-c", "raise SystemExit(2)"])
        run.step(
            "install",
            [
                sys.executable,
                "-c",
                "from pathlib import Path; import sys; Path(sys.argv[1]).touch()",
                str(marker),
            ],
            needs=("build",),
        )
        self.assertEqual(run.records["install"]["status"], "blocked")
        self.assertIsNone(run.records["install"]["exit_code"])
        self.assertFalse(marker.exists())
        self.assertFalse(run.finish())

    def test_zero_test_discovery_is_a_failure_even_when_command_exits_zero(self):
        run = self.runner()
        run.step(
            "empty-tests",
            [
                sys.executable,
                "-c",
                "import unittest; "
                "result=unittest.TextTestRunner().run(unittest.TestSuite()); "
                "raise SystemExit(not result.wasSuccessful())",
            ],
            coverage="unittest",
        )
        self.assertEqual(run.records["empty-tests"]["exit_code"], 0)
        self.assertEqual(run.records["empty-tests"]["status"], "failed")
        self.assertIn("Empty/incomplete", run.records["empty-tests"]["error"])

    def test_timeout_is_retained_as_failure(self):
        run = self.runner()
        run.step("timeout", [sys.executable, "-c", "import time; time.sleep(3)"], timeout=0.05)
        self.assertEqual(run.records["timeout"]["status"], "failed")
        self.assertIsNone(run.records["timeout"]["exit_code"])

    def test_wrong_commit_and_dirty_source_are_rejected(self):
        with self.assertRaisesRegex(guard.QualificationError, "expected source"):
            guard.source_identity(self.repo, "0" * 40)
        self.source_file.write_text("changed source\n")
        with self.assertRaisesRegex(guard.QualificationError, "clean checkout"):
            guard.source_identity(self.repo, self.sha)

    def test_source_mutation_after_checks_fails_final_receipt(self):
        run = self.runner()
        self.source_file.write_text("changed while tests were running\n")
        self.assertFalse(run.finish())
        self.assertEqual(run.records["source-after"]["status"], "failed")

    def test_missing_and_duplicate_receipts_are_rejected(self):
        with self.assertRaisesRegex(guard.QualificationError, "Missing lane"):
            guard.verify_receipts(self.repo, self.directory / "absent", ["observed"], self.sha)
        root, path, _ = self.receipt()
        shutil.copytree(path.parent, root / "duplicate")
        with self.assertRaisesRegex(guard.QualificationError, "duplicate lane"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_valid_synthetic_receipt_and_artifact_tampering(self):
        root, path, _ = self.receipt()
        result = guard.verify_receipts(self.repo, root, ["observed"], self.sha)
        self.assertEqual(set(result["lanes"]), {"observed"})
        (path.parent / "fixture.log").write_text("tampered\n")
        with self.assertRaisesRegex(guard.QualificationError, "artifact inventory"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_single_downloaded_artifact_at_flat_root_is_verified(self):
        _, path, record = self.receipt()
        flat = self.directory / "flat-download"
        shutil.copytree(path.parent, flat)
        (flat / "logs").mkdir()
        (flat / "fixture.log").rename(flat / "logs/fixture.log")
        record["artifacts"] = guard.artifact_inventory(flat)
        guard.write_json(flat / "qualification.json", record)
        result = guard.verify_receipts(self.repo, flat, ["observed"], self.sha)
        self.assertEqual(set(result["lanes"]), {"observed"})
        (flat / "logs/fixture.log").write_text("changed after download\n")
        with self.assertRaisesRegex(guard.QualificationError, "artifact inventory"):
            guard.verify_receipts(self.repo, flat, ["observed"], self.sha)

    def test_mixed_flat_and_nested_receipts_are_rejected(self):
        root, path, record = self.receipt()
        guard.write_json(root / "qualification.json", record)
        with self.assertRaisesRegex(guard.QualificationError, "Ambiguous mixed"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_unexpected_artifact_root_cannot_be_silently_ignored(self):
        root, _, _ = self.receipt()
        (root / "unexpected-artifact").mkdir()
        with self.assertRaisesRegex(guard.QualificationError, "Unexpected artifact root"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_flat_artifact_cannot_replace_a_multiple_lane_matrix(self):
        _, path, _ = self.receipt()
        with self.assertRaisesRegex(guard.QualificationError, "exactly one"):
            guard.receipt_locations(path.parent, ["observed", "decisions"])

    def test_receipt_from_another_source_is_rejected(self):
        root, path, record = self.receipt()
        record["source"]["sha"] = "0" * 40
        guard.write_json(path, record)
        with self.assertRaisesRegex(guard.QualificationError, "source identity"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_empty_or_blocked_command_inventory_cannot_pass(self):
        root, path, record = self.receipt()
        original = record["commands"]
        record["commands"] = []
        guard.write_json(path, record)
        with self.assertRaisesRegex(guard.QualificationError, "Empty/duplicate"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)
        record["commands"] = original
        record["commands"][0].update(status="blocked", exit_code=None)
        guard.write_json(path, record)
        with self.assertRaisesRegex(guard.QualificationError, "blocked or unexecuted"):
            guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_discovery_cannot_hide_a_present_lane(self):
        with self.assertRaisesRegex(guard.QualificationError, "Declared lane coverage"):
            guard.verify_receipts(self.repo, self.directory, [], self.sha)

    def test_omitted_source_or_style_guard_cannot_pass(self):
        root, path, record = self.receipt()
        original = record["commands"]
        for name in ("source-before", "source-after", "observed-format"):
            record["commands"] = [command for command in original if command["name"] != name]
            guard.write_json(path, record)
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(guard.QualificationError, "mandatory"),
            ):
                guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_missing_or_future_prerequisite_cannot_pass(self):
        root, path, record = self.receipt()
        command = next(c for c in record["commands"] if c["name"] == "fixture-tests")
        for name in ("missing-prerequisite", "source-after"):
            command["prerequisites"] = [name]
            guard.write_json(path, record)
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(guard.QualificationError, "prerequisite"),
            ):
                guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_one_executed_suite_cannot_hide_an_empty_native_suite(self):
        root, path, record = self.receipt()
        command = next(c for c in record["commands"] if c["name"] == "observed-tests")
        for count in (0, None, True):
            command["test_count"] = count
            guard.write_json(path, record)
            with (
                self.subTest(count=count),
                self.assertRaisesRegex(guard.QualificationError, "test count"),
            ):
                guard.verify_receipts(self.repo, root, ["observed"], self.sha)

    def test_failed_or_skipped_workflow_prerequisite_cannot_pass(self):
        root, _, _ = self.receipt()
        for name, state in (("controls", "failure"), ("qualify", "skipped")):
            jobs = {key: {"result": "success"} for key in ("controls", "qualify", "discovery")}
            jobs[name]["result"] = state
            with self.subTest(name=name), self.assertRaises(guard.QualificationError):
                guard.verify_receipts(self.repo, root, ["observed"], self.sha, jobs)

    def test_ignored_or_skipped_cases_are_not_accepted(self):
        with self.assertRaisesRegex(guard.QualificationError, "Ignored"):
            guard.coverage_count("test result: ok. 1 passed; 0 failed; 1 ignored;", "rust")
        with self.assertRaisesRegex(guard.QualificationError, "Skipped"):
            guard.coverage_count("Ran 2 tests in 0.1s\nOK (skipped=1)", "unittest")


if __name__ == "__main__":
    unittest.main()
