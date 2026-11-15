"""Archive acceptance uses real, isolated synthetic Conductor records."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "conductor_archive_subject", ROOT / "scripts/validate_conductor.py"
)
CONDUCTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONDUCTOR)


def project(root, *, marker="x", verification="passed"):
    """Build a complete minimal project; no live repository files are modified."""
    for relative in CONDUCTOR.REQUIRED_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Synthetic project context\n", encoding="utf-8")
    (root / "conductor/requirements.md").write_text("## RQ-01 Synthetic requirement\n")
    (root / "conductor/tracks.md").write_text(
        "| [-] | [Synthetic](tracks/synthetic/index.md) | archived | RQ-01 |\n"
    )
    track = root / "conductor/tracks/synthetic"
    track.mkdir(parents=True)
    (track / "index.md").write_text("# Synthetic track\n\nStatus: archived\n")
    (track / "spec.md").write_text("# Synthetic acceptance specification\n")
    (track / "plan.md").write_text(
        f"# Synthetic plan\n\nStatus: archived\n\n- [{marker}] T1 Verify behaviour\n"
    )
    metadata = {
        "track_id": "synthetic",
        "type": "feature",
        "status": "archived",
        "created_at": "2026-11-15",
        "updated_at": "2026-11-15",
        "description": "Synthetic validator fixture only",
        "repositories": ["edithatogo/dapane"],
        "dependencies": [],
        "owners": ["synthetic"],
        "decisions": [],
        "requirement_ids": ["RQ-01"],
        "verification": {"status": verification, "commands": ["synthetic check"]},
    }
    (track / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return root


def test_verified_complete_archive_retains_valid_dependencies_and_links(tmp_path):
    errors, counts = CONDUCTOR.validate(project(tmp_path))
    assert errors == []
    assert counts["tracks"] == 1
    assert counts["requirements"] == 1
    assert counts["tasks"] == 1


@pytest.mark.parametrize("marker", [" ", "~", "!"])
def test_archive_cannot_hide_unfinished_work(tmp_path, marker):
    errors, _ = CONDUCTOR.validate(project(tmp_path, marker=marker))
    assert any("unfinished tasks" in error for error in errors), errors


@pytest.mark.parametrize("verification", ["planned", "failed", None])
def test_archive_requires_passed_verification(tmp_path, verification):
    errors, _ = CONDUCTOR.validate(project(tmp_path, verification=verification))
    assert any("lacks passed verification" in error for error in errors), errors
