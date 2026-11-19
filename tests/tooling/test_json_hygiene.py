"""Tests for scripts/check_json_hygiene.py."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_json_hygiene", ROOT / "scripts/check_json_hygiene.py"
)
hygiene = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(hygiene)


class JsonHygieneTests(unittest.TestCase):
    def test_accepts_valid_sha256_under_neutral_key(self) -> None:
        payload = b'{"model_sha256": "' + b"a" * 64 + b'", "status": "ok"}\n'
        hygiene.validate_json_bytes(payload, label="valid.json")

    def test_rejects_duplicate_object_keys(self) -> None:
        payload = b'{"id": "first", "id": "second"}'
        with self.assertRaisesRegex(hygiene.JsonHygieneError, "duplicate JSON object key"):
            hygiene.validate_json_bytes(payload, label="dup.json")

    def test_rejects_non_finite_constants(self) -> None:
        for constant in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(constant=constant):
                payload = b'{"value": ' + constant + b"}"
                with self.assertRaisesRegex(hygiene.JsonHygieneError, "non-finite JSON constant"):
                    hygiene.validate_json_bytes(payload, label="nan.json")

    def test_rejects_risky_keys_with_64_hex_digest(self) -> None:
        digest = "0123456789abcdef" * 4
        for risky_key in ("secret", "api_key", "key", "password", "auth_token", "private-key"):
            with self.subTest(risky_key=risky_key):
                payload = f'{{"{risky_key}": "{digest}"}}'.encode()
                with self.assertRaisesRegex(hygiene.JsonHygieneError, "Gitleaks"):
                    hygiene.validate_json_bytes(payload, label="risky.json")

    def test_rejects_risky_ancestor_with_nested_digest(self) -> None:
        digest = "fedcba9876543210" * 4
        payload = f'{{"input_secrets": {{"workflow.yml": "{digest}"}}}}'.encode()
        with self.assertRaisesRegex(hygiene.JsonHygieneError, "Gitleaks"):
            hygiene.validate_json_bytes(payload, label="nested.json")

    def test_rejects_invalid_utf8(self) -> None:
        with self.assertRaisesRegex(hygiene.JsonHygieneError, "invalid UTF-8"):
            hygiene.validate_json_bytes(b"\xff\xfe", label="bad-utf8.json")

    def test_staged_mode_reads_index_blob_instead_of_working_tree(self) -> None:
        with tempfile.TemporaryDirectory(prefix="json-hygiene-git-") as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            target = repo / "sample.json"
            bad_digest = "a" * 64
            target.write_text(f'{{"api_key": "{bad_digest}"}}\n', encoding="utf-8")
            subprocess.run(["git", "add", "sample.json"], cwd=repo, check=True)
            # Clean the working copy without restaging: --staged must still catch the index blob.
            target.write_text('{"model_sha256": "' + bad_digest + '"}\n', encoding="utf-8")
            self.assertEqual(hygiene.main(["--staged", "--root", str(repo)]), 1)

            # Now stage the clean file and confirm pass.
            subprocess.run(["git", "add", "sample.json"], cwd=repo, check=True)
            self.assertEqual(hygiene.main(["--staged", "--root", str(repo)]), 0)
