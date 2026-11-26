# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Move declared static inputs to a new workbook layout."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.utils.cell import coordinate_to_tuple
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator


class _Address(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    sheet: str = Field(min_length=1)
    cell: str = Field(pattern=r"^[A-Z]{1,3}[1-9][0-9]{0,6}$")

    @field_validator("cell")
    @classmethod
    def within_excel(cls, value: str) -> str:
        row, column = coordinate_to_tuple(value)
        if row > 1_048_576 or column > 16_384:
            raise ValueError("Coordinates must lie within an Excel worksheet")
        return value


class _Move(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source: _Address
    target: _Address


_MAPPING = TypeAdapter(list[_Move])


def migrate_workbook(source: Path, template: Path, mapping: Path, output: Path) -> None:
    """Copy declared static cells into a new `.xlsx` while preserving the template.

    The mapping is a nonempty JSON array of source and target addresses.
    Input workbooks are read-only, and formulas and merged placeholders are
    protected. Existing output paths are rejected.
    """
    if any(path.suffix.lower() != ".xlsx" for path in (source, template, output)):
        raise ValueError("Source, template and output must be .xlsx workbooks")
    moves = _MAPPING.validate_json(mapping.read_bytes())
    targets = {(move.target.sheet, move.target.cell) for move in moves}
    if not moves or len(targets) != len(moves):
        raise ValueError("Provide at least one move and distinct target cells")

    previous = load_workbook(source, read_only=True)
    try:
        successor = load_workbook(template)
        try:
            for move in moves:
                origin = previous[move.source.sheet][move.source.cell]
                cell = successor[move.target.sheet][move.target.cell]
                if origin.value is None or origin.data_type not in {"b", "d", "n", "s"}:
                    raise ValueError("Sources must contain static input values")
                if isinstance(cell, MergedCell) or cell.data_type == "f":
                    raise ValueError(
                        "A move cannot replace a formula or merged placeholder"
                    )
                cell.value = origin.value
                cell.data_type = origin.data_type

            with TemporaryDirectory(dir=output.parent) as directory:
                staged = Path(directory) / output.name
                successor.save(staged)
                staged.chmod(0o600)
                output.hardlink_to(staged)
        finally:
            successor.close()
    finally:
        previous.close()
