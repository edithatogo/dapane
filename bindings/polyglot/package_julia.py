"""Build the verified Julia source and platform library archive."""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import platform
import struct
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JULIA = ROOT / "bindings/polyglot/julia"
LIBRARY_NAME = "libdapane_abi.dylib"
MACH_O_64 = 0xFEEDFACF
CPU_ARM64 = 0x0100000C
MH_DYLIB = 6


def build(library: Path, output: Path) -> str:
    if (platform.system(), platform.machine()) != ("Darwin", "arm64"):
        raise ValueError("the qualified archive builder targets macOS arm64")
    if library.name != LIBRARY_NAME or not library.is_file() or library.is_symlink():
        raise ValueError("supply the tested macOS arm64 Dapane ABI library")
    binary = library.read_bytes()
    if len(binary) < 32:
        raise ValueError("the ABI library is missing its Mach-O header")
    magic, cpu, _, kind = struct.unpack_from("<IIII", binary)
    if (magic, cpu, kind) != (MACH_O_64, CPU_ARM64, MH_DYLIB):
        raise ValueError("the ABI library must be a thin arm64 Mach-O dylib")
    files = {
        "Project.toml": (JULIA / "Project.toml").read_bytes(),
        "src/Dapane.jl": (JULIA / "src/Dapane.jl").read_bytes(),
        f"artifacts/{LIBRARY_NAME}": binary,
        "LICENSE": (ROOT / "LICENSE").read_bytes(),
        "NOTICE": (ROOT / "NOTICE").read_bytes(),
        "THIRD_PARTY_NOTICES.txt": (ROOT / "THIRD_PARTY_NOTICES.txt").read_bytes(),
    }
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        staged = Path(directory) / output.name
        with tarfile.open(staged, mode="w") as archive:
            for name, contents in sorted(files.items()):
                entry = tarfile.TarInfo(name)
                entry.size = len(contents)
                entry.mode = 0o755 if name == f"artifacts/{LIBRARY_NAME}" else 0o644
                archive.addfile(entry, io.BytesIO(contents))
        with staged.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        os.link(staged, output)
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(build(args.library, args.out))


if __name__ == "__main__":
    main()
