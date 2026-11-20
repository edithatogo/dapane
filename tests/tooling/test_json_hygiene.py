"""Tests for scripts/check_json_hygiene.py."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_json_hygiene", ROOT / "scripts/check_json_hygiene.py"
)
hygiene = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(hygiene)


@contextmanager
def staged_repository():
    with tempfile.TemporaryDirectory(prefix="json-hygiene-") as directory, patch.dict(os.environ):
        # A hook exports paths to its own checkout and index. Git lists each one.
        names = subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True)
        for name in names.splitlines():
            os.environ.pop(name, None)
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        yield root


class JsonHygieneTests(unittest.TestCase):
    def test_fixture_keeps_the_calling_repository_and_index_intact(self) -> None:
        with staged_repository() as parent:
            settings = {
                "GIT_DIR": str(parent / ".git"),
                "GIT_INDEX_FILE": str(parent / ".git/index"),
            }
            with patch.dict(os.environ, settings), staged_repository() as child:
                (child / "sample.json").write_text("{}")
                subprocess.run(["git", "add", "sample.json"], cwd=child, check=True)
                self.assertEqual(
                    subprocess.check_output(["git", "show", ":sample.json"], cwd=child), b"{}"
                )
            files = subprocess.check_output(["git", "ls-files"], cwd=parent)
            self.assertEqual(files, b"")
            bare = subprocess.check_output(["git", "rev-parse", "--is-bare-repository"], cwd=parent)
            self.assertEqual(bare.strip(), b"false")

    def test_accepts_valid_sha256_under_neutral_key(self) -> None:
        payload = b'{"model_sha256": "' + b"a" * 64 + b'", "status": "ok"}\n'
        hygiene.validate_json_bytes(payload, label="valid.json")

    def test_rejects_duplicate_object_keys(self) -> None:
        payload = b'{"id": "first", "id": "second"}'
        with self.assertRaisesRegex(
            hygiene.JsonHygieneError, r"dup\.json: duplicate JSON object key"
        ):
            hygiene.validate_json_bytes(payload, label="dup.json")

    def test_allows_duplicate_keys_only_when_explicitly_permitted(self) -> None:
        payload = b'{"id": "first", "id": "second"}'
        hygiene.validate_json_bytes(payload, label="dup.json", allow_duplicate_keys=True)

    def test_allow_duplicate_keys_still_rejects_non_finite_constants(self) -> None:
        payload = b'{"value": NaN}'
        with self.assertRaisesRegex(
            hygiene.JsonHygieneError, r"nan\.json: non-finite JSON constant"
        ):
            hygiene.validate_json_bytes(payload, label="nan.json", allow_duplicate_keys=True)

    def test_allow_duplicate_keys_scans_overwritten_risky_keys(self) -> None:
        digest = "0123456789abcdef" * 4
        payload = f'{{"api_key": "{digest}", "api_key": "safe"}}'.encode()
        with self.assertRaisesRegex(hygiene.JsonHygieneError, r"dup-risky\.json:.*Gitleaks"):
            hygiene.validate_json_bytes(payload, label="dup-risky.json", allow_duplicate_keys=True)

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
        with staged_repository() as repo:
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

    def test_staged_mode_duplicate_key_allowlist_and_secret_scan(self) -> None:
        with staged_repository() as repo:
            allowed = repo / "benchmarks/static/fixtures/cases/duplicate-json-key.json"
            allowed.parent.mkdir(parents=True, exist_ok=True)
            allowed.write_text('{"run_id": "a", "run_id": "b"}\n', encoding="utf-8")
            subprocess.run(["git", "add", str(allowed.relative_to(repo))], cwd=repo, check=True)
            self.assertEqual(hygiene.main(["--staged", "--root", str(repo)]), 0)

            other = repo / "other-dup.json"
            other.write_text('{"run_id": "a", "run_id": "b"}\n', encoding="utf-8")
            subprocess.run(["git", "add", "other-dup.json"], cwd=repo, check=True)
            self.assertEqual(hygiene.main(["--staged", "--root", str(repo)]), 1)
            subprocess.run(["git", "rm", "-q", "-f", "other-dup.json"], cwd=repo, check=True)

            bad_digest = "a" * 64
            allowed.write_text(
                f'{{"api_key": "{bad_digest}", "api_key": "safe"}}\n', encoding="utf-8"
            )
            subprocess.run(["git", "add", str(allowed.relative_to(repo))], cwd=repo, check=True)
            self.assertEqual(hygiene.main(["--staged", "--root", str(repo)]), 1)
