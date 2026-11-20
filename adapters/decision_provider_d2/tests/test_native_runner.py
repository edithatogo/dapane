"""Fail-closed provider execution guards; no fake native extension counts as qualified."""

import os
import tempfile
import unittest
import zipfile
from hashlib import sha256
from pathlib import Path

from native_voiage import ExecutionError, check_wheel, run_evpi
from study import canonical_digest, prepare_evidence_question, verify_native_evpi_receipt
from test_study import packet, protocol


class NativeRunnerTests(unittest.TestCase):
    def test_nonexistent_wheel_fails_before_provider_import(self):
        with self.assertRaisesRegex(ExecutionError, "wheel_missing"):
            check_wheel(Path("/not-a-wheel.whl"), "sha256:" + "a" * 64)

    def test_wheel_digest_mismatch_is_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            wheel = Path(d) / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr("voiage/__init__.py", "")
            with self.assertRaisesRegex(ExecutionError, "wheel_digest_mismatch"):
                check_wheel(wheel, "sha256:" + "a" * 64)

    def test_zip_without_native_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            wheel = Path(d) / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr("voiage/__init__.py", "")
            h = "sha256:" + sha256(wheel.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ExecutionError, "native_wheel_missing"):
                check_wheel(wheel, h)

    def test_reject_unsafe_archive_member(self):
        with tempfile.TemporaryDirectory() as d:
            wheel = Path(d) / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr("voiage/_core.cpython-315.so", b"fake")
                z.writestr("../voiage/unreviewed.py", b"data")
            h = "sha256:" + sha256(wheel.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ExecutionError, "unsafe_wheel_member"):
                check_wheel(wheel, h)

    def test_reject_duplicate_archive_members(self):
        with tempfile.TemporaryDirectory() as d:
            wheel = Path(d) / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr("voiage/_core.cpython-315.so", b"fake")
                import warnings

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    z.writestr("voiage/_core.cpython-315.so", b"changed")
            h = "sha256:" + sha256(wheel.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ExecutionError, "unsafe_wheel_member"):
                check_wheel(wheel, h)

    def test_run_does_not_fall_back_to_numpy_without_installed_native_provider(self):
        q = prepare_evidence_question(packet(), protocol())
        with tempfile.TemporaryDirectory() as d:
            wheel = Path(d) / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr("voiage/__init__.py", "")
            h = "sha256:" + sha256(wheel.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ExecutionError, "native_wheel_missing"):
                run_evpi(q, wheel, h, expected_revision=q["provider"]["revision"])

    def test_reject_unexpected_source_revision(self):
        q = prepare_evidence_question(packet(), protocol())
        with self.assertRaisesRegex(ExecutionError, "source_revision_mismatch"):
            run_evpi(q, Path("/not-a-wheel.whl"), "sha256:" + "a" * 64, expected_revision="d" * 40)

    def test_installed_voiage_wheel_returns_staff_time_evpi(self):
        raw = os.environ.get("DAPANE_VOIAGE_WHEEL")
        if not raw:
            self.skipTest("DAPANE_VOIAGE_WHEEL is not set")
        wheel = Path(raw)
        revision = "0978497b5047de9459ed2fca9b349a4e2a9c45d3"
        digest = "sha256:71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140"
        prepared_packet = packet()
        prepared_packet["provider"]["revision"] = revision
        prepared_packet["provider"]["artifact_digest"] = digest
        prepared_packet["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n",
            {key: value for key, value in prepared_packet.items() if key != "output_digest"},
        )
        prepared = prepare_evidence_question(prepared_packet, protocol())
        receipt = run_evpi(prepared, wheel, digest, expected_revision=revision)
        review = verify_native_evpi_receipt(
            prepared,
            receipt,
            expected_wheel=digest,
            expected_extension=receipt["native_extension_digest"],
        )
        self.assertEqual(receipt["evpi_per_assay"], 10.0)
        self.assertEqual(receipt["execution"], "native_extension_invoked")
        self.assertEqual(review["provider_revision"], revision)


if __name__ == "__main__":
    unittest.main()
