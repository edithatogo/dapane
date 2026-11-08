#!/usr/bin/env python3
"""Check Dapane's Conductor records without runtime or network dependencies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_FILES = (
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
TRACK_FILES = ("index.md", "spec.md", "plan.md", "metadata.json")
STATE_MARKERS = {
    "new": "[ ]",
    "in_progress": "[~]",
    "blocked": "[!]",
    "completed": "[x]",
    "cancelled": "[-]",
    "archived": "[-]",
}
METADATA_FIELDS = (
    "track_id",
    "type",
    "status",
    "created_at",
    "updated_at",
    "description",
    "repositories",
    "dependencies",
    "owners",
    "decisions",
    "requirement_ids",
    "verification",
)
LIST_FIELDS = (
    "repositories",
    "dependencies",
    "owners",
    "decisions",
    "requirement_ids",
)
LINK = re.compile(
    r"\[[^\]\n]+\]\((<[^>\n]+>|[^)\n]*?)"
    r"(?:\s+(?:\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|\((?:\\.|[^)\\\n])*\)))?\s*\)"
)
TASK = re.compile(r"^\s*[-*]\s+\[([ x~!\-])\]\s+(\S.*)$", re.MULTILINE)
REQUIREMENT_HEADING = re.compile(r"^#{1,6}\s+(RQ-\d{2})\b", re.MULTILINE)
REGISTRY_LINK = re.compile(r"(?:\./)?tracks/([^/\s)]+)/index\.md")


def source_path(root: Path, path: Path, errors: list[str]) -> Path | None:
    """Resolve a source before any content read or directory traversal."""
    label = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"{label}: invalid source path: {exc}")
        return None
    if not resolved.is_relative_to(root):
        errors.append(f"{label}: source path resolves outside repository")
        return None
    return resolved


def read_source(root: Path, path: Path, errors: list[str]) -> str | None:
    resolved = source_path(root, path, errors)
    if resolved is None:
        return None
    label = str(path.relative_to(root))
    try:
        if not resolved.is_file():
            errors.append(f"{label}: source file missing or not a regular file")
            return None
        return resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read source file: {exc}")
        return None


def source_directory(root: Path, path: Path, errors: list[str]) -> Path | None:
    resolved = source_path(root, path, errors)
    if resolved is None:
        return None
    try:
        if resolved.is_dir():
            return resolved
        errors.append(f"{path.relative_to(root)}: source directory missing or invalid")
    except OSError as exc:
        errors.append(f"{path.relative_to(root)}: cannot inspect source directory: {exc}")
    return None


def check_links(root: Path, paths: list[Path], errors: list[str]) -> int:
    checked = 0
    for path in paths:
        contents = read_source(root, path, errors)
        if contents is None:
            continue
        for match in LINK.finditer(contents):
            target = match.group(1).strip().strip("<>")
            try:
                parsed = urlsplit(target)
            except ValueError as exc:
                errors.append(f"{path.relative_to(root)}: invalid link target: {exc}")
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            checked += 1
            try:
                resolved = (path.parent / unquote(parsed.path)).resolve()
            except (OSError, RuntimeError, ValueError) as exc:
                errors.append(f"{path.relative_to(root)}: invalid local link: {target}: {exc}")
                continue
            if not resolved.is_relative_to(root):
                errors.append(f"{path.relative_to(root)}: local link escapes repository: {target}")
            elif not resolved.exists():
                errors.append(f"{path.relative_to(root)}: missing local link: {target}")
    return checked


def check_dependency_graph(tracks: dict[str, dict], errors: list[str]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(track_id: str, trail: list[str]) -> None:
        if track_id in visiting:
            errors.append("Local dependency cycle: " + " -> ".join([*trail, track_id]))
            return
        if track_id in visited:
            return
        visiting.add(track_id)
        for dependency in tracks[track_id].get("dependencies", []):
            if dependency not in tracks:
                errors.append(f"{track_id}: unknown local dependency {dependency!r}")
            else:
                visit(dependency, [*trail, track_id])
        visiting.remove(track_id)
        visited.add(track_id)

    for track_id in tracks:
        visit(track_id, [])


def validate(root: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts = {"tracks": 0, "requirements": 0, "tasks": 0, "local_links": 0}
    try:
        root = root.resolve()
        if not root.is_dir():
            return [f"Repository root is not a directory: {root}"], counts
    except (OSError, RuntimeError, ValueError) as exc:
        return [f"Invalid repository root: {exc}"], counts
    context: dict[str, str] = {}
    for relative in REQUIRED_FILES:
        contents = read_source(root, root / relative, errors)
        if contents is None:
            errors.append(f"Required file unavailable: {relative}")
            continue
        context[relative] = contents
        if not contents.strip():
            errors.append(f"Required file is empty: {relative}")
    if errors:
        return errors, counts

    requirements_text = context["conductor/requirements.md"]
    requirement_ids = REQUIREMENT_HEADING.findall(requirements_text)
    requirements = set(requirement_ids)
    counts["requirements"] = len(requirements)
    if not requirements:
        errors.append("No RQ-XX requirements defined in requirement headings")
    if len(requirements) != len(requirement_ids):
        errors.append("Duplicate canonical requirement headings")

    registry = context["conductor/tracks.md"]
    registered_ids = REGISTRY_LINK.findall(registry)
    tracks: dict[str, dict] = {}
    covered_requirements: set[str] = set()
    track_root = root / "conductor/tracks"
    resolved_tracks = source_directory(root, track_root, errors)
    track_paths = []
    if resolved_tracks is not None:
        try:
            for entry in sorted(resolved_tracks.iterdir()):
                path = track_root / entry.name
                resolved = source_path(root, path, errors)
                if resolved is not None and resolved.is_dir():
                    track_paths.append(path)
                elif resolved is not None and not resolved.exists():
                    errors.append(f"{path.relative_to(root)}: source directory missing or invalid")
        except OSError as exc:
            errors.append(f"conductor/tracks: cannot list source directory: {exc}")
    if not track_paths:
        errors.append("No Conductor tracks found")
    for path in track_paths:
        track_id = path.name
        track_contents = {name: read_source(root, path / name, errors) for name in TRACK_FILES}
        if any(contents is None for contents in track_contents.values()):
            continue
        try:
            metadata = json.loads(track_contents["metadata.json"])
        except (json.JSONDecodeError, UnicodeError) as exc:
            errors.append(f"{track_id}: invalid metadata JSON: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{track_id}: metadata must be a JSON object")
            continue
        missing_fields = [key for key in METADATA_FIELDS if key not in metadata]
        if missing_fields:
            errors.append(f"{track_id}: missing metadata fields: {', '.join(missing_fields)}")
            continue
        if metadata["track_id"] != track_id:
            errors.append(f"{track_id}: metadata track_id does not match its directory")
        invalid_lists = [
            field for field in LIST_FIELDS
            if not isinstance(metadata[field], list)
            or not all(isinstance(item, str) for item in metadata[field])
        ]
        if invalid_lists:
            errors.append(f"{track_id}: expected lists of strings: {', '.join(invalid_lists)}")
            continue
        if "external_dependencies" in metadata and (
            not isinstance(metadata["external_dependencies"], list)
            or not all(isinstance(item, str) for item in metadata["external_dependencies"])
        ):
            errors.append(f"{track_id}: external_dependencies must be a list of strings")
        tracks[track_id] = metadata
        state = metadata["status"]
        if not isinstance(state, str) or state not in STATE_MARKERS:
            errors.append(f"{track_id}: invalid status {state!r}")
            continue
        if registered_ids.count(track_id) != 1:
            errors.append(f"{track_id}: expected exactly one track registry entry")
        else:
            row = next(line for line in registry.splitlines() if f"tracks/{track_id}/index.md" in line)
            if STATE_MARKERS[state] not in row or not re.search(rf"\b{re.escape(state)}\b", row):
                errors.append(f"{track_id}: registry marker/status differs from metadata")
        index = track_contents["index.md"]
        if not re.search(rf"^Status:\s*`?{re.escape(state)}`?\s*$", index, re.MULTILINE):
            errors.append(f"{track_id}: index Status differs from metadata")
        tasks = TASK.findall(track_contents["plan.md"])
        counts["tasks"] += len(tasks)
        if not tasks:
            errors.append(f"{track_id}: no actionable plan tasks")
        if state == "new" and any(marker != " " for marker, _ in tasks):
            errors.append(f"{track_id}: new track contains started/completed/blocked tasks")
        if state == "completed" and any(marker not in {"x", "-"} for marker, _ in tasks):
            errors.append(f"{track_id}: completed track contains unfinished tasks")
        verification = metadata["verification"]
        if not isinstance(verification, dict) or not isinstance(verification.get("commands"), list):
            errors.append(f"{track_id}: verification requires a commands list")
        elif state == "completed" and verification.get("status") != "passed":
            errors.append(f"{track_id}: completed track lacks passed verification")
        for requirement in metadata["requirement_ids"]:
            if requirement not in requirements:
                errors.append(f"{track_id}: unknown requirement {requirement!r}")
            covered_requirements.add(requirement)

    for registered in set(registered_ids) - set(tracks):
        errors.append(f"Registry refers to absent/invalid track {registered!r}")
    for requirement in sorted(requirements - covered_requirements):
        errors.append(f"Requirement has no owning track: {requirement}")
    check_dependency_graph(tracks, errors)
    markdown = [root / "README.md", root / "AGENTS.md"]
    conductor = source_directory(root, root / "conductor", errors)
    if conductor is not None:
        try:
            # Path.rglob does not recurse through directory symlinks. Every
            # yielded source file is separately bounded before check_links reads it.
            markdown.extend(sorted(conductor.rglob("*.md")))
        except OSError as exc:
            errors.append(f"conductor: cannot scan Markdown sources: {exc}")
    counts["local_links"] = check_links(root, markdown, errors)
    counts["tracks"] = len(tracks)
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, counts = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Conductor validation failed: {len(errors)} error(s).")
        return 1
    print(
        "Conductor validation passed: "
        f"{counts['tracks']} tracks, {counts['requirements']} requirements, "
        f"{counts['tasks']} tasks, {counts['local_links']} local links."
    )
    print("This checks project records only; runtime and scientific qualification remain separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
