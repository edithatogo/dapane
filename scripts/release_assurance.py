#!/usr/bin/env python3
"""Check candidate release evidence without publishing or certifying providers.

Receipts bind locally checked artifacts to the exact clean checkout, installed
wheel bytes and independent synthetic references. They are not signatures,
registry entitlements, empirical validation or a substitute for required CI jobs.
"""

import argparse
import base64
import csv
import hashlib
import importlib
import importlib.machinery
import importlib.metadata
import io
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from copy import deepcopy
from datetime import UTC, datetime
from email.parser import Parser
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FORMAT = "dapane-release-evidence/1"
PROFILES = {"0.1": "dapane-exact-v0.1.0", "0.2": "dapane-exact-v0.2.0"}
ADDITIONAL_PROFILES = {
    "intervals": {
        "schema_version": "0.1",
        "method_version": "dapane-intervals-v0.1.0",
        "interfaces": ["Rust", "CLI"],
    },
    "run_bundle": {
        "schema_version": "0.1",
        "interfaces": ["repository-verifier"],
        "valuation_profiles": ["0.1", "0.2"],
    },
}
PROJECT_LICENSE = "Apache-2.0"
LICENSE_FILES = {"LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.txt"}
APACHE_LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
SOURCE_REDISTRIBUTION = "project-source-Apache-2.0-external-assets-excluded"
PROVIDER_STATES = {
    "workforce_provider": "qualified-selected-qld-hp3p1-base-salary",
    "genomics_provider": "qualified-manual-extraction-labour",
}
PROVIDER_PROFILES = {
    "lock_file": "docs/provider-consumers.lock.json",
    "qualification_record": "docs/python-provider-verification.md",
    "workforce_scope": "selected-quotation-and-retained-legacy-entry-points",
    "genomics_scope": "manual-dna-extraction-labour-and-bounded-historical-replay",
    "environments": "separate-locked-provider-environments",
    "source_asset_redistribution": "excluded",
}
TRACKS = {
    "core_contracts_20261108",
    "rust_kernel_20261108",
    "python_two_consumers_20261108",
}
CAPABILITIES = {
    "rust-core",
    "json-cli",
    "python-native",
    "synthetic-workforce",
    "synthetic-genomics",
    "partial-capacity",
    "declared-calendar-day-intervals",
    "versioned-run-bundles",
    "installed-workforce-quotation-consumer",
    "installed-manual-extraction-consumer",
}
PYTHONS = {"3.15.1"}


class AssuranceError(ValueError):
    """A missing or inconsistent qualification input."""


def require(condition, message):
    if not condition:
        raise AssuranceError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode_json(text):
    def invalid_constant(value):
        raise AssuranceError(f"non-finite JSON number: {value}")

    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def read_json(path):
    return decode_json(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def command(args, cwd=ROOT):
    return subprocess.run(
        args, cwd=cwd, check=True, capture_output=True, text=True, timeout=120
    ).stdout.strip()


def source_identity(root=ROOT):
    require(
        not command(["git", "status", "--porcelain", "--untracked-files=all"], root),
        "source is dirty or has untracked inputs; commit the tested inputs first",
    )
    return {
        "commit": command(["git", "rev-parse", "HEAD"], root),
        "tree": command(["git", "rev-parse", "HEAD^{tree}"], root),
        "epoch": int(command(["git", "show", "-s", "--format=%ct", "HEAD"], root)),
    }


def input_hashes(root=ROOT):
    # The commit/tree identifies all tracked implementation. Explicit hashes
    # make the release configuration, reference inputs and tool pins inspectable.
    names = {
        "Cargo.toml",
        "Cargo.lock",
        "pyproject.toml",
        "rust-toolchain.toml",
        "requirements-dev.txt",
        "requirements-release.txt",
        "deny.toml",
        ".python-version",
        ".github/actions/project-python/action.yml",
        ".github/workflows/release-assurance.yml",
        "release/capabilities.json",
        "scripts/release_assurance.py",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.txt",
        "scripts/distribution_notices.py",
        "release/distribution-notices.json",
        "release/toolchain-notices.json",
        "docs/provider-consumers.lock.json",
        "scripts/verify_provider_consumers.py",
        ".github/workflows/provider-consumers.yml",
    }
    names.update(str(p.relative_to(root)) for p in (root / "fixtures").rglob("*.json"))
    names.update(str(p.relative_to(root)) for p in (root / "schemas").rglob("*.json"))
    names.update(str(p.relative_to(root)) for p in (root / "licenses").rglob("*") if p.is_file())
    tracked = set(command(["git", "ls-files"], root).splitlines())
    require(names <= tracked, "release inputs must all be tracked")
    return {name: sha256(root / name) for name in sorted(names)}


def target_key(target):
    return tuple(target[k] for k in ("system", "machine", "implementation", "python"))


def validate_provider_lock(pins):
    require(pins.get("schema_version") == "1", "unknown provider lock format")
    require(pins.get("qualification") == "passed", "provider qualification is incomplete")
    expected = {
        "workforce": ("edithatogo/microcosting_healthworkforce", "3.15.2"),
        "genomics": ("edithatogo/microcosting_genomics", "3.15.1"),
    }
    for name, (repository, python) in expected.items():
        provider = pins.get(name, {})
        require(
            provider.get("repository") == repository and provider.get("python") == python,
            f"{name} provider owner or interpreter changed",
        )
        commit = provider.get("commit")
        require(
            isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit),
            f"{name} provider needs an immutable commit",
        )
    artifact = pins["workforce"].get("artifact_sha256")
    require(
        isinstance(artifact, str) and re.fullmatch(r"[0-9a-f]{64}", artifact),
        "workforce quotation artifact needs an external digest pin",
    )


def validate_manifest(manifest, root=ROOT):
    require(manifest["format_version"] == "1", "unknown capability manifest format")
    require(manifest["channel"] == "unpublished-candidate", "unsupported release channel")
    require(manifest["profiles"] == PROFILES, "contract/method pairing changed")
    require(
        manifest["additional_profiles"] == ADDITIONAL_PROFILES,
        "additional profile or interface claims changed",
    )
    require(
        manifest.get("provider_consumers") == PROVIDER_PROFILES,
        "provider capability scope exceeds the qualified profiles",
    )
    validate_provider_lock(read_json(root / PROVIDER_PROFILES["lock_file"]))
    capabilities = manifest["candidate_capabilities"]
    require(
        len(capabilities) == len(CAPABILITIES) and set(capabilities) == CAPABILITIES,
        "candidate capabilities need explicit implementation and reference coverage",
    )
    require(
        (root / ".python-version").read_text().strip() in PYTHONS,
        "project interpreter differs from the release target",
    )
    targets = manifest["targets"]
    require(len(targets) == len(PYTHONS), "unexpected number of interpreter targets")
    require(
        {target_key(t) for t in targets} == {("Linux", "x86_64", "CPython", p) for p in PYTHONS},
        "missing, duplicate or unsupported platform/interpreter target",
    )
    require(
        all(t["runner"] == "ubuntu-24.04" and t["abi"] == "interpreter-specific" for t in targets),
        "runner and ABI claims exceed the candidate matrix",
    )
    require(
        len(manifest["required_tracks"]) == len(TRACKS)
        and set(manifest["required_tracks"]) == TRACKS,
        "contracts, kernel and both real consumers remain release prerequisites",
    )
    require(not (set(manifest["optional_tracks"]) & TRACKS), "required track marked optional")
    require(manifest["publication"]["enabled"] is False, "this workflow cannot enable publication")
    require(
        manifest["source_rights"]["external_provider_assets"] == "excluded",
        "provider data needs a separate rights and inclusion review",
    )
    require(
        manifest["consolidation"]
        == {"selected_archives": [], "remove_duplicated_machinery": False},
        "repository archives/removals need their own qualified scope",
    )
    workspace = tomllib.loads((root / "Cargo.toml").read_text())["workspace"]
    python = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    require(
        manifest["package"] == {"name": python["name"], "version": workspace["package"]["version"]},
        "candidate package identity differs from manifests",
    )
    require(workspace["package"]["publish"] is False, "Cargo publication guard changed")
    require(python.get("dependencies", []) == [], "Python runtime dependencies changed")
    require(
        workspace["package"].get("license")
        == manifest["publication"].get("project_license")
        == PROJECT_LICENSE,
        "project licence differs across package and capability manifests",
    )
    require(
        python.get("license") is None and "license" not in python.get("dynamic", []),
        "aggregate distribution licence must not be inferred from the project licence",
    )
    require(
        set(python.get("license-files", [])) == LICENSE_FILES,
        "Python licence files must include LICENSE, NOTICE and third-party notices",
    )
    require(
        (root / "LICENSE").is_file() and sha256(root / "LICENSE") == APACHE_LICENSE_SHA256,
        "LICENSE must contain the complete Apache-2.0 licence text",
    )
    require((root / "NOTICE").is_file() and (root / "NOTICE").stat().st_size, "NOTICE is missing")
    for member in workspace["members"]:
        package = tomllib.loads((root / member / "Cargo.toml").read_text())["package"]
        require(package.get("license") == {"workspace": True}, f"{member} must inherit the licence")
        for name in LICENSE_FILES:
            path = root / member / name
            require(
                path.is_file()
                and not path.is_symlink()
                and path.read_bytes() == (root / name).read_bytes(),
                f"{member}/{name} must match the project licence/notice",
            )
    return manifest


def publication_blockers(manifest, root=ROOT):
    blockers = ["Package publication is not enabled by this candidate-assurance workflow."]
    resolved = {
        "project_license": PROJECT_LICENSE,
        "source_redistribution": SOURCE_REDISTRIBUTION,
        **PROVIDER_STATES,
    }
    for name, state in manifest["publication"].items():
        if name != "enabled" and (name not in resolved or resolved[name] != state):
            blockers.append(f"{name}: {state}")
    for track in sorted(TRACKS):
        metadata = read_json(root / "conductor/tracks" / track / "metadata.json")
        if metadata["status"] not in {"completed", "archived"}:
            blockers.append(f"required track {track}: {metadata['status']}")
    return blockers


def file_record(path, role):
    require(path.is_file() and not path.is_symlink(), f"missing or linked artifact: {path}")
    require(path.stat().st_size > 0, f"empty artifact: {path}")
    return {"role": role, "name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def verify_artifacts(records, directory):
    require(
        len(records) == 2 and {r["role"] for r in records} == {"cli", "wheel"},
        "exactly one CLI and one wheel are required",
    )
    require(len({r["name"] for r in records}) == 2, "duplicate artifact name")
    for record in records:
        name = record["name"]
        require(
            isinstance(name, str)
            and name not in {"", ".", ".."}
            and PurePosixPath(name).name == name
            and "\\" not in name,
            "artifact path must be a plain filename",
        )
        require(
            file_record(directory / name, record["role"]) == record, f"artifact changed: {name}"
        )


def verify_artifact_notices(directory, root=ROOT):
    for name in LICENSE_FILES:
        path = directory / name
        require(
            path.is_file()
            and not path.is_symlink()
            and path.read_bytes() == (root / name).read_bytes(),
            f"CLI distribution licence/notice differs: {name}",
        )


def candidate_artifacts(directory):
    wheels = list(directory.glob("*.whl"))
    require(len(wheels) == 1, f"expected exactly one wheel in {directory}")
    return [
        file_record(directory / "dapane", "cli"),
        file_record(wheels[0], "wheel"),
    ]


def compare_artifacts(first, second):
    require(first.resolve() != second.resolve(), "clean builds need distinct artifact directories")
    left, right = candidate_artifacts(first), candidate_artifacts(second)
    require(left == right, "clean builds produced different CLI/wheel bytes or names")
    return left


def verify_wheel_members(wheel, installed, version):
    """Check all wheel members and compare installed package/metadata bytes."""
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate wheel member")
        require(
            all(
                not PurePosixPath(n).is_absolute()
                and ".." not in PurePosixPath(n).parts
                and "\\" not in n
                for n in names
            ),
            "unsafe wheel member path",
        )
        metadata_names = [n for n in names if n.endswith(".dist-info/METADATA")]
        require(len(metadata_names) == 1, "expected one wheel distribution")
        metadata_name = metadata_names[0]
        metadata = Parser().parsestr(archive.read(metadata_name).decode())
        require(metadata["Name"] == "dapane", "wheel package is not dapane")
        require(metadata["Version"] == version, "wheel package version differs")
        require(not metadata.get_all("Requires-Dist"), "wheel has runtime dependencies")
        dist_info = metadata_name.rsplit("/", 1)[0]
        require(
            metadata["License-Expression"] is None and metadata["License"] is None,
            "wheel aggregate licence must not be inferred from project licensing",
        )
        require(
            set(metadata.get_all("License-File", [])) == LICENSE_FILES,
            "wheel licence declarations must include project and third-party notices",
        )
        for name in LICENSE_FILES:
            member = f"{dist_info}/licenses/{name}"
            require(
                member in names and archive.read(member) == (ROOT / name).read_bytes(),
                f"wheel licence payload differs: {name}",
            )
        record_name = f"{dist_info}/RECORD"
        rows = list(csv.reader(io.StringIO(archive.read(record_name).decode())))
        require(
            all(len(row) == 3 for row in rows) and len({r[0] for r in rows}) == len(rows),
            "invalid wheel RECORD",
        )
        records = {row[0]: row[1:] for row in rows}
        require(
            set(records) == {n for n in names if not n.endswith("/")}, "incomplete wheel RECORD"
        )
        require(
            all(n.startswith(("dapane/", "dapane.libs/", dist_info + "/")) for n in names),
            "unsupported wheel layout requires explicit installation mapping",
        )
        wheel_metadata = Parser().parsestr(archive.read(f"{dist_info}/WHEEL").decode())
        require(wheel_metadata["Root-Is-Purelib"] == "false", "wheel must contain native code")
        tags = wheel_metadata.get_all("Tag", [])
        require(
            tags
            and all(
                len(parts := tag.split("-")) == 3
                and parts[0].startswith("cp")
                and parts[0] == parts[1]
                and parts[0][2:].isdigit()
                and parts[2].endswith("x86_64")
                for tag in tags
            ),
            "wheel ABI or architecture exceeds interpreter-specific x86_64 scope",
        )
        package_names = [n for n in names if n.startswith("dapane/") and not n.endswith("/")]
        require("dapane/__init__.py" in package_names, "wheel package is missing")
        for name, (digest, length) in records.items():
            if name == record_name:
                require(digest == length == "", "RECORD must not hash itself")
                continue
            data = archive.read(name)
            expected = "sha256=" + base64.urlsafe_b64encode(
                hashlib.sha256(data).digest()
            ).decode().rstrip("=")
            require(digest == expected and length == str(len(data)), f"bad wheel RECORD: {name}")
            if not name.endswith("/"):
                path = installed / name
                require(
                    path.resolve().is_relative_to(installed.resolve()),
                    "installed file escapes prefix",
                )
                require(
                    path.is_file() and path.read_bytes() == data,
                    f"installed wheel bytes differ: {name}",
                )
        return package_names


def verify_wheel_target(wheel, runtime):
    """Bind the recorded interpreter to the artifact's native wheel tags."""
    require(runtime["implementation"] == "CPython", "wheel needs CPython evidence")
    require(
        runtime["system"] == "Linux" and runtime["machine"] == "x86_64",
        "wheel target is outside the candidate platform",
    )
    interpreter = "cp" + "".join(runtime["python"].split(".")[:2])
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if n.endswith(".dist-info/WHEEL")]
        require(len(names) == 1, "expected one WHEEL metadata record")
        metadata = Parser().parsestr(archive.read(names[0]).decode())
    tags = metadata.get_all("Tag", [])
    require(
        metadata["Root-Is-Purelib"] == "false"
        and tags
        and all(
            len(parts := tag.split("-")) == 3
            and parts[0] == parts[1] == interpreter
            and re.fullmatch(r"(linux|manylinux(?:\d+|_\d+_\d+))_x86_64", parts[2])
            for tag in tags
        ),
        "wheel tags do not match the recorded interpreter/platform",
    )


def verify_dependency_versions(dependencies, manifest, root=ROOT):
    names = [p["name"] for p in dependencies]
    require(
        len(names) == len(set(names))
        and {"dapane-core", "dapane-cli"} <= set(names)
        and not any(
            name == prefix or name.startswith(prefix + "-")
            for name in names
            for prefix in ("pyo3", "polars", "arrow", "kairos", "process_mining")
        ),
        "missing or non-minimal native dependency evidence",
    )
    locked = tomllib.loads((root / "Cargo.lock").read_text())["package"]
    allowed = {(p["name"], p["version"]) for p in locked}
    require(
        all((p["name"], p["version"]) in allowed for p in dependencies),
        "dependency evidence does not match Cargo.lock",
    )
    require(
        all(
            p["version"] == manifest["package"]["version"]
            for p in dependencies
            if p["name"] in {"dapane-core", "dapane-cli"}
        ),
        "native workspace version differs from candidate",
    )


def installed_identity(wheel, root, manifest):
    require(not Path.cwd().resolve().is_relative_to(root), "run collection outside the checkout")
    module = importlib.import_module("dapane")
    native = importlib.import_module("dapane._native")
    distribution = importlib.metadata.distribution("dapane")
    prefix = Path(distribution.locate_file("")).resolve()
    require(not prefix.is_relative_to(root), "source-tree installation cannot qualify a wheel")
    require(
        distribution.version == manifest["package"]["version"],
        "installed distribution version differs",
    )
    require(not distribution.requires, "installed distribution has runtime dependencies")
    members = verify_wheel_members(wheel, prefix, distribution.version)
    for loaded in (module, native):
        path = Path(loaded.__file__).resolve()
        require(path.is_relative_to(prefix), "import did not resolve to installed distribution")
        require(str(path.relative_to(prefix)) in members, "import is absent from supplied wheel")
    require(
        any(str(native.__file__).endswith(s) for s in importlib.machinery.EXTENSION_SUFFIXES),
        "native extension was not loaded",
    )
    forbidden = {"pandas", "polars", "pyarrow", "kairos"}
    require(not (forbidden & set(sys.modules)), "optional modules imported by minimal package")
    return module, {
        "distribution": distribution.metadata["Name"],
        "version": distribution.version,
        "requires_dist": distribution.requires or [],
        "package": str(Path(module.__file__).relative_to(prefix)),
        "native": str(Path(native.__file__).relative_to(prefix)),
        "verified_wheel_members": len(members),
    }


def core_dependencies(root=ROOT):
    metadata = decode_json(
        command(["cargo", "metadata", "--locked", "--format-version", "1"], root)
    )
    packages = {p["id"]: p for p in metadata["packages"]}
    nodes = {n["id"]: n for n in metadata["resolve"]["nodes"]}
    pending = list(metadata["workspace_default_members"])
    require(
        {packages[p]["name"] for p in pending} == {"dapane-core", "dapane-cli"},
        "default workspace members changed",
    )
    seen = set()
    while pending:
        identifier = pending.pop()
        if identifier not in seen:
            seen.add(identifier)
            pending.extend(d["pkg"] for d in nodes[identifier]["deps"])
    names = {packages[p]["name"] for p in seen}
    forbidden = ("pyo3", "polars", "arrow", "kairos", "process_mining")
    require(
        not any(n == f or n.startswith(f + "-") for n in names for f in forbidden),
        "minimal native dependency closure includes an optional runtime",
    )
    return sorted(
        ({"name": packages[p]["name"], "version": packages[p]["version"]} for p in seen),
        key=lambda p: (p["name"], p["version"]),
    )


def reference_cases(root=ROOT):
    cases = {}
    groups = (
        ("fixtures", "fixtures", "base"),
        ("fixtures/genomics-capacity", "cases", "capacity"),
    )
    for directory, key, kind in groups:
        expected_path = root / directory / "expected.json"
        for name, expected in read_json(expected_path)[key].items():
            path = f"{directory}/{name}"
            cases[path] = (kind, expected, read_json(root / path))
    require(len(cases) >= 10, "base and capacity references are required")
    return cases


def fields(actual, expected, label):
    require(
        all(key in actual and actual[key] == value for key, value in expected.items()),
        f"independent reference mismatch: {label}",
    )


def indexed(records, key):
    result = {r[key]: r for r in records}
    require(len(result) == len(records), f"duplicate reference result {key}")
    return result


def normalize_request(request):
    """Independent contract 0.1/0.2 identity normalization, without valuation."""
    result = deepcopy(request)
    optional = ("objects", "processes", "events", "object_relations", "allocations")
    for name in optional:
        result.setdefault(name, [])
    for quote in result["quotes"]:
        quote["components"].sort()
    source_records = [*result["quotes"], *result["usage"], *result.get("capacity_allocations", [])]
    for record in source_records:
        record["source"].setdefault("content_digest", None)
        record["source"].setdefault("locator", None)
    for usage in result["usage"]:
        for key in ("event_id", "process_id", "activity_id", "attribution_object_id"):
            usage.setdefault(key, None)
        usage.setdefault("object_ids", [])
        usage["object_ids"].sort()
    for event in result["events"]:
        event.setdefault("process_id", None)
        event.setdefault("activity_id", None)
        event.setdefault("object_ids", [])
        event["object_ids"].sort()
    for name in ("quotes", "usage", "objects", "processes", "events", "allocations"):
        result[name].sort(key=lambda row: row["id"])
    result["object_relations"].sort(
        key=lambda row: (row["from_object_id"], row["to_object_id"], row["relationship"])
    )
    for allocation in result["allocations"]:
        allocation["source_line_ids"].sort()
        allocation["weights"].sort(key=lambda row: row["object_id"])
    if result.get("capacity_allocations"):
        result["capacity_allocations"].sort(key=lambda row: row["id"])
        for allocation in result["capacity_allocations"]:
            allocation["source_line_ids"].sort()
            allocation["use_records"].sort(key=lambda row: row["object_id"])
    else:
        result.pop("capacity_allocations", None)
    return result


def check_provenance(report, request):
    normalized = normalize_request(request)
    version = normalized["schema_version"]
    digest = hashlib.sha256(
        f"dapane:input:{version}\n".encode() + canonical(normalized)
    ).hexdigest()
    require(report["input_digest"] == f"sha256:{digest}", "report input identity changed")
    require(report["policy"] == normalized["policy"], "report policy changed")
    require(report["quote_snapshots"] == normalized["quotes"], "quote/source snapshot changed")
    require(
        report["context"]
        == {key: normalized[key] for key in ("objects", "processes", "events", "object_relations")},
        "report context changed",
    )
    usage = indexed(normalized["usage"], "id")
    events = indexed(normalized["events"], "id")
    lines = indexed(report["lines"], "id")
    require(set(lines) == set(usage), "report usage identities changed")
    for name, row in usage.items():
        provenance = {key: value for key, value in row.items() if key != "quantity"}
        event = events.get(provenance["event_id"], {})
        for key in ("process_id", "activity_id"):
            if provenance[key] is None:
                provenance[key] = event.get(key)
        fields(lines[name], provenance, "usage provenance")
    capacities = indexed(normalized.get("capacity_allocations", []), "id")
    results = indexed(report.get("capacity_allocations", []), "id")
    require(set(capacities) == set(results), "capacity identity changed")
    for name, row in capacities.items():
        fields(
            results[name],
            {
                key: row[key]
                for key in ("source", "source_line_ids", "unit", "observation_coverage")
            },
            "capacity source provenance",
        )


def check_reference(report, kind, expected, request):
    check_provenance(report, request)
    version = request["schema_version"]
    require(report["status"] == "complete", "partial report cannot qualify a candidate")
    require(report["schema_version"] == version, "report schema changed")
    require(report["method_version"] == PROFILES[version], "report method changed")
    require(report["run_id"] == request["run_id"], "report run identity changed")
    if kind == "base":
        fields(report["totals"], expected["totals"], "totals")
        for group, identity in (
            ("lines", "id"),
            ("object_totals", "object_id"),
            ("allocations", "id"),
        ):
            actual = indexed(report[group], identity)
            require(set(actual) == set(expected[group]), f"reference members changed: {group}")
            for name, values in expected[group].items():
                fields(actual[name], {k: v for k, v in values.items() if k != "shares"}, name)
                if "shares" in values:
                    shares = indexed(actual[name]["shares"], "object_id")
                    require(set(shares) == set(values["shares"]), "reference recipients changed")
                    for recipient, amounts in values["shares"].items():
                        fields(shares[recipient], amounts, recipient)
    else:
        fields(
            report["totals"],
            {
                "rounded": expected["total"],
                "allocated": expected["allocated"],
                "unattributed": expected["unattributed"],
            },
            "capacity totals",
        )
        pools = report["capacity_allocations" if version == "0.2" else "allocations"]
        require(len(pools) == 1, "reference capacity pool count changed")
        pool = pools[0]
        fields(
            pool,
            {
                "pool_rounded": expected["pool"],
                "unallocated" if version == "0.2" else "residual": expected["unallocated"],
            },
            "capacity pool",
        )
        shares = indexed(pool["shares"], "object_id")
        require(
            {k: v["rounded"] for k, v in shares.items()} == expected["shares"],
            "capacity unknown/allocated shares differ",
        )
    payload = {k: v for k, v in report.items() if k != "output_digest"}
    digest = hashlib.sha256(f"dapane:output:{version}\n".encode() + canonical(payload)).hexdigest()
    require(report["output_digest"] == f"sha256:{digest}", "result digest differs")


def runtime_target(runtime):
    return (
        runtime["system"],
        runtime["machine"],
        runtime["implementation"],
        runtime["python"],
    )


def collect(cli, wheel, output, root=ROOT):
    manifest = validate_manifest(read_json(root / "release/capabilities.json"), root)
    source = source_identity(root)
    artifacts = [file_record(cli, "cli"), file_record(wheel, "wheel")]
    verify_artifact_notices(cli.parent, root)
    module, installation = installed_identity(wheel, root, manifest)
    runtime = {
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "libc": list(platform.libc_ver()),
        "rustc": command(["rustc", "--version", "--verbose"]),
        "cargo": command(["cargo", "--version"]),
    }
    require(
        runtime_target(runtime) in {target_key(t) for t in manifest["targets"]},
        "executed target is outside the candidate matrix",
    )
    verify_wheel_target(wheel, runtime)
    require(
        command([str(cli), "--version"], Path.cwd()).split()[:2]
        == ["dapane", manifest["package"]["version"]],
        "CLI version differs from candidate",
    )
    references = {}
    with tempfile.TemporaryDirectory(prefix="dapane-release-consumer-") as temp:
        for name, (kind, expected, request) in reference_cases(root).items():
            report = decode_json(command([str(cli), "evaluate", str(root / name)], Path(temp)))
            python_report = decode_json(module.evaluate_json((root / name).read_text()))
            require(report == python_report, f"CLI/Python parity failed: {name}")
            require(
                report["engine_version"] == manifest["package"]["version"], "engine version changed"
            )
            check_reference(report, kind, expected, request)
            references[name] = report
    result = {
        "format": FORMAT,
        "purpose": "unpublished-candidate-verification",
        "publication_ready": False,
        "source": source,
        "inputs": input_hashes(root),
        "created_at": datetime.now(UTC).isoformat(),
        "ci": {
            k: os.environ.get(k)
            for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_EVENT_NAME")
        },
        "runtime": runtime,
        "artifacts": artifacts,
        "installed_python": installation,
        "minimal_native_dependencies": core_dependencies(root),
        "references": references,
        "publication_blockers": publication_blockers(manifest, root),
        "limits": (
            "This receipt covers package identity and synthetic scalar/capacity references. "
            "Selected-provider qualification runs separately using these exact artifacts; "
            "no whole-assay, empirical, other-platform or publication qualification is implied."
        ),
    }
    write_json(output, result)
    print(
        json.dumps(
            {
                "source_commit": source["commit"],
                "target": runtime_target(runtime),
                "artifacts": artifacts,
                "independent_reference_cases": len(references),
                "publication_ready": False,
            },
            indent=2,
        )
    )


def verify_evidence(evidence, artifact_dir, root=ROOT):
    manifest = validate_manifest(read_json(root / "release/capabilities.json"), root)
    require(evidence["format"] == FORMAT, "unknown evidence format")
    require(
        evidence["purpose"] == "unpublished-candidate-verification"
        and evidence["publication_ready"] is False,
        "candidate evidence cannot establish publication readiness",
    )
    require(
        evidence["source"] == source_identity(root), "evidence belongs to another source revision"
    )
    require(
        evidence["inputs"] == input_hashes(root), "evidence input/lock/reference hashes changed"
    )
    require(
        runtime_target(evidence["runtime"]) in {target_key(t) for t in manifest["targets"]},
        "unsupported evidence target",
    )
    verify_artifacts(evidence["artifacts"], artifact_dir)
    verify_artifact_notices(artifact_dir, root)
    wheel = next(r for r in evidence["artifacts"] if r["role"] == "wheel")
    verify_wheel_target(artifact_dir / wheel["name"], evidence["runtime"])
    comparison = read_json(artifact_dir / "reproducibility.json")
    require(
        comparison["format"] == "dapane-build-comparison/1"
        and comparison["source"] == evidence["source"]
        and comparison["artifacts"] == evidence["artifacts"]
        and comparison["identical"] is True
        and comparison["comparison"] == "two-clean-builds-same-runner",
        "missing or inconsistent clean-build comparison evidence",
    )
    require(
        evidence["installed_python"]["version"] == manifest["package"]["version"]
        and evidence["installed_python"]["requires_dist"] == []
        and evidence["installed_python"]["verified_wheel_members"] > 1,
        "missing minimal installed-wheel evidence",
    )
    cases = reference_cases(root)
    require(set(evidence["references"]) == set(cases), "missing or extra reference result")
    for name, (kind, expected, request) in cases.items():
        require(
            evidence["references"][name]["engine_version"] == manifest["package"]["version"],
            "saved report engine version differs from candidate",
        )
        check_reference(evidence["references"][name], kind, expected, request)
    verify_dependency_versions(evidence["minimal_native_dependencies"], manifest, root)
    return runtime_target(evidence["runtime"])


def verify_matrix_targets(actual, manifest):
    require(
        len(actual) == len(set(actual))
        and set(actual) == {target_key(t) for t in manifest["targets"]},
        "missing, duplicate or unsupported executed matrix target",
    )


def verify_matrix(directory, root=ROOT):
    manifest = validate_manifest(read_json(root / "release/capabilities.json"), root)
    paths = list(directory.rglob("evidence.json"))
    targets = [verify_evidence(read_json(p), p.parent, root) for p in paths]
    verify_matrix_targets(targets, manifest)
    return len(paths)


def write_json(path, value):
    require(not path.exists(), f"refusing to overwrite an existing evidence record: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--publication", action="store_true")
    gather = commands.add_parser("collect")
    gather.add_argument("--cli", type=Path, required=True)
    gather.add_argument("--wheel", type=Path, required=True)
    gather.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--evidence", type=Path, required=True)
    verify.add_argument("--artifact-dir", type=Path, required=True)
    matrix = commands.add_parser("verify-matrix")
    matrix.add_argument("--directory", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.operation == "validate":
            manifest = validate_manifest(read_json(ROOT / "release/capabilities.json"))
            if args.publication:
                print(
                    json.dumps(
                        {"publication_ready": False, "blockers": publication_blockers(manifest)},
                        indent=2,
                    )
                )
                return 2
        elif args.operation == "collect":
            collect(args.cli.resolve(), args.wheel.resolve(), args.output.resolve())
        elif args.operation == "verify":
            verify_evidence(read_json(args.evidence), args.artifact_dir.resolve())
        elif args.operation == "verify-matrix":
            print(f"Verified {verify_matrix(args.directory)} installed interpreter targets")
        else:
            artifacts = compare_artifacts(args.first, args.second)
            write_json(
                args.output,
                {
                    "format": "dapane-build-comparison/1",
                    "source": source_identity(),
                    "comparison": "two-clean-builds-same-runner",
                    "identical": True,
                    "artifacts": artifacts,
                    "cross_host_reproducibility": "not_assessed",
                },
            )
    except (
        AssuranceError,
        KeyError,
        TypeError,
        OSError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(f"Release assurance failed: {error}", file=sys.stderr)
        return 1
    print(f"Release assurance {args.operation}: passed (candidate scope)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
