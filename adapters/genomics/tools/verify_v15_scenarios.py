# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compare six frozen v15 workbook scenarios through two installed replays."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from dapane_genomics.v15_replay import apply_adjustment_rate

CATALOGUE = (
    Path(__file__).resolve().parents[1]
    / "src/dapane_genomics/data/workbook_catalog.json"
)
INPUT_CHANGES = {
    "double_quantity": ("WB30", "F36", "2"),
    "increase_unit_price": ("WB30", "E36", "1.25"),
    "halve_exchange_rate": ("WB02", "B81", "0.5"),
}
ADJUSTMENT_RATES = {"zero_adjustment": "0", "revised_adjustment": "0.1375"}
EXPECTED_CHANGES = {
    "original": 0,
    "double_quantity": 2_962,
    "increase_unit_price": 2_964,
    "halve_exchange_rate": 215,
    "zero_adjustment": 10_010,
    "revised_adjustment": 9_999,
}
IDENTIFY_REPLAY = """
import hashlib, json, sys
from pathlib import Path
from dapane_genomics import v15_replay

print(json.dumps({
    "python": sys.version.split()[0],
    "replay_sha256": hashlib.sha256(Path(v15_replay.__file__).read_bytes()).hexdigest(),
}))
"""

type Address = tuple[str, str]
type CellOutcome = dict[str, Any]


def _scenario(ledger: dict[str, Any], name: str) -> None:
    if name in INPUT_CHANGES:
        sheet_id, coordinate, multiplier = INPUT_CHANGES[name]
        sheet = next(s for s in ledger["sheets"] if s["catalogue"]["id"] == sheet_id)
        cell = next((c for c in sheet["cells"] if c["coordinate"] == coordinate), None)
        if cell is None or cell["stored_type"] != "n" or "formula" in cell:
            raise ValueError(
                f"{name}: expected a numeric input at {sheet_id}!{coordinate}"
            )
        cell["stored_value"] = str(
            Fraction(cell["stored_value"]) * Fraction(multiplier)
        )
    if name in ADJUSTMENT_RATES:
        apply_adjustment_rate(ledger, ADJUSTMENT_RATES[name])


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _cells(replay: dict[str, Any], source: str) -> dict[Address, CellOutcome]:
    if replay["version"] != 1 or replay["source_sha256"] != source:
        raise ValueError("Replay identity differs from the frozen v15 source")
    cells = {}
    sheet_ids = set()
    for sheet in replay["sheets"]:
        sheet_id = sheet["id"]
        if sheet_id in sheet_ids:
            raise ValueError(f"Duplicate replay worksheet: {sheet_id}")
        sheet_ids.add(sheet_id)
        for address, outcome in sheet["formulas"].items():
            cells[sheet_id, address] = outcome
    return cells


def _compare(
    name: str,
    expected: set[Address],
    baseline: dict[Address, CellOutcome],
    candidate: dict[Address, CellOutcome],
) -> None:
    for label, results in (("baseline", baseline), ("candidate", candidate)):
        different = expected.symmetric_difference(results)
        if different:
            sheet, cell = min(different)
            issue = "includes unexpected" if (sheet, cell) in results else "is missing"
            raise ValueError(f"{name}: {label} {issue} formula address {sheet}!{cell}")
    for (sheet, cell), outcome in baseline.items():
        other = candidate[sheet, cell]
        if json.dumps(outcome, sort_keys=True) != json.dumps(other, sort_keys=True):
            kind = "Excel error" if "error" in outcome or "error" in other else "value"
            raise ValueError(f"{name}: exact {kind} differs at {sheet}!{cell}")


def _verify(
    workbook: Path, baseline_python: Path, candidate_python: Path, work: Path
) -> dict[str, Any]:
    interpreters = {"baseline": baseline_python, "candidate": candidate_python}
    installations = {
        role: json.loads(
            subprocess.check_output([python, "-I", "-c", IDENTIFY_REPLAY], cwd=work)
        )
        for role, python in interpreters.items()
    }
    inventory = work / "inventory.json"
    subprocess.run(
        [
            baseline_python,
            "-I",
            "-m",
            "dapane_genomics.workbook_ledger",
            workbook,
            CATALOGUE,
            inventory,
        ],
        cwd=work,
        check=True,
    )
    frozen = inventory.read_bytes()
    ledger = json.loads(frozen)
    source = ledger["source_sha256"]
    expected = {
        (sheet["catalogue"]["id"], cell["coordinate"])
        for sheet in ledger["sheets"]
        for cell in sheet["cells"]
        if "formula" in cell
    }
    if len(expected) != 36_411:
        raise ValueError(f"Expected 36,411 formula addresses, found {len(expected):,}")
    original: dict[Address, CellOutcome] = {}
    observations = {}
    for name, expected_changes in EXPECTED_CHANGES.items():
        scenario = json.loads(frozen)
        _scenario(scenario, name)
        ledger_path = work / f"{name}.json"
        ledger_path.write_text(json.dumps(scenario), encoding="utf-8")
        hashes = {}
        results = {}
        for role, python in interpreters.items():
            output = work / f"{name}-{role}.json"
            subprocess.run(
                [python, "-I", "-m", "dapane_genomics.v15_replay", ledger_path, output],
                cwd=work,
                check=True,
            )
            raw = output.read_bytes()
            hashes[role] = sha256(raw).hexdigest()
            results[role] = _cells(
                json.loads(raw, object_pairs_hook=_unique_object), source
            )
        baseline = results["baseline"]
        _compare(name, expected, baseline, results["candidate"])
        if name == "original":
            original = baseline
        changed = sum(
            outcome != original[address] for address, outcome in baseline.items()
        )
        errors = Counter(
            result["error"] for result in baseline.values() if "error" in result
        )
        divisions = 25 if name == "zero_adjustment" else 4
        if changed != expected_changes or errors != {"#DIV/0!": divisions, "#REF!": 3}:
            raise ValueError(
                f"{name}: changes or Excel errors differ from the frozen scenario"
            )
        observations[name] = {
            "matched_formula_cells": len(expected),
            "changed_from_original": changed,
            "matching_errors": errors.total(),
            "error_codes": dict(sorted(errors.items())),
            "result_sha256": hashes,
        }
        print(
            f"{name}: {len(expected):,} cells matched, including {errors.total()} Excel errors",
            flush=True,
        )
    return {
        "workbook_sha256": source,
        "catalogue_sha256": ledger["catalogue_sha256"],
        "installations": installations,
        "scenarios": observations,
        "coordinate_comparisons": len(expected) * len(observations),
        "excel_error_coordinate_comparisons": sum(
            result["matching_errors"] for result in observations.values()
        ),
    }


def main() -> None:
    """Run the local comparison and write a new summary receipt on success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workbook", type=Path, help="Authorised copy of the frozen v15 workbook"
    )
    parser.add_argument(
        "receipt", type=Path, help="New local JSON file for the summary"
    )
    parser.add_argument("--baseline-python", type=Path, required=True)
    parser.add_argument("--candidate-python", type=Path, required=True)
    args = parser.parse_args()
    try:
        with TemporaryDirectory(prefix="dapane-v15-") as directory:
            result = _verify(
                args.workbook.absolute(),
                args.baseline_python.absolute(),
                args.candidate_python.absolute(),
                Path(directory),
            )
        with args.receipt.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    except (
        KeyError,
        OSError,
        ValueError,
        subprocess.CalledProcessError,
    ) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
