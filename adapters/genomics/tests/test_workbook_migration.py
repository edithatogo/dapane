# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify migration through the model command with independent XLSX readback."""

import json
import sys
from hashlib import sha256

import pytest
from openpyxl import Workbook, load_workbook

from dapane_genomics.model_tables import main
from genomics_microcosting.t1_workbook_builder import build_workbook_copy


def test_migrate_preserves_the_source_template_and_formulas(tmp_path, monkeypatch):
    source = tmp_path / "previous.xlsx"
    template = tmp_path / "new-layout.xlsx"
    output = tmp_path / "migrated.xlsx"
    mapping = tmp_path / "mapping.json"

    workbook = Workbook()
    workbook.active.title = "Old"
    workbook.active["A1"] = 8
    workbook.active["A2"] = "0012"
    workbook.active["A3"] = "=A1+1"
    workbook.save(source)
    workbook.close()
    workbook = Workbook()
    workbook.active.title = "New"
    workbook.active["C5"] = "=C4*2"
    workbook.active["D1"] = "keep"
    workbook.save(template)
    workbook.close()
    original = (source.read_bytes(), template.read_bytes())
    moves = [
        {
            "source": {"sheet": "Old", "cell": "A1"},
            "target": {"sheet": "New", "cell": "C4"},
        },
        {
            "source": {"sheet": "Old", "cell": "A2"},
            "target": {"sheet": "New", "cell": "D4"},
        },
    ]
    mapping.write_text(json.dumps(moves), encoding="utf-8")
    argv = ["genomics-model", "migrate", *map(str, (source, template, mapping, output))]
    monkeypatch.setattr(sys, "argv", argv)
    assert main() == 0
    result = load_workbook(output, read_only=True)
    try:
        assert [result["New"][cell].value for cell in ("C4", "D4", "C5", "D1")] == [
            8,
            "0012",
            "=C4*2",
            "keep",
        ]
    finally:
        result.close()
    completed_bytes = output.read_bytes()
    with pytest.raises(SystemExit):
        main()
    assert output.read_bytes() == completed_bytes

    invalid = tmp_path / "invalid.xlsx"
    monkeypatch.setattr(sys, "argv", [*argv[:-1], str(invalid)])
    for invalid_moves in (
        [moves[0], moves[0]],
        [{**moves[0], "source": {"sheet": "Old", "cell": "A3"}}],
        [{**moves[0], "target": {"sheet": "New", "cell": "C5"}}],
    ):
        mapping.write_text(json.dumps(invalid_moves), encoding="utf-8")
        with pytest.raises(SystemExit):
            main()
        assert not invalid.exists()
    assert (source.read_bytes(), template.read_bytes()) == original


def test_workbook_formula_seed_fills_disjoint_ranges_and_rejects_overlaps(tmp_path):
    source = tmp_path / "source.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    for row in (2, 3, 6, 8):
        sheet[f"D{row}"] = f"=B{row}*$C$1"
    workbook.save(source)
    workbook.close()
    digest = sha256(source.read_bytes()).hexdigest()
    change = {
        "sheet": "Sheet",
        "cell": "D2",
        "ranges": ["D2:D3", "D6"],
        "original": "=B2*$C$1",
        "replacement": "=B2*$C$1+1",
    }
    output = tmp_path / "scenario.xlsx"
    build_workbook_copy(
        source,
        output,
        source_sha256=digest,
        changes=[change],
        selected_version="synthetic",
    )
    reopened = load_workbook(output)
    try:
        for row in (2, 3, 6):
            assert reopened.active[f"D{row}"].value == f"=B{row}*$C$1+1"
        assert reopened.active["D8"].value == "=B8*$C$1"
    finally:
        reopened.close()
    rejected = tmp_path / "rejected.xlsx"
    with pytest.raises(ValueError, match="Duplicate workbook target"):
        build_workbook_copy(
            source,
            rejected,
            source_sha256=digest,
            selected_version="synthetic",
            changes=[change | {"ranges": ["D2:D3", "D3"]}],
        )
    with pytest.raises(ValueError, match="Source precondition failed: Sheet!D4"):
        build_workbook_copy(
            source,
            rejected,
            source_sha256=digest,
            selected_version="synthetic",
            changes=[change | {"ranges": ["D2:D4"]}],
        )
    assert not rejected.exists()
    assert sha256(source.read_bytes()).hexdigest() == digest
