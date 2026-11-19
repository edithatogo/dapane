#!/usr/bin/env python3
"""Stage a self-contained R source package from the current Rust source tree.

Only generated output is materialised: the core's Rust bytes are copied without
edits, workspace manifest inheritance is resolved, and Cargo vendors the locked
registry graph. No source checkout manifest, lockfile or numerical code is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[1]


def toml_value(value):
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{key} = {toml_value(item)}" for key, item in value.items()) + " }"
    return json.dumps(value, ensure_ascii=False)


def resolved_core_manifest() -> str:
    core = tomllib.loads((ROOT / "crates/dapane-core/Cargo.toml").read_text())
    workspace = tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"]
    for section, values in core.items():
        for key, value in list(values.items()):
            if isinstance(value, dict) and value.get("workspace") is True:
                if set(value) != {"workspace"}:
                    raise ValueError(f"Unsupported inherited additions: {section}.{key}")
                values[key] = workspace[section][key]
    return "\n".join(
        f"[{section}]\n"
        + "\n".join(f"{key} = {toml_value(value)}" for key, value in values.items())
        + "\n"
        for section, values in core.items()
    )


def stage(output: Path) -> Path:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Output must be a new directory: {output}")
    if output.is_relative_to(ROOT):
        raise ValueError("Stage outside the source checkout to avoid recursive copies")
    shutil.copytree(
        LANE / "r", output, ignore=shutil.ignore_patterns("target", ".cargo", "*.o", "*.so")
    )
    rust = output / "src/rust"
    manifest = rust / "Cargo.toml"
    source = manifest.read_text()
    old = 'path = "../../../../../crates/dapane-core"'
    if source.count(old) != 1:
        raise ValueError("Expected one source-checkout core dependency")
    manifest.write_text(source.replace(old, 'path = "dapane-core"'))
    core = rust / "dapane-core"
    shutil.copytree(ROOT / "crates/dapane-core/src", core / "src")
    (core / "Cargo.toml").write_text(resolved_core_manifest())
    original = ROOT / "crates/dapane-core"
    hashes = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((original / "src").rglob("*.rs"))
    }
    for path in (original / "src").rglob("*.rs"):
        if path.read_bytes() != (core / path.relative_to(original)).read_bytes():
            raise ValueError(f"Staged core differs: {path}")
    provenance = output / "inst/provenance"
    provenance.mkdir(parents=True)
    shutil.copyfile(original / "Cargo.toml", provenance / "original-core-Cargo.toml")
    shutil.copyfile(ROOT / "Cargo.toml", provenance / "original-workspace-Cargo.toml")
    receipt = {
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_worktree_clean": not subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True
        ).strip(),
        "core_source_sha256": hashes,
        "binding_source_sha256": {
            path.relative_to(LANE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((LANE / "r").rglob("*"))
            if path.is_file() and "target" not in path.parts and ".cargo" not in path.parts
        },
        "binding_lock_sha256": hashlib.sha256((rust / "Cargo.lock").read_bytes()).hexdigest(),
        "scope": "Local synthetic qualification; no registry or release publication.",
    }
    (provenance / "source.json").write_text(json.dumps(receipt, indent=2) + "\n")
    subprocess.run(
        [
            "cargo",
            "vendor",
            "--locked",
            "--offline",
            "--versioned-dirs",
            "--manifest-path",
            str(manifest),
            str(output / "src/vendor"),
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    (rust / "vendor-config.toml").write_text(
        '[source.crates-io]\nreplace-with = "vendored-sources"\n\n'
        '[source.vendored-sources]\ndirectory = "vendor"\n'
    )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(stage(args.output.resolve()))
