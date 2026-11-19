"""Source-package staging must retain the existing kernel and locked graph."""

import importlib.util
import tomllib
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
ROOT = LANE.parents[1]
SPEC = importlib.util.spec_from_file_location("stage_r", LANE / "stage_r.py")
stage_r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage_r)


class PackagingTests(unittest.TestCase):
    def test_inheritance_resolution_preserves_core_dependency_features(self):
        resolved = tomllib.loads(stage_r.resolved_core_manifest())
        workspace = tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"]
        original = tomllib.loads((ROOT / "crates/dapane-core/Cargo.toml").read_text())
        for name in original["dependencies"]:
            self.assertEqual(resolved["dependencies"][name], workspace["dependencies"][name])
        for name, value in original["package"].items():
            expected = workspace["package"][name] if isinstance(value, dict) else value
            self.assertEqual(resolved["package"][name], expected)

    def test_root_locked_packages_are_not_silently_upgraded(self):
        root_packages = tomllib.loads((ROOT / "Cargo.lock").read_text())["package"]
        lane_packages = tomllib.loads((LANE / "r/src/rust/Cargo.lock").read_text())["package"]
        root = {(p["name"], p["version"]): p.get("checksum") for p in root_packages}
        for package in lane_packages:
            key = (package["name"], package["version"])
            if package["name"] in {p["name"] for p in root_packages}:
                # syn 2 is additionally required by extendr; the root uses syn 3.
                if package["name"] == "syn" and package["version"].startswith("2."):
                    continue
                self.assertIn(key, root)
                self.assertEqual(package.get("checksum"), root[key])

    def test_staging_refuses_overwrite(self):
        with self.assertRaises(FileExistsError):
            stage_r.stage(LANE)

    def test_staging_refuses_a_new_directory_inside_source(self):
        with self.assertRaises(ValueError):
            stage_r.stage(LANE / "r/new-recursive-stage")


if __name__ == "__main__":
    unittest.main()
