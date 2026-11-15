"""Exercise track completion and archival through the public validator CLI."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts/validate_conductor.py"
CONTEXT_FILES = (
    "README.md",
    "AGENTS.md",
    "conductor/index.md",
    "conductor/product.md",
    "conductor/product-guidelines.md",
    "conductor/requirements.md",
    "conductor/design.md",
    "conductor/decisions.md",
    "conductor/tech-stack.md",
    "conductor/workflow.md",
    "conductor/repository-map.md",
    "conductor/ecosystem.md",
    "conductor/research-validation.md",
    "conductor/roadmap.md",
    "conductor/tracks.md",
    "conductor/verification.md",
    "conductor/code_styleguides/index.md",
    "conductor/archive/README.md",
)


class ConductorValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "fixture"
        for relative in CONTEXT_FILES:
            self.write(relative, "# Synthetic project context\n")
        self.write(
            "conductor/requirements.md",
            "# Requirements\n\n## RQ-01 — Setup assurance\n\n"
            "Acceptance: completed records preserve their verification evidence.\n",
        )
        self.registry_rows: list[str] = []

    def write(self, relative: str, contents: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")

    def add_track(
        self,
        track_id: str = "setup_20261108",
        *,
        status: str = "completed",
        task_marker: str = "x",
        verification_status: str | None = "passed",
        dependencies: tuple[str, ...] = (),
    ) -> None:
        prefix = f"conductor/tracks/{track_id}"
        verification = {"commands": ["python3 scripts/validate_conductor.py"]}
        if verification_status is not None:
            verification["status"] = verification_status
        metadata = {
            "track_id": track_id,
            "type": "chore",
            "status": status,
            "created_at": "2026-11-08T00:00:00Z",
            "updated_at": "2026-11-15T00:00:00Z",
            "description": "Synthetic lifecycle fixture",
            "repositories": ["."],
            "dependencies": list(dependencies),
            "external_dependencies": [],
            "owners": ["fixture"],
            "decisions": [],
            "requirement_ids": ["RQ-01"],
            "verification": verification,
        }
        self.write(f"{prefix}/metadata.json", json.dumps(metadata, indent=2) + "\n")
        self.write(
            f"{prefix}/index.md",
            f"# {track_id}\n\nStatus: {status}\n\n"
            "[Specification](spec.md)\n[Plan](plan.md)\n"
            "[Metadata](metadata.json)\n[Registry](../../tracks.md)\n",
        )
        dependency_links = "".join(
            f"- [{dependency}](../{dependency}/index.md)\n"
            for dependency in dependencies
        )
        self.write(
            f"{prefix}/spec.md",
            "# Specification\n\nPreserve setup records and their evidence.\n\n"
            + dependency_links,
        )
        self.write(
            f"{prefix}/plan.md",
            f"# Implementation plan\n\nStatus: {status}\n\n"
            f"- [{task_marker}] S1 Verify the synthetic setup record.\n",
        )
        marker = {
            "new": "[ ]",
            "in_progress": "[~]",
            "completed": "[x]",
            "cancelled": "[-]",
            "archived": "[-]",
        }[status]
        self.registry_rows.append(
            f"| {marker} | [{track_id}](./tracks/{track_id}/index.md) "
            f"| {status} | RQ-01 |\n"
        )
        self.write(
            "conductor/tracks.md",
            "# Track registry\n\n| Marker | Track | Status | Requirements |\n"
            "| --- | --- | --- | --- |\n" + "".join(self.registry_rows),
        )

    def validate(self, expected_error: str | None = None) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(self.root)],
            cwd=self.temporary.name,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        self.assertEqual(
            result.returncode,
            0 if expected_error is None else 1,
            result.stdout,
        )
        if expected_error is None:
            self.assertIn("Conductor validation passed:", result.stdout)
        else:
            self.assertIn(expected_error, result.stdout)

    def check_status_forms(self, forms: tuple[str, ...], *, valid: bool) -> None:
        self.add_track(status="archived")
        for document in ("index", "plan"):
            relative = f"conductor/tracks/setup_20261108/{document}.md"
            original = (self.root / relative).read_text(encoding="utf-8")
            for form in forms:
                with self.subTest(document=document, status_form=form):
                    self.write(relative, original.replace("Status: archived", form))
                    self.validate(
                        None if valid else f"{document} Status differs from metadata"
                    )
            self.write(relative, original)

    def test_valid_completed_track_passes(self) -> None:
        self.add_track()
        self.validate()

    def test_valid_archive_remains_a_registered_dependency(self) -> None:
        self.add_track(status="archived")
        self.add_track(
            "consumer_20261108",
            status="new",
            task_marker=" ",
            verification_status="not_run",
            dependencies=("setup_20261108",),
        )
        self.validate()

    def test_archived_track_rejects_unfinished_tasks(self) -> None:
        self.add_track(status="archived")
        for marker in (" ", "~", "!"):
            with self.subTest(marker=marker):
                self.write(
                    "conductor/tracks/setup_20261108/plan.md",
                    f"# Plan\n\nStatus: archived\n\n- [{marker}] Finish setup.\n",
                )
                self.validate("archived track contains unfinished tasks")

    def test_archived_track_requires_passed_verification(self) -> None:
        self.add_track(status="archived")
        path = self.root / "conductor/tracks/setup_20261108/metadata.json"
        for status in ("not_run", "failed", None):
            with self.subTest(verification_status=status):
                metadata = json.loads(path.read_text(encoding="utf-8"))
                metadata["verification"].pop("status", None)
                if status is not None:
                    metadata["verification"]["status"] = status
                path.write_text(json.dumps(metadata), encoding="utf-8")
                self.validate("archived track lacks passed verification")

    def test_plan_status_must_match_metadata(self) -> None:
        self.add_track(status="archived")
        for status in ("completed", "new", "in_progress"):
            with self.subTest(plan_status=status):
                self.write(
                    "conductor/tracks/setup_20261108/plan.md",
                    f"# Plan\n\nStatus: {status}\n\n- [x] Finish setup.\n",
                )
                self.validate("plan Status differs from metadata")

    def test_plan_requires_status_line(self) -> None:
        self.add_track()
        self.write(
            "conductor/tracks/setup_20261108/plan.md",
            "# Plan\n\n- [x] Finish setup.\n",
        )
        self.validate("plan Status differs from metadata")

    def test_single_status_accepts_plain_and_paired_backticks(self) -> None:
        self.check_status_forms(
            ("Status: archived", "Status: `archived`", "Status:\t`archived`\t"),
            valid=True,
        )

    def test_conflicting_status_lines_are_rejected(self) -> None:
        self.check_status_forms(
            (
                "Status: completed\nStatus: archived",
                "Status: archived\nStatus: completed",
            ),
            valid=False,
        )

    def test_duplicate_status_lines_are_rejected(self) -> None:
        self.check_status_forms(
            (
                "Status: archived\nStatus: archived",
                "Status: archived\nStatus: `archived`",
            ),
            valid=False,
        )

    def test_status_backticks_must_be_paired(self) -> None:
        self.check_status_forms(
            ("Status: `archived", "Status: archived`"),
            valid=False,
        )

    def test_status_value_cannot_cross_lines(self) -> None:
        self.check_status_forms(
            ("Status:\narchived", "Status: \n\tarchived"),
            valid=False,
        )

    def test_cancellation_is_distinct_from_verified_archival(self) -> None:
        self.add_track(status="cancelled", task_marker=" ", verification_status="not_run")
        self.validate()


if __name__ == "__main__":
    unittest.main()
