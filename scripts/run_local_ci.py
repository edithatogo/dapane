#!/usr/bin/env python3
"""Run affected CI workflows locally via `act` or native parity checks with profiling."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ci_select = _load_sibling("ci_select")
ci_profile = _load_sibling("ci_profile")


def find_docker_socket() -> str | None:
    """Return a reachable Docker socket/endpoint URI, or None if unavailable."""
    docker_host = os.environ.get("DOCKER_HOST", "").strip()
    candidates: list[Path] = []
    if docker_host.startswith("unix://"):
        candidates.append(Path(docker_host.removeprefix("unix://")))
    elif docker_host and shutil.which("docker"):
        proc = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
        if proc.returncode == 0:
            return docker_host

    candidates.extend(
        [
            Path("/var/run/docker.sock"),
            Path.home() / ".colima/default/docker.sock",
            Path.home() / ".orbstack/run/docker.sock",
        ]
    )
    for sock_path in candidates:
        if sock_path.is_socket():
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            try:
                sock.connect(str(sock_path))
                return f"unix://{sock_path}"
            except OSError:
                pass
            finally:
                sock.close()
    if shutil.which("docker"):
        try:
            proc = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
            if proc.returncode == 0:
                return "default"
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def resolve_runner(requested: str) -> tuple[str, str | None, str]:
    """Resolve `auto`/`act`/`native` into `(effective_runner, docker_host, note)`."""
    act_bin = shutil.which("act")
    docker_host = find_docker_socket()
    if requested == "native":
        return "native", docker_host, "native runner explicitly selected"
    if requested == "act":
        if not act_bin:
            raise RuntimeError("`act` binary not found on PATH (install with `brew install act`).")
        if docker_host is None:
            raise RuntimeError(
                "Docker daemon is not reachable for `act` (start Colima with `colima start` "
                "or start Docker Desktop, or use `--runner auto`/`--runner native`)."
            )
        return "act", docker_host, f"using act with {docker_host}"
    if act_bin and docker_host is not None:
        return "act", docker_host, f"auto-detected act + {docker_host}"
    reasons = []
    if not act_bin:
        reasons.append("`act` not on PATH")
    if docker_host is None:
        reasons.append("Docker/Colima daemon not running")
    return "native", None, "falling back to native parity mode (" + ", ".join(reasons) + ")"


def rust_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    """Ensure pinned Rust 1.99.1 precedes default PATH entries when installed."""
    env = dict(base_env or os.environ)
    if shutil.which("rustup"):
        proc = subprocess.run(
            ["rustup", "which", "rustc", "--toolchain", "1.99.1"],
            capture_output=True,
            text=True,
            env=env,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            toolchain_bin = str(Path(proc.stdout.strip()).resolve().parent)
            env["PATH"] = f"{toolchain_bin}:{env.get('PATH', '')}"
            env["RUSTUP_TOOLCHAIN"] = "1.99.1"
    return env


def ruff_prefix() -> list[str]:
    if shutil.which("ruff"):
        return ["ruff"]
    if shutil.which("uvx"):
        return ["uvx", "--from", "ruff==0.17.4", "ruff"]
    return [sys.executable, "-m", "ruff"]


def resolve_default_base(root: Path, head: str) -> str | None:
    for ref in ("origin/main", "main", f"{head}~1"):
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", ref],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            candidate = proc.stdout.strip()
            head_sha = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", head], text=True
            ).strip()
            if ref != head and candidate != head_sha:
                return candidate
            if ref == f"{head}~1":
                return candidate
    return None


def compute_selection(
    root: Path,
    *,
    staged: bool = False,
    working: bool = False,
    base: str | None = None,
    head: str = "HEAD",
    all_scope: bool = False,
) -> tuple[Any, str, str | None, str]:
    """Return `(Selection, source_kind, resolved_base, resolved_head)`."""
    if all_scope:
        return ci_select.full_selection(root, mode="full"), "all", None, head
    if staged:
        changes, err = ci_select.collect_git_changes(root, staged=True)
        if err:
            return ci_select.full_selection(root, mode="pr", reason=err), "staged", None, head
        return ci_select.select_changes(root, changes, mode="pr"), "staged", None, head
    if working:
        changes, err = ci_select.collect_git_changes(root, working=True)
        if err:
            return ci_select.full_selection(root, mode="pr", reason=err), "working", None, head
        return ci_select.select_changes(root, changes, mode="pr"), "working", None, head

    resolved_base = base or resolve_default_base(root, head)
    if resolved_base is None:
        return (
            ci_select.full_selection(
                root, mode="pr", reason="no base ref available; failing closed to full suite"
            ),
            "all",
            None,
            head,
        )
    changes, err = ci_select.collect_git_changes(root, base=resolved_base, head=head)
    if err:
        return ci_select.full_selection(root, mode="pr", reason=err), "range", resolved_base, head
    return ci_select.select_changes(root, changes, mode="pr"), "range", resolved_base, head


def _tracked_files(root: Path, pattern: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--", pattern],
    )
    return sorted(
        p.decode("utf-8") for p in out.split(b"\x00") if p and (root / p.decode("utf-8")).is_file()
    )


def build_native_plan(
    root: Path,
    sel: Any,
    *,
    source_kind: str,
    base: str | None,
    head: str,
) -> list[tuple[str, list[str], Path]]:
    """Build ordered `(step_name, argv, cwd)` native checks matching `sel`."""
    steps: list[tuple[str, list[str], Path]] = []
    py = sys.executable

    if shutil.which("gitleaks"):
        if source_kind in {"staged", "working"}:
            steps.append(
                (
                    "gitleaks-staged",
                    ["gitleaks", "protect", "--staged", "--redact", "--no-banner"],
                    root,
                )
            )
        elif source_kind == "range" and base:
            steps.append(
                (
                    "gitleaks-history",
                    ["gitleaks", "git", f"--log-opts={base}..{head}", "--redact", "--no-banner"],
                    root,
                )
            )
        else:
            steps.append(
                ("gitleaks-dir", ["gitleaks", "dir", ".", "--redact", "--no-banner"], root)
            )

    if source_kind == "staged":
        if sel.changed_json:
            steps.append(("json-hygiene", [py, "scripts/check_json_hygiene.py", "--staged"], root))
    else:
        json_files = (
            _tracked_files(root, "*.json")
            if source_kind == "all"
            else [p for p in sel.changed_json if (root / p).is_file()]
        )
        if json_files:
            steps.append(("json-hygiene", [py, "scripts/check_json_hygiene.py", *json_files], root))

    py_files = (
        [
            p
            for p in _tracked_files(root, "*.py")
            if p.startswith(
                ("python/", "scripts/", "tests/", "adapters/", "benchmarks/", "bindings/")
            )
        ]
        if source_kind == "all"
        else [p for p in sel.changed_py if (root / p).is_file()]
    )
    if py_files:
        ruff = ruff_prefix()
        steps.append(("ruff-check", [*ruff, "check", *py_files], root))
        steps.append(("ruff-format", [*ruff, "format", "--check", *py_files], root))

    if sel.run_conductor:
        steps.append(("validate-conductor", [py, "scripts/validate_conductor.py"], root))
        steps.append(
            (
                "conductor-tests",
                [
                    py,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "tests",
                    "-p",
                    "test_conductor_validation.py",
                    "-v",
                ],
                root,
            )
        )

    if sel.run_tooling:
        steps.append(
            ("tooling-tests", [py, "-m", "unittest", "discover", "-s", "tests/tooling", "-v"], root)
        )

    if sel.run_release_validate or sel.run_release_heavy:
        steps.append(("release-validate", [py, "scripts/release_assurance.py", "validate"], root))
        steps.append(
            ("release-tests", [py, "-m", "unittest", "discover", "-s", "tests/release", "-v"], root)
        )

    use_nextest = shutil.which("cargo-nextest") is not None
    if sel.run_native:
        steps.append(("rust-fmt", ["cargo", "fmt", "--all", "--check"], root))
        steps.append(
            (
                "rust-clippy",
                [
                    "cargo",
                    "clippy",
                    "--workspace",
                    "--locked",
                    "--all-targets",
                    "--",
                    "-D",
                    "warnings",
                ],
                root,
            )
        )
        if use_nextest:
            cmd = ["cargo", "nextest", "run", "--locked", "--workspace"]
            if sys.platform == "darwin":
                cmd.extend(
                    ["-E", "not test(non_utf8_arguments_do_not_panic_and_file_paths_remain_usable)"]
                )
            steps.append(("rust-nextest", cmd, root))
        else:
            cmd = ["cargo", "test", "--locked", "--workspace"]
            if sys.platform == "darwin":
                cmd.extend(
                    ["--", "--skip", "non_utf8_arguments_do_not_panic_and_file_paths_remain_usable"]
                )
            steps.append(("rust-tests", cmd, root))

    for manifest in sel.rust_adapters:
        label = Path(manifest).parent.name
        steps.append(
            (
                f"{label}-fmt",
                ["cargo", "fmt", "--manifest-path", manifest, "--all", "--check"],
                root,
            )
        )
        if manifest.startswith("adapters/"):
            steps.append(
                (
                    f"{label}-clippy",
                    [
                        "cargo",
                        "clippy",
                        "--manifest-path",
                        manifest,
                        "--locked",
                        "--offline",
                        "--all-targets",
                        "--",
                        "-D",
                        "warnings",
                    ],
                    root,
                )
            )
            if use_nextest:
                steps.append(
                    (
                        f"{label}-nextest",
                        [
                            "cargo",
                            "nextest",
                            "run",
                            "--manifest-path",
                            manifest,
                            "--locked",
                            "--offline",
                            "--all-targets",
                        ],
                        root,
                    )
                )
            else:
                steps.append(
                    (
                        f"{label}-tests",
                        [
                            "cargo",
                            "test",
                            "--manifest-path",
                            manifest,
                            "--locked",
                            "--offline",
                            "--all-targets",
                        ],
                        root,
                    )
                )

    if "observed" in sel.lanes:
        steps.append(
            (
                "observed-python-tests",
                [py, "-m", "unittest", "discover", "-s", "adapters/observed_events/tests", "-v"],
                root,
            )
        )

    if sel.run_decision_provider_d2:
        steps.append(
            (
                "decision-d2-tests",
                [py, "-m", "unittest", "discover", "-s", "tests", "-v"],
                root / "adapters/decision_provider_d2",
            )
        )
        steps.append(
            (
                "decision-d2-compile",
                [py, "-m", "compileall", "-q", "adapters/decision_provider_d2"],
                root,
            )
        )

    return steps


def _run_step(
    name: str,
    cmd: list[str],
    cwd: Path,
    *,
    env: dict[str, str],
    profile_file: Path | None,
) -> int:
    print(
        f"\n==> [{name}] ({cwd.relative_to(ROOT) if cwd != ROOT else '.'}) {' '.join(cmd)}",
        flush=True,
    )
    if profile_file is not None:
        wrapper = [
            sys.executable,
            str(SCRIPTS_DIR / "ci_profile.py"),
            "run",
            "--name",
            name,
            "--profile-file",
            str(profile_file),
            "--cwd",
            str(cwd),
            "--",
            *cmd,
        ]
        return subprocess.run(wrapper, env=env, check=False).returncode
    return subprocess.run(cmd, cwd=cwd, env=env, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--staged", action="store_true")
    scope.add_argument("--working", action="store_true")
    scope.add_argument("--base", help="Base git ref/commit for diff.")
    scope.add_argument("--all", action="store_true", help="Run full suite unconditionally.")
    parser.add_argument("--head", default="HEAD", help="Head git ref/commit with --base.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--runner", choices=["auto", "act", "native"], default="auto")
    parser.add_argument(
        "--workflow", action="append", default=[], help="Filter specific workflow(s) in act mode."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--profile", dest="profile", action="store_true", default=True)
    parser.add_argument("--no-profile", dest="profile", action="store_false")
    parser.add_argument("--profile-output", type=Path)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    sel, source_kind, base, head = compute_selection(
        root,
        staged=args.staged,
        working=args.working,
        base=args.base,
        head=args.head,
        all_scope=args.all,
    )

    try:
        effective_runner, docker_host, runner_note = resolve_runner(args.runner)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    workflows = list(sel.workflows)
    if args.workflow:
        filters = {Path(w).name for w in args.workflow}
        workflows = [wf for wf in workflows if Path(wf).name in filters or wf in args.workflow]

    act_event = "push" if source_kind == "all" else "pull_request"
    artifact_dir = str(root / ".act-artifacts")
    act_commands = [
        ["act", act_event, "-W", wf, "--artifact-server-path", artifact_dir] for wf in workflows
    ]
    native_steps = build_native_plan(root, sel, source_kind=source_kind, base=base, head=head)

    if args.dry_run:
        payload = {
            "source_kind": source_kind,
            "base": base,
            "head": head,
            "runner_requested": args.runner,
            "runner_resolved": effective_runner,
            "runner_note": runner_note,
            "workflows": workflows,
            "act_commands": act_commands,
            "native_steps": [
                {
                    "name": name,
                    "cwd": str(cwd.relative_to(root) if cwd != root else "."),
                    "command": cmd,
                }
                for name, cmd, cwd in native_steps
            ],
            "selection": sel.to_dict(),
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"local-ci: {runner_note} | scope={source_kind} | workflows={workflows or ['none']}")

    profile_file = (
        args.profile_output
        if args.profile_output is not None
        else (root / ".ci-profiles/latest.jsonl" if args.profile else None)
    )
    if profile_file is not None and profile_file.exists():
        profile_file.unlink()

    failed: list[str] = []
    if effective_runner == "act":
        if not workflows:
            print("No affected GitHub Actions workflows to run.")
            return 0
        env = dict(os.environ)
        if docker_host and docker_host.startswith("unix://"):
            env["DOCKER_HOST"] = docker_host
        with tempfile.TemporaryDirectory(prefix="dapane-act-event-") as td:
            event_args: list[str] = []
            if act_event == "pull_request" and base:
                base_sha = subprocess.check_output(
                    ["git", "-C", str(root), "rev-parse", base], text=True
                ).strip()
                head_sha = subprocess.check_output(
                    ["git", "-C", str(root), "rev-parse", head], text=True
                ).strip()
                ev_path = Path(td) / "pr.json"
                ev_path.write_text(
                    json.dumps(
                        {"pull_request": {"base": {"sha": base_sha}, "head": {"sha": head_sha}}}
                    ),
                    encoding="utf-8",
                )
                event_args = ["-e", str(ev_path)]
            for wf in workflows:
                name = f"act:{Path(wf).stem}"
                rc = _run_step(
                    name,
                    [
                        "act",
                        act_event,
                        "-W",
                        wf,
                        "--artifact-server-path",
                        artifact_dir,
                        *event_args,
                    ],
                    root,
                    env=env,
                    profile_file=profile_file,
                )
                if rc != 0:
                    failed.append(name)
    else:
        if not native_steps:
            print("No affected native checks to run.")
        else:
            env = rust_env()
            for name, cmd, cwd in native_steps:
                rc = _run_step(name, cmd, cwd, env=env, profile_file=profile_file)
                if rc != 0:
                    failed.append(name)
            if sel.run_python:
                print(
                    f"\n[info] Python package scope selected (matrix={sel.python_versions}, "
                    f"pytest_targets={' '.join(sel.pytest_targets)}). Wheel parity tests run outside "
                    "checkout via CI or `act` with Docker/Colima.",
                    flush=True,
                )

    if profile_file is not None and profile_file.is_file():
        print()
        print(ci_profile.render_summary(ci_profile.load_records(profile_file), "Local CI Profile"))

    if failed:
        print(f"local-ci FAILED steps: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
