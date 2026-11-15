"""Build the unchanged CLI offline and retain a local, non-attested command receipt."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from .common import file_digest, load, require
from .suite import PROTOCOL, ROOT

REPO = ROOT.parents[1]


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *arguments], text=True).strip()


def runtime_files() -> list[str]:
    return [
        "Cargo.toml",
        "Cargo.lock",
        "rust-toolchain.toml",
        *git("ls-files", "crates").splitlines(),
    ]


def runtime_identity() -> dict[str, str]:
    protocol = load(PROTOCOL)
    files = runtime_files()
    require(
        not git("diff", protocol["runtime_base_sha"], "--", *files),
        "Runtime differs from protocol pin",
    )
    return {name: file_digest(REPO / name) for name in files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    require(not args.receipt.exists(), "Refusing to replace an existing build receipt")
    target = args.target_dir.resolve()
    files_before = runtime_identity()
    compiler = subprocess.check_output(["rustc", "--version", "--verbose"], text=True)
    require(compiler.startswith("rustc 1.99.1 "), "Protocol requires Rust 1.99.1")
    command = [
        "cargo",
        "build",
        "--offline",
        "--locked",
        "--release",
        "-p",
        "dapane-cli",
        "--target-dir",
        str(target),
    ]
    process = subprocess.run(command, cwd=REPO, capture_output=True, text=True, check=False)
    require(process.returncode == 0, f"Locked offline build failed:\n{process.stderr}")
    require(runtime_identity() == files_before, "Runtime sources changed during build")
    executable = target / "release" / ("dapane.exe" if os.name == "nt" else "dapane")
    receipt = {
        "receipt_type": "local-executed-build-not-attested",
        "git_source_sha": git("rev-parse", "HEAD"),
        "runtime_source_sha": load(PROTOCOL)["runtime_base_sha"],
        "runtime_files": files_before,
        "cargo_lock_sha256": file_digest(REPO / "Cargo.lock"),
        "command": command,
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "rustc_verbose": compiler,
        "cargo_version": subprocess.check_output(["cargo", "--version"], text=True).strip(),
        "compiler_environment": {
            key: value
            for key, value in os.environ.items()
            if key
            in {
                "RUSTFLAGS",
                "CARGO_ENCODED_RUSTFLAGS",
                "RUSTC_WRAPPER",
                "RUSTC_WORKSPACE_WRAPPER",
                "CARGO_BUILD_TARGET",
            }
            or key.startswith("CARGO_PROFILE_RELEASE_")
        },
        "binary_sha256": file_digest(executable),
        "binary_bytes": executable.stat().st_size,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"receipt": str(args.receipt), "binary_sha256": receipt["binary_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
