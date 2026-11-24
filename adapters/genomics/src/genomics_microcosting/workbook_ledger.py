# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Inventory the frozen genomics workbook without recalculating or changing it."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree.ElementTree import Element, tostring
from zipfile import ZipFile

from defusedxml import ElementTree
from genomics_microcosting.dapane_workbook import verified_workbook_payload
from openpyxl import load_workbook
from openpyxl.formula import Tokenizer

_RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _sheet_parts(archive: ZipFile) -> dict[str, str]:
    book = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    by_id = {entry.attrib["Id"]: entry.attrib for entry in relationships}
    parts = {}
    for sheet in book.findall("{*}sheets/{*}sheet"):
        relationship = by_id[sheet.attrib[_RELATIONSHIP_ID]]
        target = relationship["Target"]
        path = PurePosixPath(target.lstrip("/") if target.startswith("/") else f"xl/{target}")
        if (
            relationship.get("TargetMode") == "External"
            or ".." in path.parts
            or path.parts[:2] != ("xl", "worksheets")
        ):
            raise ValueError("Workbook sheet must resolve to an internal worksheet part")
        parts[sheet.attrib["name"]] = path.as_posix()
    return parts


def _cell_record(
    cell: Element, expanded_formulas: dict[str, str], texts: dict[str, str]
) -> dict[str, Any] | None:
    value = cell.findtext("{*}v")
    formula = cell.find("{*}f")
    coordinate = cell.attrib["r"]
    if formula is None and value is None and coordinate not in texts:
        return None
    record: dict[str, Any] = {
        "coordinate": coordinate,
        "stored_type": cell.get("t", "n"),
        "stored_value": value,
    }
    if coordinate in texts:
        record["text"] = texts[coordinate]
    if formula is not None:
        expanded = expanded_formulas[coordinate]
        tokens = Tokenizer(expanded).items
        record.update(
            formula=expanded,
            formula_attributes=dict(formula.attrib),
            references=[
                token.value
                for token in tokens
                if token.type == "OPERAND" and token.subtype == "RANGE"
            ],
            functions=[
                token.value[:-1].upper()
                for token in tokens
                if token.type == "FUNC" and token.subtype == "OPEN"
            ],
        )
    return record


def inventory_workbook(payload: bytes, catalogue: dict[str, Any]) -> dict[str, Any]:
    """Reconcile each original coordinate and shared formula with the legacy catalogue."""
    digest = sha256(payload).hexdigest()
    if digest != catalogue["source_sha256"]:
        raise ValueError("Workbook and catalogue source digests differ")

    workbook = load_workbook(BytesIO(payload), read_only=True, keep_links=False)
    sheets = []
    try:
        with ZipFile(BytesIO(payload)) as archive:
            parts = _sheet_parts(archive)
            if list(parts) != workbook.sheetnames:
                raise ValueError("Workbook reader and raw sheet relationships differ")
            for sheet, listed in zip(workbook.worksheets, catalogue["sheets"], strict=True):
                if sheet.title != listed["sheet"] or sheet.sheet_state != listed["state"]:
                    raise ValueError(f"Catalogue sheet identity differs at {listed['id']}")
                expanded: dict[str, str] = {}
                texts: dict[str, str] = {}
                populated = set()
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.value is None:
                            continue
                        populated.add(cell.coordinate)
                        if cell.data_type == "f":
                            expanded[cell.coordinate] = cell.value
                        elif cell.data_type in {"s", "inlineStr"}:
                            texts[cell.coordinate] = cell.value

                part = parts[sheet.title]
                content = ElementTree.fromstring(archive.read(part))
                records = {}
                for cell in content.findall("{*}sheetData/{*}row/{*}c"):
                    if (record := _cell_record(cell, expanded, texts)) is not None:
                        coordinate = record["coordinate"]
                        if coordinate in records:
                            raise ValueError(f"Duplicate coordinate {listed['id']}:{coordinate}")
                        records[coordinate] = record
                raw_formulas = {key for key, record in records.items() if "formula" in record}
                if (
                    populated != records.keys()
                    or expanded.keys() != raw_formulas
                    or len(populated) != listed["nonempty_cells"]
                    or len(raw_formulas) != listed["formulas"]
                ):
                    raise ValueError(f"Workbook, reader and catalogue disagree at {listed['id']}")

                sheets.append(
                    {
                        "catalogue": listed,
                        "part": part,
                        "layout": [
                            tostring(element, encoding="unicode")
                            for element in content
                            if element.tag.split("}")[-1] != "sheetData"
                        ],
                        "cells": list(records.values()),
                    }
                )
    finally:
        workbook.close()

    counts = Counter(
        "formula" if "formula" in cell else "input" for sheet in sheets for cell in sheet["cells"]
    )
    if len(sheets) != catalogue["sheet_count"] or counts["formula"] != catalogue["formula_count"]:
        raise ValueError("Workbook totals disagree with the frozen catalogue")
    return {
        "version": 1,
        "source_sha256": digest,
        "counts": {
            "sheets": len(sheets),
            "hidden_sheets": sum(sheet["catalogue"]["state"] != "visible" for sheet in sheets),
            "formula_cells": counts["formula"],
            "populated_nonformula_cells": counts["input"],
        },
        "sheets": sheets,
    }


def main() -> None:
    """Write the private ledger to a new restricted file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("output", type=Path, help="New local file for source-derived evidence")
    args = parser.parse_args()
    catalogue_bytes = args.catalogue.read_bytes()
    ledger = inventory_workbook(
        verified_workbook_payload(args.workbook), json.loads(catalogue_bytes)
    )
    ledger["catalogue_sha256"] = sha256(catalogue_bytes).hexdigest()
    # The ledger contains the study's input and output values.
    args.output.touch(mode=0o600, exist_ok=False)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(ledger, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
