"""Adversarial notice provenance tests; synthetic archives are not release evidence."""

import contextlib
import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "distribution_notices", ROOT / "scripts/distribution_notices.py"
)
notices = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notices)
MIT = b"Copyright 2026 Synthetic Author\nPermission is hereby granted for this synthetic fixture.\n"
RUST = b"Synthetic standard-library attribution; not an actual Rust licence.\n"


class DistributionNoticeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.cache = Path(self.temporary.name) / "cargo-home"
        self.archive_dir = self.cache / "registry/cache/index.crates.io-fixture"
        self.archive_dir.mkdir(parents=True)
        (self.root / "crates/project").mkdir(parents=True)
        (self.root / "release").mkdir()
        (self.root / "licenses/rust-1.99.1").mkdir(parents=True)
        (self.root / "Cargo.toml").write_text(
            '[workspace]\nmembers = ["crates/project"]\n[workspace.package]\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        (self.root / "crates/project/Cargo.toml").write_text(
            '[package]\nname = "project"\nversion.workspace = true\n', encoding="utf-8"
        )
        (self.root / "rust-toolchain.toml").write_text(
            '[toolchain]\nchannel = "1.99.1"\n', encoding="utf-8"
        )
        self.rust_path = "licenses/rust-1.99.1/COPYRIGHT-library.txt"
        (self.root / self.rust_path).write_bytes(RUST)
        self.toolchain = {
            "format_version": "1",
            "rust_version": "1.99.1",
            "upstream_revision": "1" * 40,
            "coverage": "Synthetic standard-library notice fixture only.",
            "files": [
                {
                    "path": self.rust_path,
                    "sha256": hashlib.sha256(RUST).hexdigest(),
                    "source_url": "https://example.invalid/rust-fixture/COPYRIGHT-library.txt",
                }
            ],
        }
        self.save_toolchain()
        self.packages = []
        self.make_archive()

    def save_toolchain(self):
        (self.root / notices.TOOLCHAIN_PATH).write_text(
            json.dumps(self.toolchain), encoding="utf-8"
        )

    def save_lock(self):
        content = 'version = 4\n\n[[package]]\nname = "project"\nversion = "0.1.0"\n'
        for package in self.packages:
            content += "\n[[package]]\n"
            content += "".join(f"{key} = {json.dumps(value)}\n" for key, value in package.items())
        (self.root / "Cargo.lock").write_text(content, encoding="utf-8")

    def make_archive(self, name="dependency", files=None, manifest=None, extra=None):
        identity = f"{name}-1.0.0"
        if files is None:
            files = [("LICENSE-MIT", MIT)]
        if manifest is None:
            manifest = f'[package]\nname = "{name}"\nversion = "1.0.0"\nlicense = "MIT"\n'
        archive_path = self.archive_dir / f"{identity}.crate"
        with tarfile.open(archive_path, "w:gz") as archive:
            contents = [("Cargo.toml", manifest.encode()), *files]
            for path, data in contents:
                member = tarfile.TarInfo(f"{identity}/{path}")
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            if extra is not None:
                archive.addfile(extra)
        package = {
            "name": name,
            "version": "1.0.0",
            "source": notices.REGISTRY,
            "checksum": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        }
        self.packages = [p for p in self.packages if p["name"] != name] + [package]
        self.save_lock()
        return archive_path

    def build(self):
        return notices.build_outputs(self.root, self.cache)

    def assert_rejected(self, pattern):
        with self.assertRaisesRegex(notices.NoticeError, pattern):
            self.build()

    def test_legal_texts_and_source_hashes_are_preserved(self):
        output = self.build()
        self.assertIn(MIT, output[notices.NOTICE_PATH])
        self.assertIn(RUST, output[notices.NOTICE_PATH])
        manifest = json.loads(output[notices.MANIFEST_PATH])
        package = manifest["packages"][0]
        self.assertEqual(package["archive_sha256"], self.packages[0]["checksum"])
        self.assertEqual(package["legal_files"][0]["sha256"], hashlib.sha256(MIT).hexdigest())
        self.assertEqual(
            manifest["output"]["sha256"], hashlib.sha256(output[notices.NOTICE_PATH]).hexdigest()
        )

    def test_identical_text_is_shared_without_losing_package_attribution(self):
        self.make_archive(name="second")
        output = self.build()
        body = output[notices.NOTICE_PATH]
        self.assertEqual(body.count(MIT), 1)
        self.assertIn(b"dependency 1.0.0: LICENSE-MIT", body)
        self.assertIn(b"second 1.0.0: LICENSE-MIT", body)
        self.assertEqual(len(json.loads(output[notices.MANIFEST_PATH])["packages"]), 2)

    def test_unicode_llvm_and_nested_notices_are_kept(self):
        files = [
            ("LICENSE-MIT", MIT),
            ("LICENSE-UNICODE", b"Synthetic Unicode notice\n"),
            ("subcrate/NOTICE", b"Synthetic nested copyright\n"),
            ("LICENSES/LLVM-exception.txt", b"Synthetic LLVM exception\n"),
        ]
        self.make_archive(files=files)
        body = self.build()[notices.NOTICE_PATH]
        for _, data in files:
            self.assertIn(data, body)

    def test_manifest_license_file_with_nonstandard_name_is_included(self):
        self.make_archive(
            files=[("legal-terms.txt", MIT)],
            manifest='[package]\nname="dependency"\nversion="1.0.0"\nlicense="MIT"\nlicense-file="legal-terms.txt"\n',
        )
        self.assertIn(MIT, self.build()[notices.NOTICE_PATH])

    def test_unlicense_alternative_is_not_dropped_from_the_notice_bundle(self):
        alternative = b"Synthetic public-domain dedication\n"
        self.make_archive(files=[("LICENSE-MIT", MIT), ("UNLICENSE", alternative)])
        body = self.build()[notices.NOTICE_PATH]
        self.assertIn(MIT, body)
        self.assertIn(alternative, body)

    def test_mutable_extracted_cache_cannot_replace_authenticated_licence(self):
        extracted = self.cache / "registry/src/index.crates.io-fixture/dependency-1.0.0"
        extracted.mkdir(parents=True)
        (extracted / "LICENSE-MIT").write_text("untrusted replacement", encoding="utf-8")
        body = self.build()[notices.NOTICE_PATH]
        self.assertIn(MIT, body)
        self.assertNotIn(b"untrusted replacement", body)

    def test_missing_archive_is_rejected(self):
        (self.archive_dir / "dependency-1.0.0.crate").unlink()
        self.assert_rejected("expected one cached archive")

    def test_checksum_tampering_is_rejected(self):
        archive = self.archive_dir / "dependency-1.0.0.crate"
        archive.write_bytes(archive.read_bytes() + b"tampered")
        self.assert_rejected("Cargo.lock checksum mismatch")

    def test_ambiguous_registry_cache_is_rejected(self):
        other = self.cache / "registry/cache/other-index"
        other.mkdir()
        (other / "dependency-1.0.0.crate").write_bytes(
            (self.archive_dir / "dependency-1.0.0.crate").read_bytes()
        )
        self.assert_rejected("expected one cached archive")

    def test_archive_manifest_identity_must_match_lock(self):
        self.make_archive(manifest='[package]\nname="impostor"\nversion="1.0.0"\nlicense="MIT"\n')
        self.assert_rejected("archive manifest identity mismatch")

    def test_registry_source_and_lock_identity_cannot_be_substituted(self):
        self.packages[0]["source"] = "git+https://example.invalid/dependency"
        self.save_lock()
        self.assert_rejected("unreviewed package source")

    def test_local_dependency_cannot_be_silently_exempted_as_project_code(self):
        del self.packages[0]["source"]
        self.save_lock()
        self.assert_rejected("unattributed local package")

    def test_duplicate_lock_record_is_rejected(self):
        self.packages.append(dict(self.packages[0]))
        self.save_lock()
        self.assert_rejected("duplicate locked package")

    def test_empty_binary_missing_and_unreadable_legal_files_are_rejected(self):
        for files, pattern in [
            ([], "no licence or attribution files"),
            ([("LICENSE-MIT", b"")], "empty"),
            ([("LICENSE-MIT", b"  \n")], "empty"),
            ([("LICENSE-MIT", b"a\0b")], "binary"),
            ([("LICENSE-MIT", b"\xff")], "not UTF-8"),
        ]:
            with self.subTest(pattern=pattern, files=files):
                self.make_archive(files=files)
                self.assert_rejected(pattern)

    def test_copyright_or_author_list_does_not_replace_licence_terms(self):
        self.make_archive(files=[("NOTICE", b"Copyright 2026 Synthetic Author\n")])
        self.assert_rejected("attribution without a licence text")

    def test_archive_traversal_and_duplicate_member_are_rejected(self):
        self.make_archive(files=[("../LICENSE", MIT)])
        self.assert_rejected("unsafe")
        self.make_archive(files=[("LICENSE-MIT", MIT), ("LICENSE-MIT", b"substitution")])
        self.assert_rejected("duplicate archive path")

    def test_symlinked_legal_file_is_rejected_without_following_it(self):
        member = tarfile.TarInfo("dependency-1.0.0/NOTICE")
        member.type = tarfile.SYMTYPE
        member.linkname = "/etc/passwd"
        self.make_archive(extra=member)
        self.assert_rejected("missing, linked")

    def test_missing_declared_license_file_is_rejected(self):
        self.make_archive(
            manifest='[package]\nname="dependency"\nversion="1.0.0"\nlicense="MIT"\nlicense-file="absent.txt"\n'
        )
        self.assert_rejected("missing, linked")

    def test_missing_toolchain_file_and_wrong_hash_are_rejected(self):
        path = self.root / self.rust_path
        path.write_bytes(b"replacement")
        self.assert_rejected("toolchain notice checksum mismatch")
        path.unlink()
        self.assert_rejected("missing, linked or external")

    def test_toolchain_version_and_revision_are_required(self):
        self.toolchain["rust_version"] = "1.98.0"
        self.save_toolchain()
        self.assert_rejected("version differs")
        self.toolchain["rust_version"] = "1.99.1"
        self.toolchain["upstream_revision"] = "main"
        self.save_toolchain()
        self.assert_rejected("exact upstream revision")

    def test_toolchain_paths_cannot_escape_the_checkout(self):
        self.toolchain["files"][0]["path"] = "../outside"
        self.save_toolchain()
        self.assert_rejected("unsafe")

    def test_generation_is_deterministic_and_check_is_read_only(self):
        first = self.build()
        self.assertEqual(first, self.build())
        notices.write_outputs(self.root, first)
        before = {name: (self.root / name).stat().st_mtime_ns for name in first}
        notices.check_outputs(self.root, self.build())
        self.assertEqual(before, {name: (self.root / name).stat().st_mtime_ns for name in first})

    def test_stale_text_or_provenance_manifest_is_rejected(self):
        expected = self.build()
        for name in expected:
            with self.subTest(name=name):
                notices.write_outputs(self.root, expected)
                (self.root / name).write_bytes(b"stale")
                with self.assertRaisesRegex(notices.NoticeError, "stale generated"):
                    notices.check_outputs(self.root, self.build())

    def test_cli_failure_does_not_write_partially_generated_notices(self):
        (self.root / self.rust_path).unlink()
        with contextlib.redirect_stderr(io.StringIO()):
            status = notices.main(
                ["--write", "--root", str(self.root), "--cargo-home", str(self.cache)]
            )
        self.assertEqual(status, 1)
        self.assertFalse((self.root / notices.NOTICE_PATH).exists())
        self.assertFalse((self.root / notices.MANIFEST_PATH).exists())


if __name__ == "__main__":
    unittest.main()
