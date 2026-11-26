# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Recalculate the original v15 workbook dialect from its frozen cell ledger."""

from __future__ import annotations

import argparse
import json
import operator
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token
from openpyxl.utils.cell import get_column_letter, range_boundaries


@dataclass(frozen=True)
class CellError:
    """An Excel error value distinct from worksheet text."""

    code: str


type CellValue = Fraction | bool | str | CellError | None
type Expression = CellValue | tuple[CellValue, ...]

_DIVISION_ERROR = CellError("#DIV/0!")
_VALUE_ERROR = CellError("#VALUE!")
_BINARY = {
    "+": (1, operator.add),
    "-": (1, operator.sub),
    "*": (2, operator.mul),
    "/": (2, operator.truediv),
}


def _numeric(value: Expression) -> Fraction | CellError:
    if value is None:
        return Fraction(0)
    if isinstance(value, CellError):
        return value
    if isinstance(value, tuple):
        return _VALUE_ERROR
    try:
        return Fraction(value)
    except ValueError, ZeroDivisionError:
        return _VALUE_ERROR


def _stored(cell: dict[str, Any]) -> CellValue:
    value = cell["stored_value"]
    kind = cell["stored_type"]
    if kind == "e":
        return CellError(value)
    if kind == "b":
        return value == "1"
    if kind == "n":
        return Fraction(value) if value not in ("", None) else None
    return cell.get("text", value)


def _pmt(arguments: list[Expression]) -> Fraction | CellError:
    rate, periods, present = map(_numeric, arguments)
    for number in (rate, periods, present):
        if isinstance(number, CellError):
            return number
    if periods.denominator != 1 or not 1 <= periods <= 1000 or rate <= -1:
        return CellError("#NUM!")
    if rate == 0:
        return -present / periods
    growth = (1 + rate) ** periods.numerator
    return -present * rate * growth / (growth - 1)


def _function(name: str, arguments: list[Expression]) -> CellValue:
    if name == "PMT" and len(arguments) == 3:
        return _pmt(arguments)
    if name not in {"SUM", "AVERAGE"}:
        raise ValueError(f"Unsupported v15 function: {name}")
    numbers = []
    for argument in arguments:
        for value in argument if isinstance(argument, tuple) else (argument,):
            if isinstance(value, CellError):
                return value
            if isinstance(value, Fraction):
                numbers.append(value)
    total = sum(numbers, Fraction(0))
    if name == "SUM":
        return total
    return total / len(numbers) if numbers else _DIVISION_ERROR


class _Formula:
    def __init__(self, workbook: WorkbookReplay, sheet: str, formula: str) -> None:
        self.workbook = workbook
        self.sheet = sheet
        self.tokens = [
            token for token in Tokenizer(formula).items if token.type != "WHITE-SPACE"
        ]
        self.position = 0

    def _peek(self) -> Token | None:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def _take(self) -> Token:
        token = self._peek()
        if token is None:
            raise ValueError("Unexpected end of v15 formula")
        self.position += 1
        return token

    def _close(self, kind: str) -> None:
        token = self._take()
        if token.type != kind or token.subtype != "CLOSE":
            raise ValueError(f"Expected close of v15 {kind.lower()}")

    def _atom(self) -> Expression:
        token = self._take()
        match token.type, token.subtype:
            case "OPERAND", "NUMBER":
                return Fraction(token.value)
            case "OPERAND", "RANGE":
                return self.workbook.reference(self.sheet, token.value)
            case "OPERAND", "ERROR":
                return CellError(token.value)
            case "PAREN", "OPEN":
                value = self._expression()
                self._close("PAREN")
                return value
            case "FUNC", "OPEN":
                arguments = [self._expression()]
                while (
                    separator := self._peek()
                ) is not None and separator.type == "SEP":
                    self._take()
                    arguments.append(self._expression())
                self._close("FUNC")
                return _function(token.value[:-1].upper(), arguments)
            case _:
                raise ValueError(f"Unsupported v15 token: {token.type}/{token.subtype}")

    def _primary(self) -> Expression:
        token = self._peek()
        if (
            token is not None
            and token.type == "OPERATOR-PREFIX"
            and token.value in ("-", "+")
        ):
            self._take()
            number = _numeric(self._primary())
            if isinstance(number, CellError) or token.value == "+":
                return number
            return -number

        value = self._atom()
        while (token := self._peek()) is not None and token.type == "OPERATOR-POSTFIX":
            if self._take().value != "%":
                raise ValueError("Unsupported v15 postfix operation")
            number = _numeric(value)
            value = number if isinstance(number, CellError) else number / 100
        return value

    def _expression(self, minimum: int = 1) -> Expression:
        value = self._primary()
        while (token := self._peek()) is not None and token.type == "OPERATOR-INFIX":
            precedence, operation = _BINARY[token.value]
            if precedence < minimum:
                break
            self._take()
            left = _numeric(value)
            right = _numeric(self._expression(precedence + 1))
            if isinstance(left, CellError):
                value = left
            elif isinstance(right, CellError):
                value = right
            else:
                try:
                    value = operation(left, right)
                except ZeroDivisionError:
                    value = _DIVISION_ERROR
        return value

    def evaluate(self) -> CellValue:
        value = self._expression()
        if self._peek() is not None:
            raise ValueError("Unconsumed tokens in v15 formula")
        if isinstance(value, tuple):
            return _VALUE_ERROR
        return Fraction(0) if value is None else value


class WorkbookReplay:
    """Evaluate dependencies and errors without reading saved formula results."""

    def __init__(
        self,
        ledger: dict[str, Any],
        *,
        overrides: dict[tuple[str, str], str] | None = None,
    ) -> None:
        self.cells = {
            sheet["catalogue"]["sheet"]: {
                cell["coordinate"]: cell for cell in sheet["cells"]
            }
            for sheet in ledger["sheets"]
        }
        self._values: dict[tuple[str, str], CellValue] = {}
        self._active: set[tuple[str, str]] = set()
        for (sheet, coordinate), value in (overrides or {}).items():
            cell = self.cells.get(sheet, {}).get(coordinate)
            if cell is None or "formula" in cell or cell["stored_type"] != "n":
                raise ValueError(
                    f"Override must name an original numeric input: {sheet}!{coordinate}"
                )
            if not isinstance(value, str):
                raise ValueError("Workbook input overrides must be exact strings")
            self._values[sheet, coordinate] = Fraction(value)

    def value(self, sheet: str, coordinate: str) -> CellValue:
        """Resolve one input, blank or formula result by workbook coordinate."""
        if sheet not in self.cells:
            return CellError("#REF!")
        key = sheet, coordinate
        if key in self._values:
            return self._values[key]
        if key in self._active:
            raise ValueError(f"Circular reference at {sheet}!{coordinate}")
        cell = self.cells[sheet].get(coordinate)
        if cell is None:
            return None
        if "formula" not in cell:
            return _stored(cell)

        self._active.add(key)
        try:
            result = _Formula(self, sheet, cell["formula"]).evaluate()
        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Unable to recalculate {sheet}!{coordinate}: {error}"
            ) from error
        finally:
            self._active.remove(key)
        self._values[key] = result
        return result

    def reference(self, sheet: str, reference: str) -> Expression:
        """Resolve a single cell or range, including references to another sheet."""
        if "!" in reference:
            target, reference = reference.rsplit("!", 1)
            sheet = target.strip("'").replace("''", "'")
        if ":" not in reference:
            return self.value(sheet, reference.replace("$", "").upper())
        left, top, right, bottom = range_boundaries(reference.upper())
        if None in (left, top, right, bottom):
            raise ValueError("Expected a bounded v15 cell range")
        return tuple(
            self.value(sheet, f"{get_column_letter(column)}{row}")
            for row in range(min(top, bottom), max(top, bottom) + 1)
            for column in range(min(left, right), max(left, right) + 1)
        )


def _transport(value: CellValue) -> dict[str, str | bool | None]:
    if isinstance(value, Fraction):
        return {
            "numerator": str(value.numerator),
            "denominator": str(value.denominator),
        }
    if isinstance(value, CellError):
        return {"error": value.code}
    return {"value": value}


def replay_workbook(ledger: dict[str, Any]) -> dict[str, Any]:
    """Return exact formula outcomes, with their original sheet IDs and addresses."""
    replay = WorkbookReplay(ledger)
    sheets = []
    counts: Counter[str] = Counter()
    for sheet in ledger["sheets"]:
        metadata = sheet["catalogue"]
        values = {}
        for cell in sheet["cells"]:
            if "formula" not in cell:
                continue
            coordinate = cell["coordinate"]
            result = _transport(replay.value(metadata["sheet"], coordinate))
            values[coordinate] = result
            counts["formulas"] += 1
            if "error" in result:
                counts["errors"] += 1
        sheets.append({"id": metadata["id"], "formulas": values})
    return {
        "version": 1,
        "source_sha256": ledger["source_sha256"],
        "counts": dict(counts),
        "sheets": sheets,
    }


def main() -> None:
    """Write replayed V15 formula results to a new restricted file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument(
        "output", type=Path, help="New restricted file for formula results"
    )
    args = parser.parse_args()
    result = replay_workbook(json.loads(args.ledger.read_bytes()))
    args.output.touch(mode=0o600, exist_ok=False)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
