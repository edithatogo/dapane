"""Guard regressions using synthetic metadata; not fetched-package evidence."""

import importlib.util
import json
import tomllib
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("qualify_kernel", ROOT / "scripts/qualify_kernel.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def synthetic_metadata(lock: dict, recorded: dict) -> dict:
    """Model Cargo's response from declarations solely to test the guard."""
    ids = {
        package["name"]: f"fixture:{package['name']}@{package['version']}"
        for package in lock["package"]
    }
    packages = []
    nodes = []
    for package in lock["package"]:
        item = deepcopy(package)
        item["id"] = ids[item["name"]]
        if item.get("source"):
            record = recorded[guard.identity(item)]
            item["license"] = record["declared_license"]
            item["rust_version"] = record["declared_rust_version"]
        else:
            item["publish"] = ["crates-io"] if item["name"] == "dapane-core" else []
            item["rust_version"] = guard.RUST_BASELINE
        packages.append(item)
        nodes.append(
            {
                "id": ids[package["name"]],
                "features": ["parsing"] if package["name"] == "time" else [],
                "deps": [
                    {
                        "pkg": ids[dependency.split()[0]],
                        "dep_kinds": [{"kind": None}],
                    }
                    for dependency in package.get("dependencies", [])
                ],
            }
        )
    return {
        "packages": packages,
        "workspace_members": [ids[name] for name in sorted(guard.NATIVE_ROOTS | {"dapane-python"})],
        "workspace_default_members": [ids[name] for name in sorted(guard.NATIVE_ROOTS)],
        "resolve": {"nodes": nodes},
    }


class KernelQualificationTests(unittest.TestCase):
    def setUp(self):
        self.lock = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
        self.inventory = json.loads((ROOT / "docs/dependencies.json").read_text(encoding="utf-8"))
        self.recorded = guard.check_inventory(self.lock, self.inventory)
        self.metadata = synthetic_metadata(self.lock, self.recorded)

    def test_actual_static_declarations_pass(self):
        _, recorded, members = guard.load_static(ROOT)
        self.assertEqual(len(recorded), 41)
        self.assertEqual(set(members), {"dapane-core", "dapane-cli", "dapane-python"})
        self.assertEqual(members["dapane-core"]["publish"], ["crates-io"])

    def test_changed_checksum_is_rejected(self):
        self.inventory["packages"][0]["checksum"] = "0" * 64
        with self.assertRaisesRegex(guard.QualificationError, "checksum mismatch"):
            guard.check_inventory(self.lock, self.inventory)

    def test_missing_or_duplicate_inventory_record_is_rejected(self):
        mutations = (
            lambda values: values.pop(),
            lambda values: values.append(values[0]),
        )
        for mutate in mutations:
            inventory = deepcopy(self.inventory)
            mutate(inventory["packages"])
            with self.assertRaises(guard.QualificationError):
                guard.check_inventory(self.lock, inventory)

    def test_unreviewed_licence_and_unsupported_msrv_are_rejected(self):
        changes = (
            ("declared_license", "unknown"),
            ("declared_rust_version", "2.0.0"),
        )
        for field, value in changes:
            inventory = deepcopy(self.inventory)
            inventory["packages"][0][field] = value
            with self.assertRaises(guard.QualificationError):
                guard.check_inventory(self.lock, inventory)

    def test_synthetic_resolved_closure_excludes_wrapper(self):
        native = guard.check_metadata(self.metadata, self.lock, self.recorded)
        names = {package["name"] for package in native}
        self.assertEqual(names, guard.NATIVE_PACKAGES)
        self.assertNotIn("pyo3", names)

    def test_fetched_manifest_drift_is_rejected(self):
        for field, value in (("license", "unknown"), ("rust_version", "2.0.0")):
            metadata = deepcopy(self.metadata)
            package = next(p for p in metadata["packages"] if p.get("source"))
            package[field] = value
            with self.assertRaisesRegex(guard.QualificationError, "differs from inventory"):
                guard.check_metadata(metadata, self.lock, self.recorded)

    def test_wrapper_build_dependency_in_native_closure_is_rejected(self):
        core = next(
            node for node in self.metadata["resolve"]["nodes"] if "dapane-core@" in node["id"]
        )
        pyo3 = next(package for package in self.metadata["packages"] if package["name"] == "pyo3")
        core["deps"].append({"pkg": pyo3["id"], "dep_kinds": [{"kind": "build"}]})
        with self.assertRaisesRegex(guard.QualificationError, "Unqualified dependency"):
            guard.check_metadata(self.metadata, self.lock, self.recorded)

    def test_clock_features_are_rejected(self):
        time = next(node for node in self.metadata["resolve"]["nodes"] if "time@" in node["id"])
        time["features"].append("local-offset")
        with self.assertRaisesRegex(guard.QualificationError, "parsing only"):
            guard.check_metadata(self.metadata, self.lock, self.recorded)

    def test_resolved_publication_gate_is_enforced(self):
        invalid_scopes = (
            ("dapane-core", None),
            ("dapane-core", ["crates-io", "other"]),
            ("dapane-cli", ["crates-io"]),
            ("dapane-python", ["crates-io"]),
        )
        for name, registry in invalid_scopes:
            with self.subTest(name=name, registry=registry):
                metadata = deepcopy(self.metadata)
                package = next(p for p in metadata["packages"] if p["name"] == name)
                package["publish"] = registry
                with self.assertRaisesRegex(guard.QualificationError, "publication scope"):
                    guard.check_metadata(metadata, self.lock, self.recorded)

    def test_default_wrapper_is_rejected(self):
        wrapper = next(
            package for package in self.metadata["packages"] if package["name"] == "dapane-python"
        )
        self.metadata["workspace_default_members"].append(wrapper["id"])
        with self.assertRaisesRegex(guard.QualificationError, "default workspace members"):
            guard.check_metadata(self.metadata, self.lock, self.recorded)

    def test_stable_version_comparison_preserves_cargo_patch_independence(self):
        self.assertEqual(guard.version("1.99"), (1, 99, 0))
        self.assertEqual(guard.version("1.99.0")[:2], guard.version("1.99.1")[:2])
        for value in ("nightly", "1.99.0-nightly", "1", "1.99.0.1"):
            with self.assertRaises(guard.QualificationError):
                guard.version(value)


if __name__ == "__main__":
    unittest.main()
