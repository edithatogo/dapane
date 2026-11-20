#!/usr/bin/env python3
"""Select affected CI workflows, test suites, Rust crates, and roadmap lanes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LANE_ORDER: tuple[str, ...] = (
    "observed",
    "newborn",
    "decisions",
    "static",
    "mchs",
    "bindings",
    "reporting",
)

LANE_PATHS: dict[str, tuple[str, ...]] = {
    "observed": ("adapters/observed_events",),
    "newborn": ("fixtures/newborn-synthetic", "tests/python/test_newborn_synthetic.py"),
    "decisions": ("adapters/decision_draws",),
    "static": ("benchmarks/static",),
    "mchs": ("adapters/mchs_sources",),
    "bindings": ("bindings/polyglot",),
    "reporting": ("adapters/reporting_profiles",),
}

STANDALONE_CARGO_MANIFESTS: tuple[str, ...] = (
    "adapters/observed_events/Cargo.toml",
    "adapters/decision_draws/Cargo.toml",
    "adapters/process_models/Cargo.toml",
    "bindings/polyglot/abi/Cargo.toml",
    "bindings/polyglot/r/src/rust/Cargo.toml",
)

ALL_PYTHON_VERSIONS: list[str] = ["3.12", "3.13", "3.14", "3.15"]
PR_PYTHON_VERSIONS: list[str] = ["3.12", "3.15"]

CORE_EXACT_FILES = frozenset({"Cargo.toml", "Cargo.lock", "rust-toolchain.toml"})
CORE_PREFIXES = ("crates/dapane-core/", "crates/dapane-cli/", "schemas/")
PACKAGING_EXACT_FILES = frozenset({"pyproject.toml", "requirements-dev.txt"})
MATRIX_TRIGGERS = frozenset(
    {
        "pyproject.toml",
        "requirements-dev.txt",
        "rust-toolchain.toml",
        ".github/workflows/runtime.yml",
    }
)
CONDUCTOR_EXACT_FILES = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "scripts/validate_conductor.py",
        "tests/test_conductor_validation.py",
        ".github/workflows/conductor.yml",
    }
)
JSON_HYGIENE_FILES = frozenset(
    {"scripts/check_json_hygiene.py", "tests/tooling/test_json_hygiene.py"}
)
CI_TOOLING_FILES = frozenset(
    {
        "scripts/ci_select.py",
        "scripts/ci_profile.py",
        "scripts/run_local_ci.py",
        "tests/tooling/test_ci_select.py",
        "tests/tooling/test_ci_profile.py",
        "tests/tooling/test_run_local_ci.py",
        ".config/nextest.toml",
        ".actrc",
        ".pre-commit-config.yaml",
    }
)
KERNEL_TOOLING_FILES = frozenset(
    {
        "scripts/validate_contract.py",
        "scripts/validate_intervals.py",
        "scripts/qualify_kernel.py",
        "scripts/verify_run_bundle.py",
        "scripts/benchmark_cli.py",
        "tests/tooling/test_qualify_kernel.py",
    }
)
ROADMAP_TOOLING_FILES = frozenset(
    {
        "scripts/qualify_roadmap.py",
        "tests/tooling/test_roadmap_qualification.py",
        ".github/workflows/roadmap-lanes.yml",
    }
)
PROVIDER_CONSUMER_FILES = frozenset(
    {
        "docs/provider-consumers.lock.json",
        "scripts/verify_provider_consumers.py",
        ".github/workflows/provider-consumers.yml",
    }
)
RELEASE_EXACT_FILES = frozenset(
    {
        "scripts/release_assurance.py",
        "scripts/distribution_notices.py",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.txt",
        "deny.toml",
        "requirements-release.txt",
        ".github/workflows/release-assurance.yml",
    }
)
RELEASE_PREFIXES = ("release/", "licenses/", "tests/release/")


@dataclass
class ChangeRecord:
    """Normalized repository path change with git status code."""

    path: str
    status: str = "M"


@dataclass
class Selection:
    """Computed execution scope for local hooks, local runner, and CI workflows."""

    mode: str
    changed_files: list[str] = field(default_factory=list)
    changed_json: list[str] = field(default_factory=list)
    changed_py: list[str] = field(default_factory=list)
    run_native: bool = False
    run_python: bool = False
    full_python_matrix: bool = False
    python_versions: list[str] = field(default_factory=list)
    pytest_targets: list[str] = field(default_factory=list)
    run_process_models: bool = False
    run_decision_provider_d2: bool = False
    run_provider_consumers: bool = False
    run_release_validate: bool = False
    run_release_heavy: bool = False
    run_conductor: bool = False
    run_tooling: bool = False
    lanes: list[str] = field(default_factory=list)
    rust_adapters: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)
    fail_closed_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "changed_files": self.changed_files,
            "changed_json": self.changed_json,
            "changed_py": self.changed_py,
            "run_native": self.run_native,
            "run_python": self.run_python,
            "full_python_matrix": self.full_python_matrix,
            "python_versions": self.python_versions,
            "pytest_targets": self.pytest_targets,
            "run_process_models": self.run_process_models,
            "run_decision_provider_d2": self.run_decision_provider_d2,
            "run_provider_consumers": self.run_provider_consumers,
            "run_release_validate": self.run_release_validate,
            "run_release_heavy": self.run_release_heavy,
            "run_conductor": self.run_conductor,
            "run_tooling": self.run_tooling,
            "lanes": self.lanes,
            "rust_adapters": self.rust_adapters,
            "workflows": self.workflows,
            "fail_closed_reason": self.fail_closed_reason,
        }


def normalize_path(raw: str) -> str:
    return raw.replace("\\", "/").lstrip("./")


def present_lanes(root: Path) -> list[str]:
    return [
        lane
        for lane in LANE_ORDER
        if any((root / candidate).exists() for candidate in LANE_PATHS[lane])
    ]


def _present_manifests(root: Path, candidates: set[str] | tuple[str, ...]) -> list[str]:
    order = {manifest: idx for idx, manifest in enumerate(STANDALONE_CARGO_MANIFESTS)}
    filtered = [m for m in candidates if (root / m).is_file()]
    return sorted(filtered, key=lambda m: (order.get(m, 999), m))


def _workflows_for(sel: Selection) -> list[str]:
    wfs: list[str] = []
    if sel.run_conductor:
        wfs.append(".github/workflows/conductor.yml")
    if sel.run_native or sel.run_python or sel.run_tooling:
        wfs.append(".github/workflows/runtime.yml")
    if sel.run_process_models:
        wfs.append(".github/workflows/process-models.yml")
    if sel.run_decision_provider_d2:
        wfs.append(".github/workflows/decision-provider-d2.yml")
    if sel.lanes:
        wfs.append(".github/workflows/roadmap-lanes.yml")
    if sel.run_provider_consumers:
        wfs.append(".github/workflows/provider-consumers.yml")
    if sel.run_release_heavy or sel.run_release_validate:
        wfs.append(".github/workflows/release-assurance.yml")
    return wfs


def full_selection(
    root: Path,
    *,
    mode: str = "full",
    changed_files: list[str] | None = None,
    reason: str | None = None,
) -> Selection:
    files = sorted({normalize_path(p) for p in (changed_files or []) if p})
    sel = Selection(
        mode=mode,
        changed_files=files,
        changed_json=[p for p in files if p.endswith(".json")],
        changed_py=[p for p in files if p.endswith(".py")],
        run_native=True,
        run_python=True,
        full_python_matrix=True,
        python_versions=list(ALL_PYTHON_VERSIONS),
        pytest_targets=["tests/python"],
        run_process_models=True,
        run_decision_provider_d2=True,
        run_provider_consumers=True,
        run_release_validate=True,
        run_release_heavy=True,
        run_conductor=True,
        run_tooling=True,
        lanes=present_lanes(root),
        rust_adapters=_present_manifests(root, STANDALONE_CARGO_MANIFESTS),
        fail_closed_reason=reason,
    )
    sel.workflows = _workflows_for(sel)
    return sel


def _parse_name_status_z(raw: bytes) -> list[ChangeRecord]:
    tokens = [part.decode("utf-8", errors="surrogateescape") for part in raw.split(b"\x00") if part]
    records: list[ChangeRecord] = []
    idx = 0
    while idx < len(tokens):
        status = tokens[idx]
        idx += 1
        code = status[:1]
        if code in {"R", "C"} and idx + 1 < len(tokens):
            old_path = normalize_path(tokens[idx])
            new_path = normalize_path(tokens[idx + 1])
            idx += 2
            records.append(ChangeRecord(path=old_path, status=code))
            records.append(ChangeRecord(path=new_path, status=code))
        elif idx < len(tokens):
            records.append(ChangeRecord(path=normalize_path(tokens[idx]), status=code))
            idx += 1
    return records


def collect_git_changes(
    root: Path,
    *,
    staged: bool = False,
    working: bool = False,
    base: str | None = None,
    head: str = "HEAD",
) -> tuple[list[ChangeRecord], str | None]:
    try:
        if staged:
            out = subprocess.check_output(
                ["git", "-C", str(root), "diff", "--cached", "--name-status", "-z"],
                stderr=subprocess.PIPE,
            )
            return _parse_name_status_z(out), None
        if working:
            out = subprocess.check_output(
                ["git", "-C", str(root), "diff", "--name-status", "-z", "HEAD"],
                stderr=subprocess.PIPE,
            )
            records = _parse_name_status_z(out)
            untracked = subprocess.check_output(
                ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard", "-z"],
                stderr=subprocess.PIPE,
            )
            for item in untracked.split(b"\x00"):
                if item:
                    records.append(
                        ChangeRecord(path=normalize_path(item.decode("utf-8")), status="A")
                    )
            return records, None
        if base:
            for spec in (f"{base}...{head}", f"{base}..{head}"):
                proc = subprocess.run(
                    ["git", "-C", str(root), "diff", "--name-status", "-z", spec],
                    capture_output=True,
                )
                if proc.returncode == 0:
                    return _parse_name_status_z(proc.stdout), None
            return [], f"Unable to resolve git diff between {base} and {head}"
    except (OSError, subprocess.SubprocessError) as exc:
        return [], f"Git inspection failed: {exc}"
    return [], "No diff source supplied"


def select_changes(
    root: Path,
    changes: list[ChangeRecord],
    *,
    mode: str = "pr",
) -> Selection:
    if mode == "full":
        return full_selection(root, mode="full", changed_files=[c.path for c in changes])

    available = set(present_lanes(root))
    lanes: set[str] = set()
    adapters: set[str] = set()
    specific_pytest_files: set[str] = set()
    broad_python = False

    files = sorted({normalize_path(c.path) for c in changes if c.path})
    sel = Selection(
        mode=mode,
        changed_files=files,
        changed_json=[p for p in files if p.endswith(".json")],
        changed_py=[p for p in files if p.endswith(".py")],
    )

    for rec in changes:
        path = normalize_path(rec.path)
        if not path:
            continue

        if rec.status in {"A", "D", "R", "C"}:
            sel.run_conductor = True

        # Specific single-lane fixtures before shared fixtures/ rule.
        if path.startswith("fixtures/newborn-synthetic/"):
            lanes.add("newborn")
            sel.run_python = True
            specific_pytest_files.add("tests/python/test_newborn_synthetic.py")
            continue

        if path == "tests/python/test_newborn_synthetic.py":
            lanes.add("newborn")
            sel.run_python = True
            sel.run_provider_consumers = True
            sel.run_release_heavy = True
            specific_pytest_files.add(path)
            continue

        if path.startswith("tests/python/"):
            sel.run_python = True
            sel.run_provider_consumers = True
            sel.run_release_heavy = True
            name = Path(path).name
            if (
                name.startswith("test_")
                and path.endswith(".py")
                and rec.status not in {"D", "R"}
                and (root / path).is_file()
            ):
                specific_pytest_files.add(path)
            else:
                broad_python = True
            continue

        if (
            path in CORE_EXACT_FILES
            or path.startswith(CORE_PREFIXES)
            or path.startswith("fixtures/")
        ):
            sel.run_native = True
            sel.run_python = True
            sel.run_process_models = True
            sel.run_provider_consumers = True
            sel.run_release_heavy = True
            lanes.update({"newborn", "decisions", "static", "mchs", "bindings", "reporting"})
            adapters.add("adapters/decision_draws/Cargo.toml")
            if path == "rust-toolchain.toml":
                sel.full_python_matrix = True
                sel.run_tooling = True
            if path in {"Cargo.toml", "Cargo.lock"} or path.startswith("schemas/"):
                sel.run_release_validate = True
            continue

        if (
            path.startswith("crates/dapane-python/")
            or path.startswith("python/")
            or path in PACKAGING_EXACT_FILES
        ):
            sel.run_python = True
            sel.run_process_models = True
            sel.run_provider_consumers = True
            sel.run_release_heavy = True
            lanes.update({"newborn", "mchs", "reporting"})
            if path.startswith("crates/dapane-python/"):
                sel.run_native = True
                sel.full_python_matrix = True
            if path in MATRIX_TRIGGERS:
                sel.full_python_matrix = True
            if path in PACKAGING_EXACT_FILES:
                sel.run_release_validate = True
                if path == "requirements-dev.txt":
                    sel.run_decision_provider_d2 = True
            continue

        if path.startswith("power_platform/"):
            sel.run_python = True
            continue

        if path.startswith("adapters/observed_events/"):
            lanes.add("observed")
            adapters.add("adapters/observed_events/Cargo.toml")
            continue

        if path.startswith("adapters/decision_draws/"):
            lanes.add("decisions")
            adapters.add("adapters/decision_draws/Cargo.toml")
            continue

        if path.startswith("adapters/process_models/"):
            sel.run_process_models = True
            adapters.add("adapters/process_models/Cargo.toml")
            continue

        if path.startswith("adapters/decision_provider_d2/"):
            sel.run_decision_provider_d2 = True
            continue

        if path.startswith("adapters/mchs_sources/"):
            lanes.add("mchs")
            continue

        if path.startswith("adapters/reporting_profiles/"):
            lanes.add("reporting")
            continue

        if path.startswith("benchmarks/static/"):
            lanes.add("static")
            continue

        if path.startswith("bindings/polyglot/"):
            lanes.add("bindings")
            adapters.add("bindings/polyglot/abi/Cargo.toml")
            adapters.add("bindings/polyglot/r/src/rust/Cargo.toml")
            continue

        if (
            path.startswith("conductor/")
            or path in CONDUCTOR_EXACT_FILES
            or (path.startswith("docs/") and path.endswith(".md"))
        ):
            sel.run_conductor = True
            continue

        if path in JSON_HYGIENE_FILES:
            sel.run_tooling = True
            sel.run_native = True
            sel.run_process_models = True
            sel.run_decision_provider_d2 = True
            continue

        if path in CI_TOOLING_FILES or path.startswith(".githooks/"):
            sel.run_tooling = True
            sel.run_native = True
            continue

        if path in KERNEL_TOOLING_FILES:
            sel.run_tooling = True
            sel.run_native = True
            continue

        if path in ROADMAP_TOOLING_FILES:
            sel.run_tooling = True
            lanes.update(available)
            continue

        if path in PROVIDER_CONSUMER_FILES:
            sel.run_provider_consumers = True
            sel.run_release_heavy = True
            if path in {
                "docs/provider-consumers.lock.json",
                "scripts/verify_provider_consumers.py",
            }:
                sel.run_release_validate = True
            continue

        if path in RELEASE_EXACT_FILES or path.startswith(RELEASE_PREFIXES):
            sel.run_release_validate = True
            sel.run_release_heavy = True
            continue

        if path == ".github/workflows/runtime.yml":
            sel.run_native = True
            sel.run_python = True
            sel.full_python_matrix = True
            continue

        if path == ".github/workflows/process-models.yml":
            sel.run_process_models = True
            continue

        if path == ".github/workflows/decision-provider-d2.yml":
            sel.run_decision_provider_d2 = True
            continue

        if path.endswith(".py") and path.startswith(("scripts/", "tests/tooling/")):
            sel.run_tooling = True
            sel.run_native = True

    sel.lanes = [lane for lane in LANE_ORDER if lane in (lanes & available)]
    sel.rust_adapters = _present_manifests(root, adapters)
    if sel.run_python:
        sel.python_versions = (
            list(ALL_PYTHON_VERSIONS) if sel.full_python_matrix else list(PR_PYTHON_VERSIONS)
        )
        if (
            not broad_python
            and specific_pytest_files
            and not sel.run_native
            and not sel.full_python_matrix
        ):
            sel.pytest_targets = sorted(specific_pytest_files)
        else:
            sel.pytest_targets = ["tests/python"]
    sel.workflows = _workflows_for(sel)
    return sel


def write_github_output(path: Path, sel: Selection) -> None:
    lines = [
        f"run_native={'true' if sel.run_native else 'false'}",
        f"run_python={'true' if sel.run_python else 'false'}",
        f"run_process_models={'true' if sel.run_process_models else 'false'}",
        f"run_decision_provider_d2={'true' if sel.run_decision_provider_d2 else 'false'}",
        f"run_provider_consumers={'true' if sel.run_provider_consumers else 'false'}",
        f"run_release_validate={'true' if sel.run_release_validate else 'false'}",
        f"run_release_heavy={'true' if sel.run_release_heavy else 'false'}",
        f"run_conductor={'true' if sel.run_conductor else 'false'}",
        f"run_tooling={'true' if sel.run_tooling else 'false'}",
        "python_versions=" + json.dumps(sel.python_versions, separators=(",", ":")),
        "pytest_targets=" + " ".join(sel.pytest_targets),
        "lanes=" + json.dumps(sel.lanes, separators=(",", ":")),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        for line in lines:
            stream.write(line + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["pr", "full"], default="pr")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--working", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--base", help="Base git ref/commit for diff.")
    parser.add_argument("--head", default="HEAD", help="Head git ref/commit for diff.")
    parser.add_argument("--files", nargs="*", help="Explicit changed repo-relative paths.")
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if args.all or args.mode == "full":
        changes: list[ChangeRecord] = []
        if args.staged or args.working or args.base:
            changes, _ = collect_git_changes(
                root, staged=args.staged, working=args.working, base=args.base, head=args.head
            )
        elif args.files:
            changes = [ChangeRecord(path=normalize_path(p)) for p in args.files]
        sel = full_selection(root, mode="full", changed_files=[c.path for c in changes])
    elif args.files is not None:
        records: list[ChangeRecord] = []
        for p in args.files:
            norm = normalize_path(p)
            status = "M" if (root / norm).exists() else "D"
            records.append(ChangeRecord(path=norm, status=status))
        sel = select_changes(root, records, mode="pr")
    else:
        changes, error = collect_git_changes(
            root, staged=args.staged, working=args.working, base=args.base, head=args.head
        )
        if error is not None:
            print(f"ci_select: failing closed ({error})", file=sys.stderr)
            sel = full_selection(root, mode="pr", reason=error)
        else:
            sel = select_changes(root, changes, mode="pr")

    if args.github_output:
        write_github_output(args.github_output, sel)
    if args.json or not args.github_output:
        print(json.dumps(sel.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
