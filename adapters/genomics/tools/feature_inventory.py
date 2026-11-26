# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Record the frozen legacy source interfaces and plan entries for qualification."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import tomllib
from collections import defaultdict
from hashlib import sha256
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

_SOURCE = Path("src/genomics_microcosting")
_PLANS = {
    "R": "GENOMICS_REFACTORING_PLAN.md",
    "S": "docs/STANDARDIZATION_PLAN.md",
    "Q": "ROBUSTNESS_IMPROVEMENT_PLAN.md",
    "T": "TODO.md",
    "I": ".qoder/quests/implementation_plan.md",
    "E": ".qoder/quests/execute-plan.md",
    "A": ".qoder/quests/repo-mapping-and-gap-analysis.md",
    "C": "IMPLEMENTATION_PLAN_COMPLETION_SUMMARY.md",
    "B": "ROBUSTNESS_IMPROVEMENT_COMPLETION_SUMMARY.md",
}
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def _module(path: Path) -> str:
    parts = path.with_suffix("").parts[1:]
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _exports(
    nodes: list[ast.stmt],
    prefix: str = "",
    *,
    documentation: bool = False,
) -> list[dict[str, Any]]:
    symbols = []
    for node in nodes:
        if not isinstance(node, (*_FUNCTIONS, ast.ClassDef)) or node.name.startswith(
            "_"
        ):
            continue
        name = prefix + node.name
        symbol: dict[str, Any] = {"name": name, "line": node.lineno}
        if documentation:
            symbol["docstring"] = ast.get_docstring(node)
        if isinstance(node, ast.ClassDef):
            symbol["kind"] = "class"
            constructor = next(
                (
                    member
                    for member in node.body
                    if isinstance(member, _FUNCTIONS) and member.name == "__init__"
                ),
                None,
            )
            if constructor is not None:
                symbol["arguments"] = ast.unparse(constructor.args)
            symbols.append(symbol)
            symbols.extend(_exports(node.body, name + ".", documentation=documentation))
        else:
            symbol.update(kind="callable", arguments=ast.unparse(node.args))
            symbols.append(symbol)
    return symbols


def _routes(tree: ast.Module) -> list[dict[str, Any]]:
    return [
        {"line": node.lineno, "route": ast.unparse(node)}
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_url_rule"
    ]


def _markdown_rows(text: str, prefix: str) -> list[dict[str, Any]]:
    rows = []
    in_fence = False
    heading = ""
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        if match := re.match(r"^#{1,6}\s+(.+)", line):
            heading = match[1]
        if marker := re.match(r"^\s*(?:[-*]|[0-9]+\.)\s+(\S.*)", line):
            rows.append(
                {
                    "id": f"{prefix}-{line_number:03}",
                    "line": line_number,
                    "section": heading,
                    "source_text": marker[1],
                }
            )
    return rows


def inventory_features(
    repo: Path, revision: str, issues: list[list[dict[str, Any]]]
) -> dict[str, Any]:
    """Bind candidate features to source coordinates and existing test files."""
    if _git(repo, "rev-parse", "HEAD").decode().strip() != revision:
        raise ValueError("Legacy checkout is not at the frozen revision")
    if _git(repo, "status", "--porcelain", "-z"):
        raise ValueError("Legacy checkout has uncommitted files")

    tracked = [
        Path(path.decode())
        for path in _git(repo, "ls-files", "-z").split(b"\0")
        if path
    ]
    tests = [
        path for path in tracked if path.parts[0] == "tests" and path.suffix == ".py"
    ]
    tested_by: dict[str, set[str]] = defaultdict(set)
    for path in tests:
        tree = ast.parse((repo / path).read_text(encoding="utf-8"), str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                tested_by[node.module].add(path.as_posix())
                for alias in node.names:
                    tested_by[f"{node.module}.{alias.name}"].add(path.as_posix())
            if isinstance(node, ast.Import):
                for alias in node.names:
                    tested_by[alias.name].add(path.as_posix())

    modules = []
    for path in tracked:
        if path.suffix != ".py" or not path.is_relative_to(_SOURCE):
            continue
        source = (repo / path).read_bytes()
        tree = ast.parse(source, str(path))
        module = _module(path)
        modules.append(
            {
                "id": module,
                "source": path.as_posix(),
                "sha256": sha256(source).hexdigest(),
                "symbols": _exports(tree.body),
                "routes": _routes(tree),
                "candidate_tests": sorted(tested_by[module]),
            }
        )

    plans = []
    for prefix, path in _PLANS.items():
        source = (repo / path).read_bytes()
        plans.append(
            {
                "id": prefix,
                "source": path,
                "sha256": sha256(source).hexdigest(),
                "entries": _markdown_rows(source.decode(), prefix),
            }
        )
    for issue in sorted(
        (
            issue
            for page in issues
            for issue in page
            if issue["number"] in {163, 164, 165, 170}
        ),
        key=lambda issue: issue["number"],
    ):
        prefix = f"GH{issue['number']}"
        plans.append(
            {
                "id": prefix,
                "source": issue["html_url"],
                "version": issue["updated_at"],
                "entries": _markdown_rows(issue["body"] or "", prefix),
            }
        )

    project = tomllib.loads((repo / "pyproject.toml").read_text())["project"]
    return {
        "version": 1,
        "legacy_revision": revision,
        "distribution": project["name"],
        "console_scripts": project["scripts"],
        "extras": sorted(project["optional-dependencies"]),
        "configuration": [
            path.as_posix()
            for path in tracked
            if path.parts[0]
            in {"config", "configs", "config.yaml", "pyproject.toml", "uv.lock"}
        ],
        "modules": modules,
        "resources": [
            path.as_posix()
            for path in tracked
            if path.is_relative_to(_SOURCE) and path.suffix != ".py"
        ],
        "source_commands": [
            path.as_posix()
            for path in tracked
            if path.parts[0] in {"scripts", "tools"}
            and path.suffix == ".py"
            and path.name != "__init__.py"
        ],
        "documents": [
            path.as_posix()
            for path in tracked
            if path.suffix == ".md"
            and (path.parts[0] == "docs" or len(path.parts) == 1)
        ],
        "tests": [path.as_posix() for path in tests],
        "plans": plans,
    }


def installed_reference(output: Path) -> dict[str, int]:
    """Generate a reference from all declared public interfaces in the installed wheel."""
    installed = distribution("genomics-microcosting")
    roots = {"genomics_microcosting", "dapane_genomics"}
    paths = sorted(
        path
        for path in installed.files or ()
        if path.suffix == ".py" and path.parts[0] in roots
    )
    if not paths:
        raise ValueError("Install the genomics wheel before building the reference")
    lines = ["# Genomics Python API", "", f"Installed version {installed.version}."]
    counts = {"modules": len(paths), "declarations": 0, "documented": 0}
    for path in paths:
        tree = ast.parse(installed.locate_file(path).read_bytes(), str(path))
        lines.extend(
            (
                "",
                f"## `{_module(Path('src') / path)}`",
                "",
                ast.get_docstring(tree) or "",
            )
        )
        for symbol in _exports(tree.body, documentation=True):
            counts["declarations"] += 1
            if symbol["docstring"]:
                counts["documented"] += 1
            signature = symbol["name"]
            if "arguments" in symbol:
                signature += f"({symbol['arguments']})"
            lines.extend(
                ("", "```python", signature, "```", "", symbol["docstring"] or "")
            )
    with output.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")
    return counts


def main() -> None:
    """Write the frozen inventory or generate the installed public API reference."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("legacy_repo", type=Path, nargs="?")
    parser.add_argument("revision", nargs="?")
    parser.add_argument("frozen_issues", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument(
        "--installed-api", type=Path, help="Write a new Markdown API reference"
    )
    args = parser.parse_args()
    source_args = [args.legacy_repo, args.revision, args.frozen_issues, args.output]
    if args.installed_api is not None:
        if any(argument is not None for argument in source_args):
            parser.error(
                "Select the installed reference or the frozen source inventory"
            )
        print(json.dumps(installed_reference(args.installed_api), sort_keys=True))
        return
    if any(argument is None for argument in source_args):
        parser.error("Provide the legacy repository, revision, issues file and output")
    report = inventory_features(
        args.legacy_repo, args.revision, json.loads(args.frozen_issues.read_bytes())
    )
    args.output.touch(mode=0o600, exist_ok=False)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
