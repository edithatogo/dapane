"""Negative qualification cases independent of Cargo, downloads and Rust builds."""

import copy
import json
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

from scripts import qualify_kernel as qualification

ROOT = Path(__file__).resolve().parents[2]


def fixture_metadata(lock: dict, inventory: dict) -> dict:
    """Model Cargo's public metadata shape; use real pinned identities as inputs."""
    recorded = {entry["name"]: entry for entry in inventory["packages"]}
    identifiers = {
        entry["name"]: f"fixture:{entry['name']}@{entry['version']}" for entry in lock["package"]
    }
    packages, nodes = [], []
    for entry in lock["package"]:
        name = entry["name"]
        source = entry.get("source")
        packages.append(
            {
                "id": identifiers[name],
                "name": name,
                "version": entry["version"],
                "source": source,
                "license": recorded[name]["declared_license"] if source else None,
                "rust_version": recorded[name]["declared_rust_version"] if source else "1.99.1",
                "publish": None if source else [],
            }
        )
        nodes.append(
            {
                "id": identifiers[name],
                "features": ["alloc", "std"] if name == "chrono" else [],
                "deps": [
                    {"pkg": identifiers[dependency], "dep_kinds": [{"kind": None, "target": None}]}
                    for dependency in entry.get("dependencies", [])
                ],
            }
        )
    return {"packages": packages, "resolve": {"nodes": nodes}}


class DependencyQualificationTests(unittest.TestCase):
    def setUp(self):
        self.lock = tomllib.loads((ROOT / "Cargo.lock").read_text())
        self.inventory = json.loads((ROOT / "docs/dependencies.json").read_text())
        self.recorded = qualification.check_inventory(self.lock, self.inventory)
        self.metadata = fixture_metadata(self.lock, self.inventory)

    def package(self, name):
        return next(package for package in self.metadata["packages"] if package["name"] == name)

    def node(self, name):
        return next(
            node
            for node in self.metadata["resolve"]["nodes"]
            if node["id"] == self.package(name)["id"]
        )

    def test_current_inventory_and_metadata_preserve_native_boundary(self):
        result = qualification.check_metadata(self.metadata, self.recorded)
        self.assertEqual(len(result["native_registry_packages"]), 27)
        self.assertEqual(result["chrono_features"], ["alloc", "std"])
        self.assertEqual(result["missing_declared_rust_versions"], ["target-lexicon"])

    def test_checksum_change_is_rejected(self):
        self.inventory["packages"][0]["checksum"] = "0" * 64
        with self.assertRaisesRegex(qualification.QualificationFailure, "checksum mismatch"):
            qualification.check_inventory(self.lock, self.inventory)

    def test_missing_inventory_package_is_rejected(self):
        self.inventory["packages"].pop()
        with self.assertRaisesRegex(qualification.QualificationFailure, "identities differ"):
            qualification.check_inventory(self.lock, self.inventory)

    def test_duplicate_inventory_identity_is_rejected(self):
        self.inventory["packages"].append(copy.deepcopy(self.inventory["packages"][0]))
        with self.assertRaisesRegex(qualification.QualificationFailure, "Duplicate inventory"):
            qualification.check_inventory(self.lock, self.inventory)

    def test_dependency_msrv_above_pin_is_rejected(self):
        self.inventory["packages"][0]["declared_rust_version"] = "1.100.0"
        with self.assertRaisesRegex(
            qualification.QualificationFailure, "above the supported compiler"
        ):
            qualification.check_inventory(self.lock, self.inventory)

    def test_unknown_licence_is_not_silently_accepted(self):
        self.inventory["packages"][0]["declared_license"] = None
        with self.assertRaisesRegex(qualification.QualificationFailure, "Missing declared licence"):
            qualification.check_inventory(self.lock, self.inventory)

    def test_unicode_and_obligation_cannot_be_lost(self):
        self.package("unicode-ident")["license"] = "MIT OR Apache-2.0"
        with self.assertRaisesRegex(
            qualification.QualificationFailure, "licence expression differs"
        ):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_missing_msrv_cannot_be_replaced_with_invented_value(self):
        self.package("target-lexicon")["rust_version"] = "1.85"
        with self.assertRaisesRegex(
            qualification.QualificationFailure, "Rust-version declaration differs"
        ):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_cargo_normalized_rust_version_is_equivalent(self):
        self.package("num-rational")["rust_version"] = "1.60.0"
        qualification.check_metadata(self.metadata, self.recorded)

    def test_wrapper_dependency_is_rejected_even_if_already_in_lock(self):
        self.node("dapane-core")["deps"].append(
            {"pkg": self.package("pyo3")["id"], "dep_kinds": [{"kind": None, "target": None}]}
        )
        with self.assertRaisesRegex(qualification.QualificationFailure, "Unqualified dependency"):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_build_dependency_cannot_hide_wrapper(self):
        self.node("dapane-core")["deps"].append(
            {"pkg": self.package("pyo3")["id"], "dep_kinds": [{"kind": "build", "target": None}]}
        )
        with self.assertRaisesRegex(qualification.QualificationFailure, "Unqualified dependency"):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_chrono_clock_feature_is_rejected(self):
        self.node("chrono")["features"].append("clock")
        with self.assertRaisesRegex(
            qualification.QualificationFailure, "Chrono resolved unqualified"
        ):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_missing_resolved_graph_is_not_a_pass(self):
        self.metadata["resolve"] = None
        with self.assertRaisesRegex(qualification.QualificationFailure, "no resolved graph"):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_metadata_publication_is_checked(self):
        self.package("dapane-core")["publish"] = None
        with self.assertRaisesRegex(qualification.QualificationFailure, "Cargo allows publication"):
            qualification.check_metadata(self.metadata, self.recorded)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(qualification.QualificationFailure, "Duplicate JSON key"):
            json.loads(
                '{"license":"MIT","license":"GPL-3.0-only"}',
                object_pairs_hook=qualification.unique_object,
            )


class ManifestQualificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        paths = ["Cargo.toml", "rust-toolchain.toml"]
        paths += [f"crates/{name}/Cargo.toml" for name in qualification.WORKSPACE_CRATES]
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def replace(self, path, before, after):
        target = self.root / path
        text = target.read_text()
        self.assertIn(before, text)
        target.write_text(text.replace(before, after))

    def test_current_manifests_pass(self):
        qualification.check_manifests(self.root)

    def test_updating_toolchain_and_msrv_does_not_silently_widen_qualification(self):
        self.replace("Cargo.toml", 'rust-version = "1.99.1"', 'rust-version = "1.100.0"')
        self.replace("rust-toolchain.toml", 'channel = "1.99.1"', 'channel = "1.100.0"')
        with self.assertRaisesRegex(qualification.QualificationFailure, "toolchain pin changed"):
            qualification.check_manifests(self.root)

    def test_chrono_default_features_are_rejected(self):
        self.replace("Cargo.toml", "default-features = false", "default-features = true")
        with self.assertRaisesRegex(qualification.QualificationFailure, "Chrono must use only std"):
            qualification.check_manifests(self.root)

    def test_core_publication_cannot_be_enabled(self):
        self.replace("crates/dapane-core/Cargo.toml", "publish = false", "publish = true")
        with self.assertRaisesRegex(
            qualification.QualificationFailure, "publication must stay disabled"
        ):
            qualification.check_manifests(self.root)


if __name__ == "__main__":
    unittest.main()
