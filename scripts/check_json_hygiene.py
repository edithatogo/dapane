#!/usr/bin/env python3
"""Check JSON files or staged JSON blobs for structural and secret-hygiene issues."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

RISKY_KEY_RE = re.compile(
    r"(?:secret|token|password|api[_-]?key|private[_-]?key|\bkey\b)",
    re.IGNORECASE,
)
HEX_64_RE = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")


class JsonHygieneError(ValueError):
    """Raised when JSON decoding or key/digest hygiene checks fail."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JsonHygieneError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> Any:
    raise JsonHygieneError(f"non-finite JSON constant: {value}")


def _scan_value(value: Any, path: str, *, risky_ancestor: bool = False) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}/{key}"
            is_risky = risky_ancestor or bool(RISKY_KEY_RE.search(key))
            findings.extend(_scan_value(item, child_path, risky_ancestor=is_risky))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            findings.extend(_scan_value(item, f"{path}[{idx}]", risky_ancestor=risky_ancestor))
    elif isinstance(value, str) and risky_ancestor and HEX_64_RE.search(value):
        findings.append(
            f"{path}: risky key pattern paired with 64-character hex string "
            "(triggers Gitleaks generic-api-key)"
        )
    return findings


def validate_json_bytes(raw: bytes, label: str = "<input>") -> None:
    """Validate UTF-8 decoding, strict JSON syntax, and risky key+digest pairs."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise JsonHygieneError(f"{label}: invalid UTF-8: {exc}") from exc
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
    except json.JSONDecodeError as exc:
        raise JsonHygieneError(f"{label}: invalid JSON: {exc}") from exc
    findings = _scan_value(parsed, "$")
    if findings:
        raise JsonHygieneError(f"{label}: " + "; ".join(findings))


def staged_json_paths(repo_root: Path) -> list[str]:
    """Return staged Added/Copied/Modified/Renamed *.json paths relative to repo_root."""
    output = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
        cwd=repo_root,
    )
    paths = [entry.decode("utf-8") for entry in output.split(b"\x00") if entry]
    return [path for path in paths if path.endswith(".json")]


def read_staged_blob(repo_root: Path, rel_path: str) -> bytes:
    """Read staged index bytes for a relative path."""
    return subprocess.check_output(["git", "show", f":{rel_path}"], cwd=repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Read staged *.json blobs from the git index.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used with --staged (defaults to current working directory).",
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Explicit JSON file paths to inspect.")
    args = parser.parse_args(argv)

    if not args.staged and not args.paths:
        parser.error("supply --staged or one or more JSON file paths")

    checked = 0
    errors: list[str] = []

    if args.staged:
        for rel_path in staged_json_paths(args.root):
            checked += 1
            try:
                validate_json_bytes(read_staged_blob(args.root, rel_path), label=rel_path)
            except (JsonHygieneError, subprocess.CalledProcessError) as exc:
                errors.append(str(exc))

    for file_path in args.paths:
        checked += 1
        try:
            validate_json_bytes(file_path.read_bytes(), label=str(file_path))
        except (JsonHygieneError, OSError) as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"JSON hygiene passed ({checked} file(s) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
