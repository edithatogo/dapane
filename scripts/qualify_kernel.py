#!/usr/bin/env python3
"""Check the pinned kernel dependency boundary; this does not authorise a release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST_BASELINE = "1.99.1"
NATIVE_ROOTS = {"dapane-core", "dapane-cli"}
PUBLISH_REGISTRIES = {"dapane-core": ["crates-io"]}
# A positive list rejects new dependencies without relying on category/name guesses.
NATIVE_PACKAGES = {
    "autocfg",
    "block-buffer",
    "cfg-if",
    "const-oid",
    "cpufeatures",
    "crypto-common",
    "dapane-cli",
    "dapane-core",
    "deranged",
    "digest",
    "hybrid-array",
    "itoa",
    "libc",
    "memchr",
    "num-bigint",
    "num-conv",
    "num-integer",
    "num-rational",
    "num-traits",
    "powerfmt",
    "proc-macro2",
    "quote",
    "serde",
    "serde_core",
    "serde_derive",
    "serde_json",
    "sha2",
    "syn",
    "time",
    "time-core",
    "time-macros",
    "typenum",
    "unicode-ident",
    "zmij",
}
REVIEWED_LICENCES = {
    "MIT",
    "MIT OR Apache-2.0",
    "Apache-2.0 OR MIT",
    "Unlicense OR MIT",
    "(MIT OR Apache-2.0) AND Unicode-3.0",
    "Apache-2.0 WITH LLVM-exception",
}


class QualificationError(ValueError):
    """A source, toolchain or dependency-boundary check did not pass."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationError(message)


def version(value: str) -> tuple[int, int, int]:
    require(
        bool(re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", value)),
        f"Expected a stable Rust version, got {value!r}",
    )
    parts = [int(part) for part in value.split(".")]
    return tuple(parts + [0] * (3 - len(parts)))


def identity(package: dict) -> tuple[str, str, str | None]:
    return package["name"], package["version"], package.get("source")


def indexed(packages: list[dict], label: str) -> dict[tuple, dict]:
    result = {identity(package): package for package in packages}
    require(len(result) == len(packages), f"Duplicate package identity in {label}")
    return result


def check_inventory(lock: dict, inventory: dict) -> dict:
    """Compare static source records, without claiming fetched package identity."""
    registry = indexed(
        [package for package in lock["package"] if package.get("source")],
        "Cargo.lock",
    )
    recorded = indexed(inventory["packages"], "docs/dependencies.json")
    require(set(registry) == set(recorded), "Registry inventory differs from Cargo.lock")
    for key, package in registry.items():
        require(
            key[2] == "registry+https://github.com/rust-lang/crates.io-index",
            f"Unreviewed package source: {key}",
        )
        entry = recorded[key]
        checksum = package.get("checksum", "")
        require(
            bool(re.fullmatch(r"[0-9a-f]{64}", checksum)),
            f"Missing or malformed lock checksum: {key}",
        )
        require(
            checksum == entry.get("checksum"),
            f"Inventory checksum mismatch: {key}",
        )
        require(
            entry.get("declared_license") in REVIEWED_LICENCES,
            f"Dependency licence expression needs review: {key}",
        )
        if entry.get("declared_rust_version") is not None:
            require(
                version(entry["declared_rust_version"]) <= version(RUST_BASELINE),
                f"Dependency declares Rust above the tested baseline: {key}",
            )
    return recorded


def load_static(root: Path) -> tuple[dict, dict, dict]:
    manifest = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
    toolchain = tomllib.loads((root / "rust-toolchain.toml").read_text(encoding="utf-8"))
    workspace = manifest["workspace"]
    require(
        toolchain["toolchain"]["channel"] == RUST_BASELINE,
        "Toolchain pin differs from the qualified kernel baseline",
    )
    require(
        workspace["package"]["rust-version"] == RUST_BASELINE,
        "Workspace tested minimum differs from the toolchain pin",
    )
    require(
        workspace["package"]["publish"] is False,
        "Workspace publication gate must remain disabled",
    )
    require(
        set(workspace["default-members"]) == {"crates/dapane-core", "crates/dapane-cli"},
        "Default members must remain the independent native core and CLI",
    )
    members = {}
    for member in workspace["members"]:
        member_path = root / member / "Cargo.toml"
        package = tomllib.loads(member_path.read_text(encoding="utf-8"))["package"]
        publish = package.get("publish")
        if publish is False or publish == {"workspace": True}:
            publish = []
        require(
            publish == PUBLISH_REGISTRIES.get(package["name"], []),
            f"Unexpected Cargo publication scope: {package['name']}",
        )
        rust_version = package.get("rust-version")
        require(
            rust_version == RUST_BASELINE or rust_version == {"workspace": True},
            f"Package does not declare the tested Rust minimum: {package['name']}",
        )
        require(package["name"] not in members, "Duplicate workspace package name")
        members[package["name"]] = package
    require(
        set(members) == NATIVE_ROOTS | {"dapane-python"},
        "Workspace package set changed and requires qualification",
    )
    lock = tomllib.loads((root / "Cargo.lock").read_text(encoding="utf-8"))
    inventory_path = root / "docs/dependencies.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    recorded = check_inventory(lock, inventory)
    return lock, recorded, members


def check_metadata(metadata: dict, lock: dict, recorded: dict) -> list[dict]:
    """Verify fetched manifests and the resolved normal/build native closure."""
    packages = indexed(metadata["packages"], "Cargo metadata")
    locked = indexed(lock["package"], "Cargo.lock")
    require(
        set(packages) == set(locked),
        "Fetched package identities differ from Cargo.lock",
    )
    by_id = {package["id"]: package for package in metadata["packages"]}
    for key, record in recorded.items():
        package = packages[key]
        require(
            package.get("license") == record["declared_license"],
            f"Fetched licence declaration differs from inventory: {key}",
        )
        require(
            package.get("rust_version") == record.get("declared_rust_version"),
            f"Fetched Rust minimum differs from inventory: {key}",
        )
    workspace_ids = set(metadata["workspace_members"])
    roots = {key for key in workspace_ids if by_id[key]["name"] in NATIVE_ROOTS}
    require(
        {by_id[key]["name"] for key in roots} == NATIVE_ROOTS,
        "Native workspace roots are missing",
    )
    require(
        set(metadata["workspace_default_members"]) == roots,
        "Resolved default workspace members include a wrapper or omit a native root",
    )
    for key in workspace_ids:
        package = by_id[key]
        require(
            package.get("publish") == PUBLISH_REGISTRIES.get(package["name"], []),
            f"Unexpected resolved publication scope: {package['name']}",
        )
        require(
            by_id[key].get("rust_version") == RUST_BASELINE,
            f"Resolved workspace Rust minimum differs: {by_id[key]['name']}",
        )
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    pending = list(roots)
    visited = set()
    while pending:
        key = pending.pop()
        if key in visited:
            continue
        visited.add(key)
        package = by_id[key]
        require(
            package["name"] in NATIVE_PACKAGES,
            f"Unqualified dependency in minimal native closure: {package['name']}",
        )
        node = nodes[key]
        if package["name"] == "time":
            require(
                set(node["features"]) == {"parsing"},
                "Time native features must be parsing only",
            )
        for dependency in node["deps"]:
            if any(kind["kind"] != "dev" for kind in dependency["dep_kinds"]):
                pending.append(dependency["pkg"])
    closure = [{"name": by_id[key]["name"], "version": by_id[key]["version"]} for key in visited]
    return sorted(closure, key=lambda item: (item["name"], item["version"]))


def command(root: Path, arguments: list[str]) -> str:
    process = subprocess.run(
        arguments,
        cwd=root,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
        check=False,
    )
    require(
        process.returncode == 0,
        f"{' '.join(arguments)} failed: {process.stderr.strip()[:1200]}",
    )
    return process.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Check repository declarations only; do not claim runtime qualification",
    )
    args = parser.parse_args()
    lock, recorded, members = load_static(ROOT)
    licence_counts = Counter(package["declared_license"] for package in recorded.values())
    result = {
        "scope": "static_inventory" if args.inventory_only else "fetched_dependency_boundary",
        "rust_baseline": RUST_BASELINE,
        "workspace_packages": sorted(members),
        "registry_packages": len(recorded),
        "declared_licence_counts": dict(sorted(licence_counts.items())),
        "missing_declared_rust_minimum": sorted(
            package["name"]
            for package in recorded.values()
            if package.get("declared_rust_version") is None
        ),
        "project_licence": tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"][
            "package"
        ].get("license", "unselected"),
        "release_qualified": False,
        "compilation_verified_by_this_script": False,
    }
    if not args.inventory_only:
        rustc = command(ROOT, ["rustc", "--version", "--verbose"])
        details = dict(line.split(": ", 1) for line in rustc.splitlines() if ": " in line)
        require(
            details.get("release") == RUST_BASELINE,
            "Active Rust compiler does not match the pinned tested minimum",
        )
        cargo = command(ROOT, ["cargo", "--version"]).strip()
        require(
            version(cargo.split()[1])[:2] == version(RUST_BASELINE)[:2],
            "Active Cargo release series differs from the pinned compiler",
        )
        metadata = json.loads(
            command(ROOT, ["cargo", "metadata", "--locked", "--format-version", "1"])
        )
        result["native_closure"] = check_metadata(metadata, lock, recorded)
        result["rustc"] = rustc.splitlines()[0]
        result["cargo"] = cargo
        result["host"] = details.get("host")
    result["status"] = "passed"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        QualificationError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
        subprocess.TimeoutExpired,
    ) as error:
        print(json.dumps({"status": "failed", "error": str(error)}), file=sys.stderr)
        raise SystemExit(1) from error
