# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Recalculate the original v15 workbook dialect from its frozen cell ledger."""

from __future__ import annotations

import argparse
import json
import operator
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
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
type _Rule = Callable[[_Formula], Expression]
type _Pattern = tuple[tuple[str, str | int], ...]

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


def _syntax(token: Token) -> tuple[str, str | int]:
    """Keep the grammar needed to parse the expression, with its data bound at use."""
    if token.type == "OPERAND":
        return token.type, ""
    if token.type == "FUNC":
        return token.type, token.subtype
    if token.type == "OPERATOR-INFIX":
        return token.type, _BINARY[token.value][0]
    return token.type, token.value


def _scale(rule: _Rule, factor: int | Fraction, formula: _Formula) -> Expression:
    value = _numeric(rule(formula))
    return value if isinstance(value, CellError) else value * factor


def _combine(
    operation: Callable[[Fraction, Fraction], Fraction],
    left: Expression,
    right: Expression,
) -> Expression:
    first = _numeric(left)
    second = _numeric(right)
    if isinstance(first, CellError):
        return first
    if isinstance(second, CellError):
        return second
    try:
        return operation(first, second)
    except ZeroDivisionError:
        return _DIVISION_ERROR


class _Formula:
    """Bind one cell's tokens and sheet to a reusable expression."""

    def __init__(
        self, tokens: tuple[Token, ...], reference: Callable[[str], Expression]
    ) -> None:
        self.tokens = tokens
        self.reference = reference
        self.position = 0

    def _operand(self, index: int) -> Expression:
        token = self.tokens[index]
        match token.subtype:
            case "NUMBER":
                return Fraction(token.value)
            case "RANGE":
                return self.reference(token.value)
            case "ERROR":
                return CellError(token.value)
            case _:
                raise ValueError(f"Unsupported v15 token: {token.type}/{token.subtype}")

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

    def _atom(self) -> _Rule:
        index = self.position
        token = self._take()
        match token.type, token.subtype:
            case "OPERAND", _:
                return lambda formula: formula._operand(index)
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
                return lambda formula: _function(
                    formula.tokens[index].value[:-1].upper(),
                    [argument(formula) for argument in arguments],
                )
            case _:
                raise ValueError(f"Unsupported v15 token: {token.type}/{token.subtype}")

    def _primary(self) -> _Rule:
        token = self._peek()
        if (
            token is not None
            and token.type == "OPERATOR-PREFIX"
            and token.value in ("-", "+")
        ):
            self._take()
            return partial(_scale, self._primary(), 1 if token.value == "+" else -1)

        value = self._atom()
        percent_divisor = 1
        while (token := self._peek()) is not None and token.type == "OPERATOR-POSTFIX":
            if self._take().value != "%":
                raise ValueError("Unsupported v15 postfix operation")
            percent_divisor *= 100
        if percent_divisor != 1:
            value = partial(_scale, value, Fraction(1, percent_divisor))
        return value

    def _expression(self, minimum: int = 1) -> _Rule:
        first = self._primary()
        steps: list[tuple[int, _Rule]] = []
        while (token := self._peek()) is not None and token.type == "OPERATOR-INFIX":
            precedence, _ = _BINARY[token.value]
            if precedence < minimum:
                break
            index = self.position
            self._take()
            steps.append((index, self._expression(precedence + 1)))
        if not steps:
            return first

        def calculate(formula: _Formula) -> Expression:
            result = first(formula)
            for index, right in steps:
                _, operation = _BINARY[formula.tokens[index].value]
                result = _combine(operation, result, right(formula))
            return result

        return calculate

    def compile(self) -> _Rule:
        value = self._expression()
        if self._peek() is not None:
            raise ValueError("Unconsumed tokens in v15 formula")
        return value


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
        self._rules: dict[_Pattern, _Rule] = {}
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
            result = self._evaluate(sheet, cell["formula"])
        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Unable to recalculate {sheet}!{coordinate}: {error}"
            ) from error
        finally:
            self._active.remove(key)
        self._values[key] = result
        return result

    def _evaluate(self, sheet: str, formula: str) -> CellValue:
        tokens = tuple(
            token for token in Tokenizer(formula).items if token.type != "WHITE-SPACE"
        )
        pattern = tuple(map(_syntax, tokens))
        expression = _Formula(tokens, partial(self.reference, sheet))
        rule = self._rules.get(pattern)
        if rule is None:
            rule = expression.compile()
            self._rules[pattern] = rule
        value = rule(expression)
        if isinstance(value, tuple):
            return _VALUE_ERROR
        return Fraction(0) if value is None else value

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
