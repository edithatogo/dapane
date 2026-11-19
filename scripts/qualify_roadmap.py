#!/usr/bin/env python3
"""Execute explicit optional-lane checks without promoting release capabilities.

Each command retains its actual outcome. Independent tests still run after style
failures; failed prerequisites block their dependants and fail the final receipt.
Only retained/ is uploaded. Build targets, environments and vendor caches stay in
work/. This helper neither publishes packages nor changes another lane's source.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib
import importlib.metadata
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
RUST = "1.99.1"
LANES = {
    "observed": ("adapters/observed_events",),
    "newborn": ("fixtures/newborn-synthetic", "tests/python/test_newborn_synthetic.py"),
    "decisions": ("adapters/decision_draws",),
    "static": ("benchmarks/static",),
    "mchs": ("adapters/mchs_sources",),
    "bindings": ("bindings/polyglot",),
    "reporting": ("adapters/reporting_profiles",),
}
COVERAGE = {
    "observed": {"observed-tests", "fixture-tests"},
    "newborn": {"newborn-tests"},
    "decisions": {"decisions-tests"},
    "static": {"static-tests", "static-protocol", "static-verify"},
    "mchs": {"mchs-tests", "mchs-installed-smoke"},
    "bindings": {"r-tests", "abi-tests", "packaging-tests", "r-installed", "c-consumer"},
    "reporting": {"reporting-tests", "reporting-intervals"},
}
RUST_MINIMUM = {"observed": 37, "decisions": 37, "r": 1, "abi": 5}
TEST_MINIMUM = {
    **{f"{name}-tests": minimum for name, minimum in RUST_MINIMUM.items()},
    "fixture-tests": 12,
    "newborn-tests": 63,
    "static-tests": 23,
    "mchs-tests": 34,
    "packaging-tests": 4,
    "polyglot-cases": 24,
    "r-installed": 24,
    "reporting-tests": 41,
}
RECORDED_ENVIRONMENT = {
    "RUSTUP_TOOLCHAIN",
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
    "CARGO_BUILD_TARGET",
    "CARGO_TARGET_DIR",
    "CARGO_INCREMENTAL",
    "CARGO_PROFILE_RELEASE_STRIP",
    "CARGO_PROFILE_RELEASE_PANIC",
    "SOURCE_DATE_EPOCH",
    "PYO3_PYTHON",
    "PYTHONHASHSEED",
    "PYTHONDONTWRITEBYTECODE",
    "TZ",
    "LC_ALL",
    "R_HOME",
    "CC",
    "CXX",
    "ASAN_OPTIONS",
    "UBSAN_OPTIONS",
    "DAPANE_TEST_CLI",
    "DAPANE_BENCH_CLI",
    "DAPANE_REPORTING_SOURCES",
}


def required_checks(lane: str) -> set[str]:
    """The aggregate must reject a receipt that silently omits a required stage."""
    common = {
        "source-before",
        "source-after",
        "rust-install",
        "rust-version",
        "cargo-version",
        "python-tools",
        "build-packages",
    }
    style = {"python-lint", "python-format"}
    native = {"native-fetch", "native-build", "native-cli", "native-metadata"}
    wheel = native | {
        "native-wheel",
        "consumer-environment",
        "native-wheel-selection",
        "native-install",
        "native-installed-identity",
        "consumer-dependency-check",
        "consumer-packages",
    }

    def rust(name: str) -> set[str]:
        return {f"{name}-{stage}" for stage in ("fetch", "format", "clippy", "tests", "metadata")}

    specific = {
        "observed": rust("observed") | style | {"fixture-tests"},
        "decisions": rust("decisions"),
        "newborn": wheel | style | {"newborn-test-tools", "newborn-tests"},
        "mchs": wheel
        | style
        | {
            "mchs-source-copy",
            "mchs-wheel",
            "mchs-wheel-selection",
            "mchs-install",
            "mchs-installed-identity",
            "mchs-tests",
            "mchs-installed-smoke",
        },
        "reporting": wheel
        | style
        | {"reporting-sources", "reporting-dependencies", "reporting-tests", "reporting-intervals"},
        "static": style
        | {
            "static-fetch",
            "static-build",
            "static-cli",
            "static-tests",
            "static-protocol",
            "static-verify",
        },
        "bindings": native
        | style
        | rust("r")
        | rust("abi")
        | {
            "r-version",
            "gcc-version",
            "make-version",
            "nm-version",
            "packaging-tests",
            "polyglot-cases",
            "r-stage",
            "r-stage-identity",
            "r-source-build",
            "r-source-artifact",
            "r-install",
            "r-installed",
            "r-library-artifact",
            "abi-build",
            "abi-library",
            "c-compile",
            "c-consumer",
            "abi-exports",
        },
    }
    return common | specific[lane]


class QualificationError(ValueError):
    """A required source, execution or receipt condition was not satisfied."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments], text=True, encoding="utf-8", timeout=60
    ).strip()


def discover(root: Path) -> list[str]:
    return [name for name, paths in LANES.items() if any((root / p).exists() for p in paths)]


def source_identity(root: Path, expected: str) -> dict:
    require(bool(re.fullmatch(r"[0-9a-f]{40}", expected)), "Expected a full source commit")
    sha = git(root, "rev-parse", "HEAD")
    require(sha == expected, "Checkout source does not match the expected source commit")
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    require(not status, f"Qualification requires a clean checkout: {status}")
    files = git(root, "ls-files", "-z").split("\0")
    hashes = {}
    for name in filter(None, files):
        path = root / name
        require(path.is_file() and not path.is_symlink(), f"Non-regular source file: {name}")
        hashes[name] = digest(path)
    require(bool(hashes), "Empty source inventory")
    return {
        "sha": sha,
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "files": hashes,
        "clean": True,
        "epoch": int(git(root, "show", "-s", "--format=%ct", "HEAD")),
    }


def coverage_count(text: str, kind: str, minimum: int = 1) -> int:
    patterns = {
        "unittest": r"Ran (\d+) tests? in ",
        "rust": r"test result: ok\. (\d+) passed;",
        "pytest": r"(?:^|\s)(\d+) passed(?:[,\s]|$)",
        "cases": r"Prepared (\d+) synthetic parity cases",
        "r": r"(\d+) shared cases; host rejection, GC and two interpreter checks passed",
    }
    counts = [int(value) for value in re.findall(patterns[kind], text)]
    count = sum(counts)
    require(count >= minimum, f"Empty/incomplete {kind} coverage: {count}; need {minimum}")
    if kind in {"unittest", "pytest"}:
        require(
            not re.search(r"\b(?:skipped|xfailed|xpassed)\b", text, re.I),
            "Skipped or expected-failure cases do not qualify this suite",
        )
    if kind == "rust":
        require(not re.search(r"; [1-9]\d* ignored;", text), "Ignored native tests")
    return count


class Runner:
    """Record independent checks and explicit prerequisite failures."""

    def __init__(self, root: Path, output: Path, lane: str, expected: str):
        self.root, self.output = root.resolve(), output.resolve()
        require(not self.output.is_relative_to(self.root), "Output must be outside checkout")
        require(not self.output.exists(), "Refusing to overwrite qualification output")
        self.retained = self.output / "retained"
        self.work = self.output / "work"
        self.retained.mkdir(parents=True)
        self.work.mkdir()
        self.artifacts = self.retained / "artifacts"
        self.artifacts.mkdir()
        self.records: dict[str, dict] = {}
        self.report = {
            "format": "dapane-roadmap-qualification/1",
            "lane": lane,
            "expected_source": expected,
            "status": "running",
            "source": None,
            "started_at": datetime.now(UTC).isoformat(),
            "host": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": sys.version,
                "python_executable": sys.executable,
            },
            "scope": "Synthetic standalone candidate checks; no publication or capability promotion",
            "original_polyglot_qualify_sh_executed": False,
            "commands": [],
            "coverage": {},
            "artifacts": {},
        }
        self.env = os.environ.copy() | {
            "RUSTUP_TOOLCHAIN": RUST,
            "CARGO_INCREMENTAL": "0",
            "CARGO_TERM_COLOR": "never",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "TZ": "UTC",
            "LC_ALL": "C.UTF-8",
        }
        self.save()

    def save(self) -> None:
        self.report["commands"] = list(self.records.values())
        write_json(self.retained / "qualification.json", self.report)

    def passed(self, name: str) -> bool:
        return self.records.get(name, {}).get("status") == "passed"

    def step(
        self,
        name: str,
        arguments: list[str] | None = None,
        *,
        action=None,
        needs: tuple[str, ...] = (),
        cwd: Path | None = None,
        env: dict | None = None,
        timeout: int = 900,
        coverage: str | None = None,
        minimum: int = 1,
        stdout: Path | None = None,
        validate=None,
    ) -> bool:
        require(name not in self.records, f"Duplicate check: {name}")
        record = {
            "name": name,
            "arguments": arguments,
            "cwd": str(cwd or self.root),
            "prerequisites": list(needs),
            "status": "running",
            "exit_code": None,
        }
        effective_environment = self.env | (env or {})
        record["environment"] = {
            key: effective_environment[key]
            for key in sorted(RECORDED_ENVIRONMENT & effective_environment.keys())
        }
        self.records[name] = record
        unmet = [item for item in needs if not self.passed(item)]
        if unmet:
            record.update(status="blocked", error=f"Failed or missing prerequisites: {unmet}")
            self.save()
            print(f"{name}: blocked ({', '.join(unmet)})", flush=True)
            return False
        log = self.retained / "logs" / f"{name}.log"
        log.parent.mkdir(exist_ok=True)
        record["log"] = str(log.relative_to(self.retained))
        started = time.monotonic()
        self.save()
        try:
            with log.open("w", encoding="utf-8") as stream:
                if action is not None:
                    value = action()
                    stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
                    record["exit_code"] = 0
                else:
                    require(bool(arguments), "A check needs a command or action")
                    destination = None
                    if stdout is not None:
                        stdout.parent.mkdir(parents=True, exist_ok=True)
                        destination = stdout.open("w", encoding="utf-8")
                        record["stdout"] = str(stdout.relative_to(self.retained))
                    try:
                        process = subprocess.run(
                            arguments,
                            cwd=cwd or self.root,
                            env=effective_environment,
                            stdout=destination or stream,
                            stderr=stream if destination else subprocess.STDOUT,
                            timeout=timeout,
                            check=False,
                        )
                    finally:
                        if destination is not None:
                            destination.close()
                    record["exit_code"] = process.returncode
                    require(process.returncode == 0, f"Command exited {process.returncode}")
            content = log.read_text(encoding="utf-8", errors="replace")
            if stdout is not None:
                content += stdout.read_text(encoding="utf-8", errors="replace")
            if coverage is not None:
                record["test_count"] = coverage_count(content, coverage, minimum)
            if validate is not None:
                validate(content)
            record["status"] = "passed"
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            record.update(status="failed", error=str(error))
            with log.open("a", encoding="utf-8") as stream:
                stream.write(f"\nQUALIFICATION FAILURE: {error}\n")
        record["elapsed_seconds"] = round(time.monotonic() - started, 6)
        self.save()
        print(f"{name}: {record['status']}", flush=True)
        return self.passed(name)

    def finish(self) -> bool:
        self.step(
            "source-after",
            action=lambda: require(
                source_identity(self.root, self.report["expected_source"]) == self.report["source"],
                "Source identity changed during qualification",
            ),
            needs=("source-before",),
        )
        coverage = {
            name: self.records.get(name, {}).get("status", "missing")
            for name in COVERAGE[self.report["lane"]]
        }
        self.report["coverage"] = coverage
        okay = bool(self.records) and all(r["status"] == "passed" for r in self.records.values())
        okay = okay and all(state == "passed" for state in coverage.values())
        self.report["required_checks"] = {
            name: self.records.get(name, {}).get("status", "missing")
            for name in required_checks(self.report["lane"])
        }
        okay = okay and all(state == "passed" for state in self.report["required_checks"].values())
        self.report["status"] = "passed" if okay else "failed"
        self.report["finished_at"] = datetime.now(UTC).isoformat()
        self.report["artifacts"] = artifact_inventory(self.retained)
        self.save()
        return okay


def artifact_inventory(directory: Path) -> dict:
    result = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), f"Retained artifact is a symlink: {path}")
        if path.is_file() and path.name != "qualification.json":
            result[str(path.relative_to(directory))] = {
                "sha256": digest(path),
                "bytes": path.stat().st_size,
            }
    return result


def install_tools(run: Runner, *, native: bool = False, setuptools: bool = False) -> None:
    run.step(
        "rust-install",
        [
            "rustup",
            "toolchain",
            "install",
            RUST,
            "--profile",
            "minimal",
            "--component",
            "rustfmt",
            "--component",
            "clippy",
        ],
        needs=("source-before",),
        timeout=600,
    )
    run.step(
        "rust-version",
        ["rustc", "--version", "--verbose"],
        needs=("rust-install",),
        validate=lambda text: require(f"release: {RUST}\n" in text, "Wrong Rust compiler"),
    )
    run.step("cargo-version", ["cargo", "--version"], needs=("rust-install",))
    packages = ["ruff==0.17.4"]
    if native:
        packages.append("maturin==1.16.0")
    if setuptools:
        packages.append("setuptools==84.2.1")
    run.step(
        "python-tools",
        [sys.executable, "-m", "pip", "install", "--only-binary=:all:", *packages],
        needs=("source-before",),
        timeout=600,
    )
    run.step(
        "build-packages",
        [sys.executable, "-m", "pip", "freeze", "--all"],
        stdout=run.artifacts / "build-python-packages.txt",
    )


def lint(run: Runner, *paths: str) -> None:
    for mode, arguments in (("lint", ["check"]), ("format", ["format", "--check"])):
        run.step(
            f"python-{mode}",
            [sys.executable, "-m", "ruff", *arguments, *paths],
            needs=("python-tools",),
        )


def rust_suite(run: Runner, name: str, manifest: str) -> None:
    target = run.work / f"{name}-target"
    run.step(
        f"{name}-fetch",
        ["cargo", "fetch", "--locked", "--manifest-path", manifest],
        needs=("rust-version",),
    )
    run.step(
        f"{name}-format",
        ["cargo", "fmt", "--manifest-path", manifest, "--all", "--check"],
        needs=("rust-version",),
    )
    common = [
        "--manifest-path",
        manifest,
        "--offline",
        "--locked",
        "--all-targets",
        "--target-dir",
        str(target),
    ]
    run.step(
        f"{name}-clippy",
        ["cargo", "clippy", *common, "--", "-D", "warnings"],
        needs=(f"{name}-fetch",),
        timeout=1200,
    )
    run.step(
        f"{name}-tests",
        ["cargo", "test", *common],
        needs=(f"{name}-fetch",),
        coverage="rust",
        minimum=RUST_MINIMUM[name],
        timeout=1200,
    )
    run.step(
        f"{name}-metadata",
        [
            "cargo",
            "metadata",
            "--manifest-path",
            manifest,
            "--locked",
            "--offline",
            "--format-version",
            "1",
        ],
        needs=(f"{name}-fetch",),
        stdout=run.artifacts / f"{name}-cargo-metadata.json",
    )


def copy_artifact(source: Path, destination: Path) -> dict:
    require(source.is_file() and not source.is_symlink(), f"Missing regular artifact: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    require(digest(source) == digest(destination), "Copied artifact differs")
    return {"path": str(destination), "sha256": digest(destination)}


def one_wheel(directory: Path, prefix: str) -> Path:
    wheels = list(directory.glob(f"{prefix}-*.whl"))
    require(len(wheels) == 1, f"Expected one {prefix} wheel, found {len(wheels)}")
    return wheels[0]


def build_native(run: Runner, *, wheel: bool) -> tuple[Path, Path]:
    target, artifacts = run.work / "native-target", run.artifacts / "native"
    artifacts.mkdir()
    cli = artifacts / "dapane"
    run.step("native-fetch", ["cargo", "fetch", "--locked"], needs=("rust-version",))
    run.step(
        "native-build",
        [
            "cargo",
            "build",
            "--locked",
            "--offline",
            "--release",
            "--no-default-features",
            "-p",
            "dapane-cli",
            "--target-dir",
            str(target),
        ],
        needs=("native-fetch",),
        timeout=1200,
    )
    run.step(
        "native-cli",
        action=lambda: copy_artifact(target / "release/dapane", cli),
        needs=("native-build",),
    )
    if wheel:
        run.step(
            "native-wheel",
            [
                sys.executable,
                "-m",
                "maturin",
                "build",
                "--locked",
                "--offline",
                "--release",
                "--interpreter",
                sys.executable,
                "--out",
                str(artifacts),
            ],
            env={"CARGO_TARGET_DIR": str(target)},
            needs=("native-fetch", "python-tools"),
            timeout=1200,
        )
    run.step(
        "native-metadata",
        ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"],
        needs=("native-fetch",),
        stdout=run.artifacts / "native-cargo-metadata.json",
    )
    return cli, artifacts


def consumer(run: Runner, native_artifacts: Path) -> tuple[Path, Path]:
    environment, cwd = run.work / "consumer", run.work / "consumer-cwd"
    cwd.mkdir(exist_ok=True)
    python = environment / "bin/python"
    run.step(
        "consumer-environment",
        [sys.executable, "-m", "venv", str(environment)],
        needs=("source-before",),
    )
    # Selection runs only after the build, so a missing or ambiguous wheel blocks installation.
    selected: dict[str, Path] = {}
    run.step(
        "native-wheel-selection",
        action=lambda: selected.update(wheel=one_wheel(native_artifacts, "dapane")),
        needs=("native-wheel",),
    )
    wheel = selected.get("wheel", native_artifacts / "missing-wheel")
    run.step(
        "native-install",
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        cwd=cwd,
        needs=("consumer-environment", "native-wheel-selection"),
    )
    run.step(
        "native-installed-identity",
        [
            str(python),
            "-I",
            str(ROOT / "scripts/qualify_roadmap.py"),
            "installed",
            "--wheel",
            str(wheel),
            "--checkout",
            str(run.root),
            "--distribution",
            "dapane",
            "--module",
            "dapane",
            "--receipt",
            str(run.artifacts / "installed-native.json"),
        ],
        cwd=cwd,
        needs=("native-install",),
    )
    return python, cwd


def verify_installed(wheel: Path, checkout: Path, distribution: str, module: str) -> dict:
    package = importlib.import_module(module)
    prefix = Path(sys.prefix).resolve()
    imported = Path(package.__file__).resolve()
    require(
        imported.is_relative_to(prefix) and not imported.is_relative_to(checkout.resolve()),
        "Package was not imported from the isolated installed environment",
    )
    dist = importlib.metadata.distribution(distribution)
    verified = []
    with zipfile.ZipFile(wheel) as archive:
        records = [name for name in archive.namelist() if name.endswith(".dist-info/RECORD")]
        require(len(records) == 1, "Wheel has no unique RECORD")
        for name, encoded, size in csv.reader(io.StringIO(archive.read(records[0]).decode())):
            relative = PurePosixPath(name)
            require(
                not relative.is_absolute() and ".." not in relative.parts, "Unsafe wheel member"
            )
            if not encoded:
                require(name == records[0], "Unhashed wheel payload")
                continue
            algorithm, expected = encoded.split("=", 1)
            require(algorithm == "sha256", "Unsupported wheel digest")
            raw = archive.read(name)
            actual = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b"=").decode()
            require(actual == expected and len(raw) == int(size), "Wheel RECORD digest mismatch")
            installed = Path(dist.locate_file(name)).resolve()
            require(
                installed.is_relative_to(prefix) and installed.is_file(),
                "Installed wheel member is absent or outside the environment",
            )
            require(installed.read_bytes() == raw, f"Installed member differs from wheel: {name}")
            verified.append(name)
    require(
        verified and any(name.startswith(module + "/") for name in verified),
        "Wheel does not contain the imported module",
    )
    verified_paths = {Path(dist.locate_file(name)).resolve() for name in verified}
    require(imported in verified_paths, "Imported module is not one of the verified wheel members")
    result = {
        "distribution": distribution,
        "version": dist.version,
        "module_path": str(imported),
        "wheel_sha256": digest(wheel),
        "verified_members": verified,
        "python": sys.version,
        "prefix": str(prefix),
    }
    if module == "dapane":
        native = Path(importlib.import_module("dapane._native").__file__).resolve()
        require(
            native.is_relative_to(prefix) and not native.is_relative_to(checkout.resolve()),
            "Native extension resolved inside checkout",
        )
        require(native in verified_paths, "Imported native extension is not in the verified wheel")
        require(not dist.requires, "Minimal native wheel acquired runtime dependencies")
        result["native_path"] = str(native)
    return result


def python_lane(run: Runner, lane: str, sources: Path | None) -> None:
    cli, artifacts = build_native(run, wheel=True)
    python, cwd = consumer(run, artifacts)
    if lane == "newborn":
        lint(run, "tests/python/test_newborn_synthetic.py")
        run.step(
            "newborn-test-tools",
            [str(python), "-m", "pip", "install", "pytest==9.2.0", "jsonschema==4.26.0"],
            needs=("native-installed-identity",),
        )
        run.step(
            "newborn-tests",
            [
                str(python),
                "-I",
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "--import-mode=importlib",
                str(run.root / "tests/python/test_newborn_synthetic.py"),
                "--junitxml",
                str(run.artifacts / "newborn-tests.xml"),
                "-q",
            ],
            cwd=cwd,
            needs=("newborn-test-tools",),
            coverage="pytest",
            minimum=63,
        )
    elif lane == "mchs":
        lint(run, "adapters/mchs_sources")
        stage = run.work / "mchs-source"
        run.step(
            "mchs-source-copy",
            action=lambda: copy_tracked(run, "adapters/mchs_sources", stage),
            needs=("source-before",),
        )
        wheels = run.artifacts / "mchs"
        run.step(
            "mchs-wheel",
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(wheels),
                str(stage),
            ],
            needs=("mchs-source-copy", "python-tools"),
        )
        selected: dict[str, Path] = {}
        run.step(
            "mchs-wheel-selection",
            action=lambda: selected.update(wheel=one_wheel(wheels, "dapane_mchs_atlas")),
            needs=("mchs-wheel",),
        )
        wheel = selected.get("wheel", wheels / "missing-wheel")
        run.step(
            "mchs-install",
            [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
            cwd=cwd,
            needs=("native-installed-identity", "mchs-wheel-selection"),
        )
        run.step(
            "mchs-installed-identity",
            [
                str(python),
                "-I",
                str(ROOT / "scripts/qualify_roadmap.py"),
                "installed",
                "--wheel",
                str(wheel),
                "--checkout",
                str(run.root),
                "--distribution",
                "dapane-mchs-atlas",
                "--module",
                "dapane_mchs_atlas",
                "--receipt",
                str(run.artifacts / "installed-mchs.json"),
            ],
            cwd=cwd,
            needs=("mchs-install",),
        )
        run.step(
            "mchs-tests",
            [
                str(python),
                "-I",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(run.root / "adapters/mchs_sources/tests"),
                "-v",
            ],
            cwd=cwd,
            env={"DAPANE_TEST_CLI": str(cli)},
            needs=("mchs-installed-identity", "native-cli"),
            coverage="unittest",
            minimum=34,
        )
        run.step(
            "mchs-installed-smoke",
            [
                str(python),
                "-I",
                str(run.root / "adapters/mchs_sources/tests/installed_smoke.py"),
                "--fixture",
                str(run.root / "adapters/mchs_sources/fixtures/parallel-views.json"),
            ],
            cwd=cwd,
            needs=("mchs-installed-identity",),
        )
    else:
        lint(run, "adapters/reporting_profiles")
        run.step(
            "reporting-sources",
            action=lambda: reporting_sources(run.root, sources),
            needs=("source-before",),
        )
        run.step(
            "reporting-dependencies",
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "--only-binary=:all:",
                "-r",
                str(run.root / "adapters/reporting_profiles/requirements.lock"),
            ],
            needs=("native-installed-identity",),
        )
        run.step(
            "reporting-tests",
            [
                str(python),
                "-m",
                "unittest",
                "discover",
                "-s",
                "adapters/reporting_profiles/tests",
                "-v",
            ],
            env={"DAPANE_REPORTING_SOURCES": str(sources)},
            needs=("reporting-sources", "reporting-dependencies"),
            coverage="unittest",
            minimum=41,
        )
        run.step(
            "reporting-intervals",
            [str(python), "scripts/validate_intervals.py", "--cli", str(cli)],
            needs=("reporting-dependencies", "native-cli"),
        )
    run.step(
        "consumer-dependency-check",
        [str(python), "-m", "pip", "check"],
        needs=("native-installed-identity",),
    )
    run.step(
        "consumer-packages",
        [str(python), "-m", "pip", "freeze", "--all"],
        needs=("consumer-environment",),
        stdout=run.artifacts / "consumer-packages.txt",
    )


def copy_tracked(run: Runner, relative: str, destination: Path) -> dict:
    require(not destination.exists(), "Source staging directory already exists")
    copied = {}
    for name, expected in run.report["source"]["files"].items():
        if name.startswith(relative + "/"):
            path = run.root / name
            require(digest(path) == expected, "Source changed before package staging")
            output = destination / Path(name).relative_to(relative)
            copy_artifact(path, output)
            copied[name] = expected
    require(bool(copied), "No tracked package source")
    return copied


def reporting_sources(root: Path, sources: Path | None) -> dict:
    require(sources is not None and sources.is_dir(), "Reporting source snapshots are missing")
    require(
        not sources.resolve().is_relative_to(root.resolve()),
        "Keep upstream snapshots outside Dapane",
    )
    manifest = json.loads((root / "adapters/reporting_profiles/sources.lock.json").read_text())
    observed = {}
    for name, record in manifest["sources"].items():
        checkout = sources / name
        require(
            git(checkout, "rev-parse", "HEAD") == record["commit"],
            "Upstream source commit mismatch",
        )
        verified = {}
        for relative, entry in record["files"].items():
            path = checkout / relative
            require(path.is_file() and not path.is_symlink(), "Missing regular upstream file")
            raw = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(
                (digest(path), len(raw), blob)
                == (entry["sha256"], entry["bytes"], entry["git_blob"]),
                f"Upstream source bytes differ: {name}/{relative}",
            )
            verified[relative] = entry
        observed[name] = {"commit": record["commit"], "files": verified}
    return observed


def static_lane(run: Runner) -> None:
    lint(run, "benchmarks/static")
    run.step("static-fetch", ["cargo", "fetch", "--locked"], needs=("rust-version",))
    target, receipt, bundle = (
        run.work / "static-target",
        run.artifacts / "static-build.json",
        run.artifacts / "static-results",
    )
    run.step(
        "static-build",
        [
            sys.executable,
            "-m",
            "benchmarks.static.build",
            "--target-dir",
            str(target),
            "--receipt",
            str(receipt),
        ],
        needs=("static-fetch",),
        timeout=1200,
    )
    cli = target / "release/dapane"
    run.step(
        "static-cli",
        action=lambda: copy_artifact(cli, run.artifacts / "static-dapane"),
        needs=("static-build",),
    )
    run.step(
        "static-tests",
        [sys.executable, "-m", "unittest", "discover", "-s", "benchmarks/static/tests", "-v"],
        env={"DAPANE_BENCH_CLI": str(cli)},
        needs=("static-build",),
        coverage="unittest",
        minimum=23,
    )
    run.step(
        "static-protocol",
        [
            sys.executable,
            "-m",
            "benchmarks.static.run",
            "--cli",
            str(cli),
            "--build-receipt",
            str(receipt),
            "--output",
            str(bundle),
        ],
        needs=("static-build",),
        timeout=900,
    )
    run.step(
        "static-verify",
        [sys.executable, "-m", "benchmarks.static.verify", str(bundle)],
        needs=("static-protocol",),
    )


def bindings_lane(run: Runner) -> None:
    lane = run.root / "bindings/polyglot"
    lint(run, "bindings/polyglot/stage_r.py", "bindings/polyglot/tests")
    run.step(
        "r-version",
        ["Rscript", "--vanilla", "-e", "cat(as.character(getRversion()))"],
        validate=lambda text: require(text.strip() == "4.5.0", "Expected exact R 4.5.0"),
    )
    for tool in ("gcc", "make", "nm"):
        run.step(f"{tool}-version", [tool, "--version"])
    rust_suite(run, "r", "bindings/polyglot/r/src/rust/Cargo.toml")
    rust_suite(run, "abi", "bindings/polyglot/abi/Cargo.toml")
    run.step(
        "packaging-tests",
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(lane / "tests"),
            "-p",
            "test_*.py",
            "-v",
        ],
        coverage="unittest",
        minimum=4,
    )
    cli, _ = build_native(run, wheel=False)
    cases = run.artifacts / "polyglot-cases"
    run.step(
        "polyglot-cases",
        [
            sys.executable,
            str(lane / "tests/prepare_cases.py"),
            "--cli",
            str(cli),
            "--output",
            str(cases),
        ],
        needs=("native-cli",),
        coverage="cases",
        minimum=24,
    )
    stage = run.work / "stage/dapaneR"
    run.step(
        "r-stage",
        [sys.executable, str(lane / "stage_r.py"), "--output", str(stage)],
        needs=("r-fetch",),
    )
    run.step("r-stage-identity", action=lambda: staged_r_identity(run, stage), needs=("r-stage",))
    r_cwd, library = run.work / "r-build", run.work / "r-library"
    r_cwd.mkdir()
    library.mkdir()
    run.step(
        "r-source-build",
        ["R", "CMD", "build", "--no-build-vignettes", "--no-manual", str(stage)],
        cwd=r_cwd,
        needs=("r-stage-identity", "r-version"),
    )
    tarball = run.artifacts / "dapaneR_0.1.0.tar.gz"
    run.step(
        "r-source-artifact",
        action=lambda: copy_artifact(r_cwd / tarball.name, tarball),
        needs=("r-source-build",),
    )
    run.step(
        "r-install",
        ["R", "CMD", "INSTALL", "--preclean", f"--library={library}", str(tarball)],
        cwd=r_cwd,
        needs=("r-source-artifact", "rust-version", "gcc-version", "make-version"),
        timeout=1200,
    )
    run.step(
        "r-installed",
        ["Rscript", "--vanilla", str(lane / "tests/installed.R"), str(library), str(cases)],
        cwd=r_cwd,
        needs=("r-install", "polyglot-cases"),
        coverage="r",
        minimum=24,
        timeout=600,
    )
    run.step(
        "r-library-artifact",
        action=lambda: copy_artifact(
            library / "dapaneR/libs/dapaneR.so", run.artifacts / "dapaneR.so"
        ),
        needs=("r-install",),
    )
    abi_target = run.work / "abi-release"
    run.step(
        "abi-build",
        [
            "cargo",
            "build",
            "--offline",
            "--locked",
            "--release",
            "--manifest-path",
            str(lane / "abi/Cargo.toml"),
            "--target-dir",
            str(abi_target),
        ],
        needs=("abi-fetch",),
        timeout=1200,
    )
    native_library = run.artifacts / "libdapane_abi.so"
    run.step(
        "abi-library",
        action=lambda: copy_artifact(abi_target / "release/libdapane_abi.so", native_library),
        needs=("abi-build",),
    )
    executable = run.artifacts / "c-consumer"
    run.step(
        "c-compile",
        [
            "gcc",
            "-std=c11",
            "-O1",
            "-g",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer",
            "-I",
            str(lane / "abi/include"),
            str(lane / "tests/c_consumer.c"),
            "-L",
            str(run.artifacts),
            f"-Wl,-rpath,{run.artifacts}",
            "-ldapane_abi",
            "-pthread",
            "-o",
            str(executable),
        ],
        needs=("abi-library", "gcc-version"),
    )
    run.step(
        "c-consumer",
        [str(executable), str(cases)],
        cwd=r_cwd,
        env={"ASAN_OPTIONS": "detect_leaks=1:halt_on_error=1", "UBSAN_OPTIONS": "halt_on_error=1"},
        needs=("c-compile", "polyglot-cases"),
        timeout=300,
    )
    run.step(
        "abi-exports",
        ["nm", "-D", "--defined-only", str(native_library)],
        needs=("abi-library", "nm-version"),
        stdout=run.artifacts / "abi-exports.txt",
    )
    run.report["binding_execution"] = (
        "Documented stages orchestrated independently; original qualify.sh not invoked; C consumer alone has ASan/UBSan instrumentation"
    )


def staged_r_identity(run: Runner, stage: Path) -> dict:
    receipt = json.loads((stage / "inst/provenance/source.json").read_text())
    require(
        receipt["repository_commit"] == run.report["expected_source"]
        and receipt["source_worktree_clean"],
        "Staged R source provenance does not match clean qualified source",
    )
    expected_core = {
        name: value
        for name, value in run.report["source"]["files"].items()
        if name.startswith("crates/dapane-core/src/")
    }
    require(
        expected_core and receipt["core_source_sha256"] == expected_core,
        "Staged R core source inventory mismatch",
    )
    for name, value in expected_core.items():
        copied = stage / "src/rust/dapane-core" / Path(name).relative_to("crates/dapane-core")
        require(copied.is_file() and digest(copied) == value, "Staged R core source bytes differ")
    expected_binding = {
        str(Path(name).relative_to("bindings/polyglot")): value
        for name, value in run.report["source"]["files"].items()
        if name.startswith("bindings/polyglot/r/")
    }
    require(
        receipt["binding_source_sha256"] == expected_binding,
        "Staged R binding source inventory mismatch",
    )
    require(
        receipt["binding_lock_sha256"] == expected_binding["r/src/rust/Cargo.lock"],
        "Staged R lock differs from qualified source",
    )
    for path in (stage / "inst/provenance").iterdir():
        copy_artifact(path, run.artifacts / "r-provenance" / path.name)
    return receipt


def execute(root: Path, lane: str, output: Path, expected: str, sources: Path | None) -> bool:
    run = Runner(root, output, lane, expected)
    source: dict = {}
    run.step("source-before", action=lambda: source.update(source_identity(root, expected)))
    run.report["source"] = source or None
    if not run.passed("source-before"):
        return run.finish()
    run.env.update(
        SOURCE_DATE_EPOCH=str(source["epoch"]),
        RUSTFLAGS=f"--remap-path-prefix={run.root}=/dapane/source --remap-path-prefix={run.work}=/dapane/roadmap",
    )
    try:
        require(lane in discover(root), "Requested lane is absent from this source")
        require(sys.version_info[:2] == (3, 12), "Standalone host must be CPython 3.12")
        install_tools(
            run, native=lane in {"newborn", "mchs", "reporting"}, setuptools=lane == "mchs"
        )
        if lane == "observed":
            rust_suite(run, "observed", "adapters/observed_events/Cargo.toml")
            lint(run, "adapters/observed_events/tests/test_fixtures.py")
            run.step(
                "fixture-tests",
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "adapters/observed_events/tests",
                    "-p",
                    "test_fixtures.py",
                    "-v",
                ],
                coverage="unittest",
                minimum=12,
            )
        elif lane == "decisions":
            rust_suite(run, "decisions", "adapters/decision_draws/Cargo.toml")
        elif lane == "static":
            static_lane(run)
        elif lane == "bindings":
            bindings_lane(run)
        else:
            python_lane(run, lane, sources)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        message = str(error)
        run.step("orchestration-failure", action=lambda: require(False, message))
    return run.finish()


def receipt_locations(directory: Path, lanes: list[str]) -> list[Path]:
    """Accept the two download-artifact v8 layouts without guessing recursively.

    At the pinned action revision, one matching artifact is extracted directly
    into the requested path even when merge-multiple is false. Multiple matches
    each receive a named subdirectory. A mixed layout must never hide a receipt.
    """
    if not directory.exists():
        return []
    require(directory.is_dir() and not directory.is_symlink(), "Invalid artifact download root")
    entries = list(directory.iterdir())
    flat = directory / "qualification.json"
    if flat.exists():
        require(flat.is_file() and not flat.is_symlink(), "Invalid flat qualification receipt")
        require(len(lanes) == 1, "Flat artifact layout requires exactly one expected lane")
        require(
            not any(path.is_dir() and (path / "qualification.json").exists() for path in entries),
            "Ambiguous mixed flat and nested artifact layout",
        )
        require(
            {path.name for path in entries} <= {"qualification.json", "artifacts", "logs"},
            "Unexpected roots in flat artifact layout",
        )
        return [flat]
    receipts = []
    for path in entries:
        receipt = path / "qualification.json"
        require(
            path.is_dir()
            and not path.is_symlink()
            and receipt.is_file()
            and not receipt.is_symlink(),
            "Unexpected artifact root or missing qualification receipt",
        )
        receipts.append(receipt)
    return receipts


def verify_receipts(
    root: Path,
    directory: Path,
    lanes: list[str],
    expected: str,
    jobs: dict | None = None,
    *,
    expected_lanes: list[str] | None = None,
) -> dict:
    require(
        len(lanes) == len(set(lanes)) and set(lanes) <= set(LANES),
        "Invalid expected lane inventory",
    )
    discovered = discover(root)
    if expected_lanes is None:
        require(lanes == discovered, "Declared lane coverage differs from this source")
    else:
        require(
            len(expected_lanes) == len(set(expected_lanes))
            and set(expected_lanes) <= set(discovered),
            "Selective expected lanes contain unknown or absent lane",
        )
        require(
            lanes == expected_lanes, "Declared lane coverage differs from selective change scope"
        )
    source = source_identity(root, expected)
    if jobs is not None:
        for name in ("discovery", "controls"):
            require(
                jobs.get(name, {}).get("result") == "success", f"Required job did not pass: {name}"
            )
        require(
            jobs.get("qualify", {}).get("result") == ("success" if lanes else "skipped"),
            "Lane matrix failed, was cancelled or was unexpectedly skipped",
        )
    receipts = receipt_locations(directory, lanes)
    found = {}
    for path in receipts:
        record = json.loads(path.read_text())
        lane = record.get("lane")
        require(lane in lanes and lane not in found, "Unknown or duplicate lane receipt")
        require(record.get("format") == "dapane-roadmap-qualification/1", "Unknown receipt format")
        require(
            record.get("expected_source") == expected and record.get("source") == source,
            "Receipt source identity differs from the checked-out source",
        )
        require(record.get("status") == "passed", f"Lane did not pass: {lane}")
        commands = record.get("commands", [])
        require(
            commands and len({r["name"] for r in commands}) == len(commands),
            "Empty/duplicate commands",
        )
        require(
            all(r.get("status") == "passed" and r.get("exit_code") == 0 for r in commands),
            "Failed, blocked or unexecuted command in passing receipt",
        )
        named = {r["name"]: r for r in commands}
        required = required_checks(lane)
        require(required <= named.keys(), "Missing mandatory qualification command")
        require(
            commands[0]["name"] == "source-before" and commands[-1]["name"] == "source-after",
            "Source checks must surround all execution",
        )
        preceding = set()
        for command in commands:
            prerequisites = command.get("prerequisites")
            require(
                isinstance(prerequisites, list) and len(prerequisites) == len(set(prerequisites)),
                "Invalid prerequisite inventory",
            )
            require(
                all(
                    name in preceding and named[name]["status"] == "passed"
                    for name in prerequisites
                ),
                "Missing, failed or out-of-order command prerequisite",
            )
            preceding.add(command["name"])
        require(
            record.get("required_checks") == dict.fromkeys(required, "passed"),
            "Incomplete mandatory-check receipt",
        )
        for name, minimum in TEST_MINIMUM.items():
            if name in required:
                count = named[name].get("test_count")
                require(
                    type(count) is int and count >= minimum,
                    f"Missing or incomplete executed test count: {name}",
                )
        require(COVERAGE[lane] <= named.keys(), "Missing required lane coverage")
        require(
            record.get("coverage") == dict.fromkeys(COVERAGE[lane], "passed"),
            "Incomplete coverage receipt",
        )
        require(any(r.get("test_count", 0) > 0 for r in commands), "No executed test coverage")
        inventory = artifact_inventory(path.parent)
        require(
            inventory and record.get("artifacts") == inventory,
            "Retained artifact inventory mismatch",
        )
        found[lane] = {
            "commands": len(commands),
            "test_counts": {
                name: r["test_count"] for name, r in named.items() if "test_count" in r
            },
        }
    require(set(found) == set(lanes), "Missing lane receipts")
    return {
        "status": "passed",
        "source": expected,
        "tree": source["tree"],
        "lanes": found,
        "scope": "Only present standalone candidates; no upstream/native-import/Julia/publication promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    discovery = commands.add_parser("discover")
    discovery.add_argument("--github-output", type=Path)
    run = commands.add_parser("run")
    run.add_argument("--lane", choices=sorted(LANES), required=True)
    run.add_argument("--expected-source", required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--reporting-sources", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--expected-source", required=True)
    verify.add_argument("--directory", type=Path, required=True)
    verify.add_argument("--lanes", required=True)
    verify.add_argument("--expected-lanes")
    verify.add_argument("--job-results")
    installed = commands.add_parser("installed")
    installed.add_argument("--wheel", type=Path, required=True)
    installed.add_argument("--checkout", type=Path, required=True)
    installed.add_argument("--distribution", required=True)
    installed.add_argument("--module", required=True)
    installed.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "discover":
        lanes = discover(ROOT)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                stream.write("lanes=" + json.dumps(lanes, separators=(",", ":")) + "\n")
        print(json.dumps({"lanes": lanes}))
    elif args.command == "run":
        return (
            0
            if execute(ROOT, args.lane, args.output, args.expected_source, args.reporting_sources)
            else 1
        )
    elif args.command == "verify":
        print(
            json.dumps(
                verify_receipts(
                    ROOT,
                    args.directory,
                    json.loads(args.lanes),
                    args.expected_source,
                    json.loads(args.job_results) if args.job_results else None,
                    expected_lanes=(
                        json.loads(args.expected_lanes) if args.expected_lanes else None
                    ),
                ),
                indent=2,
            )
        )
    else:
        receipt = verify_installed(args.wheel, args.checkout, args.distribution, args.module)
        write_json(args.receipt, receipt)
        print('{"status": "verified"}')
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}), file=sys.stderr)
        raise SystemExit(1) from error
