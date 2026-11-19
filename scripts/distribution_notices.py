#!/usr/bin/env python3
"""Reproduce distribution notices from authenticated Cargo archives and Rust notices.

This covers every registry package in Cargo.lock, including build dependencies.
It is deliberately a superset of linked code, not a linker inventory or permission
to redistribute provider assets. No package sources are extracted or executed.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
NOTICE_PATH = "THIRD_PARTY_NOTICES.txt"
MANIFEST_PATH = "release/distribution-notices.json"
TOOLCHAIN_PATH = "release/toolchain-notices.json"
LEGAL_NAME = re.compile(
    r"^(?:UNLICEN[SC]E|LICEN[SC]E|COPYING|COPYRIGHT|NOTICE|AUTHORS|PATENTS)(?:[._-].*)?$", re.I
)
LICENSE_NAME = re.compile(r"^(?:UNLICEN[SC]E|LICEN[SC]E|COPYING)(?:[._-].*)?$", re.I)
LEGAL_DIRECTORIES = {"license", "licenses", "licence", "licences"}
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
MAX_TEXT_BYTES = 8 * 1024 * 1024


class NoticeError(ValueError):
    """The available inputs do not establish the requested notice contents."""


def require(condition, message):
    if not condition:
        raise NoticeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def relative_path(value):
    require(isinstance(value, str) and value, "empty or non-string input path")
    path = PurePosixPath(value)
    require(
        path.parts
        and not path.is_absolute()
        and "\\" not in value
        and all(part not in {".", ".."} for part in path.parts)
        and str(path) == value,
        f"unsafe or non-canonical input path: {value!r}",
    )
    return path


def read_local(root, name):
    relative_path(name)
    path = root / name
    require(
        not path.is_symlink() and path.is_file() and path.resolve().is_relative_to(root.resolve()),
        f"missing, linked or external input: {name}",
    )
    return path.read_bytes()


def legal_text(data, label):
    require(0 < len(data) <= MAX_TEXT_BYTES, f"empty or oversized legal text: {label}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise NoticeError(f"legal text is not UTF-8: {label}") from error
    require(text.strip() and "\0" not in text, f"empty or binary legal text: {label}")
    return data


def workspace_inputs(root):
    names = {"Cargo.toml", "Cargo.lock", "rust-toolchain.toml", TOOLCHAIN_PATH}
    cargo = tomllib.loads(read_local(root, "Cargo.toml").decode())
    workspace = cargo["workspace"]
    members = set()
    for member in workspace["members"]:
        relative_path(member)
        name = f"{member}/Cargo.toml"
        names.add(name)
        package = tomllib.loads(read_local(root, name).decode())["package"]
        version = package["version"]
        if version == {"workspace": True}:
            version = workspace["package"]["version"]
        identity = (package["name"], version)
        require(identity not in members, f"duplicate workspace identity: {identity}")
        members.add(identity)
    lock = tomllib.loads(read_local(root, "Cargo.lock").decode())
    require(isinstance(lock.get("package"), list) and lock["package"], "empty Cargo.lock graph")
    identities = set()
    local = set()
    registry = []
    for package in lock["package"]:
        name, version = package["name"], package["version"]
        require(
            isinstance(name, str)
            and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]*", name)
            and isinstance(version, str)
            and re.fullmatch(r"[0-9][A-Za-z0-9.+-]*", version),
            f"invalid Cargo package identity: {name!r} {version!r}",
        )
        identity = (name, version, package.get("source"))
        require(identity not in identities, f"duplicate locked package: {name} {version}")
        identities.add(identity)
        if package.get("source") is None:
            local.add((name, version))
            continue
        require(package["source"] == REGISTRY, f"unreviewed package source: {identity}")
        require(
            isinstance(package.get("checksum"), str) and HEX64.fullmatch(package["checksum"]),
            f"missing or invalid registry checksum: {name} {version}",
        )
        registry.append(package)
    require(
        local == members, "unattributed local package or missing workspace package in Cargo.lock"
    )
    require(registry, "Cargo.lock contains no registry packages")
    return sorted(registry, key=lambda item: (item["name"], item["version"])), names


def legal_member(path):
    return bool(LEGAL_NAME.fullmatch(path.name)) or any(
        part.lower() in LEGAL_DIRECTORIES for part in path.parts[:-1]
    )


def read_archive(package, cargo_home):
    identity = f"{package['name']}-{package['version']}"
    candidates = sorted((cargo_home / "registry/cache").glob(f"*/{identity}.crate"))
    require(
        len(candidates) == 1, f"expected one cached archive for {identity}; found {len(candidates)}"
    )
    archive = candidates[0]
    require(
        not archive.is_symlink() and archive.is_file(), f"linked or invalid archive: {identity}"
    )
    archive_bytes = archive.read_bytes()
    actual_checksum = digest(archive_bytes)
    require(actual_checksum == package["checksum"], f"Cargo.lock checksum mismatch: {identity}")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as source:
        members = {}
        for member in source.getmembers():
            path = relative_path(member.name.removesuffix("/") if member.isdir() else member.name)
            require(path.parts[0] == identity, f"archive path outside package root: {member.name}")
            require(str(path) not in members, f"duplicate archive path: {member.name}")
            members[str(path)] = member

        def read_member(name):
            member = members.get(f"{identity}/{name}")
            require(
                member is not None and member.isfile() and 0 < member.size <= MAX_TEXT_BYTES,
                f"missing, linked, empty or oversized archive file: {identity}/{name}",
            )
            return source.extractfile(member).read()

        manifest = tomllib.loads(read_member("Cargo.toml").decode())["package"]
        require(
            (manifest.get("name"), manifest.get("version"))
            == (package["name"], package["version"]),
            f"archive manifest identity mismatch: {identity}",
        )
        expression = manifest.get("license")
        require(
            isinstance(expression, str) and expression.strip() and "\n" not in expression,
            f"missing licence declaration: {identity}",
        )
        selected = {
            str(PurePosixPath(name).relative_to(identity))
            for name, member in members.items()
            if len(PurePosixPath(name).parts) > 1
            and not member.isdir()
            and legal_member(PurePosixPath(name).relative_to(identity))
        }
        if manifest.get("license-file"):
            selected.add(str(relative_path(manifest["license-file"])))
        require(selected, f"no licence or attribution files in archive: {identity}")
        require(
            manifest.get("license-file")
            or any(
                LICENSE_NAME.fullmatch(PurePosixPath(name).name)
                or any(part.lower() in LEGAL_DIRECTORIES for part in PurePosixPath(name).parts[:-1])
                for name in selected
            ),
            f"attribution without a licence text in archive: {identity}",
        )
        texts = {
            name: legal_text(read_member(name), f"{identity}/{name}") for name in sorted(selected)
        }
        authors = manifest.get("authors", [])
        require(
            isinstance(authors, list) and all(isinstance(author, str) for author in authors),
            f"invalid authors declaration: {identity}",
        )
    return {
        "name": package["name"],
        "version": package["version"],
        "source": package["source"],
        "archive_sha256": actual_checksum,
        "license_expression": expression,
        "authors": authors,
        "legal_files": [
            {"path": name, "sha256": digest(data), "bytes": len(data)}
            for name, data in texts.items()
        ],
    }, texts


def read_toolchain(root):
    record = json.loads(read_local(root, TOOLCHAIN_PATH))
    pin = tomllib.loads(read_local(root, "rust-toolchain.toml").decode())["toolchain"]["channel"]
    require(record.get("format_version") == "1", "unknown toolchain notice format")
    require(record.get("rust_version") == pin, "toolchain notice version differs from Rust pin")
    require(
        isinstance(record.get("upstream_revision"), str)
        and HEX40.fullmatch(record["upstream_revision"]),
        "toolchain notices need an exact upstream revision",
    )
    require(
        isinstance(record.get("coverage"), str) and record["coverage"].strip(),
        "missing Rust notice scope",
    )
    require(isinstance(record.get("files"), list) and record["files"], "missing Rust notice files")
    texts = {}
    for entry in record["files"]:
        name = entry["path"]
        require(name not in texts, f"duplicate toolchain notice path: {name}")
        require(
            isinstance(entry.get("sha256"), str) and HEX64.fullmatch(entry["sha256"]),
            f"invalid toolchain notice digest: {name}",
        )
        require(
            isinstance(entry.get("source_url"), str) and entry["source_url"].startswith("https://"),
            f"missing toolchain notice source: {name}",
        )
        data = legal_text(read_local(root, name), name)
        require(digest(data) == entry["sha256"], f"toolchain notice checksum mismatch: {name}")
        texts[name] = data
    return record, texts


def build_outputs(root, cargo_home):
    packages, inputs = workspace_inputs(root)
    records = []
    unique_texts = {}
    uses = {}

    def retain(data, label):
        key = digest(data)
        require(key not in unique_texts or unique_texts[key] == data, "legal text digest collision")
        unique_texts[key] = data
        uses.setdefault(key, []).append(label)

    for package in packages:
        record, texts = read_archive(package, cargo_home)
        records.append(record)
        for name, data in texts.items():
            retain(data, f"{package['name']} {package['version']}: {name}")
    toolchain, rust_texts = read_toolchain(root)
    inputs.update(rust_texts)
    for name, data in rust_texts.items():
        retain(data, f"Rust {toolchain['rust_version']}: {name}")

    lines = [
        "Dapane third-party distribution notices",
        "======================================",
        "",
        "Generated by scripts/distribution_notices.py. Do not edit by hand.",
        "",
        "Scope: every registry package in Cargo.lock, including build dependencies,",
        "procedural macros and target-specific dependencies. This is a conservative",
        "superset, not a claim that every listed package is linked into every artifact.",
        "Upstream legal files are reproduced in full, with identical bytes deduplicated.",
        "Licence alternatives, additional conditions and attribution remain upstream's.",
        "Dapane's Apache-2.0 licence does not replace these terms.",
        "",
        "Rust standard-library coverage: " + toolchain["coverage"],
        "External system libraries, independently installed Python interpreters and",
        "provider data are not redistributed by this notice inventory.",
        "",
        "Registry package provenance",
        "===========================",
    ]
    for record in records:
        lines.extend(
            [
                "",
                f"Package: {record['name']} {record['version']}",
                f"Source: {record['source']}",
                f"Cargo archive SHA-256: {record['archive_sha256']}",
                f"Declared licence expression: {record['license_expression']}",
                "Authors declared upstream: " + json.dumps(record["authors"], ensure_ascii=False),
            ]
        )
        for entry in record["legal_files"]:
            lines.append(f"Legal file: {entry['path']} (SHA-256 {entry['sha256']})")
    lines.extend(
        [
            "",
            "Rust toolchain provenance",
            "========================",
            f"Rust version: {toolchain['rust_version']}",
            f"Upstream revision: {toolchain['upstream_revision']}",
        ]
    )
    for entry in sorted(toolchain["files"], key=lambda item: item["path"]):
        lines.extend(
            [
                f"Legal file: {entry['path']} (SHA-256 {entry['sha256']})",
                f"Source: {entry['source_url']}",
            ]
        )
    lines.extend(["", "Complete upstream legal texts", "=============================", ""])
    chunks = [("\n".join(lines)).encode()]
    for key, data in sorted(unique_texts.items()):
        header = ["", f"--- BEGIN LEGAL TEXT SHA-256 {key} ---", "Used by:"]
        header.extend(f"  {label}" for label in sorted(uses[key]))
        chunks.extend(
            [
                ("\n".join(header) + "\n\n").encode(),
                data,
                (f"\n--- END LEGAL TEXT SHA-256 {key} ---\n").encode(),
            ]
        )
    notices = b"".join(chunks)
    manifest = {
        "format_version": "1",
        "generator": "scripts/distribution_notices.py",
        "coverage": "all-locked-registry-packages-and-recorded-rust-standard-library-notices",
        "linkage_claim": "conservative-superset-not-an-exact-linker-inventory",
        "external_provider_assets": "excluded",
        "inputs": {name: digest(read_local(root, name)) for name in sorted(inputs)},
        "packages": records,
        "toolchain": toolchain,
        "unique_legal_texts": len(unique_texts),
        "output": {"path": NOTICE_PATH, "sha256": digest(notices), "bytes": len(notices)},
    }
    return {NOTICE_PATH: notices, MANIFEST_PATH: json_bytes(manifest)}


def write_outputs(root, outputs):
    for name, data in outputs.items():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                stream.write(data)
                stream.close()
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)


def check_outputs(root, outputs):
    for name, expected in outputs.items():
        require(read_local(root, name) == expected, f"stale generated distribution notices: {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--check", action="store_true", help="Compare both generated files without writing"
    )
    action.add_argument(
        "--write", action="store_true", help="Regenerate both files after all inputs pass"
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--cargo-home",
        type=Path,
        default=Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo")),
    )
    args = parser.parse_args(argv)
    try:
        outputs = build_outputs(args.root, args.cargo_home)
        if args.write:
            write_outputs(args.root, outputs)
        else:
            check_outputs(args.root, outputs)
        manifest = json.loads(outputs[MANIFEST_PATH])
        print(
            json.dumps(
                {
                    "status": "written" if args.write else "verified",
                    "registry_packages": len(manifest["packages"]),
                    "unique_legal_texts": manifest["unique_legal_texts"],
                    "notice_sha256": manifest["output"]["sha256"],
                    "rust_version": manifest["toolchain"]["rust_version"],
                },
                sort_keys=True,
            )
        )
        return 0
    except (NoticeError, OSError, KeyError, TypeError, ValueError, tarfile.TarError) as error:
        print(f"Distribution notice verification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
