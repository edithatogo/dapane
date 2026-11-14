"""Adversarial checks for evidence integrity; these do not simulate native qualification."""

import base64
import copy
import csv
import hashlib
import importlib.util
import io
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "release_assurance", ROOT / "scripts/release_assurance.py"
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = release.read_json(ROOT / "release/capabilities.json")

    def test_current_candidate_is_explicitly_unpublished(self):
        release.validate_manifest(self.manifest)
        self.assertFalse(self.manifest["publication"]["enabled"])
        self.assertTrue(release.publication_blockers(self.manifest))

    def test_duplicate_target_does_not_cover_missing_interpreter(self):
        self.manifest["targets"][3] = copy.deepcopy(self.manifest["targets"][0])
        with self.assertRaisesRegex(release.AssuranceError, "target"):
            release.validate_manifest(self.manifest)

    def test_wheel_tag_cannot_extend_platform_claims(self):
        self.manifest["targets"][0]["system"] = "Windows"
        with self.assertRaisesRegex(release.AssuranceError, "target"):
            release.validate_manifest(self.manifest)

    def test_stable_abi_is_not_inferred(self):
        self.manifest["targets"][0]["abi"] = "abi3"
        with self.assertRaisesRegex(release.AssuranceError, "ABI"):
            release.validate_manifest(self.manifest)

    def test_real_provider_prerequisite_cannot_be_made_optional(self):
        self.manifest["required_tracks"].remove("python_two_consumers_20261108")
        with self.assertRaisesRegex(release.AssuranceError, "prerequisites"):
            release.validate_manifest(self.manifest)

    def test_candidate_flag_cannot_enable_publication(self):
        self.manifest["publication"]["enabled"] = True
        with self.assertRaisesRegex(release.AssuranceError, "publication"):
            release.validate_manifest(self.manifest)

    def test_optional_research_does_not_gate_candidate_validation(self):
        self.manifest["optional_tracks"].append("future_optional_experiment")
        release.validate_manifest(self.manifest)

    def test_missing_and_duplicate_executed_targets_fail(self):
        targets = [release.target_key(t) for t in self.manifest["targets"]]
        release.verify_matrix_targets(targets, self.manifest)
        for altered in (targets[:-1], targets + [targets[0]]):
            with self.subTest(altered=altered):
                with self.assertRaisesRegex(release.AssuranceError, "matrix target"):
                    release.verify_matrix_targets(altered, self.manifest)

    def test_dependency_versions_must_exist_in_the_lockfile(self):
        dependencies = [
            {"name": "dapane-core", "version": "0.1.0"},
            {"name": "dapane-cli", "version": "0.1.0"},
        ]
        release.verify_dependency_versions(dependencies, self.manifest)
        dependencies[0]["version"] = "999"
        with self.assertRaisesRegex(release.AssuranceError, "Cargo.lock"):
            release.verify_dependency_versions(dependencies, self.manifest)

    def test_duplicate_json_keys_and_nonfinite_values_fail(self):
        for encoded in ('{"ready": false, "ready": true}', '{"value": NaN}'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(release.AssuranceError):
                    release.decode_json(encoded)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.first, self.second = self.root / "first", self.root / "second"
        for directory in (self.first, self.second):
            directory.mkdir()
            (directory / "dapane").write_bytes(b"synthetic CLI identity fixture")
            (directory / "dapane-0.1.0-cp312-cp312-linux_x86_64.whl").write_bytes(
                b"synthetic wheel identity fixture"
            )

    def test_identical_build_artifacts_compare(self):
        records = release.compare_artifacts(self.first, self.second)
        release.verify_artifacts(records, self.first)

    def test_changed_cli_bytes_fail(self):
        records = release.candidate_artifacts(self.first)
        (self.first / "dapane").write_bytes(b"tampered")
        with self.assertRaisesRegex(release.AssuranceError, "changed"):
            release.verify_artifacts(records, self.first)

    def test_changed_declared_digest_fails(self):
        records = release.candidate_artifacts(self.first)
        records[0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(release.AssuranceError, "changed"):
            release.verify_artifacts(records, self.first)

    def test_one_directory_cannot_impersonate_two_clean_builds(self):
        with self.assertRaisesRegex(release.AssuranceError, "distinct"):
            release.compare_artifacts(self.first, self.first)

    def test_second_clean_build_must_match(self):
        wheel = next(self.second.glob("*.whl"))
        wheel.write_bytes(b"different native content")
        with self.assertRaisesRegex(release.AssuranceError, "different"):
            release.compare_artifacts(self.first, self.second)

    def test_missing_wheel_and_missing_artifact_fail(self):
        records = release.candidate_artifacts(self.first)
        next(self.first.glob("*.whl")).unlink()
        with self.assertRaisesRegex(release.AssuranceError, "missing"):
            release.verify_artifacts(records, self.first)
        with self.assertRaisesRegex(release.AssuranceError, "exactly one wheel"):
            release.compare_artifacts(self.first, self.second)

    def test_path_traversal_is_rejected(self):
        records = release.candidate_artifacts(self.first)
        records[0]["name"] = "../dapane"
        with self.assertRaisesRegex(release.AssuranceError, "plain filename"):
            release.verify_artifacts(records, self.first)


class WheelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.installed = self.root / "site-packages"
        self.installed.mkdir()
        self.wheel = self.root / "dapane-0.1.0-cp312-cp312-linux_x86_64.whl"
        self.members = {
            "dapane/__init__.py": b"test-only transport module\n",
            "dapane/_native.so": b"test-only binary identity; never imported\n",
            "dapane-0.1.0.dist-info/METADATA": b"Name: dapane\nVersion: 0.1.0\n",
            "dapane-0.1.0.dist-info/WHEEL": (
                b"Wheel-Version: 1.0\nRoot-Is-Purelib: false\nTag: cp312-cp312-linux_x86_64\n"
            ),
        }
        self.write_wheel()

    def write_wheel(self):
        record = io.StringIO()
        writer = csv.writer(record, lineterminator="\n")
        for name, data in self.members.items():
            digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
            writer.writerow([name, "sha256=" + digest, str(len(data))])
        writer.writerow(["dapane-0.1.0.dist-info/RECORD", "", ""])
        with zipfile.ZipFile(self.wheel, "w") as archive:
            for name, data in self.members.items():
                archive.writestr(name, data)
                path = self.installed / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            archive.writestr("dapane-0.1.0.dist-info/RECORD", record.getvalue())

    def test_installed_files_match_supplied_wheel(self):
        members = release.verify_wheel_members(self.wheel, self.installed, "0.1.0")
        self.assertIn("dapane/_native.so", members)

    def test_wheel_cannot_be_relabelled_as_another_interpreter(self):
        runtime = {
            "system": "Linux",
            "machine": "x86_64",
            "implementation": "CPython",
            "python": "3.12.14",
        }
        release.verify_wheel_target(self.wheel, runtime)
        runtime["python"] = "3.15.1"
        with self.assertRaisesRegex(release.AssuranceError, "recorded interpreter"):
            release.verify_wheel_target(self.wheel, runtime)

    def test_same_package_version_does_not_hide_native_substitution(self):
        (self.installed / "dapane/_native.so").write_bytes(b"unrelated native implementation")
        with self.assertRaisesRegex(release.AssuranceError, "installed wheel bytes"):
            release.verify_wheel_members(self.wheel, self.installed, "0.1.0")

    def test_runtime_dependency_is_rejected(self):
        self.members["dapane-0.1.0.dist-info/METADATA"] += b"Requires-Dist: polars\n"
        self.write_wheel()
        with self.assertRaisesRegex(release.AssuranceError, "runtime dependencies"):
            release.verify_wheel_members(self.wheel, self.installed, "0.1.0")

    def test_wheel_record_cannot_omit_a_payload(self):
        with zipfile.ZipFile(self.wheel, "a") as archive:
            archive.writestr("dapane/unrecorded.py", "pass\n")
        with self.assertRaisesRegex(release.AssuranceError, "incomplete wheel RECORD"):
            release.verify_wheel_members(self.wheel, self.installed, "0.1.0")


class SourceTests(unittest.TestCase):
    def test_dirty_tracked_source_cannot_produce_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commands = (
                ["git", "init", "-q"],
                ["git", "config", "user.name", "Synthetic test author"],
                ["git", "config", "user.email", "test@example.invalid"],
            )
            for args in commands:
                subprocess.run(args, cwd=root, check=True, capture_output=True)
            source = root / "input.txt"
            source.write_text("original\n")
            subprocess.run(["git", "add", "input.txt"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-qm", "synthetic source fixture"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            self.assertEqual(len(release.source_identity(root)["commit"]), 40)
            untracked = root / "untracked.rs"
            untracked.write_text("untracked build input\n")
            with self.assertRaisesRegex(release.AssuranceError, "untracked"):
                release.source_identity(root)
            untracked.unlink()
            source.write_text("uncommitted change\n")
            with self.assertRaisesRegex(release.AssuranceError, "dirty"):
                release.source_identity(root)

    def test_previous_commit_receipt_is_rejected_before_any_runtime_claim(self):
        receipt = {
            "format": release.FORMAT,
            "purpose": "unpublished-candidate-verification",
            "publication_ready": False,
            "source": {"commit": "0" * 40, "tree": "1" * 40, "epoch": 1},
        }
        with patch.object(release, "source_identity", return_value={"commit": "2" * 40}):
            with self.assertRaisesRegex(release.AssuranceError, "another source"):
                release.verify_evidence(receipt, ROOT)

    def test_changed_reference_or_lock_hash_is_rejected(self):
        receipt = {
            "format": release.FORMAT,
            "purpose": "unpublished-candidate-verification",
            "publication_ready": False,
            "source": {"commit": "2" * 40},
            "inputs": {"Cargo.lock": "0" * 64},
        }
        with (
            patch.object(release, "source_identity", return_value=receipt["source"]),
            patch.object(release, "input_hashes", return_value={"Cargo.lock": "1" * 64}),
        ):
            with self.assertRaisesRegex(release.AssuranceError, "input/lock/reference"):
                release.verify_evidence(receipt, ROOT)


class ReferenceTests(unittest.TestCase):
    def capacity_report(self):
        path = "fixtures/genomics-capacity/time-missing-use.json"
        kind, expected, request = release.reference_cases()[path]
        report = {
            "schema_version": "0.2",
            "status": "complete",
            "method_version": "dapane-exact-v0.2.0",
            "run_id": request["run_id"],
            "totals": {"rounded": "900.00", "allocated": "30.00", "unattributed": "870.00"},
            "capacity_allocations": [
                {
                    "pool_rounded": "300.00",
                    "unallocated": "270.00",
                    "shares": [
                        {"object_id": "cohort-a", "rounded": "30.00"},
                        {"object_id": "cohort-b", "rounded": None},
                    ],
                }
            ],
        }
        normalized = release.normalize_request(request)
        report["input_digest"] = (
            "sha256:"
            + hashlib.sha256(b"dapane:input:0.2\n" + release.canonical(normalized)).hexdigest()
        )
        report["policy"] = normalized["policy"]
        report["quote_snapshots"] = normalized["quotes"]
        report["context"] = {
            key: normalized[key] for key in ("objects", "processes", "events", "object_relations")
        }
        report["lines"] = normalized["usage"]
        capacity = normalized["capacity_allocations"][0]
        report["capacity_allocations"][0].update(
            {
                key: capacity[key]
                for key in ("id", "source", "source_line_ids", "unit", "observation_coverage")
            }
        )
        digest = hashlib.sha256(b"dapane:output:0.2\n" + release.canonical(report)).hexdigest()
        report["output_digest"] = "sha256:" + digest
        return report, kind, expected, request

    def test_unknown_capacity_is_compared_as_unknown(self):
        release.check_reference(*self.capacity_report())

    def test_unknown_capacity_cannot_be_replaced_by_zero(self):
        report, *arguments = self.capacity_report()
        report["capacity_allocations"][0]["shares"][1]["rounded"] = "0.00"
        with self.assertRaisesRegex(release.AssuranceError, "unknown/allocated"):
            release.check_reference(report, *arguments)

    def test_rehashed_source_substitution_fails(self):
        report, *arguments = self.capacity_report()
        report["quote_snapshots"][0]["source"]["version"] = "substituted"
        report.pop("output_digest")
        report["output_digest"] = (
            "sha256:"
            + hashlib.sha256(b"dapane:output:0.2\n" + release.canonical(report)).hexdigest()
        )
        with self.assertRaisesRegex(release.AssuranceError, "quote/source snapshot"):
            release.check_reference(report, *arguments)

    def test_changed_input_identity_is_rejected(self):
        report, *arguments = self.capacity_report()
        report["input_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(release.AssuranceError, "input identity"):
            release.check_reference(report, *arguments)

    def test_result_digest_tampering_fails(self):
        report, *arguments = self.capacity_report()
        report["output_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(release.AssuranceError, "digest"):
            release.check_reference(report, *arguments)

    def test_fixture_inventory_covers_both_profiles(self):
        cases = release.reference_cases()
        self.assertEqual(len(cases), 10)
        self.assertEqual(
            {request["schema_version"] for _, _, request in cases.values()}, {"0.1", "0.2"}
        )


if __name__ == "__main__":
    unittest.main()
