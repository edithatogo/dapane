#!/usr/bin/env python3
"""Check the unpublished kernel's pinned toolchain and dependency boundary.

The default check uses already fetched Cargo metadata, with --locked --offline.
Use --static-only explicitly when Cargo or its cache is unavailable; that result
does not qualify fetched metadata, the compiler, a build, or licence compatibility.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST_VERSION = "1.99.1"
NATIVE_CRATES = {"dapane-core", "dapane-cli"}
WORKSPACE_CRATES = NATIVE_CRATES | {"dapane-python"}
# These are the existing scalar graph, not a general list of approved licences.
# A new dependency needs an explicit boundary review before this set changes.
NATIVE_REGISTRY_PACKAGES = {
    "autocfg",
    "block-buffer",
    "cfg-if",
    "chrono",
    "const-oid",
    "cpufeatures",
    "crypto-common",
    "digest",
    "hybrid-array",
    "itoa",
    "libc",
    "memchr",
    "num-bigint",
    "num-integer",
    "num-rational",
    "num-traits",
    "proc-macro2",
    "quote",
    "serde",
    "serde_core",
    "serde_derive",
    "serde_json",
    "sha2",
    "syn",
    "typenum",
    "unicode-ident",
    "zmij",
}


class QualificationFailure(ValueError):
    """A pinned input or dependency boundary did not match its recorded contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationFailure(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def version_tuple(value: str) -> tuple[int, int, int]:
    require(
        isinstance(value, str) and re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", value) is not None,
        f"Expected a stable Rust version, got {value!r}",
    )
    parts = tuple(map(int, value.split(".")))
    return (*parts, 0) if len(parts) == 2 else parts


def identity(package: dict) -> tuple[str, str, str]:
    return package["name"], package["version"], package["source"]


def indexed(packages: list[dict], label: str) -> dict[tuple[str, str, str], dict]:
    result = {}
    for package in packages:
        key = identity(package)
        require(key not in result, f"Duplicate {label} package: {key}")
        result[key] = package
    return result


def check_manifests(root: Path) -> None:
    workspace = tomllib.loads((root / "Cargo.toml").read_text())["workspace"]
    toolchain = tomllib.loads((root / "rust-toolchain.toml").read_text())["toolchain"]
    require(toolchain["channel"] == RUST_VERSION, "The qualified Rust toolchain pin changed")
    require(workspace["package"]["rust-version"] == RUST_VERSION, "Workspace MSRV differs from pin")
    require(
        workspace["package"].get("publish") is False,
        "Workspace publication must stay disabled",
    )
    require(
        set(workspace["default-members"]) == {f"crates/{name}" for name in NATIVE_CRATES},
        "Default workspace members must be core and CLI only",
    )
    require(
        set(workspace["members"]) == {f"crates/{name}" for name in WORKSPACE_CRATES},
        "Workspace members changed; qualify the new boundary explicitly",
    )
    chrono = workspace["dependencies"]["chrono"]
    require(
        chrono.get("default-features") is False and set(chrono.get("features", [])) == {"std"},
        "Chrono must use only std, with its default/clock features disabled",
    )
    for name in sorted(WORKSPACE_CRATES):
        manifest = tomllib.loads((root / "crates" / name / "Cargo.toml").read_text())
        package = manifest["package"]
        require(package["name"] == name, f"Unexpected package identity: {name}")
        require(
            package["rust-version"] == {"workspace": True},
            f"{name} must inherit the MSRV",
        )
        require(
            package.get("publish") is False or package.get("publish") == {"workspace": True},
            f"{name} publication must stay disabled",
        )
        require(
            manifest.get("lints") == {"workspace": True},
            f"{name} must inherit workspace lints",
        )


def check_inventory(lock: dict, inventory: dict) -> dict[tuple[str, str, str], dict]:
    external = [package for package in lock["package"] if "source" in package]
    require(
        all(
            package["source"] == "registry+https://github.com/rust-lang/crates.io-index"
            for package in external
        ),
        "An external dependency does not use the recorded registry source",
    )
    locked = indexed(external, "lockfile")
    recorded = indexed(inventory["packages"], "inventory")
    require(set(locked) == set(recorded), "Inventory identities differ from Cargo.lock")
    for key, package in locked.items():
        entry = recorded[key]
        require(
            re.fullmatch(r"[0-9a-f]{64}", package.get("checksum", "")) is not None,
            f"Invalid locked registry checksum: {key}",
        )
        require(package["checksum"] == entry.get("checksum"), f"Inventory checksum mismatch: {key}")
        require(
            isinstance(entry.get("declared_license"), str)
            and bool(entry["declared_license"].strip()),
            f"Missing declared licence expression: {key}",
        )
        require("declared_rust_version" in entry, f"Missing Rust-version declaration field: {key}")
        rust_version = entry["declared_rust_version"]
        if rust_version is not None:
            require(
                version_tuple(rust_version) <= version_tuple(RUST_VERSION),
                f"Dependency declares a Rust version above the supported compiler: {key}",
            )
    return recorded


def check_metadata(metadata: dict, recorded: dict[tuple[str, str, str], dict]) -> dict:
    packages = metadata["packages"]
    fetched = indexed([package for package in packages if package.get("source")], "Cargo metadata")
    require(
        set(fetched) == set(recorded),
        "Fetched Cargo package identities differ from the inventory",
    )
    for key, package in fetched.items():
        entry = recorded[key]
        require(
            package.get("license") == entry["declared_license"],
            f"Fetched licence expression differs from inventory: {key}",
        )
        actual, expected = package.get("rust_version"), entry["declared_rust_version"]
        require(
            (actual is None and expected is None)
            or (
                actual is not None
                and expected is not None
                and version_tuple(actual) == version_tuple(expected)
            ),
            f"Fetched Rust-version declaration differs from inventory: {key}",
        )
    by_id = {package["id"]: package for package in packages}
    require(len(by_id) == len(packages), "Duplicate Cargo package IDs")
    local = [package for package in packages if not package.get("source")]
    require(
        {package["name"] for package in local} == WORKSPACE_CRATES
        and len(local) == len(WORKSPACE_CRATES),
        "Unexpected local package in the resolved workspace",
    )
    for package in local:
        require(package.get("publish") == [], f"Cargo allows publication of {package['name']}")
        require(
            version_tuple(package.get("rust_version")) == version_tuple(RUST_VERSION),
            f"Cargo resolved an unexpected MSRV for {package['name']}",
        )
    require(metadata.get("resolve") is not None, "Cargo metadata has no resolved graph")
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    require(len(nodes) == len(metadata["resolve"]["nodes"]), "Duplicate Cargo resolve nodes")
    pending = [package["id"] for package in local if package["name"] in NATIVE_CRATES]
    native = set()
    while pending:
        package_id = pending.pop()
        if package_id in native:
            continue
        require(
            package_id in by_id and package_id in nodes,
            f"Unresolved native dependency: {package_id}",
        )
        native.add(package_id)
        for dependency in nodes[package_id]["deps"]:
            kinds = dependency["dep_kinds"]
            require(bool(kinds), "Missing dependency-kind metadata")
            require(
                all(kind["kind"] in {None, "build", "dev"} for kind in kinds),
                "Unknown dependency kind",
            )
            if any(kind["kind"] in {None, "build"} for kind in kinds):
                pending.append(dependency["pkg"])
    native_names = {by_id[package_id]["name"] for package_id in native}
    unexpected = native_names - NATIVE_CRATES - NATIVE_REGISTRY_PACKAGES
    require(
        not unexpected,
        f"Unqualified dependency in the scalar core/CLI graph: {sorted(unexpected)}",
    )
    chrono_nodes = [
        nodes[package_id] for package_id in native if by_id[package_id]["name"] == "chrono"
    ]
    require(len(chrono_nodes) == 1, "Expected one Chrono package in the native graph")
    chrono_features = set(chrono_nodes[0]["features"])
    require(
        "std" in chrono_features and chrono_features <= {"std", "alloc"},
        f"Chrono resolved unqualified features: {sorted(chrono_features)}",
    )
    return {
        "native_registry_packages": sorted(native_names - NATIVE_CRATES),
        "chrono_features": sorted(chrono_features),
        "missing_declared_rust_versions": sorted(
            package["name"] for package in fetched.values() if package.get("rust_version") is None
        ),
    }


def run(command: list[str], root: Path) -> str:
    result = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=True, timeout=120
    )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--cargo", default="cargo")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    root = args.repository.resolve(strict=True)
    try:
        check_manifests(root)
        lock = tomllib.loads((root / "Cargo.lock").read_text())
        inventory = json.loads(
            (root / "docs/dependencies.json").read_text(), object_pairs_hook=unique_object
        )
        recorded = check_inventory(lock, inventory)
        result = {
            "status": "static_checks_passed",
            "rust_version": RUST_VERSION,
            "registry_packages": len(recorded),
            "publication_enabled": False,
            "project_license": "unresolved; release_consolidation_20261108 L1.2",
            "scope": "Dependency metadata and native boundary only; no build or legal compatibility claim",
        }
        if args.static_only:
            result["fetched_metadata"] = "not_checked"
            result["compiler"] = "not_checked"
            result["native_graph"] = "not_checked"
        else:
            compiler = run([args.rustc, "--version", "--verbose"], root)
            require(
                f"release: {RUST_VERSION}" in compiler.splitlines(),
                "Running rustc does not match the qualified toolchain",
            )
            metadata = json.loads(
                run(
                    [
                        args.cargo,
                        "metadata",
                        "--locked",
                        "--offline",
                        "--no-default-features",
                        "--format-version",
                        "1",
                    ],
                    root,
                ),
                object_pairs_hook=unique_object,
            )
            result.update(check_metadata(metadata, recorded))
            result["compiler"] = compiler.strip()
            result["fetched_metadata"] = "checked_offline"
            result["native_graph"] = "normal_and_build_dependencies_checked"
            result["status"] = "dependency_metadata_passed"
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"Kernel qualification failed: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr.strip(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
