"""Explicit installed Voiage Rust EVPI execution for a reviewed D3 packet.

Requires a *separately installed* qualified wheel in this Python environment.
No source import, Python VOI calculation, NumPy fallback, dependency install or
implicit latest-version selection is offered. Native and artifact hashes are
verified before executing the provider's own kernel.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from importlib import import_module, metadata
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile
from typing import Any

from study import canonical_digest

_SHA = re.compile(r"sha256:[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")


class ExecutionError(ValueError):
    """Fail-closed native-provider acquisition or execution error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _hash(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def check_wheel(path: Path, expected_digest: str) -> tuple[str, ...]:
    """Confirm the selected wheel and its native extension member exist."""
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ExecutionError("wheel_missing")
    if not isinstance(expected_digest, str) or _SHA.fullmatch(expected_digest) is None:
        raise ExecutionError("invalid_wheel_digest")
    if path.stat().st_size > 512 * 1024 * 1024:
        raise ExecutionError("wheel_size_limit")
    if _hash(path.read_bytes()) != expected_digest:
        raise ExecutionError("wheel_digest_mismatch")
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if len(names) > 10_000 or len(set(names)) != len(names):
                raise ExecutionError("unsafe_wheel_member")
            if sum(entry.file_size for entry in entries) > 512 * 1024 * 1024:
                raise ExecutionError("wheel_size_limit")
            for entry in entries:
                member = PurePosixPath(entry.filename)
                if (member.is_absolute() or '..' in member.parts or not entry.filename
                    or '\\' in entry.filename or any(ord(c) < 32 for c in entry.filename)
                    or entry.file_size > 128 * 1024 * 1024):
                    raise ExecutionError("unsafe_wheel_member")
            modules = tuple(sorted(name for name in names if name.startswith("voiage/_core")
                                   and name.endswith((".so", ".pyd", ".dylib"))))
            if len(modules) != 1:
                raise ExecutionError("native_wheel_missing")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ExecutionError("invalid_wheel") from exc
    return modules


def run_evpi(prepared: dict[str, Any], wheel: Path, expected_digest: str,
             *, expected_revision: str) -> dict[str, Any]:
    """Execute the pinned installed Rust EVPI path, preserving a reviewable receipt."""
    if not isinstance(prepared, dict) or prepared.get("schema_version") != "dapane-d3-prepared/0.1":
        raise ExecutionError("unsupported_study")
    pin = prepared.get("provider", {})
    if (not isinstance(pin, dict) or not isinstance(expected_revision, str)
        or _REV.fullmatch(expected_revision) is None
        or pin.get("revision") != expected_revision):
        raise ExecutionError("source_revision_mismatch")
    fingerprint = prepared.get("prepared_digest")
    if not isinstance(fingerprint, str) or fingerprint != canonical_digest(
        "dapane:d3-prepared:0.1\n", {k:v for k,v in prepared.items() if k!="prepared_digest"}
    ):
        raise ExecutionError("study_digest_mismatch")
    members = check_wheel(wheel, expected_digest)
    if pin.get("artifact_digest") != expected_digest:
        raise ExecutionError("provider_artifact_mismatch")
    # Import only after the exact wheel has been selected and checked.
    try:
        dist = metadata.distribution("voiage")
        installed_root = Path(dist.locate_file("")).resolve()
        package = import_module("voiage")
        native = import_module("voiage._core")
        runtime = import_module("voiage._runtime")
    except (ImportError, metadata.PackageNotFoundError, AttributeError) as exc:
        raise ExecutionError("native_provider_unavailable") from exc
    native_path = Path(getattr(native, "__file__", ""))
    package_path = Path(getattr(package, "__file__", ""))
    if (not native_path.is_file() or not package_path.is_file()
        or not native_path.resolve().is_relative_to(installed_root)
        or not package_path.resolve().is_relative_to(installed_root)
        or native_path.name != Path(members[0]).name):
        raise ExecutionError("provider_import_not_installed")
    try:
        with zipfile.ZipFile(wheel) as archive:
            # The exact native library *and* every shipped Python module must
            # match the installed artifact, not merely an imported filename.
            for entry in archive.infolist():
                if not entry.filename.startswith("voiage/") or entry.is_dir():
                    continue
                destination = installed_root / entry.filename
                if not destination.is_file() or _hash(destination.read_bytes()) != _hash(archive.read(entry)):
                    raise ExecutionError("installed_wheel_mismatch")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ExecutionError("wheel_read_failed") from exc
    fn = getattr(runtime, "compute_evpi", None)
    if not callable(fn) or not callable(getattr(native, "compute_evpi", None)):
        raise ExecutionError("native_method_unavailable")
    value_array = prepared.get("value_array", {})
    values = value_array.get("net_benefit") if isinstance(value_array, dict) else None
    if (not isinstance(values, list) or len(values) < 1
        or any(not isinstance(row, list) or len(row) < 2 for row in values)
        or any(type(v) not in (float, int) or not math.isfinite(v) for row in values for v in row)):
        raise ExecutionError("invalid_value_array")
    try:
        evpi = fn(values)
    except Exception as exc:
        raise ExecutionError("native_evpi_failed") from exc
    if type(evpi) is not float or not math.isfinite(evpi) or evpi < 0:
        raise ExecutionError("invalid_native_result")
    return {"schema_version": "dapane-d3-native-evpi/0.1",
            "method": "voiage._runtime.compute_evpi",
            "input_digest": fingerprint,
            "provider_revision": expected_revision,
            "wheel_digest": expected_digest,
            "native_extension_digest": _hash(native_path.read_bytes()),
            "evpi_per_assay": evpi,
            "execution": "native_extension_invoked",
            "source": "externally_run_installed_wheel"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--wheel-digest", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        prepared = json.loads(args.prepared.read_text(encoding="utf-8"))
        observed = run_evpi(prepared, args.wheel, args.wheel_digest, expected_revision=args.revision)
        # Do not overwrite any existing provenance receipt.
        with args.output.open("x", encoding="utf-8") as dest:
            dest.write(json.dumps(observed, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (ExecutionError, ValueError, OSError, TypeError) as exc:
        print("Native VOI verification failed: " +
              (exc.code if isinstance(exc, ExecutionError) else "invalid_input_or_output"),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
