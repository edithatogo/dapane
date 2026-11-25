# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify distribution contents against source without extracting archive paths."""

import argparse
import logging
import tarfile
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING
from zipfile import ZipFile

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from email.message import Message
FORBIDDEN_SUFFIXES = {".xlsx", ".xlsm", ".parquet", ".pkl", ".docx", ".ipynb"}
FORBIDDEN_PARTS = {"conductor", ".private-runs", "data", "manuscripts", "reports"}
SDIST_ROOTS = {
    ".dockerignore",
    ".gitignore",
    "Dockerfile",
    "deploy",
    "src",
    "tests",
    "scripts",
    "tools",
    "pyproject.toml",
    "config.yaml",
    "config",
    "configs",
    "uv.lock",
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "SECURITY.md",
    "PKG-INFO",
}
SDIST_HELPERS = {
    "scripts/__init__.py",
    "scripts/convert_to_csv.py",
    "scripts/parse_cost_tables.py",
    "scripts/parse_additional_tables.py",
    "scripts/generate_report.py",
    "scripts/generate_comprehensive_report.py",
    "scripts/prepare_all_sheets.py",
    "scripts/run_web.py",
    "scripts/validate_all_sheets.py",
    "scripts/demonstrate_excel_version_control.py",
    "scripts/prepare_publication_tables.py",
    "scripts/replicate_bi_comp_stor_costs.py",
    "scripts/replicate_consumable_costs.py",
    "scripts/replicate_equipment_costs.py",
    "scripts/replicate_labour_costs.py",
    "scripts/validate_labour_usage.py",
    "scripts/advanced_validation.py",
    "scripts/analyze_model_consistency.py",
    "scripts/analyze_scenarios.py",
    "scripts/automated_standardization.py",
    "scripts/compare_performance.py",
    "scripts/create_ground_truth.py",
    "scripts/demonstrate_plugins.py",
    "scripts/enhanced_reporting.py",
    "scripts/manage_data.py",
    "scripts/run_scenario_analysis.py",
    "scripts/run_advanced_scenario_analysis.py",
    "scripts/validate_process_sheet.py",
    "scripts/validate_data_consistency.py",
    "scripts/visualize_costs.py",
    "scripts/establish_performance_baselines.py",
    "scripts/excel_data_extractor.py",
    "scripts/extract_excel_comprehensive.py",
    "scripts/extract_excel_data_properly.py",
    "scripts/generate_templates.py",
    "scripts/model_transformation.py",
    "scripts/phase3_data_enhancement.py",
    "scripts/prepare_reference_tables.py",
    "scripts/profile_and_optimize.py",
    "scripts/replicate_calculations.py",
    "scripts/replicate_detailed_table.py",
    "scripts/transfer_validate_tables.py",
    "scripts/validate_bi_comp_stor_costs.py",
    "scripts/validate_calculation_engine.py",
    "scripts/validate_calculations.py",
    "scripts/validate_data_integrity.py",
    "scripts/validate_excel_comparison.py",
    "scripts/validate_simple_tables.py",
    "scripts/validate_standardization.py",
    "scripts/validation_pipeline.py",
    "tools/__init__.py",
    "tools/select_tests.py",
    "tools/check_package.py",
    "tools/build_t1_scenario.py",
}
DEPLOYMENT_FILES = {
    ".dockerignore",
    "Dockerfile",
    "deploy/README.md",
    "deploy/container-app.bicep",
    "deploy/ecs-task.yml",
    "deploy/lab-setup.md",
    "deploy/lab-setup.mp4",
    "deploy/promote.sh",
}
PACKAGE_DATA_HASHES = {
    "genomics_microcosting/data/t1_known_zero_lineage.json": (
        "c9c7b042ce024af28307be2d080f97f256933392d05c846cef0af2bad0222e54"
    ),
    "dapane_genomics/data/workbook_catalog.json": (
        "85f61076a8a0a00ae615a2ac26f962c9f0f159e348017b12454afe4c36e7df21"
    ),
}


def check_paths(names: list[str]) -> None:
    """Reject research payloads and nonportable archive traversal paths."""
    for name in names:
        path = PurePosixPath(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "\\" in name
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or FORBIDDEN_PARTS.intersection(path.parts)
        ):
            message = f"Disallowed distribution path: {name}"
            raise ValueError(message)


def check_distribution_paths(payloads: dict[str, bytes]) -> None:
    """Classify the reviewed dependency index and workbook catalogue.

    The pinned files contain structural identities. Arbitrary data stays forbidden.
    """
    for name, payload in payloads.items():
        parts = PurePosixPath(name).parts
        package_name = (
            PurePosixPath(*parts[2:]).as_posix() if parts[1:2] == ("src",) else name
        )
        expected = PACKAGE_DATA_HASHES.get(package_name)
        if expected is None:
            check_paths([name])
            continue
        if sha256(payload).hexdigest() != expected:
            message = "Packaged structural data differs from reviewed source bytes"
            raise ValueError(message)
        classified = PurePosixPath(*parts[:-2], "generated_code", parts[-1])
        check_paths([str(classified)])


def check_distributions(root: Path, dist_dir: Path) -> str:
    """Check source bytes, licence, typing marker and version identity."""
    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        message = "Expected exactly one wheel and one source distribution"
        raise ValueError(message)
    with ZipFile(wheels[0]) as archive:
        wheel = {name: archive.read(name) for name in archive.namelist()}
        if len(wheel) != len(archive.namelist()):
            message = "Wheel contains duplicate members"
            raise ValueError(message)
    sdist = _read_sdist(sdists[0])
    check_distribution_paths(wheel)
    check_distribution_paths(sdist)
    _check_source_allowlist(sdist)
    _check_sdist_sources(root, sdist)
    licence = (root / "LICENSE").read_bytes()
    _require_single_payload(wheel, "/licenses/LICENSE", licence)
    _require_single_payload(sdist, "/LICENSE", licence)
    expected_names: set[str] = set()
    packaged_files = {
        path.relative_to(root / "src").as_posix(): path
        for package in ("genomics_microcosting", "dapane_genomics")
        for path in (root / "src" / package).rglob("*")
        if path.is_file()
        and path.name != "ruff.toml"
        and not {"__pycache__", ".ruff_cache", ".pytest_cache"}.intersection(path.parts)
    }
    packaged_files.update(
        {
            "genomics_microcosting/config.yaml": root / "config.yaml",
            "genomics_microcosting/CITATION.cff": root / "CITATION.cff",
        },
    )
    for source, target in (
        ("config", "configuration"),
        ("configs", "analysis_defaults"),
    ):
        directory = root / source
        packaged_files.update(
            {
                f"genomics_microcosting/{target}/{path.relative_to(directory).as_posix()}": path
                for path in directory.rglob("*")
                if path.is_file()
            },
        )
    for name, source_path in packaged_files.items():
        expected_names.add(name)
        expected = source_path.read_bytes()
        if wheel.get(name) != expected:
            message = f"Wheel source differs: {name}"
            raise ValueError(message)
        _require_single_payload(
            sdist, "/" + source_path.relative_to(root).as_posix(), expected
        )
    _check_wheel_allowlist(wheel, expected_names)
    marker = "genomics_microcosting/py.typed"
    if marker not in wheel:
        message = "Wheel lacks the PEP 561 typing marker"
        raise ValueError(message)
    wheel_metadata = _metadata(wheel, "/METADATA")
    source_metadata = _metadata(sdist, "/PKG-INFO")
    _check_metadata(wheel_metadata, source_metadata)
    return str(wheel_metadata["Version"])


def _check_metadata(wheel_metadata: Message, source_metadata: Message) -> None:
    """Keep runtime/licence policy and wheel/source metadata aligned."""
    for field in ("Version", "Requires-Python", "License-Expression"):
        if not wheel_metadata[field] or wheel_metadata[field] != source_metadata[field]:
            message = f"Distribution metadata disagrees: {field}"
            raise ValueError(message)
    if (
        wheel_metadata["Requires-Python"] != "==3.15.1"
        or wheel_metadata["License-Expression"] != "Apache-2.0"
    ):
        message = "Distribution runtime/licence policy disagrees with the project"
        raise ValueError(message)


def _check_sdist_sources(root: Path, sdist: dict[str, bytes]) -> None:
    """Compare included tests, helpers and maintained package metadata exactly."""
    source_root = next(iter(sdist)).partition("/")[0]
    paths = set((root / "tests").rglob("*.py"))
    paths.update(root / name for name in SDIST_HELPERS)
    paths.update(root / name for name in DEPLOYMENT_FILES)
    metadata_paths = (
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "SECURITY.md",
        "pyproject.toml",
        "config.yaml",
        "uv.lock",
    )
    paths.update(root / name for name in metadata_paths)
    paths.add(root / "src/genomics_microcosting/ruff.toml")
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if sdist.get(f"{source_root}/{relative}") != path.read_bytes():
            message = f"Missing or changed source file: {relative}"
            raise ValueError(message)


def _check_wheel_allowlist(wheel: dict[str, bytes], expected_names: set[str]) -> None:
    """Allow exact package files plus the generated distribution metadata."""
    actual = {
        name
        for name in wheel
        if not PurePosixPath(name).parts[0].endswith(".dist-info")
    }
    if actual != expected_names:
        difference = actual ^ expected_names
        message = f"Wheel contains unexpected/missing package files: {difference}"
        raise ValueError(message)


def _check_source_allowlist(sdist: dict[str, bytes]) -> None:
    """Require one source root and the maintained source-distribution allowlist."""
    roots = {PurePosixPath(name).parts[0] for name in sdist}
    if len(roots) != 1:
        message = "Source archive contains multiple roots"
        raise ValueError(message)
    for name in sdist:
        relative = PurePosixPath(*PurePosixPath(name).parts[1:])
        if (
            not relative.parts
            or relative.parts[0] not in SDIST_ROOTS
            or (
                relative.parts[0] in {"scripts", "tools"}
                and relative.as_posix() not in SDIST_HELPERS
            )
            or (
                relative.parts[0] in {"deploy", "Dockerfile", ".dockerignore"}
                and relative.as_posix() not in DEPLOYMENT_FILES
            )
        ):
            message = f"Unexpected source distribution member: {name}"
            raise ValueError(message)


def _read_sdist(path: Path) -> dict[str, bytes]:
    """Read only regular source archive members without materializing paths."""
    with tarfile.open(path) as archive:
        sdist: dict[str, bytes] = {}
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                message = f"Nonregular source archive member: {member.name}"
                raise ValueError(message)
            if member.name in sdist:
                message = "Source archive contains duplicate members"
                raise ValueError(message)
            stream = archive.extractfile(member)
            if stream is None:
                raise AssertionError(member.name)
            sdist[member.name] = stream.read()
    return sdist


def _metadata(payloads: dict[str, bytes], suffix: str) -> Message:
    """Read exactly one generated distribution metadata record."""
    records = [value for name, value in payloads.items() if name.endswith(suffix)]
    if len(records) != 1:
        message = f"Expected one metadata record ending in {suffix}"
        raise ValueError(message)
    return BytesParser().parsebytes(records[0])


def _require_single_payload(
    payloads: dict[str, bytes],
    suffix: str,
    expected: bytes,
) -> None:
    """Require exact single-member content rather than approximate licence labels."""
    records = [value for name, value in payloads.items() if name.endswith(suffix)]
    if records != [expected]:
        message = f"Missing, duplicated or changed source payload: {suffix}"
        raise ValueError(message)


def main() -> None:
    """Validate a local build directory and log the qualified distribution version."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist_dir", type=Path)
    options = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    check_distributions(Path(__file__).resolve().parents[1], options.dist_dir)
    logger.info("Distribution source, licence and version checks passed")


if __name__ == "__main__":
    main()
